"""
Regresión lineal por mínimos cuadrados.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.utils.templates import format_decimal
from app.unidad3.exceptions import EquisConstantes, PocosPuntos
from app.unidad3.utils import MetodoLineal, calcular_r

Punto = tuple[float, float]


@dataclass(frozen=True)
class RegresionLinealParams:
    puntos: Sequence[Punto]
    tolerancia: float


@dataclass(frozen=True)
class RegresionLinealResult:
    metodo: MetodoLineal
    a1: float
    a0: float
    funcion: str
    r: float
    aceptable: bool
    puntos: tuple[Punto, ...]
    tolerancia: float


def calcular_regresion_lineal(params: RegresionLinealParams) -> RegresionLinealResult:

    puntos = [(float(x), float(y)) for x, y in params.puntos]

    if len(puntos) < 2:
        raise PocosPuntos()

    if len({x for x, _ in puntos}) == 1:
        raise EquisConstantes()

    n = len(puntos)
    suma_x = sum(x for x, _ in puntos)
    suma_y = sum(y for _, y in puntos)
    suma_xy = sum(x * y for x, y in puntos)
    suma_x2 = sum(x * x for x, _ in puntos)

    denominador = n * suma_x2 - suma_x ** 2
    a1 = (n * suma_xy - suma_x * suma_y) / denominador
    a0 = suma_y / n - a1 * (suma_x / n)
    r = calcular_r(puntos, (a0, a1))
    signo = "+" if a0 >= 0 else "-"
    funcion = f"y = {format_decimal(a1)}x {signo} {format_decimal(abs(a0))}"

    return RegresionLinealResult(
        metodo=MetodoLineal.REGRESION_LINEAL,
        a1=a1,
        a0=a0,
        funcion=funcion,
        r=r,
        aceptable=r > params.tolerancia,
        puntos=tuple(puntos),
        tolerancia=params.tolerancia,
    )
