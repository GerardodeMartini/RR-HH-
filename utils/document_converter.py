import os
import uuid
import tempfile
import subprocess
from django.core.files import File

def ensure_pdf_resume(candidate):
    """
    Asegura que el CV subido sea un PDF.
    Si es doc/docx, intenta convertirlo usando LibreOffice.
    Requiere libreoffice instalado en el sistema (ej. libreoffice-writer).
    """
    if not candidate.resume_file:
        return False
        
    ext = os.path.splitext(candidate.resume_file.name)[1].lower()
    if ext == '.pdf':
        return True
        
    if ext not in ['.doc', '.docx']:
        return False
        
    # Necesitamos que el archivo esté guardado en disco para que LibreOffice lo lea
    try:
        file_path = candidate.resume_file.path
    except NotImplementedError:
        # Pasa si el archivo no está guardado aún localmente de forma adecuada
        return False
        
    if not os.path.exists(file_path):
        return False
        
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Comando para modo headless de LibreOffice
            # En windows podría ser 'soffice.exe' o estar en una ruta específica
            is_windows = os.name == 'nt'
            cmd = 'soffice'
            if is_windows:
                # Intenta rutas comunes o simplemente asume que está en el PATH
                common_paths = [
                    r"C:\Program Files\LibreOffice\program\soffice.exe",
                    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
                ]
                for p in common_paths:
                    if os.path.exists(p):
                        cmd = p
                        break
            
            command = [
                cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', tmpdir,
                file_path
            ]
            
            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            except FileNotFoundError:
                print("LibreOffice no encontrado. No se pudo convertir a PDF.")
                return False
                
            if result.returncode != 0:
                print(f"Error de LibreOffice: {result.stderr.decode()}")
                return False
                
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            pdf_path = os.path.join(tmpdir, f"{base_name}.pdf")
            
            if os.path.exists(pdf_path):
                # Guarda el nuevo archivo PDF sobreescribiendo la referencia actual
                with open(pdf_path, 'rb') as pdf_file:
                    new_filename = f"{uuid.uuid4().hex[:8]}_{base_name}.pdf"
                    candidate.resume_file.save(new_filename, File(pdf_file), save=True)
                    
                # Borra el archivo original opcionalmente
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                    
                return True
                
    except Exception as e:
        print(f"Error en conversión de documento: {e}")
        return False
        
    return False
