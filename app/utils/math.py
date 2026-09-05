from math import isfinite

from sympy import diff, lambdify, symbols

from app.utils.exceptions import Error


PASO_DERIVADA = 0.0001


class ImageNotReal(Error):
    """
    Excepción lanzada cuando f(x) no es un número real
    """

    def __init__(self, x: float):
        super().__init__(x=x)


def evalr(f, x) -> float:
    """ Evalúa f(x) como un float real. """

    try:
        y = f(x)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ImageNotReal(x) from exc

    if isinstance(y, complex):
        raise ImageNotReal(x)

    try:
        valor = float(y)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ImageNotReal(x) from exc

    if not isfinite(valor):
        raise ImageNotReal(x)

    return valor


def derivada_simbolica(f):
    try:
        return lambdify(symbols("x"), diff(f, symbols("x")), modules="math")
    except (ValueError, TypeError, OverflowError, ZeroDivisionError, NotImplementedError):
        return lambda _: float("nan")


def derivada_numerica(xi, fxi, f, df) -> float:
    """ Dx(xi) si se puede; si no, (f(xi + h) - f(xi)) / h. """

    try:
        derivada = float(df(xi))
        if isfinite(derivada):
            return derivada
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        pass

    try: # Intento aproximar
        return (float(f(xi + PASO_DERIVADA)) - fxi) / PASO_DERIVADA
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        return float("nan")
