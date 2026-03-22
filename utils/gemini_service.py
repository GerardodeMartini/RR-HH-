from google import genai
from google.genai import types
from django.conf import settings
from applications.models import Application
import os
import json
from pydantic import BaseModel, Field
from typing import Optional, List

# Define the response schema using Pydantic
class FeedbackSchema(BaseModel):
    pros: List[str] = Field(description="List of positive points about the candidate")
    cons: List[str] = Field(description="List of negative points or missing skills")

class AnalysisSchema(BaseModel):
    summary: str = Field(description="Executive summary of the candidate evaluation")
    score: int = Field(description="Match score from 0 to 100")
    feedback: FeedbackSchema = Field(description="Detailed feedback with pros and cons")
    consistency_warning: Optional[str] = Field(description="Warning if the candidate's name on the CV does not match the application form")

def get_api_key():
    # Retrieve API Key from Database Settings (Staff Panel)
    try:
        from dashboard.models import SystemSettings
        system_settings = SystemSettings.objects.first()
        if system_settings and system_settings.gemini_api_key:
            return system_settings.gemini_api_key
    except Exception:
        pass
        
    # Fallback to Django Settings (.env)
    if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY:
        return settings.GEMINI_API_KEY
    return None

def analyze_application(application_id):
    try:
        app = Application.objects.get(id=application_id)
        api_key = get_api_key()
        
        if not api_key:
            return {"error": "API Key not configured."}

        # Initialize the client with the new SDK
        client = genai.Client(api_key=api_key)
        
        # Prepare Context
        candidate = app.candidate
        vacancy = app.vacancy
        
        prompt_intro = f"""
        ERES UN RECLUTADOR EXPERTO QUE HABLA SOLAMENTE ESPAÑOL.
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
        - Resumen: DEBE empezar diciendo "GRAVE: El CV adjunto pertenece a [Nombre en CV], no a [Nombre Candidato]".
        - Puntaje: 0.
        - Consistency Warning: "Nombre en CV no coincide con candidato".
        
        CASO 2: LOS DATOS COINCIDEN:
        - Realiza el análisis normal de habilidades.
        - Resumen: Breve evaluación profesional.
        - Puntaje: 0 a 100 basado en requisitos vs habilidades reales del CV.
        """

        contents = [prompt_intro]

        # Upload Resume if exists
        if candidate.resume_file:
            try:
                file_path = candidate.resume_file.path
                if os.path.exists(file_path):
                    # Upload file using the new SDK
                    # Note: We need to read the file content or pass the path if supported. 
                    # The client.files.upload method supports path.
                    with open(file_path, "rb") as f:
                         file_content = f.read()
                    
                    # For Gemni 2.0 Flash / 1.5 Flash we can pass the file content directly in parts
                    # But uploading is better for larger files. 
                    # Let's use the standard upload mechanism if we were using the file API, 
                    # but for simplicity and speed with local files, passing bytes directly to generate_content 
                    # (if supported) or using the upload_file helper is best.
                    
                    # New SDK "client.files.upload"
                    uploaded_file = client.files.upload(
                        file=file_path,
                        config=types.UploadFileConfig(mime_type='application/pdf')
                    )
                    contents.append(types.Content(
                        role="user",
                        parts=[
                            types.Part.from_uri(
                                file_uri=uploaded_file.uri,
                                mime_type=uploaded_file.mime_type
                            )
                        ]
                    ))
                else:
                    contents.append("Error: El archivo de CV no se encuentra en el servidor.")
            except Exception as e:
                return {"error": f"Error preparando archivo para Gemini: {str(e)}"}
        else:
            contents.append("\n(No se adjuntó archivo de CV, analizar solo con datos del formulario)")
        
        # input is a list of contents. The first part is text, second is the file.
        # However, the SDK expects a single Content object or a list of parts/strings.
        # Let's restructure properly.
        
        final_contents = []
        final_contents.append(prompt_intro)
        
        if candidate.resume_file and 'uploaded_file' in locals():
             final_contents.append(types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type
             ))
        elif candidate.resume_file and not 'uploaded_file' in locals():
             pass # Error handled above or file didn't exist
        
        # Generate Content with Structured Output
        response = client.models.generate_content(
            model='gemini-flash-latest', # Reverting to the latest stable alias
            contents=final_contents,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=AnalysisSchema
            )
        )
        
        # Parse result
        if not response.text:
             return {"error": "La IA no generó ninguna respuesta."}
             
        analysis_data = response.parsed # This should work if schema is provided, otherwise json.loads(response.text)
        
        # Fallback if parsed is not automatic (depends on SDK version version, but let's assume it works or use json.loads)
        if analysis_data is None:
             analysis_data = AnalysisSchema.model_validate_json(response.text)

        # Update Application
        summary = analysis_data.summary
        
        # Check for consistency warnings
        if analysis_data.consistency_warning:
            summary = f"⚠️ **ALERTA DE DATOS: {analysis_data.consistency_warning}**\n\n{summary}"
        
        app.ai_summary = summary
        app.ai_match_score = analysis_data.score
        
        # Format Feedback
        feedback_str = "**Pros:**\n"
        feedback_str += "\n".join([f"- {item}" for item in analysis_data.feedback.pros])
        feedback_str += "\n\n**Contras:**\n"
        feedback_str += "\n".join([f"- {item}" for item in analysis_data.feedback.cons])
        
        app.ai_feedback = feedback_str
            
        app.save()
        
        return {"success": True, "score": app.ai_match_score}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error interno de IA: {str(e)}"}
class CandidateExtractionSchema(BaseModel):
    first_name: Optional[str] = Field(description="First name of the candidate")
    last_name: Optional[str] = Field(description="Last name of the candidate")
    email: Optional[str] = Field(description="Email address of the candidate")
    phone: Optional[str] = Field(description="Phone number of the candidate")
    skills: Optional[str] = Field(description="Comma-separated list of technical skills found")
    missing_data_warnings: List[str] = Field(description="List of fields that could not be confidently extracted")

def extract_candidate_data(file_path):
    try:
        api_key = get_api_key()
        if not api_key:
            return {"error": "API Key not configured."}

        client = genai.Client(api_key=api_key)
        
        prompt = """
        ERES UN ASISTENTE DE RRHH EXPERTO EN EXTRACCIÓN DE DATOS.
        Tu tarea es extraer información estructurada del CV adjunto en español.
        
        Extrae los siguientes campos:
        - Nombre (first_name)
        - Apellido (last_name)
        - Email (email): Si hay múltiples correos, únelos con comas.
        - Teléfono (phone)
        - Habilidades (skills): Lista separada por comas de habilidades técnicas relevantes.
        
        SI ALGÚN DATO NO ESTÁ CLARO O NO SE ENCUENTRA:
        - Deja el campo como null o string vacío.
        - Agrega una nota en 'missing_data_warnings' indicando qué campo falta (ej: "No se encontró número de teléfono").
        """

        if not os.path.exists(file_path):
             return {"error": "Archivo no encontrado."}

        # Upload file (using the same logic as analyze_application)
        uploaded_file = client.files.upload(
            file=file_path,
            config=types.UploadFileConfig(mime_type='application/pdf')
        )
        
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=[
                prompt,
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema=CandidateExtractionSchema
            )
        )
        
        if not response.text:
             return {"error": "La IA no pudo procesar el archivo."}

        # Return parsed data as dict
        return json.loads(response.text)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Error de extracción: {str(e)}"}
