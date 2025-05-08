from flask import Flask, request, jsonify
from db import get_user_by_query

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = get_user_by_query({"username": username, "password": password})
    if user:
        return jsonify({"message": "Login successful", "role": user.get("role", "user")})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/profile", methods=["GET"])
def profile():
    user_id = request.args.get("id")
    if not user_id:
        return jsonify({"error": "Missing ID"}), 400
    user = get_user_by_query({"_id": user_id})
    if user:
        return jsonify({"username": user["username"], "email": user["email"]})
    return jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
