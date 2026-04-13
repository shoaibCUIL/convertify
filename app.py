import os
import uuid

from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

# ================= INIT =================
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")


# ================= PDF MERGE =================
@app.route("/merge", methods=["POST"])
def merge_pdf():
    try:
        if "files" not in request.files:
            return "No files uploaded", 400

        files = request.files.getlist("files")

        if not files or files[0].filename == "":
            return "No files selected", 400

        merger = PdfMerger()

        for file in files:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            merger.append(filepath)

        output_filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

        merger.write(output_path)
        merger.close()

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= PDF SPLIT (RANGE BASED) =================
@app.route("/split", methods=["POST"])
def split_pdf():
    try:
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        start_page = request.form.get("start_page")
        end_page = request.form.get("end_page")

        if file.filename == "":
            return "No file selected", 400

        if not start_page or not end_page:
            return "Please provide page range", 400

        start_page = int(start_page)
        end_page = int(end_page)

        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(pdf_path)

        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)

        if start_page < 1 or end_page > total_pages or start_page > end_page:
            return f"Invalid range. PDF has {total_pages} pages.", 400

        writer = PdfWriter()

        for i in range(start_page - 1, end_page):
            writer.add_page(reader.pages[i])

        output_filename = f"split_{uuid.uuid4()}.pdf"
        output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

        with open(output_path, "wb") as f:
            writer.write(f)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= DOCX → PDF (DISABLED SAFE) =================
@app.route("/docx-to-pdf", methods=["POST"])
def docx_to_pdf():
    return jsonify({
        "message": "DOCX to PDF is currently disabled on this server (requires Docker + LibreOffice)."
    }), 501


# ================= HEALTH =================
@app.route("/health")
def health():
    return {"status": "running"}


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)