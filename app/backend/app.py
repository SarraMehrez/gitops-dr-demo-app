from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route("/api/status", methods=["GET"])
def status():
    hostname = socket.gethostname()
    return jsonify({
        "message": "GitOps DR Demo API is healthy",
        "pod": hostname,
        "env": os.environ.get("ENVIRONMENT", "dev")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)