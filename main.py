from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from database import init_db, save_stats, get_aggregate_stats
from storage import upload_to_gcs
from analysis import analyze_image
import io

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    content = await file.read()
    
    # Analyze
    try:
        stats = analyze_image(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    # Upload to GCS
    # We need a file-like object for GCS upload, so we wrap bytes
    file_obj = io.BytesIO(content)
    url = await upload_to_gcs(file_obj, file.filename)
    
    # Save to DB
    image_id = save_stats(file.filename, url, stats)
    
    return {"id": image_id, "url": url, "stats": stats}

@app.get("/stats")
def get_stats():
    return get_aggregate_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
