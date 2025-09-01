# cron_scan.py — PSX branded hourly (or manual) scan email
from scanner import scan_ports, parse_port_input
from emailer import send_email

def run():
    # === EDIT THESE 3 LINES IF YOU WANT ===
    host = "scanme.nmap.org"          # demo host; or use one you own/have permission for
    ports_text = "22,80,443"          # e.g. "1-1024" or "22,80,443"
    to_email = "rishabsolemn@gmail.com"  # verified sender/recipient
    # ======================================

    ports = parse_port_input(ports_text)
    opened = scan_ports(host, ports)

    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;background:#0d1117;color:#f0f6fc;padding:16px">
      <h2 style="color:#2575fc;margin:0 0 8px 0;">PSX – Port Scanner Xtreme Report</h2>
      <p style="margin:6px 0"><b>Host:</b> {host}</p>
      <p style="margin:6px 0"><b>Ports scanned:</b> {ports_text}</p>
      <p style="margin:6px 0"><b>Open Ports:</b> {opened or 'None'}</p>
      <hr style="border:none;border-top:1px solid #27313e;margin:14px 0">
      <p style="font-size:12px;color:#9fb3c9;margin:0">Note: Scan only hosts you have permission to test.</p>
    </div>
    """
    subject = f"[PSX Report] {host} — open: {len(opened)}"
    send_email(to_email, subject, html)
    print(f"Scanned {host}: {opened}")

if __name__ == "__main__":
    run()
