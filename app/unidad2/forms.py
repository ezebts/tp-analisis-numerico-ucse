from pydantic import BaseModel, Field, ValidationInfo, field_validator
from pydantic_core import PydanticCustomError

from app.unidad2.sistemas_de_ecuaciones.metodos_directos import MetodoDirecto
from app.unidad2.sistemas_de_ecuaciones.metodos_iterativos import MetodoIterativo

MetodoSistema = MetodoDirecto | MetodoIterativo


DIMENSION_MIN = 2
DIMENSION_MAX = 10


class GenerarForm(BaseModel):
    dimension: int = Field(ge=DIMENSION_MIN, le=DIMENSION_MAX)
    metodo: MetodoSistema
    matriz: list[float] = Field(default_factory=list)

    @field_validator("dimension", "metodo", "matriz", mode="before")
    @classmethod
    def normalize(cls, value: object, info: ValidationInfo) -> object:
        return _normalize(value, info.field_name)


class CalcularForm(BaseModel):
    dimension: int = Field(ge=DIMENSION_MIN, le=DIMENSION_MAX)
    metodo: MetodoSistema
    iteraciones: int | None = Field(default=None, gt=0)
    tolerancia: float | None = None
    matriz: list[float]

    @field_validator("dimension", "metodo", "iteraciones", "tolerancia", "matriz", mode="before")
    @classmethod
    def normalize(cls, value: object, info: ValidationInfo) -> object:
        return _normalize(value, info.field_name)

    @field_validator("iteraciones", "tolerancia")
    @classmethod
    def require_unless_jordan(cls, value: object, info: ValidationInfo) -> object:
        if value is None and info.data.get("metodo") != MetodoDirecto.GAUSS_JORDAN:
            raise PydanticCustomError(
                "required",
                "required",
                {"field": info.field_name},
            )
        return value


def _normalize(value: object, field_name: str | None) -> object:
    if field_name == "matriz":
        return _normalize_coeficientes(value)

    if not isinstance(value, str):
        return value

    texto = value.strip()
    if field_name in {"dimension", "iteraciones", "tolerancia"}:
        texto = texto.replace(",", ".")

    if not texto:
        if field_name in {"iteraciones", "tolerancia"}:
            return None
        raise PydanticCustomError(
            "required",
            "required",
            {"field": field_name},
        )

    return texto


def _normalize_coeficientes(value: object) -> list:
    if value is None:
        return []

    items = value if isinstance(value, list) else [value]
    normalizados = []

    for item in items:
        if isinstance(item, str):
            texto = item.strip().replace(",", ".")
            if not texto:
                raise PydanticCustomError(
                    "required",
                    "required",
                    {"field": "matriz"},
                )
            normalizados.append(texto)
        else:
            normalizados.append(item)

    return normalizados
