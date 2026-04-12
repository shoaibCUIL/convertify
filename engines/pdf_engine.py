import os
import uuid
from PyPDF2 import PdfReader, PdfWriter
from docx import Document


class PDFEngine:
    """PDF processing engine"""

    # =========================
    # PDF → TEXT
    # =========================
    def pdf_to_text(self, input_path, output_folder):
        try:
            reader = PdfReader(input_path)
            text = ""

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            output_filename = f"pdf_text_{uuid.uuid4()}.txt"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # PDF → HTML
    # =========================
    def pdf_to_html(self, input_path, output_folder):
        try:
            reader = PdfReader(input_path)
            html_content = "<html><body>"

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    html_content += f"<p>{text}</p>"

            html_content += "</body></html>"

            output_filename = f"pdf_html_{uuid.uuid4()}.html"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return {"success": True, "output_path": output_path}

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

            output_filename = f"pdf_docx_{uuid.uuid4()}.docx"
            output_path = os.path.join(output_folder, output_filename)

            doc.save(output_path)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # MERGE PDFs
    # =========================
    def merge_pdfs(self, input_paths, output_folder):
        try:
            writer = PdfWriter()

            for path in input_paths:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)

            output_filename = f"merged_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb") as f:
                writer.write(f)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # SPLIT PDF (FIRST PAGE ONLY)
    # =========================
    def split_pdf(self, input_path, output_folder):
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()

            # Extract first page (simple split)
            writer.add_page(reader.pages[0])

            output_filename = f"split_{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "wb") as f:
                writer.write(f)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # EXTRACT TEXT (RAW)
    # =========================
    def extract_text(self, input_path):
        try:
            reader = PdfReader(input_path)
            text = ""

            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

            return {"success": True, "text": text}

        except Exception as e:
            return {"success": False, "error": str(e)}