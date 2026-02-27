from .gemini_v import GeminiProvider
import os

class AIFactory:
    @staticmethod
    def get_provider():
        provider_type = os.environ.get('AI_PROVIDER', 'gemini').lower()
        if provider_type == 'gemini':
            return GeminiProvider()
        # ... otros proveedores ...