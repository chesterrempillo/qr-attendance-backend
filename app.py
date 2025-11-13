from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import qrcode, os, sqlite3
from datetime import datetime

# --- Flask app ---
app = Flask(__name__)

# ✅ Allow CORS from both local and deployed frontend
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",  # React dev
    "https://qr-attendance-frontend.onrender.com"  # deployed frontend
]}}, supports_credentials=True)

# --- Swagger API ---
api = Api(app, title="QR Attendance API", description="Backend API with Swagger UI")

# --- Directories & DB ---
QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)
DATABASE = "attendance.db"

# --- Database helpers ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            time TEXT,
            device TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Models for Swagger ---
attendance_model = api.model('Attendance', {
    'student_id': fields.String(required=True, description='Student ID')
})

student_model = api.model('Student', {
    'student_id': fields.String(required=True, description='Student ID'),
    'name': fields.String(required=True, description='Student Name')
})

# --- Routes ---
@api.route('/generate_daily_qr')
class GenerateDailyQR(Resource):
    def get(self):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{QR_DIR}/daily_qr_{today}.png"

        # ✅ Make sure this URL points to your *actual* frontend
        FRONTEND_URL = os.environ.get(
            "FRONTEND_URL", "https://qr-attendance-frontend.onrender.com/attendance"
        )

        # Always re-generate daily QR to update links if needed
        qrcode.make(FRONTEND_URL).save(filename)

        qr_image_url = url_for("static", filename=f"qrcodes/daily_qr_{today}.png", _external=True)
        return {
            "message": "Daily QR generated successfully!",
            "qr_image": qr_image_url,
            "attendance_url": FRONTEND_URL
        }

@api.route('/record_attendance')
class RecordAttendance(Resource):
    @api.expect(attendance_model)
    def post(self):
        data = request.json
        student_id = data.get("student_id")
        device = request.headers.get("X-Device-ID", "unknown_device")
        now = datetime.now()

        if not student_id:
            return {"error": "Student ID required"}, 400

        conn = get_db()
        student = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if not student:
            conn.close()
            return {"error": "Student not found"}, 404

        conn.execute(
            "INSERT INTO attendance (student_id, date, time, device) VALUES (?, ?, ?, ?)",
            (student_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), device)
        )
        conn.commit()
        conn.close()

        return {"message": f"Attendance recorded for {student['name']} ✅"}

@api.route('/add_student')
class AddStudent(Resource):
    @api.expect(student_model)
    def post(self):
        data = request.json
        student_id = data.get("student_id")
        name = data.get("name")

        if not student_id or not name:
            return {"error": "Student ID and Name required"}, 400

        conn = get_db()
        try:
            conn.execute("INSERT INTO students (student_id, name) VALUES (?, ?)", (student_id, name))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return {"error": "Student ID already exists"}, 400
        conn.close()
        return {"message": f"Student {name} added ✅"}

@api.route('/attendance')
class AttendanceList(Resource):
    def get(self):
        """Get all attendance records"""
        conn = get_db()
        rows = conn.execute("""
            SELECT a.id, s.name, a.student_id, a.date, a.time, a.device
            FROM attendance a
            JOIN students s ON s.student_id = a.student_id
            ORDER BY a.date DESC, a.time DESC
        """).fetchall()
        conn.close()

        data = [dict(row) for row in rows]
        return jsonify({
            "count": len(data),
            "records": data
        })

# --- Run app ---
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
