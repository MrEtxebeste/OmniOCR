import os
import json
from google import genai
from .base import BaseAIProvider

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        # Inicializamos el cliente con el nuevo SDK de Google
        self.client = genai.Client(api_key=self.api_key)

    def extract_data(self, file_path: str, doc_type: str) -> dict:
        # 1. Subir el archivo a Google
        document = self.client.files.upload(file=file_path)
        
        # 2. El Prompt Maestro (adaptado a tus columnas de base de datos)
        prompt = f"""
        Analiza este documento de tipo {doc_type}. 
        Extrae los datos y devuélvelos en JSON con estas claves exactas:
        - emisor: Nombre de la empresa que emite.
        - cifemisor: CIF o NIF del emisor.
        - numdocumento: Número del documento.
        - fechadocumento: Fecha (DD/MM/YYYY).
        - fechavalidez: Fecha de validez si existe (DD/MM/YYYY).
        - importebruto: Base imponible total (solo numero, usa punto para decimales).
        - importeiva: Cuota de IVA total (solo numero, usa punto para decimales).
        - importeneto: Total del documento (solo numero, usa punto para decimales).
        - porcentajeiva: El tipo de IVA aplicado (ej: 21).
        - lines: Lista de artículos con (descripcion, cantidad, precio_unidad, total).
        
        No escribas nada más que el JSON puro, no incluyas bloques de código como ```json.
        """
        
        # 3. Llamar al modelo de IA (usamos el modelo más reciente y rápido)
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[document, prompt]
        )
        
        # 4. Limpiar y parsear la respuesta
        text_response = response.text.replace('```json', '').replace('```', '').strip()
        
        try:
            return json.loads(text_response)
        except json.JSONDecodeError:
            # Por si la IA se equivoca y no devuelve un JSON válido
            raise Exception("La IA no devolvió un formato JSON válido.")