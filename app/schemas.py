# app/schemas.py
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any

class LineaDocumento(BaseModel):
    numlinea: int
    referencia: str
    descripcion: str
    unidades: float
    preciounitario: float
    descuento: float
    preciototal: float
    articulobc: str
    naturaleza: str

class DatosCabecera(BaseModel):
    tipodocumento: str
    idempresa: str
    numdocumento: str
    fechadocumento: str
    fecharecepcion: str
    fechavalidez: str
    numpedidoproveedor: str
    numpedidocliente: str
    codigoproyectoprov: str
    codigoproyectobc: str
    codigoproveedorbc: str
    emisor: str
    cifemisor: str
    importebruto: float
    porcentajeiva: float
    importeiva: float
    importeneto: float
    naturaleza: str
    lines: List[LineaDocumento]

class RespuestaIA(BaseModel):
    data: DatosCabecera
    validaciones: List[Dict[str, Any]]
    paginas: Dict[str, Any]