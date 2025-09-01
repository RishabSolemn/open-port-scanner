# scanner.py
import os
import socket
import concurrent.futures

DEFAULT_PORTS = [20,21,22,23,25,53,80,110,143,443,465,587,993,995,3306,3389,8080,8443]
DEFAULT_TIMEOUT = float(os.getenv("SCAN_TIMEOUT", "0.8"))  # allow override via env

def _resolve_host(host: str) -> str:
    # Resolve once; prefer IPv4 for simplicity on classroom demos
    try:
        return socket.getaddrinfo(host, None, family=socket.AF_INET)[0][4][0]
    except Exception as e:
        raise RuntimeError(f"Could not resolve host '{host}': {e}")

def is_port_open(ip: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            return s.connect_ex((ip, port)) == 0
        except Exception:
            return False

def scan_ports(host: str, ports=None, timeout: float = DEFAULT_TIMEOUT):
    ports = ports or DEFAULT_PORTS
    if not ports:
        return []
    # Resolve once
    ip = _resolve_host(host)
    results = []
    max_workers = min(len(ports), 200)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(is_port_open, ip, p, timeout): p for p in ports}
        for fut in concurrent.futures.as_completed(futs):
            p = futs[fut]
            try:
                if fut.result():
                    results.append(p)
            except Exception:
                # swallow per-port errors; continue scanning
                pass
    return sorted(results)

def parse_port_input(port_text: str):
    """Accept '22,80,443' or '1-1024' or mixed '22,80-90'."""
    if not port_text:
        return None
    ports = set()
    for chunk in port_text.split(","):
        part = chunk.strip()
        if not part:
            continue
        try:
            if "-" in part:
                a, b = part.split("-", 1)
                a, b = int(a), int(b)
                lo, hi = min(a, b), max(a, b)
                # guard against outrageous ranges on free instances
                hi = min(hi, 65535)
                for p in range(max(1, lo), hi + 1):
                    ports.add(p)
            else:
                p = int(part)
                if 1 <= p <= 65535:
                    ports.add(p)
        except ValueError:
            # ignore non-numeric pieces gracefully
            continue
    return sorted(ports) if ports else None
