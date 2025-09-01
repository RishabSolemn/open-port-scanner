# cron_scan.py  — simple hourly scan with a hard-coded target (no DB)
from scanner import scan_ports, parse_port_input
from emailer import send_email

def run():
    # === EDIT THESE 3 LINES IF YOU WANT ===
    host = "scanme.nmap.org"     # demo host; or use a host you own/have permission for
    ports_text = "22,80,443"     # e.g. "1-1024" or "22,80,443"
    to_email = "rishabsolemn@gmail.com"  # your verified sender/recipient
    # ======================================

    ports = parse_port_input(ports_text)
    opened = scan_ports(host, ports)

    html = f"""
    <h3>Hourly Port Scan Report</h3>
    <p><b>Host:</b> {host}</p>
    <p><b>Ports scanned:</b> {ports_text}</p>
    <p><b>Open Ports:</b> {opened or 'None'}</p>
    """

    send_email(to_email, f"[Scan] {host} — open: {len(opened)}", html)
    print(f"Scanned {host}: {opened}")

if __name__ == "__main__":
    run()
