from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="L'Étoile Noire & DarkFactory Command Center", version="2.1.0")

# Ensure required directories exist to prevent startup crashes
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files safely
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Mock database for stations / tables
TABLES_DB = [
    {"id": 1, "seats": 2, "status": "Available"},
    {"id": 2, "seats": 4, "status": "Reserved"},
    {"id": 3, "seats": 6, "status": "Available"},
    {"id": 4, "seats": 8, "status": "Available"},
    {"id": 5, "seats": 2, "status": "Reserved"},
]

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request, message: str = None):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "tables": TABLES_DB,
        "message": message
    })

@app.post("/reserve", response_class=HTMLResponse)
async def reserve_table(
    request: Request, 
    table_id: int = Form(...), 
    customer_name: str = Form(...),
    country_code: str = Form(...),
    phone_number: str = Form(...)
):
    # Find and update table status
    table_found = False
    for table in TABLES_DB:
        if table["id"] == table_id:
            table_found = True
            if table["status"] == "Reserved":
                message = f"⚠️ Warning: Station #{table_id} is already reserved!"
            else:
                table["status"] = "Reserved"
                full_phone = f"{country_code} {phone_number}"
                message = f"✅ Success: Slot #{table_id} securely locked for {customer_name} ({full_phone})."
            break
            
    if not table_found:
        message = f"⚠️ Error: Station #{table_id} does not exist in the matrix."

    return templates.TemplateResponse("index.html", {
        "request": request,
        "tables": TABLES_DB,
        "message": message
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("dark_factory_app:app", host="127.0.0.1", port=8000, reload=True)