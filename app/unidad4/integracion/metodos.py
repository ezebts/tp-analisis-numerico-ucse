"""
Integración numérica: trapecios, Simpson 1/3, Simpson 3/8 y la combinación de ambos.
"""

from enum import StrEnum
from dataclasses import dataclass

from sympy import Expr, lambdify, symbols

from app.utils.exceptions import Error, ValidationError
from app.utils.interval import Interval
from app.utils.math import evalr
from app.unidad4.exceptions import PocosSubintervalos, SubintervalosImpares


class MetodoIntegracion(StrEnum):
    TRAPECIOS_SIMPLE = "trapecios_simple"
    TRAPECIOS_MULTIPLE = "trapecios_multiple"
    SIMPSON_13_SIMPLE = "simpson_13_simple"
    SIMPSON_13_MULTIPLE = "simpson_13_multiple"
    SIMPSON_38 = "simpson_38"
    SIMPSON_COMBINADO = "simpson_combinado"


NOMBRES_METODO = {
    MetodoIntegracion.TRAPECIOS_SIMPLE: "Trapecios simple",
    MetodoIntegracion.TRAPECIOS_MULTIPLE: "Trapecios múltiples",
    MetodoIntegracion.SIMPSON_13_SIMPLE: "Simpson 1/3 simple",
    MetodoIntegracion.SIMPSON_13_MULTIPLE: "Simpson 1/3 múltiple",
    MetodoIntegracion.SIMPSON_38: "Simpson 3/8",
    MetodoIntegracion.SIMPSON_COMBINADO: "Simpson 1/3 y 3/8 combinados",
}

PASOS_PANEL = 12


def requiere_n(metodo: MetodoIntegracion) -> bool:
    return metodo in {
        MetodoIntegracion.TRAPECIOS_MULTIPLE,
        MetodoIntegracion.SIMPSON_13_MULTIPLE,
        MetodoIntegracion.SIMPSON_COMBINADO,
    }


@dataclass(frozen=True)
class IntegracionParams:
    func: Expr
    metodo: MetodoIntegracion
    interval: Interval
    n: int | None = None

    def get_metodo(self):
        if self.metodo == MetodoIntegracion.TRAPECIOS_SIMPLE:
            return trapecios_simple
        if self.metodo == MetodoIntegracion.TRAPECIOS_MULTIPLE:
            return trapecios_multiple
        if self.metodo == MetodoIntegracion.SIMPSON_13_SIMPLE:
            return simpson_13_simple
        if self.metodo == MetodoIntegracion.SIMPSON_13_MULTIPLE:
            return simpson_13_multiple
        if self.metodo == MetodoIntegracion.SIMPSON_38:
            return simpson_38
        if self.metodo == MetodoIntegracion.SIMPSON_COMBINADO:
            return simpson_combinado
        raise ValidationError(Error("invalid_method", value=self.metodo))


@dataclass(frozen=True)
class IntegracionResult:
    metodo: MetodoIntegracion
    area: float
    interval: Interval
    n: int | None
    paneles: tuple[tuple[float, float], ...]


def _valores(f, xi: float, xd: float, n: int) -> tuple[float, list[float]]:
    h = (xd - xi) / n
    ys = [evalr(f, xi + i * h) for i in range(n)]
    ys.append(evalr(f, xd))
    return h, ys


def _exigir_n(n: int | None, minimo: int) -> int:
    if n is None or n < minimo:
        raise PocosSubintervalos(n=0 if n is None else n, minimo=minimo)
    return n


def trapecios_simple(f, xi: float, xd: float, n: int | None = None) -> float:
    """Un solo trapecio entre xi y xd."""
    return (xd - xi) / 2 * (evalr(f, xi) + evalr(f, xd))


def trapecios_multiple(f, xi: float, xd: float, n: int | None = None) -> float:
    """Trapecios sobre n subintervalos iguales."""
    cantidad = _exigir_n(n, 1)
    h, ys = _valores(f, xi, xd, cantidad)
    return (h / 2) * (ys[0] + 2 * sum(ys[1:-1]) + ys[-1])


def simpson_13_simple(f, xi: float, xd: float, n: int | None = None) -> float:
    """Simpson 1/3 sobre el intervalo, con el punto medio."""
    h = (xd - xi) / 2
    return (h / 3) * (evalr(f, xi) + 4 * evalr(f, xi + h) + evalr(f, xd))


def simpson_13_multiple(f, xi: float, xd: float, n: int | None = None) -> float:
    """Simpson 1/3 sobre n subintervalos. n tiene que ser par."""
    cantidad = _exigir_n(n, 2)
    if cantidad % 2 != 0:
        raise SubintervalosImpares(n=cantidad)
    h, ys = _valores(f, xi, xd, cantidad)
    impares = sum(ys[i] for i in range(1, cantidad, 2))
    pares = sum(ys[i] for i in range(2, cantidad, 2))
    return (h / 3) * (ys[0] + 4 * impares + 2 * pares + ys[-1])


def simpson_38(f, xi: float, xd: float, n: int | None = None) -> float:
    """Simpson 3/8 sobre el intervalo, partido en tres."""
    h = (xd - xi) / 3
    return (3 * h / 8) * (
        evalr(f, xi)
        + 3 * evalr(f, xi + h)
        + 3 * evalr(f, xi + 2 * h)
        + evalr(f, xd)
    )


def simpson_combinado(f, xi: float, xd: float, n: int | None = None) -> float:
    """Si n es impar, Simpson 3/8 en los últimos 3 subintervalos y 1/3 en el resto."""
    cantidad = _exigir_n(n, 2)
    h = (xd - xi) / cantidad
    area = 0.0
    derecha = xd
    if cantidad % 2 == 1:
        inicio = xi + h * (cantidad - 3)
        area += simpson_38(f, inicio, xd)
        derecha = inicio
        cantidad -= 3
    if cantidad > 0:
        area += simpson_13_multiple(f, xi, derecha, cantidad)
    return area


def _parabola(y0: float, y1: float, y2: float, t: float) -> float:
    return (
        y0 * (t - 1) * (t - 2) / 2
        - y1 * t * (t - 2)
        + y2 * t * (t - 1) / 2
    )


def _cubica(y0: float, y1: float, y2: float, y3: float, t: float) -> float:
    nodos = (0, 1, 2, 3)
    ys = (y0, y1, y2, y3)
    total = 0.0
    for i, yi in enumerate(ys):
        base = 1.0
        for j, nodo in enumerate(nodos):
            if i == j:
                continue
            base *= (t - nodo) / (nodos[i] - nodo)
        total += yi * base
    return total


def _muestras(x0: float, x1: float, t_max: float, evaluar) -> list[tuple[float, float]]:
    puntos: list[tuple[float, float]] = []
    for k in range(PASOS_PANEL + 1):
        fraccion = k / PASOS_PANEL
        puntos.append((x0 + (x1 - x0) * fraccion, evaluar(t_max * fraccion)))
    return puntos


def _paneles_parabola(xi: float, h: float, ys: list[float]) -> list[tuple[float, float]]:
    puntos: list[tuple[float, float]] = []
    for i in range(0, len(ys) - 1, 2):
        x0 = xi + i * h
        pieza = _muestras(
            x0,
            x0 + 2 * h,
            2,
            lambda t, y0=ys[i], y1=ys[i + 1], y2=ys[i + 2]: _parabola(y0, y1, y2, t),
        )
        puntos.extend(pieza[1:] if puntos else pieza)
    return puntos


def _paneles_cubica(xi: float, h: float, ys: list[float]) -> list[tuple[float, float]]:
    return _muestras(
        xi,
        xi + 3 * h,
        3,
        lambda t: _cubica(ys[0], ys[1], ys[2], ys[3], t),
    )


def curva_cuadratura(
    metodo: MetodoIntegracion,
    f,
    xi: float,
    xd: float,
    n: int | None,
) -> tuple[tuple[float, float], ...]:
    """Puntos de la curva que el método integra, para sombrear el área."""
    if metodo == MetodoIntegracion.TRAPECIOS_SIMPLE:
        return ((xi, evalr(f, xi)), (xd, evalr(f, xd)))

    if metodo == MetodoIntegracion.SIMPSON_13_SIMPLE:
        h = (xd - xi) / 2
        ys = [evalr(f, xi), evalr(f, xi + h), evalr(f, xd)]
        return tuple(_paneles_parabola(xi, h, ys))

    if metodo == MetodoIntegracion.SIMPSON_38:
        h = (xd - xi) / 3
        ys = [evalr(f, xi), evalr(f, xi + h), evalr(f, xi + 2 * h), evalr(f, xd)]
        return tuple(_paneles_cubica(xi, h, ys))

    cantidad = n or 0
    h, ys = _valores(f, xi, xd, cantidad)

    if metodo == MetodoIntegracion.TRAPECIOS_MULTIPLE:
        puntos = [(xi + i * h, ys[i]) for i in range(cantidad)]
        puntos.append((xd, ys[-1]))
        return tuple(puntos)

    if metodo == MetodoIntegracion.SIMPSON_13_MULTIPLE:
        return tuple(_paneles_parabola(xi, h, ys))

    if cantidad % 2 == 1:
        corte = cantidad - 3
        puntos: list[tuple[float, float]] = []
        if corte > 0:
            puntos.extend(_paneles_parabola(xi, h, ys[: corte + 1]))
        cubica = _paneles_cubica(xi + corte * h, h, ys[corte:])
        puntos.extend(cubica[1:] if puntos else cubica)
        return tuple(puntos)

    return tuple(_paneles_parabola(xi, h, ys))


def calcular_integral(params: IntegracionParams) -> IntegracionResult:
    integrar = params.get_metodo()
    f = lambdify(symbols("x"), params.func, modules="math")
    xi, xd = params.interval.xi, params.interval.xd
    area = integrar(f, xi, xd, params.n)
    paneles = curva_cuadratura(params.metodo, f, xi, xd, params.n)
    return IntegracionResult(
        metodo=params.metodo,
        area=area,
        interval=params.interval,
        n=params.n,
        paneles=paneles,
    )
