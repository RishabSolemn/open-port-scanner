# app.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scanner import scan_ports, parse_port_input
from models import init_db, add_target, list_targets

PORT = int(os.getenv("PORT", "10000"))  # Render sets PORT
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html",
        {"request": request, "targets": list_targets(), "message": ""})

@app.post("/scan", response_class=HTMLResponse)
def do_scan(request: Request, host: str = Form(...), ports: str = Form(""), email: str = Form("")):
    plist = parse_port_input(ports)
    opened = scan_ports(host, plist)
    msg = f"Open ports on {host}: {opened or 'None'}"
    # Optionally save target for cron if email provided
    if email:
        from models import add_target
        add_target(host, plist, email)
        msg += " — Target saved for hourly scan."
    return templates.TemplateResponse("index.html",
        {"request": request, "targets": list_targets(), "message": msg, "opened": opened, "host": host})

