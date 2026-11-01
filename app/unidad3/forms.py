from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from pydantic_core import PydanticCustomError

from app.unidad3.utils import (
    GRADO_INICIAL,
    GRADO_MAX,
    GRADO_MIN,
    MetodoAjuste,
    PUNTOS_MAX,
    PUNTOS_MIN,
    emparejar_puntos,
)

TOLERANCIA_MIN = 0
TOLERANCIA_MAX = 100


class PuntosForm(BaseModel):
    metodo: MetodoAjuste
    tolerancia: float
    grado: int = Field(default=GRADO_INICIAL, ge=GRADO_MIN, le=GRADO_MAX)
    xmin: float
    xmax: float
    xs: list[float]
    ys: list[float]

    @field_validator("metodo", "tolerancia", "grado", "xmin", "xmax", "xs", "ys", mode="before")
    @classmethod
    def normalize(cls, value: object, info: ValidationInfo) -> object:
        return _normalize(value, info.field_name)

    @field_validator("tolerancia")
    @classmethod
    def rango_tolerancia(cls, value: float) -> float:
        if value <= TOLERANCIA_MIN or value > TOLERANCIA_MAX:
            raise PydanticCustomError(
                "out_of_range",
                "out_of_range",
                {
                    "field": "tolerancia",
                    "min": TOLERANCIA_MIN,
                    "max": TOLERANCIA_MAX,
                    "value": value,
                },
            )
        return value

    @field_validator("grado")
    @classmethod
    def rango_grado(cls, value: int) -> int:
        if value < GRADO_MIN or value > GRADO_MAX:
            raise PydanticCustomError(
                "out_of_range",
                "out_of_range",
                {
                    "field": "grado",
                    "min": GRADO_MIN,
                    "max": GRADO_MAX,
                    "value": value,
                },
            )
        return value

    @model_validator(mode="after")
    def validar_puntos(self):
        if len(self.xs) != len(self.ys):
            raise PydanticCustomError(
                "required",
                "required",
                {"field": "puntos"},
            )
        if len(self.xs) > PUNTOS_MAX:
            raise PydanticCustomError(
                "cantidad_puntos",
                "cantidad_puntos",
                {
                    "field": "puntos",
                    "min": PUNTOS_MIN,
                    "max": PUNTOS_MAX,
                    "value": len(self.xs),
                },
            )
        return self

    def puntos(self) -> list[tuple[float, float]]:
        return emparejar_puntos(self.xs, self.ys)


class QuitarPuntoForm(PuntosForm):
    indice: int = Field(ge=0)

    @field_validator("indice", mode="before")
    @classmethod
    def normalize_indice(cls, value: object, info: ValidationInfo) -> object:
        return _normalize(value, info.field_name)


class RectaModificadaForm(PuntosForm):
    funcion_modificada: str

    @field_validator("funcion_modificada", mode="before")
    @classmethod
    def normalize_funcion(cls, value: object, info: ValidationInfo) -> object:
        return _normalize(value, info.field_name)


def _normalize(value: object, field_name: str | None) -> object:
    if field_name in {"xs", "ys"}:
        return _normalize_lista(value, field_name or "puntos")

    if not isinstance(value, str):
        return value

    texto = value.strip()
    if field_name in {"tolerancia", "indice", "grado", "xmin", "xmax"}:
        texto = texto.replace(",", ".")

    if not texto:
        raise PydanticCustomError(
            "required",
            "required",
            {"field": field_name},
        )

    return texto


def _normalize_lista(value: object, field_name: str) -> list:
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
                    {"field": field_name},
                )
            normalizados.append(texto)
        else:
            normalizados.append(item)

    return normalizados
