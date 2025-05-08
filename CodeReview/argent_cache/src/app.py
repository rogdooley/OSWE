from flask import Flask, request, make_response

app = Flask(__name__)

@app.route("/")
def index():
    user = request.headers.get("X-User", "guest")
    resp = make_response(f"Hello, {user}!")
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp

if __name__ == "__main__":
    app.run()
