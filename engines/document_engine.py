"""
Document Engine
Handles document conversions (DOCX, XLSX, PPTX, etc.) using LibreOffice
"""

import os
import uuid
import subprocess


class DocumentEngine:
    """Engine for document conversions"""
    
    def convert_format(self, input_path, target_format, output_folder):
        """
        Convert document to different format using LibreOffice
        
        Args:
            input_path: Document file path
            target_format: Target format (pdf, docx, txt, html, etc.)
            output_folder: Output directory
            
        Returns:
            dict: Result with output path
        """
        try:
            # Use LibreOffice headless for conversion
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', target_format,
                '--outdir', output_folder,
                input_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'LibreOffice conversion error: {result.stderr}'
                }
            
            # Find the output file
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_filename = f"{base_name}.{target_format}"
            output_path = os.path.join(output_folder, output_filename)
            
            # Rename to unique filename
            if os.path.exists(output_path):
                unique_filename = f"converted_{uuid.uuid4()}.{target_format}"
                unique_path = os.path.join(output_folder, unique_filename)
                os.rename(output_path, unique_path)
                output_path = unique_path
            
            if not os.path.exists(output_path):
                return {
                    'success': False,
                    'error': 'Conversion completed but output file not found'
                }
            
            return {
                'success': True,
                'output_path': output_path
            }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Conversion timeout - file may be too large or complex'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def docx_to_pdf(self, input_path, output_folder):
        """Convert DOCX to PDF"""
        return self.convert_format(input_path, 'pdf', output_folder)
    
    def xlsx_to_pdf(self, input_path, output_folder):
        """Convert XLSX to PDF"""
        return self.convert_format(input_path, 'pdf', output_folder)
    
    def pptx_to_pdf(self, input_path, output_folder):
        """Convert PPTX to PDF"""
        return self.convert_format(input_path, 'pdf', output_folder)
    
    def docx_to_txt(self, input_path, output_folder):
        """Convert DOCX to TXT"""
        return self.convert_format(input_path, 'txt', output_folder)
    
    def xlsx_to_csv(self, input_path, output_folder):
        """Convert XLSX to CSV"""
        return self.convert_format(input_path, 'csv', output_folder)
    
    def doc_to_docx(self, input_path, output_folder):
        """Convert old DOC to DOCX"""
        return self.convert_format(input_path, 'docx', output_folder)
    
    def xls_to_xlsx(self, input_path, output_folder):
        """Convert old XLS to XLSX"""
        return self.convert_format(input_path, 'xlsx', output_folder)
    
    def ppt_to_pptx(self, input_path, output_folder):
        """Convert old PPT to PPTX"""
        return self.convert_format(input_path, 'pptx', output_folder)
    
    def rtf_to_docx(self, input_path, output_folder):
        """Convert RTF to DOCX"""
        return self.convert_format(input_path, 'docx', output_folder)
    
    def odt_to_docx(self, input_path, output_folder):
        """Convert ODT to DOCX"""
        return self.convert_format(input_path, 'docx', output_folder)
    
    def ods_to_xlsx(self, input_path, output_folder):
        """Convert ODS to XLSX"""
        return self.convert_format(input_path, 'xlsx', output_folder)
    
    def odp_to_pptx(self, input_path, output_folder):
        """Convert ODP to PPTX"""
        return self.convert_format(input_path, 'pptx', output_folder)
    
    def html_to_pdf(self, input_path, output_folder):
        """Convert HTML to PDF"""
        return self.convert_format(input_path, 'pdf', output_folder)
    
    def docx_to_html(self, input_path, output_folder):
        """Convert DOCX to HTML"""
        return self.convert_format(input_path, 'html', output_folder)