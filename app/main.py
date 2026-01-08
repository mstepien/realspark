from fastapi import FastAPI, Request, Response, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.database import init_db, save_stats, get_aggregate_stats
from app.storage import upload_to_gcs
from app.analysis import prepare_image, compute_hog, detect_ai, compute_fractal_stats
from app.analysis.histogram import compute_histogram
import io
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.models import UploadResponse, TaskStatus, AggregateStats

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/tmp", StaticFiles(directory="tmp"), name="tmp")

templates = Jinja2Templates(directory="app/templates")

from app.analysis.aiclassifiers import warmup_classifier

@app.on_event("startup")
def on_startup():
    init_db()
    # Preload model to prevent first-request timeout
    # Running in a separate thread to avoid blocking startup health checks if they exist,
    # though strict startup often waits.
    warmup_classifier()

tasks = {}
active_sessions = {} # session_id -> (task_id, asyncio.Task)
executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 4)
STEP_TIMEOUT = 90 # seconds for each individual step
STEPS = [
    "Preprocessing",
    "Histogram Analysis",
    "HOG Analysis", 
    "AI Classifier",
    "Fractal Analysis",
    "Uploading to Storage",
    "Saving to Database"
]

async def process_image_task(task_id: str, session_id: str, content: bytes, filename: str):
    logger = uvicorn.config.logger
    loop = asyncio.get_event_loop()

    async def _analyze():
        try:
            # Phase 1: Sequential Initialization
            tasks[task_id]["status"] = "Preprocessing..."
            tasks[task_id]["current_step"] = "Preprocessing"
            tasks[task_id]["progress"] = 5 
            tasks[task_id]["partial_results"] = {}
            
            # Step 1: Preprocessing
            try:
                image, np_image, width, height, mean_color = await asyncio.wait_for(
                    loop.run_in_executor(executor, prepare_image, content),
                    timeout=STEP_TIMEOUT
                )
            except asyncio.TimeoutError:
                raise Exception("Preprocessing timed out")
                
            tasks[task_id]["completed_steps"].append("Preprocessing")
            tasks[task_id]["progress"] = 10

            # Phase 2: Parallel Analysis Cluster
            tasks[task_id]["status"] = "Performing Parallel Analysis & Upload..."
            tasks[task_id]["current_step"] = "Parallel Analysis & Upload"

            async def run_histogram():
                try:
                    data = await asyncio.wait_for(
                        loop.run_in_executor(executor, compute_histogram, np_image),
                        timeout=STEP_TIMEOUT
                    )
                    tasks[task_id]["partial_results"].update(data)
                    tasks[task_id]["completed_steps"].append("Histogram Analysis")
                    return data
                except asyncio.TimeoutError:
                    logger.warning(f"Histogram analysis timed out for task {task_id}")
                    tasks[task_id]["timed_out_steps"].append("Histogram Analysis")
                    return {"histogram_r": [], "histogram_g": [], "histogram_b": []}

            async def run_hog():
                try:
                    fd, hog_buf = await asyncio.wait_for(
                        loop.run_in_executor(executor, compute_hog, np_image),
                        timeout=STEP_TIMEOUT
                    )
                    hog_filename = f"hog_{task_id}.png"
                    hog_path = os.path.join("tmp", hog_filename)
                    with open(hog_path, "wb") as f:
                        f.write(hog_buf.getvalue())
                    tasks[task_id]["partial_results"]["hog_image_url"] = f"/tmp/{hog_filename}"
                    tasks[task_id]["completed_steps"].append("HOG Analysis")
                    return fd, hog_buf, hog_filename
                except asyncio.TimeoutError:
                    logger.warning(f"HOG analysis timed out for task {task_id}")
                    tasks[task_id]["timed_out_steps"].append("HOG Analysis")
                    return [], None, None

            async def run_ai():
                try:
                    score = await asyncio.wait_for(
                        loop.run_in_executor(executor, detect_ai, image),
                        timeout=STEP_TIMEOUT
                    )
                    tasks[task_id]["partial_results"]["ai_probability"] = score
                    tasks[task_id]["completed_steps"].append("AI Classifier")
                    return score
                except asyncio.TimeoutError:
                    logger.warning(f"AI analysis timed out for task {task_id}")
                    tasks[task_id]["timed_out_steps"].append("AI Classifier")
                    return None

            async def run_fractal():
                try:
                    # Validating fractal time with a timeout (e.g. 5s)
                    # If it hangs, we abandon this specific sub-result but keep the session alive.
                    f_stats = await asyncio.wait_for(
                        loop.run_in_executor(executor, compute_fractal_stats, np_image),
                        timeout=STEP_TIMEOUT
                    )
                    logger.info(f"Fractal analysis computed: {f_stats}")
                    tasks[task_id]["partial_results"].update(f_stats)
                    tasks[task_id]["completed_steps"].append("Fractal Analysis")
                    return f_stats
                except asyncio.TimeoutError:
                    logger.warning(f"Fractal analysis timed out for task {task_id}")
                    # Mark as complete so UI doesn't hang, but return default/empty stats
                    tasks[task_id]["partial_results"].update({"fd_default": None})
                    tasks[task_id]["completed_steps"].append("Fractal Analysis")
                    tasks[task_id]["timed_out_steps"].append("Fractal Analysis")
                    return {"fd_default": None} 
                except Exception as e:
                    logger.error(f"Fractal analysis failed with error: {e}")
                    tasks[task_id]["partial_results"].update({"fd_default": None})
                    tasks[task_id]["completed_steps"].append("Fractal Analysis")
                    tasks[task_id]["timed_out_steps"].append("Fractal Analysis")
                    return {"fd_default": None}

            async def run_upload():
                try:
                    file_obj = io.BytesIO(content)
                    url = await asyncio.wait_for(
                        upload_to_gcs(file_obj, filename),
                        timeout=STEP_TIMEOUT
                    )
                    tasks[task_id]["completed_steps"].append("Uploading to Storage")
                    return url
                except asyncio.TimeoutError:
                    logger.warning(f"Upload timed out for task {task_id}")
                    tasks[task_id]["timed_out_steps"].append("Uploading to Storage")
                    return None

            # Execute parallel tasks
            res_hist, res_hog, res_ai, res_frac, res_upload = await asyncio.gather(
                run_histogram(),
                run_hog(),
                run_ai(),
                run_fractal(),
                run_upload(),
                return_exceptions=True
            )

            # Check for errors in parallel cluster
            for result in [res_hist, res_hog, res_ai, res_frac, res_upload]:
                if isinstance(result, Exception):
                    raise result

            fd, hog_image_buffer, hog_filename = res_hog
            ai_score = res_ai
            fractal_stats = res_frac
            url = res_upload

            analysis_results = {
                "width": width,
                "height": height,
                "mean_color": mean_color.tolist(),
                "hog_features": fd if isinstance(fd, list) else fd.tolist(),
                "hog_image_buffer": hog_image_buffer,
                "ai_probability": ai_score,
                **fractal_stats
            }
            tasks[task_id]["progress"] = 85

            # Phase 3: Final Sequential Steps (DB Only)
            tasks[task_id]["status"] = "Saving to Database..."
            tasks[task_id]["current_step"] = "Saving to Database"
            
            image_id = save_stats(filename, url, analysis_results)
            
            if 'hog_image_buffer' in analysis_results:
                del analysis_results['hog_image_buffer']
            analysis_results['hog_image_url'] = f"/tmp/{hog_filename}"

            tasks[task_id]["completed_steps"].append("Saving to Database")
            tasks[task_id]["progress"] = 100
            tasks[task_id]["status"] = "Complete"
            tasks[task_id]["current_step"] = None
            tasks[task_id]["result"] = {"id": image_id, "url": url, "stats": analysis_results}
            
        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was abandoned/cancelled")
            tasks[task_id]["status"] = "Abandoned"
            tasks[task_id]["error"] = "Task abandoned because a new upload was started."
            raise
        except Exception as e:
            logger.error(f"Task failed: {e}")
            tasks[task_id]["status"] = "Error"
            tasks[task_id]["error"] = str(e)

    try:
        await _analyze()
    # Timeout handling is now distributed per-step
    except asyncio.CancelledError:
        # Already handled inside _analyze, but ensuring it propagates
        raise
    except Exception as e:
        logger.error(f"Unexpected error in task {task_id}: {e}")
        tasks[task_id]["status"] = "Error"
        tasks[task_id]["error"] = str(e)
    finally:
        # Cleanup session tracking
        if active_sessions.get(session_id) and active_sessions[session_id][0] == task_id:
            active_sessions.pop(session_id, None)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload", response_model=UploadResponse)
async def start_upload(request: Request, response: Response, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Session tracking for task abandonment
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie("session_id", session_id)
        
    content = await file.read()

    # Abandon previous task if exists for this session
    # Doing this AFTER read prevents race conditions where multiple requests
    # pass the check before either registers the new task.
    if session_id in active_sessions:
        old_task_id, old_task = active_sessions[session_id]
        if not old_task.done():
            old_task.cancel()
            uvicorn.config.logger.info(f"Cancelling previous task {old_task_id} for session {session_id}")
            if old_task_id in tasks:
                tasks[old_task_id]["status"] = "Abandoned"
                tasks[old_task_id]["error"] = "Task abandoned because a new upload was started."
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "Starting...",
        "progress": 0,
        "steps": STEPS,
        "current_step": "Starting...",
        "completed_steps": [],
        "timed_out_steps": [],
        "partial_results": {}
    }
    
    # Use loop.create_task for manual control over cancellation
    loop = asyncio.get_running_loop()
    task = loop.create_task(process_image_task(task_id, session_id, content, file.filename))
    active_sessions[session_id] = (task_id, task)
    
    return {"task_id": task_id}

@app.get("/progress/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/stats", response_model=AggregateStats)
def get_stats():
    return get_aggregate_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
