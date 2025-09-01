# scanner.py
import socket
import concurrent.futures

DEFAULT_PORTS = [20,21,22,23,25,53,80,110,143,443,465,587,993,995,3306,3389,8080,8443]

def is_port_open(host: str, port: int, timeout: float = 0.8) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            return s.connect_ex((host, port)) == 0
        except Exception:
            return False

def scan_ports(host: str, ports=None, timeout: float = 0.8):
    ports = ports or DEFAULT_PORTS
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as ex:
        futs = {ex.submit(is_port_open, host, p, timeout): p for p in ports}
        for fut in concurrent.futures.as_completed(futs):
            p = futs[fut]
            open_ = False
            try:
                open_ = fut.result()
            except Exception:
                open_ = False
            if open_:
                results.append(p)
    return sorted(results)

def parse_port_input(port_text: str):
    """Accept '22,80,443' or '1-1024' or mixed '22,80-90'."""
    if not port_text:
        return None
    ports = set()
    for chunk in port_text.split(","):
        part = chunk.strip()
        if "-" in part:
            a,b = part.split("-",1)
            a,b = int(a), int(b)
            for p in range(min(a,b), max(a,b)+1):
                ports.add(p)
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 1 <= p <= 65535)

