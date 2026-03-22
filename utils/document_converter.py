import os
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def convert_docx_to_pdf_libreoffice(input_path):
    """
    Convierte un archivo doc/docx a PDF utilizando LibreOffice en modo headless.
    Retorna el path del nuevo archivo .pdf si fue exitoso, o None en caso de error.
    """
    if not os.path.exists(input_path):
        return None
        
    ext = os.path.splitext(input_path)[1].lower()
    if ext not in ['.doc', '.docx']:
        return None

    output_dir = os.path.dirname(input_path)
    
    try:
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            input_path, '--outdir', output_dir
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        
        if result.returncode == 0:
            pdf_path = os.path.splitext(input_path)[0] + '.pdf'
            return pdf_path if os.path.exists(pdf_path) else None
        else:
            logger.error(f"LibreOffice conversion error: {result.stderr.decode('utf-8')}")
            return None
    except Exception as e:
        logger.error(f"LibreOffice Exception: {e}")
        return None

def ensure_pdf_resume(candidate):
    """
    Checks if candidate resume is a word document, converts it to PDF, 
    updates the database, and deletes the old file.
    """
    if not candidate.resume_file:
        return
        
    file_path = candidate.resume_file.path
    if file_path.lower().endswith(('.doc', '.docx')):
        pdf_path = convert_docx_to_pdf_libreoffice(file_path)
        
        if pdf_path:
            relative_name = os.path.relpath(pdf_path, settings.MEDIA_ROOT)
            # Re-asign clean string relative to MEDIA_ROOT
            candidate.resume_file.name = relative_name.replace('\\', '/')
            candidate.save(update_fields=['resume_file'])
            
            # Remove original docx
            try:
                os.remove(file_path)
            except OSError:
                pass
