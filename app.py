from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import json
import os
from ping_cctv import run_ping_and_save_results, run_ping_with_progress
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
socketio = SocketIO(app)

USERNAME = 'admin'
PASSWORD = 'admin123'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    # Do NOT auto-refresh on page load
    results = {"last_refreshed": "N/A", "data": []}
    if os.path.exists("results.json"):
        try:
            with open("results.json", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:
                    results = json.loads(file_content)
        except Exception as e:
            print(f"Error reading results.json: {e}")
    return render_template("dashboard.html", results=results)

@app.route("/api/results")
@login_required
def api_results():
    run_ping_and_save_results()
    results = {"last_refreshed": "N/A", "data": []}
    if os.path.exists("results.json"):
        try:
            with open("results.json", encoding="utf-8") as f:
                file_content = f.read().strip()
                if file_content:
                    results = json.loads(file_content)
        except Exception as e:
            print(f"Error reading results.json: {e}")
    return jsonify(results)

@app.route("/refresh", methods=["POST"])
@login_required
def refresh():
    from ping_cctv import run_ping_with_progress
    last_output = None
    for _idx, _total, output in run_ping_with_progress():
        last_output = output
    return jsonify(last_output)

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    ip_file = "ip_list.txt"
    success = False

    if request.method == "POST":
        try:
            ip_data = request.form.get("ip_list")
            with open(ip_file, "w", encoding="utf-8") as f:
                f.write(ip_data)
            success = True
        except Exception as e:
            print("Error writing to ip_list.txt:", e)

    ip_data = ""
    if os.path.exists(ip_file):
        with open(ip_file, "r", encoding="utf-8") as f:
            ip_data = f.read()

    return render_template("admin.html", ip_data=ip_data, success=success)

@socketio.on('start_ping')
def handle_start_ping():
    last_output = None
    for idx, total, output in run_ping_with_progress():
        emit('progress', {'current': idx, 'total': total}, broadcast=False)
        last_output = output
    if last_output:
        emit('ping_results', last_output, broadcast=False)

if __name__ == "__main__":
    print("Launching Flask-SocketIO on http://0.0.0.0:5000 ...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
