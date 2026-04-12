import os
import uuid
import logging
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

from utils.converter import UniversalConverter
from utils.file_detector import detect_file_type

# ================= CONFIG =================
app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["OUTPUT_FOLDER"] = "outputs"
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB

# Create folders
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Converter
converter = UniversalConverter()

# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


# ================= UPLOAD =================
@app.route("/api/upload", methods=["POST"])
def upload():
    try:
        logger.info("Upload called")

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # 🔥 NO STRICT VALIDATION (fixes your issue)
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1]

        new_filename = file_id + ext
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

        file.save(filepath)

        # Detect file type
        file_type = detect_file_type(filepath)

        return jsonify({
            "success": True,
            "filename": new_filename,
            "file_type": file_type.get("type")
        })

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


# ================= CONVERT =================
@app.route("/api/convert", methods=["POST"])
def convert():
    try:
        data = request.get_json()

        filename = data.get("filename")
        target_format = data.get("target_format")

        if not filename or not target_format:
            return jsonify({"error": "Missing parameters"}), 400

        input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        if not os.path.exists(input_path):
            return jsonify({"error": "File not found"}), 404

        result = converter.convert(
            input_path,
            target_format,
            {"output_folder": app.config["OUTPUT_FOLDER"]}
        )

        if result["success"]:
            return jsonify({
                "success": True,
                "output": os.path.basename(result["output_path"])
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


# ================= DOWNLOAD =================
@app.route("/api/download/<filename>")
def download(filename):
    try:
        path = os.path.join(app.config["OUTPUT_FOLDER"], filename)

        if not os.path.exists(path):
            return jsonify({"error": "File not found"}), 404

        return send_file(path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= HEALTH =================
@app.route("/api/health")
def health():
    return jsonify({"status": "running"})


# ================= ERRORS =================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)