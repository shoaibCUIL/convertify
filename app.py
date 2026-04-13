import os
import uuid
import zipfile

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


# ================= PDF SPLIT (FIXED + ZIP) =================
@app.route("/split", methods=["POST"])
def split_pdf():
    try:
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]

        if file.filename == "":
            return "No file selected", 400

        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(pdf_path)

        reader = PdfReader(pdf_path)

        if len(reader.pages) == 0:
            return "Invalid or empty PDF", 400

        unique_id = str(uuid.uuid4())
        zip_path = os.path.join(app.config["OUTPUT_FOLDER"], f"{unique_id}.zip")

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)

                temp_pdf = os.path.join(
                    app.config["OUTPUT_FOLDER"], f"{unique_id}_page_{i+1}.pdf"
                )

                with open(temp_pdf, "wb") as f:
                    writer.write(f)

                zipf.write(temp_pdf, f"page_{i+1}.pdf")

                # cleanup temp file
                os.remove(temp_pdf)

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= DOCX → PDF (SAFE HANDLING) =================
@app.route("/docx-to-pdf", methods=["POST"])
def docx_to_pdf():
    return jsonify({
        "message": "DOCX to PDF is currently disabled on this server. Requires LibreOffice/Docker setup."
    }), 501


# ================= HEALTH CHECK =================
@app.route("/health")
def health():
    return {"status": "running"}


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)