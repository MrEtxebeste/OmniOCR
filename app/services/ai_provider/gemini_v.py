import os
import google.generativeai as genai
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash') # El más rápido y optimizado para esto

    def extract_data(self, file_path: str, doc_type: str) -> dict:
        # 1. Subir el archivo a la API de Google (temporalmente)
        sample_file = genai.upload_file(path=file_path)
        
        # 2. El "Prompt" maestro para el OCR
        prompt = f"""
        Analiza este documento de tipo {doc_type}. 
        Extrae la siguiente información en formato JSON puro:
        - supplier_name: Nombre de la empresa que emite.
        - doc_date: Fecha en formato YYYY-MM-DD.
        - total_base: Suma de bases imponibles (número).
        - total_tax: Suma de cuotas de IVA (número).
        - total_amount: Total factura (número).
        - lines: Una lista de objetos con (description, quantity, price_unit, total_line).
        
        No escribas nada más que el JSON.
        """
        
        # 3. Generar la respuesta
        response = self.model.generate_content([sample_file, prompt])
        
        # 4. Limpiar y convertir la respuesta a diccionario
        # (Añadiremos lógica para limpiar los ```json ... ``` que a veces devuelve)
        import json
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text_response)