from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "✅ Flask works on 172.16.5.30!"

if __name__ == "__main__":
    print("Starting...")
    app.run(host="0.0.0.0", port=5000)
