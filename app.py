from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image
import numpy as np
import os, uuid, sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fake-seed-prototype-secret"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "data", "detections.db")
ALLOWED = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence REAL NOT NULL,
            quality_score REAL NOT NULL,
            brightness REAL NOT NULL,
            texture_score REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

def allowed_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED

def analyze_seed(path):
    """
    Prototype-only image analysis.
    This is NOT a scientifically validated fake-seed detector.
    It uses visible image statistics to demonstrate the complete workflow.
    A trained CNN/transfer-learning model can replace this function later.
    """
    img = Image.open(path).convert("RGB")
    img.thumbnail((600, 600))
    arr = np.asarray(img, dtype=np.float32)

    gray = arr.mean(axis=2)
    brightness = float(gray.mean())
    contrast = float(gray.std())

    # Edge/texture approximation using neighboring pixel differences.
    dx = np.abs(np.diff(gray, axis=1)).mean() if gray.shape[1] > 1 else 0
    dy = np.abs(np.diff(gray, axis=0)).mean() if gray.shape[0] > 1 else 0
    texture = float((dx + dy) / 2)

    # Color variation can help distinguish a clean seed photo from
    # an unusually uniform/poor-quality sample in this prototype.
    color_std = float(arr.std(axis=(0, 1)).mean())

    # Demo scoring: balanced around typical photographed objects.
    # The score is intentionally labeled "prototype score".
    brightness_score = max(0.0, 1.0 - abs(brightness - 135.0) / 135.0)
    texture_score = min(texture / 30.0, 1.0)
    color_score = min(color_std / 55.0, 1.0)

    quality = 100 * (0.45 * brightness_score + 0.35 * texture_score + 0.20 * color_score)
    quality = max(0.0, min(100.0, quality))

    # Classification threshold for the demo prototype.
    if quality >= 58:
        result = "Likely Genuine"
        confidence = min(98.0, 55.0 + quality * 0.43)
    else:
        result = "Likely Fake"
        confidence = min(96.0, 55.0 + (100.0 - quality) * 0.41)

    return {
        "result": result,
        "confidence": round(confidence, 1),
        "quality_score": round(quality, 1),
        "brightness": round(brightness, 1),
        "texture": round(texture, 1)
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "seed_image" not in request.files:
        flash("Please select a seed image.")
        return redirect(url_for("index"))

    file = request.files["seed_image"]
    if not file.filename:
        flash("Please select a seed image.")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Allowed formats: JPG, JPEG, PNG, WEBP.")
        return redirect(url_for("index"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)

    try:
        analysis = analyze_seed(path)
    except Exception as exc:
        os.remove(path)
        flash(f"Could not analyze image: {exc}")
        return redirect(url_for("index"))

    con = sqlite3.connect(DB_PATH)
    con.execute("""
        INSERT INTO detections
        (filename, result, confidence, quality_score, brightness, texture_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        filename, analysis["result"], analysis["confidence"],
        analysis["quality_score"], analysis["brightness"],
        analysis["texture"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    con.commit()
    con.close()

    return render_template("result.html", filename=filename, original_name=file.filename, **analysis)

@app.route("/history")
def history():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM detections ORDER BY id DESC LIMIT 50").fetchall()
    con.close()
    return render_template("history.html", rows=rows)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
