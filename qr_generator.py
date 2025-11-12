from flask import Flask, jsonify, url_for
from flask_cors import CORS
import qrcode, os
from datetime import datetime

app = Flask(__name__)

# ✅ Allow requests from any origin
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Folder to store QR codes
QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

@app.route("/generate_daily_qr")
def generate_daily_qr():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"{QR_DIR}/daily_qr_{today}.png"

    # ✅ Use the deployed frontend URL
    FRONTEND_URL = os.environ.get(
        "FRONTEND_URL",
        "https://qr-attendance-frontend.onrender.com/attendance"
    )

    # Only generate the QR if it doesn't exist
    if not os.path.exists(filename):
        qrcode.make(FRONTEND_URL).save(filename)

    qr_image_url = url_for(
        "static",
        filename=f"qrcodes/daily_qr_{today}.png",
        _external=True
    )

    return jsonify({
        "message": "Daily QR generated successfully!",
        "qr_image": qr_image_url,
        "attendance_url": FRONTEND_URL
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # ✅ Host 0.0.0.0 so backend is reachable on Render or LAN
    app.run(host="0.0.0.0", port=port)
