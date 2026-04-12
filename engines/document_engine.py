import os
import uuid

from PyPDF2 import PdfReader
from docx import Document
from reportlab.pdfgen import canvas


class DocumentEngine:
    """Engine for document conversions"""

    # =========================
    # MAIN CONVERTER
    # =========================
    def convert(self, input_path, output_format, output_folder):
        try:
            ext = os.path.splitext(input_path)[1].lower()

            if ext == ".pdf" and output_format == "docx":
                return self.pdf_to_docx(input_path, output_folder)

            elif ext == ".docx" and output_format == "pdf":
                return self.docx_to_pdf(input_path, output_folder)

            elif ext == ".txt" and output_format == "docx":
                return self.txt_to_docx(input_path, output_folder)

            elif ext == ".docx" and output_format == "txt":
                return self.docx_to_txt(input_path, output_folder)

            else:
                return {
                    "success": False,
                    "error": f"Conversion not supported: {ext} → {output_format}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # PDF → DOCX
    # =========================
    def pdf_to_docx(self, input_path, output_folder):
        try:
            reader = PdfReader(input_path)
            doc = Document()

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    doc.add_paragraph(text)

            output_filename = f"pdf_to_docx_{uuid.uuid4()}.docx"
            output_path = os.path.join(output_folder, output_filename)

            doc.save(output_path)

            return {
                "success": True,
                "output_path": output_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → PDF (Simple)
    # =========================
    def docx_to_pdf(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            output_filename = f"docx_to_pdf_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            c = canvas.Canvas(output_path)

            y = 800

            for para in doc.paragraphs:
                text = para.text.strip()

                if not text:
                    continue

                if y < 50:
                    c.showPage()
                    y = 800

                c.drawString(50, y, text)
                y -= 20

            c.save()

            return {
                "success": True,
                "output_path": output_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # TXT → DOCX
    # =========================
    def txt_to_docx(self, input_path, output_folder):
        try:
            doc = Document()

            with open(input_path, "r", encoding="utf-8") as f:
                for line in f:
                    doc.add_paragraph(line.strip())

            output_filename = f"txt_to_docx_{uuid.uuid4()}.docx"
            output_path = os.path.join(output_folder, output_filename)

            doc.save(output_path)

            return {
                "success": True,
                "output_path": output_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → TXT
    # =========================
    def docx_to_txt(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            output_filename = f"docx_to_txt_{uuid.uuid4()}.txt"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                for para in doc.paragraphs:
                    f.write(para.text + "\n")

            return {
                "success": True,
                "output_path": output_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # TEXT EXTRACTION
    # =========================
    def extract_text(self, input_path):
        try:
            ext = os.path.splitext(input_path)[1].lower()

            if ext == ".pdf":
                reader = PdfReader(input_path)
                text = ""

                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                return {"success": True, "text": text}

            elif ext == ".docx":
                doc = Document(input_path)
                text = "\n".join([p.text for p in doc.paragraphs])
                return {"success": True, "text": text}

            elif ext == ".txt":
                with open(input_path, "r", encoding="utf-8") as f:
                    return {"success": True, "text": f.read()}

            else:
                return {"success": False, "error": "Unsupported file"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # FILE INFO
    # =========================
    def get_file_info(self, input_path):
        try:
            size = os.path.getsize(input_path)
            ext = os.path.splitext(input_path)[1].lower()

            return {
                "success": True,
                "file_type": ext,
                "size_bytes": size
            }

        except Exception as e:
            return {"success": False, "error": str(e)}