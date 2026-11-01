from math import isfinite

from sympy import Expr, Integral, N, integrate, symbols

from app.utils.interval import Interval


DECIMALES_AREA = 4


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
