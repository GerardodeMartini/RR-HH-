import google.generativeai as genai
from django.conf import settings
from applications.models import Application
import os

def get_api_key():
    # Retrieve API Key from Django Settings (backend configuration)
    if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY != 'TU_API_KEY_AQUI':
        return settings.GEMINI_API_KEY
    return None

def analyze_application(application_id):
    try:
        app = Application.objects.get(id=application_id)
        api_key = get_api_key()
        
        if not api_key:
            return {"error": "API Key not configured."}

        genai.configure(api_key=api_key)
        # Using gemini-flash-latest which is the working alias for this user
        model = genai.GenerativeModel('gemini-flash-latest')

        # Prepare Context
        candidate = app.candidate
        vacancy = app.vacancy
        
        # Prepare inputs for Gemini
        inputs = []
        
        prompt_intro = f"""
        ERES UN RECLUTADOR QUE HABLA SOLAMENTE ESPAÑOL.
        Tu tarea es analizar el Candidato (basado en su CV adjunto y los datos provistos) frente a la Vacante.
        
        VACANTE:
        Título: {vacancy.title}
        Descripción: {vacancy.description}
        Habilidades Requeridas: {vacancy.required_skills}
        
        CANDIDATO (Datos del Formulario):
        Nombre: {candidate.first_name} {candidate.last_name}
        Habilidades Declaradas: {candidate.skills}
        
        TAREA:
        1. Analiza el archivo PDF adjunto (CV) en detalle.
        2. **Verificación de Identidad**: Compara el nombre del candidato en el formulario ({candidate.first_name} {candidate.last_name}) con el nombre que aparece en el CV. ¿Coinciden?
        
        CASO 1: LOS DATOS NO COINCIDEN (NOMBRE/DATOS):
        - **Resumen**: DEBE empezar diciendo "GRAVE: El CV adjunto pertenece a [Nombre en CV], no a [Nombre Candidato]".
        - **Puntaje**: 0.
        - **Feedback**:  
            - **Pros**: Ninguno (ya que no es su CV).
            - **Contras**: "El cv no pertenece al candidato."
        - **Consistency Warning**: "Nombre en CV no coincide con candidato".
        
        CASO 2: LOS DATOS COINCIDEN:
        - Realiza el análisis normal de habilidades.
        - Resumen: Breve evaluación profesional (EN ESPAÑOL).
        - Puntaje: 0 a 100 basado en requisitos vs habilidades reales del CV.
        - Feedback: Lista de pros y contras.
        
        FORMATO DE SALIDA (JSON):
        
        FORMATO DE SALIDA (JSON):
        
        FORMATO DE SALIDA (JSON):
        {{
            "summary": "...",
            "score": 85,
            "feedback": "...",
            "consistency_warning": null  // Si todo coincide, devuelve null. Si hay incongruencias (ej. nombres distintos), devuelve un string corto explicando el problema.
        }}
        """
        inputs.append(prompt_intro)

        # Upload Resume if exists
        file_uploaded = None
        if candidate.resume_file:
            try:
                file_path = candidate.resume_file.path
                # Upload the file to Gemini
                file_uploaded = genai.upload_file(file_path, mime_type='application/pdf')
                inputs.append(file_uploaded)
            except Exception as e:
                return {"error": f"Error subiendo archivo a Gemini: {str(e)}"}
        else:
            inputs.append("\n(No se adjuntó archivo de CV, analizar solo con datos del formulario)")
        
        # Generate Content
        response = model.generate_content(inputs)
        
        # Clean response to ensure JSON
        text = response.text.replace('```json', '').replace('```', '')
        
        import json
        data = json.loads(text)
        
        # Update Application
        summary = data.get('summary', 'No summary generated.')
        
        
        # Check for consistency warnings
        consistency_warning = data.get('consistency_warning')
        if consistency_warning:
            summary = f"⚠️ **ALERTA DE DATOS: {consistency_warning}**\n\n{summary}"
        
        app.ai_summary = summary
        app.ai_match_score = data.get('score', 0)
        
        # Sanitize Feedback (Handle if AI returns list/dict instead of string)
        feedback_data = data.get('feedback', 'No feedback generated.')
        if isinstance(feedback_data, list):
            # Convert list to bullet points
            feedback_str = ""
            for item in feedback_data:
                feedback_str += f"- {str(item)}\n"
            app.ai_feedback = feedback_str
        elif isinstance(feedback_data, dict):
            # Convert dict (pros/cons) to markdown
            feedback_str = ""
            if 'pros' in feedback_data:
                feedback_str += "**Pros:**\n" + "\n".join([f"- {item}" for item in feedback_data['pros']]) + "\n\n"
            if 'cons' in feedback_data:
                feedback_str += "**Contras:**\n" + "\n".join([f"- {item}" for item in feedback_data['cons']])
            app.ai_feedback = feedback_str
        else:
            # Assume it's already a string
            app.ai_feedback = str(feedback_data)
            
        app.save()
        
        # Cleanup: Delete file from Gemini cloud to save space/privacy if needed (optional usually)
        # if file_uploaded:
        #    genai.delete_file(file_uploaded.name)
        
        return {"success": True, "score": app.ai_match_score}
        
    except Exception as e:
        import traceback
        return {"error": f"Error interno de IA: {str(e)}"}
