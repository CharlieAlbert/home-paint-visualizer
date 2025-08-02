from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "images"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Hello, World"}


@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...)):
    ext = image.filename.split(".")[-1].lower()
    if ext not in ["jpg", "png", "jpeg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    file_id = f"{uuid4()}.{ext}"
    file_path = UPLOAD_DIR / file_id

    with open(file_path, "wb") as f:
        content = await image.read()
        f.write(content)

    return {
        "id": file_id.split(".")[0],
        "filename": image.filename,
        "url": f"/static/images/{file_id}",
    }


@app.get("/images")
async def list_images():
    if not UPLOAD_DIR.exists():
        return JSONResponse(content={"images": []})
    image_files = [
        {"filename": img.name, "url": f"{UPLOAD_DIR}/{img.name}"}
        for img in UPLOAD_DIR.iterdir()
        if img.is_file() and img.suffix.lower() in [".jpg", ".jpeg", ".png"]
    ]

    return {"images": image_files}


@app.get("/images/{file_name}")
async def get_images(file_name: str):
    file_path = UPLOAD_DIR / file_name
    if not file_path.exists():
        raise HTTPException(status_code=400, detail="File does not exist")
    return FileResponse(file_path)
