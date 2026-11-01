import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from app.utils.parser import polinomio, x
from app.unidad3.exceptions import AjustePeorQuePromedio, OrdenadasConstantes, PocosPuntos

PUNTOS_MIN = 2
PUNTOS_MAX = 20
PUNTOS_INICIALES = 4

GRADO_MIN = 2
GRADO_MAX = 10
GRADO_INICIAL = 2


class MetodoLineal(StrEnum):
    REGRESION_LINEAL = "regresion_lineal"


class MetodoPolinomial(StrEnum):
    REGRESION_POLINOMIAL = "regresion_polinomial"


MetodoAjuste = MetodoLineal | MetodoPolinomial


def emparejar_puntos(xs: Sequence[float], ys: Sequence[float]) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in zip(xs, ys, strict=True)]


def agregar_punto(xs: Sequence[float], ys: Sequence[float]) -> tuple[list[float], list[float]]:
    nuevos_xs = [float(x) for x in xs]
    nuevos_ys = [float(y) for y in ys]
    if len(nuevos_xs) >= PUNTOS_MAX:
        return nuevos_xs, nuevos_ys
    nuevos_xs.append(0.0)
    nuevos_ys.append(0.0)
    return nuevos_xs, nuevos_ys


def quitar_punto(
    xs: Sequence[float],
    ys: Sequence[float],
    indice: int,
) -> tuple[list[float], list[float]]:
    nuevos_xs = [float(x) for x in xs]
    nuevos_ys = [float(y) for y in ys]
    if len(nuevos_xs) <= PUNTOS_MIN or not 0 <= indice < len(nuevos_xs):
        return nuevos_xs, nuevos_ys
    del nuevos_xs[indice]
    del nuevos_ys[indice]
    return nuevos_xs, nuevos_ys


def evaluar_polinomio(abscisa: float, coeficientes: Sequence[float]) -> float:
    return sum(coef * abscisa**i for i, coef in enumerate(coeficientes))


def calcular_r(
    puntos: Sequence[tuple[float, float]],
    coeficientes: Sequence[float],
) -> float:
    """st, sr y el coeficiente de correlación r, en porcentaje."""
    if len(puntos) < 2:
        raise PocosPuntos()
    if len({y for _, y in puntos}) == 1:
        raise OrdenadasConstantes()

    n = len(puntos)
    promedio_y = sum(y for _, y in puntos) / n
    st = 0.0
    sr = 0.0
    for x, y in puntos:
        prediccion = evaluar_polinomio(x, coeficientes)
        st += (promedio_y - y) ** 2
        sr += (prediccion - y) ** 2

    diferencia = st - sr
    if diferencia < 0:
        if st > 0 and diferencia > -1e-8 * st:
            diferencia = 0.0
        else:
            raise AjustePeorQuePromedio()

    return math.sqrt(diferencia / st) * 100


@dataclass(frozen=True)
class FuncionModificadaResult:
    funcion: str
    coeficientes: tuple[float, ...]
    r: float
    aceptable: bool


def r_funcion_modificada(
    puntos: Sequence[tuple[float, float]],
    funcion: str,
    tolerancia: float,
    grado: int,
) -> FuncionModificadaResult:
    """r de una función escrita por el usuario, de grado a lo sumo el pedido."""
    curva = polinomio(funcion, grado=grado)
    coeficientes = tuple(
        float(curva.coeff_monomial(x**i if i else 1)) for i in range(grado + 1)
    )
    r = calcular_r(puntos, coeficientes)
    return FuncionModificadaResult(
        funcion=funcion.strip(),
        coeficientes=coeficientes,
        r=r,
        aceptable=r > tolerancia,
    )
