
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError

from app.unidad1.raices_de_funciones.metodos_abiertos import MetodoAbierto
from app.unidad1.raices_de_funciones.metodos_cerrados import MetodoCerrado


class CalcularForm(BaseModel):
    funcion: str
    metodo: MetodoCerrado | MetodoAbierto
    iteraciones: int = Field(gt=0)
    tolerancia: float
    xi: float
    xd: float | None = None
    xmin: float
    xmax: float

    @field_validator(
        "funcion",
        "metodo",
        "iteraciones",
        "tolerancia",
        "xi",
        "xd",
        "xmin",
        "xmax",
        mode="before",
    )
    @classmethod
    def normalize(cls, value: object, info: ValidationInfo) -> object:
        if not isinstance(value, str):
            return value
        
        texto = value.strip()
        
        if info.field_name in {"iteraciones", "tolerancia", "xi", "xd", "xmin", "xmax"}:
            texto = texto.replace(",", ".")
        
        if not texto:
            if info.field_name == "xd":
                return None
            raise PydanticCustomError(
                "required",
                "required",
                {"field": info.field_name},
            )
        
        return texto

    @field_validator("xd")
    @classmethod
    def require_xd_unless_tangente(cls, value: float | None, info: ValidationInfo) -> float | None:
        if value is None and info.data.get("metodo") != MetodoAbierto.TANGENTE:
            raise PydanticCustomError(
                "required",
                "required",
                {"field": "xd"},
            )
        return value
