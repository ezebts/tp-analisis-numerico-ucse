from pydantic import BaseModel, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError

from app.unidad4.integracion.metodos import MetodoIntegracion, requiere_n


class CalcularForm(BaseModel):
    funcion: str
    metodo: MetodoIntegracion
    xi: float
    xd: float
    n: int | None = None

    @field_validator("funcion", "metodo", "xi", "xd", "n", mode="before")
    @classmethod
    def normalize(cls, value: object, info: ValidationInfo) -> object:
        if not isinstance(value, str):
            return value

        texto = value.strip()
        if info.field_name in {"xi", "xd", "n"}:
            texto = texto.replace(",", ".")

        if not texto:
            if info.field_name == "n":
                return None
            raise PydanticCustomError(
                "required",
                "required",
                {"field": info.field_name},
            )
        return texto

    @field_validator("n")
    @classmethod
    def n_si_el_metodo_lo_pide(cls, value: int | None, info: ValidationInfo) -> int | None:
        metodo = info.data.get("metodo")
        if metodo is None or not requiere_n(metodo):
            return value
        if value is None:
            raise PydanticCustomError(
                "required",
                "required",
                {"field": "n"},
            )
        if value < 1:
            raise PydanticCustomError(
                "PocosSubintervalos",
                "PocosSubintervalos",
                {"field": "n", "n": value, "minimo": 1},
            )
        return value
