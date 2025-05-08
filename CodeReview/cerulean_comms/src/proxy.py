from flask import Flask, request, redirect
import requests

app = Flask(__name__)

@app.route("/ws-proxy")
def ws_proxy():
    target = request.args.get("target")
    if not target.startswith("ws://") and not target.startswith("wss://"):
        return "Invalid target", 400
    # Simulated upgrade
    return redirect(target, code=307)

if __name__ == "__main__":
    app.run(port=5001)
