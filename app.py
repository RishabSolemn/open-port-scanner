# app.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scanner import scan_ports, parse_port_input
from models import init_db, add_target, list_targets

# Render provides PORT, but uvicorn uses it from env in start command; keeping this is harmless.
PORT = int(os.getenv("PORT", "10000"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "targets": list_targets(), "message": ""}
    )

@app.post("/scan", response_class=HTMLResponse)
async def do_scan(
    request: Request,
    host: str = Form(...),
    ports: str | None = Form(None),
    email: str | None = Form(None),
):
    plist = parse_port_input(ports or "")
    opened = scan_ports(host, plist)
    msg = f"Open ports on {host}: {opened or 'None'}"

    # Optionally save target for hourly scans
    if email:
        add_target(host, plist, email)
        msg += " — Target saved for hourly scan."

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "targets": list_targets(), "message": msg, "opened": opened, "host": host}
    )
