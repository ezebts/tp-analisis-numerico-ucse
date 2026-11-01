from dataclasses import dataclass
from math import isfinite

from sympy import Expr, Integral, N, integrate, lambdify, symbols

from app.utils.interval import Interval
from app.utils.math import ImageNotReal, evalr


DECIMALES_AREA = 4
MUESTRAS_CURVA = 80
TOPE_GRAFICO = 1e6


@dataclass(frozen=True)
class GraficoIntegracion:
    xs: list[float]
    ys: list[float | None]
    area_xs: list[float]
    area_ys: list[float]


def integral_exacta(func: Expr, interval: Interval) -> float | None:
    """Valor de la integral si sympy la resuelve. Si no, None."""
    x = symbols("x")
    try:
        valor = integrate(func, (x, interval.xi, interval.xd))
    except Exception:
        return None
    if valor.free_symbols or valor.has(Integral):
        return None
    try:
        numero = complex(N(valor))
    except Exception:
        return None
    if numero.imag != 0 or not isfinite(numero.real):
        return None
    return float(numero.real)


def muestrear_funcion(
    func: Expr,
    interval: Interval,
    muestras: int = MUESTRAS_CURVA,
) -> tuple[list[float], list[float | None]]:
    f = lambdify(symbols("x"), func, modules="math")
    xi, xd = interval.xi, interval.xd
    paso = (xd - xi) / (muestras - 1) if muestras > 1 else 0
    xs: list[float] = []
    ys: list[float | None] = []
    for i in range(muestras):
        abscisa = xd if i == muestras - 1 else xi + paso * i
        xs.append(abscisa)
        try:
            ordenada = evalr(f, abscisa)
        except ImageNotReal:
            ys.append(None)
            continue
        ys.append(ordenada if abs(ordenada) <= TOPE_GRAFICO else None)
    return xs, ys


def grafico_desde_resultado(func: Expr, resultado) -> GraficoIntegracion:
    xs, ys = muestrear_funcion(func, resultado.interval)
    return GraficoIntegracion(
        xs=xs,
        ys=ys,
        area_xs=[x for x, _ in resultado.paneles],
        area_ys=[y for _, y in resultado.paneles],
    )
