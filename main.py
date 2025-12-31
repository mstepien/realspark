from fastapi import FastAPI, Request, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from database import init_db, save_stats, get_aggregate_stats
from storage import upload_to_gcs
from analysis import prepare_image, compute_hog, detect_ai, compute_fractal_stats
import io
import os
import uuid
import asyncio

app = FastAPI()

app.mount("/tmp", StaticFiles(directory="tmp"), name="tmp")

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    init_db()

tasks = {}
STEPS = [
    "Preprocessing",
    "HOG Analysis", 
    "AI Classifier",
    "Fractal Analysis",
    "Uploading to Storage",
    "Saving to Database"
]

async def process_image_task(task_id: str, content: bytes, filename: str):
    logger = uvicorn.config.logger
    try:
        # Step 1: Preprocessing (Weight 1)
        tasks[task_id]["status"] = "Preprocessing..."
        tasks[task_id]["current_step"] = "Preprocessing"
        tasks[task_id]["progress"] = 5 
        
        # Simulate tiny work
        await asyncio.sleep(0.1) 
        tasks[task_id]["completed_steps"].append("Preprocessing")
        
        # Step 2: HOG Analysis (Weight 5)
        tasks[task_id]["status"] = "HOG Analysis..."
        tasks[task_id]["current_step"] = "HOG Analysis"
        tasks[task_id]["progress"] = 10

        image, np_image, width, height, mean_color = await asyncio.to_thread(prepare_image, content)
        fd, hog_image_buffer = await asyncio.to_thread(compute_hog, np_image)

        tasks[task_id]["completed_steps"].append("HOG Analysis")
        tasks[task_id]["progress"] = 25

        # Step 3: AI Classifier (Weight 5)
        tasks[task_id]["status"] = "AI Classifier..."
        tasks[task_id]["current_step"] = "AI Classifier"
        tasks[task_id]["progress"] = 25 # Start where previous left off

        ai_score = await asyncio.to_thread(detect_ai, image)
        tasks[task_id]["completed_steps"].append("AI Classifier")
        tasks[task_id]["progress"] = 40

        # Step 4: Fractal Analysis (Weight 10)
        tasks[task_id]["status"] = "Fractal Analysis..."
        tasks[task_id]["current_step"] = "Fractal Analysis"
        tasks[task_id]["progress"] = 40
        
        fractal_stats = await asyncio.to_thread(compute_fractal_stats, np_image)
        tasks[task_id]["completed_steps"].append("Fractal Analysis")
        tasks[task_id]["progress"] = 70

        stats = {
            "width": width,
            "height": height,
            "mean_color": mean_color.tolist(),
            "hog_features": fd.tolist(),
            "hog_image_buffer": hog_image_buffer,
            "ai_probability": ai_score,
            **fractal_stats
        }

        tasks[task_id]["progress"] = 75

        # Step 5: Upload to GCS (Weight 1)
        tasks[task_id]["status"] = "Uploading to Storage..."
        tasks[task_id]["current_step"] = "Uploading to Storage"
        file_obj = io.BytesIO(content)
        url = await upload_to_gcs(file_obj, filename)
        tasks[task_id]["completed_steps"].append("Uploading to Storage")
        tasks[task_id]["progress"] = 85
        
        # Step 6: Save to DB (Weight 1)
        tasks[task_id]["status"] = "Saving to Database..."
        tasks[task_id]["current_step"] = "Saving to Database"
        image_id = save_stats(filename, url, stats)
        
        # Save HOG image locally
        if 'hog_image_buffer' in stats:
            hog_buffer = stats.pop('hog_image_buffer')
            hog_filename = f"hog_{image_id}.png"
            hog_path = os.path.join("tmp", hog_filename)
            
            with open(hog_path, "wb") as f:
                f.write(hog_buffer.getvalue())
                
            stats['hog_image_url'] = f"/tmp/{hog_filename}"
            
        tasks[task_id]["completed_steps"].append("Saving to Database")
        tasks[task_id]["progress"] = 100
        tasks[task_id]["status"] = "Complete"
        tasks[task_id]["current_step"] = None
        tasks[task_id]["result"] = {"id": image_id, "url": url, "stats": stats}
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
        tasks[task_id]["status"] = "Error"
        tasks[task_id]["error"] = str(e)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload")
async def start_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "status": "Starting...",
        "progress": 0,
        "steps": STEPS,
        "current_step": "Starting...",
        "completed_steps": []
    }
    
    background_tasks.add_task(process_image_task, task_id, content, file.filename)
    
    return {"task_id": task_id}

@app.get("/progress/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/stats")
def get_stats():
    return get_aggregate_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
