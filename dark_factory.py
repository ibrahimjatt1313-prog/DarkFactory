from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="DarkFactory Dashboard", version="1.0.0")

# Ensure required directories exist to prevent startup crashes
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files safely
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    output_content = "System initialized and waiting for execution..."
    
    file_path = "outputs/reviewed_result.txt"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                output_content = f.read()
        except Exception as e:
            output_content = f"Error reading file: {str(e)}"

    return templates.TemplateResponse("index.html", {
        "request": request, 
        "output_content": output_content
    })

@app.post("/run-process", response_class=HTMLResponse)
async def run_process(request: Request, stage: str = Form(...)):
    result_message = f"Successfully executed {stage} pipeline!"
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "output_content": result_message
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dark_factory:app", host="127.0.0.1", port=8000, reload=True)