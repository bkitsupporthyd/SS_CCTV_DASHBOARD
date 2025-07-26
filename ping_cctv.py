import os
import time
import json
import subprocess
import pytz
from datetime import datetime

def run_ping_with_progress():
    PING_COUNT = 3
    PING_TIMEOUT = 0.5  # in seconds
    MAX_REPORTS = 3
    IP_LIST_FILE = "ip_list.txt"
    RESULT_FILE = "results.json"
    REPORT_DIR = "reports"
    TIMEZONE = "Asia/Kolkata"

    ip_list = []
    with open(IP_LIST_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("=", 1)
            if len(parts) == 2:
                ip_list.append((parts[0].strip(), parts[1].strip()))

    os.makedirs(REPORT_DIR, exist_ok=True)
    results = []
    total = len(ip_list)

    for idx, (ip, description) in enumerate(ip_list):
        try:
            completed = subprocess.run(
                ["ping", "-n", str(PING_COUNT), "-w", str(int(PING_TIMEOUT * 1000)), ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=PING_COUNT * PING_TIMEOUT + 1
            )
            status = "Up" if completed.returncode == 0 else "Down"
        except subprocess.TimeoutExpired:
            status = "Down (Timeout)"
        except Exception as e:
            status = f"Error: {str(e)}"
        results.append({
            "ip": ip,
            "description": description,
            "status": status
        })
        # Progress update after each IP
        tz = pytz.timezone(TIMEZONE)
        refresh_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
        output = {
            "last_refreshed": refresh_time,
            "data": results.copy()
        }
        yield idx, total, output

    # Write results
    with open(RESULT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    report_file = os.path.join(REPORT_DIR, f"report_{int(time.time())}.json")
    with open(report_file, "w") as f:
        json.dump(output, f, indent=2)
    all_reports = sorted(os.listdir(REPORT_DIR), key=lambda x: os.path.getmtime(os.path.join(REPORT_DIR, x)))
    while len(all_reports) > MAX_REPORTS:
        to_delete = all_reports.pop(0)
        os.remove(os.path.join(REPORT_DIR, to_delete))


def run_ping_and_save_results():
    # For compatibility with existing code
    for _idx, _total, _output in run_ping_with_progress():
        pass

if __name__ == "__main__":
    run_ping_and_save_results()
