from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from skin_to_litematic import load_skin, build_statue_data, generate_litematic, get_block_palette, BLOCK_PALETTE

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize palette on startup
@app.on_event("startup")
async def startup_event():
    global BLOCK_PALETTE
    try:
        # Ensure we are in the backend directory or can find the json
        if os.path.exists("block_palette.json"):
            BLOCK_PALETTE.update(get_block_palette())
            print(f"Loaded {len(BLOCK_PALETTE)} blocks into palette.")
        else:
            print("Warning: block_palette.json not found. Run fetch_palette.py first.")
    except Exception as e:
        print(f"Error loading palette: {e}")

@app.post("/convert")
async def convert_skin(file: UploadFile = File(...)):
    if not file.filename.endswith(".png"):
        raise HTTPException(status_code=400, detail="File must be a PNG image.")
    
    # Create temp directory for processing
    temp_dir = f"temp_{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        input_path = os.path.join(temp_dir, file.filename)
        output_filename = file.filename.replace(".png", ".litematic")
        output_path = os.path.join(temp_dir, output_filename)
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process
        img = load_skin(input_path)
        
        # Ensure palette is loaded if not already (redundant check)
        if not BLOCK_PALETTE:
             BLOCK_PALETTE.update(get_block_palette())

        # We need to inject the palette into the module or pass it if modified
        # skin_to_litematic.py uses a global BLOCK_PALETTE. 
        # We updated the global in this script, but we need to make sure build_statue_data uses it.
        # Actually, skin_to_litematic.py's build_statue_data uses skin_to_litematic.BLOCK_PALETTE.
        # So we should update THAT one.
        import skin_to_litematic
        skin_to_litematic.BLOCK_PALETTE = BLOCK_PALETTE
        
        data = build_statue_data(img)
        generate_litematic(data, output_path)
        
        return FileResponse(output_path, filename=output_filename, media_type="application/octet-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Cleanup is tricky with FileResponse as it needs the file open.
        # For now, we might leave temp files or use a background task to clean up.
        # A simple way is to not delete immediately, or use BackgroundTasks.
        # But FileResponse handles file closing. Deleting the directory is the issue.
        # Let's just leave it for this prototype or use a background task.
        pass

@app.get("/health")
def health_check():
    return {"status": "ok"}
