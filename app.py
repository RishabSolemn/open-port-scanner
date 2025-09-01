# app.py
import os, time
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scanner import scan_ports, parse_port_input, _resolve_host
from models import init_db, add_target, list_targets

# Render provides PORT via env; uvicorn uses it from the start command.
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
    host = (host or "").strip()
    plist = parse_port_input(ports or "")

    # Try to resolve once (for display); don't fail the whole request if it can't resolve here.
    resolved_ip = None
    try:
        resolved_ip = _resolve_host(host)
    except Exception:
        pass

    t0 = time.perf_counter()
    try:
        opened = scan_ports(host, plist)
        elapsed = round(time.perf_counter() - t0, 3)
        msg = f"Open ports on {host}: {opened or 'None'}"

        if email:
            add_target(host, plist, email)
            msg += " — Target saved for hourly scan."

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "targets": list_targets(),
                "message": msg,
                "opened": opened,
                "host": host,
                "resolved_ip": resolved_ip,
                "elapsed": elapsed,
            }
        )
    except Exception:
        # Friendly message instead of 500
        hint = ""
        if host.lower().replace(" ", "") in {"nmap.scanme.org", "scanme.nmap.org"}:
            hint = " (Tip: correct demo host is 'scanme.nmap.org')"
        err = f"Could not resolve host '{host}'.{hint}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "targets": list_targets(),
                "message": err,
                "opened": None,
                "host": host
            }
        )
