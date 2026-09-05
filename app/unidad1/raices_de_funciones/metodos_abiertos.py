"""
Implementación de los metodos abiertos tangente y secante.
"""

from enum import StrEnum
from typing import Optional
from dataclasses import dataclass
from math import isfinite, isnan

from sympy import Expr, diff, lambdify, symbols

from app.unidad1.utils import Tolerance
from app.utils.exceptions import ValidationError, Error


PASO_DERIVADA = 0.0001


class MetodoAbierto(StrEnum):
    TANGENTE = "tangente"
    SECANTE = "secante"


@dataclass(frozen=True)
class MetodoAbiertoParams:
    func: Expr
    metodo: MetodoAbierto
    max_iteraciones: int
    tolerancia: Tolerance
    xi: float
    xd: Optional[float] = None

    def get_metodo(self):

        if self.metodo == MetodoAbierto.TANGENTE:
            return tangente(self.func, self.tolerancia)

        if self.metodo == MetodoAbierto.SECANTE:
            return secante

        raise ValidationError(
            Error("invalid_method", value=self.metodo)
        )


@dataclass(frozen=True)
class MetodoAbiertoResult:
    metodo: MetodoAbierto
    iteraciones: int
    max_iteraciones: int
    tolerancia: Tolerance
    xi: float
    xd: Optional[float]
    error: float
    converge: bool
    raiz: Optional[float]


def derivada_simbolica(func: Expr):
    try:
        return lambdify(symbols("x"), diff(func, symbols("x")), modules="math")
    except (ValueError, TypeError, OverflowError, ZeroDivisionError, NotImplementedError):
        return None


def derivada_numerica(xi, fxi, f, df) -> float:
    """ Dx(xi) si se puede; si no, (f(xi + h) - f(xi)) / h. """
    
    if df is not None:
        try:
            derivada = float(df(xi))
            if isfinite(derivada):
                return derivada
        except (ValueError, TypeError, OverflowError, ZeroDivisionError):
            pass
    
    try: # Aproximamos
        return (float(f(xi + PASO_DERIVADA)) - fxi) / PASO_DERIVADA
    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        return float("nan")


def tangente(func: Expr, tolerancia: Tolerance):
    """ Estrategia de la tangente (Newton-Raphson). """
    f = lambdify(symbols("x"), func, modules="math")
    df = derivada_simbolica(func)

    def calcular_xr(xi, xd, fxi, fxd):
        derivada = derivada_numerica(xi, fxi, f, df)
        if isnan(derivada) or abs(derivada) < tolerancia.value:
            return float("nan")
        return xi - fxi / derivada

    return calcular_xr


def secante(xi, xd, fxi, fxd) -> float:
    """ Estrategia de la secante. """
    return (fxd * xi - fxi * xd) / (fxd - fxi)


def calcular_metodo_abierto(params: MetodoAbiertoParams) -> MetodoAbiertoResult:

    calcular_xr = params.get_metodo()

    f = lambdify(symbols("x"), params.func, modules="math")

    xi, xd = params.xi, params.xd
    xant = 0.0
    error = 0.0
    xr = xi

    fxi = float(f(xi))
    if params.tolerancia.acepts(fxi):
        return MetodoAbiertoResult(
            metodo=params.metodo,
            iteraciones=1,
            max_iteraciones=params.max_iteraciones,
            tolerancia=params.tolerancia,
            xi=params.xi,
            xd=params.xd,
            error=0.0,
            converge=True,
            raiz=xi,
        )

    if params.metodo == MetodoAbierto.SECANTE:
        fxd = float(f(xd))
        if params.tolerancia.acepts(fxd):
            return MetodoAbiertoResult(
                metodo=params.metodo,
                iteraciones=1,
                max_iteraciones=params.max_iteraciones,
                tolerancia=params.tolerancia,
                xi=params.xi,
                xd=params.xd,
                error=0.0,
                converge=True,
                raiz=xd,
            )

    for i in range(1, params.max_iteraciones + 1):
        fxi = float(f(xi))
        fxd = float(f(xd)) if xd is not None else fxi

        try:
            xr = calcular_xr(xi, xd if xd is not None else xi, fxi, fxd)
        except (ValueError, TypeError, OverflowError, ZeroDivisionError):
            xr = float("nan")

        if isnan(xr):
            return MetodoAbiertoResult(
                metodo=params.metodo,
                iteraciones=i,
                max_iteraciones=params.max_iteraciones,
                tolerancia=params.tolerancia,
                xi=params.xi,
                xd=params.xd,
                error=error,
                converge=False,
                raiz=None,
            )

        fxr = float(f(xr))

        if xr != 0:
            error = abs(xr - xant) / abs(xr)
        else:
            error = abs(xr - xant)

        if params.tolerancia.acepts(fxr) or params.tolerancia.acepts(error):
            return MetodoAbiertoResult(
                metodo=params.metodo,
                iteraciones=i,
                max_iteraciones=params.max_iteraciones,
                tolerancia=params.tolerancia,
                xi=params.xi,
                xd=params.xd,
                error=error,
                converge=True,
                raiz=xr,
            )

        if params.metodo == MetodoAbierto.TANGENTE:
            xi = xr
        else:
            xi = xd
            xd = xr

        xant = xr

    return MetodoAbiertoResult(
        metodo=params.metodo,
        iteraciones=params.max_iteraciones,
        max_iteraciones=params.max_iteraciones,
        tolerancia=params.tolerancia,
        xi=params.xi,
        xd=params.xd,
        error=error,
        converge=False,
        raiz=xr,
    )
