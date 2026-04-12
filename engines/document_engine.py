import os
import uuid
from docx import Document
from reportlab.pdfgen import canvas
import csv


class DocumentEngine:
    """Document processing engine"""

    # =========================
    # DOCX → PDF
    # =========================
    def docx_to_pdf(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            output_filename = f"docx_pdf_{uuid.uuid4()}.pdf"
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

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → HTML
    # =========================
    def docx_to_html(self, input_path, output_folder):
        try:
            doc = Document(input_path)
            html = "<html><body>"

            for para in doc.paragraphs:
                html += f"<p>{para.text}</p>"

            html += "</body></html>"

            output_filename = f"docx_html_{uuid.uuid4()}.html"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → XML
    # =========================
    def docx_to_xml(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            xml = "<document>\n"

            for para in doc.paragraphs:
                xml += f"  <paragraph>{para.text}</paragraph>\n"

            xml += "</document>"

            output_filename = f"docx_xml_{uuid.uuid4()}.xml"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → CSV
    # =========================
    def docx_to_csv(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            output_filename = f"docx_csv_{uuid.uuid4()}.csv"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                for para in doc.paragraphs:
                    writer.writerow([para.text])

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → XLSX (basic CSV-style)
    # =========================
    def docx_to_xlsx(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            # NOTE: we simulate XLSX using CSV format (Excel opens it)
            output_filename = f"docx_xlsx_{uuid.uuid4()}.xlsx"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                for para in doc.paragraphs:
                    f.write(para.text + "\n")

            return {"success": True, "output_path": output_path}

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

            output_filename = f"txt_docx_{uuid.uuid4()}.docx"
            output_path = os.path.join(output_folder, output_filename)

            doc.save(output_path)

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # DOCX → TXT
    # =========================
    def docx_to_txt(self, input_path, output_folder):
        try:
            doc = Document(input_path)

            output_filename = f"docx_txt_{uuid.uuid4()}.txt"
            output_path = os.path.join(output_folder, output_filename)

            with open(output_path, "w", encoding="utf-8") as f:
                for para in doc.paragraphs:
                    f.write(para.text + "\n")

            return {"success": True, "output_path": output_path}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================
    # ROUTER METHOD
    # =========================
    def convert(self, input_path, target_format, output_folder):
        ext = os.path.splitext(input_path)[1].lower()

        if ext == ".docx":
            if target_format == "pdf":
                return self.docx_to_pdf(input_path, output_folder)
            elif target_format == "html":
                return self.docx_to_html(input_path, output_folder)
            elif target_format == "xml":
                return self.docx_to_xml(input_path, output_folder)
            elif target_format == "csv":
                return self.docx_to_csv(input_path, output_folder)
            elif target_format == "xlsx":
                return self.docx_to_xlsx(input_path, output_folder)
            elif target_format == "txt":
                return self.docx_to_txt(input_path, output_folder)

        elif ext == ".txt":
            if target_format == "docx":
                return self.txt_to_docx(input_path, output_folder)

        return {"success": False, "error": "Unsupported conversion"}