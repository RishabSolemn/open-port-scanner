# cron_scan.py
from models import list_targets, save_result
from scanner import scan_ports
from emailer import send_email

def html_report(host, opened):
    opened_str = ", ".join(map(str, opened)) if opened else "None"
    return f"<h3>Hourly Port Scan</h3><p><b>Host:</b> {host}</p><p><b>Open ports:</b> {opened_str}</p>"

def run_all():
    targets = list_targets()
    if not targets:
        print("No targets configured.")
        return
    for t in targets:
        opened = scan_ports(t["host"], t["ports"])
        save_result(t["id"], opened)
        send_email(
            to_email=t["email"],
            subject=f"[Scan] {t['host']} open ports: {len(opened)}",
            html=html_report(t["host"], opened)
        )
        print(f"Scanned {t['host']}: {opened}")

if __name__ == "__main__":
    run_all()

