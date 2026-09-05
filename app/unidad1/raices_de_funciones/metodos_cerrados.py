"""
Implementación de los metodos cerrados bisección y regla falsa.
"""

from enum import StrEnum
from typing import Optional
from dataclasses import dataclass

from sympy import Expr, lambdify, symbols

from app.unidad1.utils import Interval, Tolerance
from app.utils.exceptions import ValidationError, Error
from app.unidad1.exceptions import IntervalDoesntCrossZero


class MetodoCerrado(StrEnum):
    BISECCION = "biseccion"
    REGLA_FALSA = "regla_falsa"


@dataclass(frozen=True)
class MetodoCerradoParams:
    func: Expr
    metodo: MetodoCerrado
    max_iteraciones: int
    tolerancia: Tolerance
    interval: Interval
    
    def get_metodo(self):
        
        if self.metodo == MetodoCerrado.BISECCION:
            return biseccion
        
        if self.metodo == MetodoCerrado.REGLA_FALSA:
            return regla_falsa
        
        raise ValidationError(
            Error("invalid_method", value=self.metodo)
        )


@dataclass(frozen=True)
class MetodoCerradoResult:
    metodo: MetodoCerrado
    iteraciones: int
    max_iteraciones: int
    tolerancia: Tolerance
    interval: Interval
    error: float
    converge: bool
    raiz: Optional[float]


def biseccion(xi, xd, fxi, fxd) -> float:
    """ Estrategia de la bisección. """
    return (xi + xd) / 2


def regla_falsa(xi, xd, fxi, fxd) -> float:
    """ Estrategia de la regla falsa. """
    return (fxd * xi - fxi * xd) / (fxd - fxi)


def calcular_metodo_cerrado(params: MetodoCerradoParams) -> MetodoCerradoResult:

    calcular_xr = params.get_metodo()

    f = lambdify(symbols("x"), params.func, modules="math")

    xi, xd = params.interval.xi, params.interval.xd
    xant = 0.0
    error = 0.0

    for i in range(1, params.max_iteraciones + 1):
        fxi = float(f(xi))
        fxd = float(f(xd))

        if fxi == 0 or fxd == 0:
            return MetodoCerradoResult(
                metodo=params.metodo,
                iteraciones=i,
                max_iteraciones=params.max_iteraciones,
                tolerancia=params.tolerancia,
                interval=params.interval,
                error=0.0,
                converge=True,
                raiz=xi if fxi == 0 else xd,
            )

        if fxi * fxd > 0:
            raise IntervalDoesntCrossZero(params.interval)

        xr = calcular_xr(xi, xd, fxi, fxd)
        fxr = float(f(xr))

        if xr != 0:
            error = abs(xr - xant) / abs(xr)
        else:
            error = abs(xr - xant)

        if fxr == 0 or params.tolerancia.acepts(error) or params.tolerancia.acepts(fxr):
            return MetodoCerradoResult(
                metodo=params.metodo,
                iteraciones=i,
                max_iteraciones=params.max_iteraciones,
                tolerancia=params.tolerancia,
                interval=params.interval,
                error=error,
                converge=True,
                raiz=xr,
            )

        if fxi * fxr < 0:
            xd = xr
        else:
            xi = xr

        xant = xr

    return MetodoCerradoResult(
        metodo=params.metodo,
        iteraciones=params.max_iteraciones,
        max_iteraciones=params.max_iteraciones,
        tolerancia=params.tolerancia,
        interval=params.interval,
        error=error,
        converge=False,
        raiz=None,
    )
