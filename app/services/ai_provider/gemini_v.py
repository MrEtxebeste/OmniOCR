# app/services/ai_provider/gemini_v.py
import os
import json
from google import genai
from flask import current_app
from datetime import datetime
from pydantic import ValidationError

# IMPORTAMOS EL ESQUEMA GLOBAL
from app.schemas import RespuestaIA  
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)

    def extract_data(self, file_path: str, doc_type: str) -> dict:
        document = self.client.files.upload(file=file_path)
        
        prompt_path = os.path.join(current_app.root_path, 'prompts', 'master_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as file:
            raw_prompt = file.read()
            
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
        prompt = raw_prompt.replace('{doc_type}', doc_type.upper()).replace('{fecha_actual}', fecha_hoy)
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[document, prompt]
        )
        
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            raw_json = json.loads(text_response)
            # PASAMOS EL FILTRO GLOBAL INDEPENDIENTE DE LA IA
            json_validado = RespuestaIA(**raw_json)
            return json_validado.model_dump()
            
        except json.JSONDecodeError:
            raise Exception("La IA no devolvió un formato JSON válido.")
        except ValidationError as e:
            error_msg = f"El JSON de la IA no cumple el formato esperado. Detalles:\n{e.errors()}"
            raise Exception(error_msg)