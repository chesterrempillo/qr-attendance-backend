from flask import Flask, jsonify, url_for
from flask_cors import CORS
import qrcode, os, socket
from datetime import datetime

app = Flask(__name__)

# ✅ Allow requests from any origin (so mobile and different Wi-Fi can connect)
CORS(app, resources={r"/*": {"origins": "*"}})

QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

@app.route("/generate_daily_qr")
def generate_daily_qr():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{QR_DIR}/daily_qr_{today}.png"

    # ✅ Get local IP automatically for LAN use
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except:
        local_ip = "localhost"

    # ✅ FRONTEND_URL: use environment variable if set, otherwise local IP
    FRONTEND_URL = os.environ.get(
        "FRONTEND_URL", f"http://{local_ip}:3000/attendance"
    )

    # Only generate QR if it doesn't exist
    if not os.path.exists(filename):
        qrcode.make(FRONTEND_URL).save(filename)

    qr_image_url = url_for("static", filename=f"qrcodes/daily_qr_{today}.png", _external=True)
    return jsonify({
        "message": "Daily QR generated successfully!",
        "qr_image": qr_image_url,
        "attendance_url": FRONTEND_URL
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # ✅ Host 0.0.0.0 so other devices on LAN can access it
    app.run(host="0.0.0.0", port=port)
