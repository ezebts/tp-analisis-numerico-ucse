from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from sympy import Expr, lambdify, symbols

from app.utils.math import ImageNotReal, evalr


TOPE_GRAFICO = 1e6
MUESTRAS_FUNCION = 240
MUESTRAS = 80


class GraphInterval(Protocol):
    xi: float
    xd: float


def muestrear(
    func: Expr,
    interval: GraphInterval,
    muestras: int = MUESTRAS,
) -> tuple[list[float], list[float | None]]:
    """Muestras de f(x) en el intervalo. Los valores no graficables quedan en None."""
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


@dataclass(frozen=True)
class Grafico:
    """Series que grafico.js dibuja. Cada unidad completa solo las que usa."""

    xs: list[float]
    ys: list[float | None]
    xmin: float
    xmax: float
    puntos_x: list[float] = field(default_factory=list)
    puntos_y: list[float] = field(default_factory=list)
    area_xs: list[float] = field(default_factory=list)
    area_ys: list[float] = field(default_factory=list)
    raiz: float | None = None
    curva: str = "f(x)"
    titulo_x: str = "x"
    titulo_y: str = "y"
    uno_a_uno: bool = False
    misma_escala: bool = False
    incluye_cero: bool = False
    etiqueta_area: str = ""
    places: int = 4
    aria: str = "Gráfico de la función"

    @classmethod
    def de_funcion(
        cls,
        func: Expr,
        interval: GraphInterval,
        *,
        muestras: int = MUESTRAS,
        raiz: float | None = None,
        area: Sequence[tuple[float, float]] = (),
        etiqueta_area: str = "",
        curva: str = "f(x)",
        titulo_x: str = "x",
        titulo_y: str = "y",
        uno_a_uno: bool = False,
        misma_escala: bool = False,
        incluye_cero: bool = False,
        places: int = 4,
        aria: str = "Gráfico de la función",
    ) -> "Grafico":
        xs, ys = muestrear(func, interval, muestras)
        return cls(
            xs=xs,
            ys=ys,
            xmin=float(interval.xi),
            xmax=float(interval.xd),
            area_xs=[float(x) for x, _ in area],
            area_ys=[float(y) for _, y in area],
            raiz=raiz,
            curva=curva,
            titulo_x=titulo_x,
            titulo_y=titulo_y,
            uno_a_uno=uno_a_uno,
            misma_escala=misma_escala,
            incluye_cero=incluye_cero,
            etiqueta_area=etiqueta_area,
            places=places,
            aria=aria,
        )

    @classmethod
    def de_ajuste(
        cls,
        puntos: Sequence[tuple[float, float]],
        escala: GraphInterval,
        coeficientes: Sequence[float] | None = None,
        muestras: int = MUESTRAS,
    ) -> "Grafico":
        xs: list[float] = []
        ys: list[float | None] = []
        if coeficientes:
            x = symbols("x")
            curva = sum(coef * x**i for i, coef in enumerate(coeficientes))
            xs, ys = muestrear(curva, escala, muestras)
        return cls(
            xs=xs,
            ys=ys,
            xmin=float(escala.xi),
            xmax=float(escala.xd),
            puntos_x=[float(abscisa) for abscisa, _ in puntos],
            puntos_y=[float(ordenada) for _, ordenada in puntos],
            curva="Curva de ajuste",
            titulo_x="X",
            titulo_y="Y",
            misma_escala=True,
            aria="Gráfico del ajuste",
        )
