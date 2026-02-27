from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    @abstractmethod
    def extract_data(self, file_path: str, doc_type: str) -> dict:
        """
        Debe recibir la ruta del archivo y el tipo (factura, albaran, presupuesto...)
        Debe devolver un diccionario (JSON) con los datos extraídos.
        """
        pass