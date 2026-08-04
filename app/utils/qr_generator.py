import io
import base64
import qrcode
import json
import hashlib

def generate_qr_payload(data_dict, secret_key="CODEALPHA_SECURE_TOKEN"):
    """
    Generates a payload string with SHA256 checksum for verification.
    """
    raw_json = json.dumps(data_dict, sort_keys=True)
    signature = hashlib.sha256((raw_json + secret_key).encode('utf-8')).hexdigest()[:12]
    payload = {
        "data": data_dict,
        "sig": signature
    }
    return json.dumps(payload)

def generate_qr_base64(data_string):
    """
    Generates a Base64-encoded Data URI string of the QR Code for HTML embedding.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(data_string)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def verify_qr_payload(payload_json_str, secret_key="CODEALPHA_SECURE_TOKEN"):
    """
    Verifies payload signature to prevent ticket forgery.
    """
    try:
        payload = json.loads(payload_json_str)
        data_dict = payload.get("data")
        sig = payload.get("sig")
        raw_json = json.dumps(data_dict, sort_keys=True)
        expected_sig = hashlib.sha256((raw_json + secret_key).encode('utf-8')).hexdigest()[:12]
        return sig == expected_sig, data_dict
    except Exception:
        return False, None
