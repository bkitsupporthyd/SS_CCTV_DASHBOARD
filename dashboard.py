from flask import Flask, render_template
import os

app = Flask(__name__)

# Load IPs from file
def load_ips():
    with open("ip_list.txt", "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Ping check
def is_reachable(ip):
    response = os.system(f"ping -n 1 -w 1000 {ip} >nul")  # Windows
    return response == 0

@app.route("/")
def dashboard():
    ip_list = load_ips()
    status_list = []

    for ip in ip_list:
        reachable = is_reachable(ip)
        status_list.append({"ip": ip, "status": "UP" if reachable else "DOWN"})

    return render_template("dashboard.html", status_list=status_list)

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, host="127.0.0.1", port=5000)
