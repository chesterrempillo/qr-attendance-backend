from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)  # allow React frontend to send requests

# Mock database
students = {"2023-001": "Alice", "2023-002": "Bob"}
attendance_records = []

@app.route("/record_attendance", methods=["POST", "OPTIONS"])
def record_attendance():
    if request.method == "OPTIONS":
        # Preflight request
        response = app.make_default_options_response()
        return response

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data sent"}), 400

    student_id = data.get("student_id")
    if student_id not in students:
        return jsonify({"error": "Student not found"}), 404

    # Save attendance
    now = datetime.now()
    record = {
        "student_id": student_id,
        "name": students[student_id],
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "device": request.headers.get("User-Agent", "Unknown"),
        "ip": request.remote_addr
    }
    attendance_records.append(record)

    return jsonify({"message": f"{students[student_id]} logged successfully!", "record": record})
