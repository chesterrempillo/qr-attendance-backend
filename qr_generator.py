from flask_cors import cross_origin
from flask_restx import Resource
import os
import qrcode
from datetime import datetime
from flask import url_for
import socket

# Helper to get current LAN IP dynamically
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # connect to a public IP to detect active network interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@api.route('/generate_daily_qr')
class GenerateDailyQR(Resource):

    @cross_origin()  # Allows requests from your React frontend
    def get(self):
        today = datetime.now().strftime("%Y-%m-%d")
        qr_dir = "static/qrcodes"
        os.makedirs(qr_dir, exist_ok=True)
        filename = f"{qr_dir}/daily_qr_{today}.png"

        # Dynamically detect LAN IP
        local_ip = get_local_ip()
        qr_url = f"http://{local_ip}:3000/attendance"

        # If QR already exists, return existing
        if os.path.exists(filename):
            qr_image_url = url_for("static", filename=f"qrcodes/daily_qr_{today}.png", _external=True)
            return {
                "message": "Today's QR already exists",
                "qr_image": qr_image_url,
                "qr_url": qr_url
            }

        # Generate new QR image
        qrcode.make(qr_url).save(filename)
        qr_image_url = url_for("static", filename=f"qrcodes/daily_qr_{today}.png", _external=True)

        return {
            "message": "Daily QR generated successfully!",
            "qr_image": qr_image_url,
            "qr_url": qr_url
        }
