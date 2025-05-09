from flask import Flask, request, jsonify
import os
from tasks import process_file

app = Flask(__name__)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return "No file provided", 400
    filepath = os.path.join(UPLOAD_DIR, f.filename)
    f.save(filepath)
    return jsonify({"message": "File saved", "path": filepath})

@app.route("/start-task", methods=["POST"])
def start_task():
    file = request.form.get("file")
    if not file:
        return "Missing filename", 400
    task = process_file.delay(file)
    return jsonify({"task_id": task.id})

if __name__ == "__main__":
    app.run(debug=True)
