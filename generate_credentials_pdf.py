
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf():
    filename = "credenciales_acceso.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Credenciales de Acceso - Proyecto RRHH</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Aquí tienes las credenciales para los diferentes perfiles del sistema:", styles['BodyText']))
    elements.append(Spacer(1, 12))

    # Data
    data = [
        ['Perfil', 'Usuario', 'Contraseña', 'Función'],
        ['Candidato', 'candidato', 'candidato123', 'Busca trabajo y carga su CV'],
        ['Candidato 2', 'maria', 'maria123', 'Perfil adicional'],
        ['Candidato 3', 'gerardo', 'gerardo123', 'Perfil adicional'],
        ['Empresa', 'empresa', 'empresa123', 'Publica vacantes y revisa candidatos'],
        ['Dueña (Admin)', 'admin', 'admin123', 'Acceso total al sistema']
    ]

    # Table
    t = Table(data, colWidths=[100, 100, 100, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 24))
    
    elements.append(Paragraph("<b>URL del sistema:</b> http://127.0.0.1:8000/", styles['BodyText']))

    doc.build(elements)
    print(f"PDF generado: {filename}")

if __name__ == "__main__":
    generate_pdf()
