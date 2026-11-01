"""
Regresión polinómica por mínimos cuadrados (matriz de potencias + Gauss-Jordan).
"""

from collections.abc import Sequence
from dataclasses import dataclass

from app.utils.templates import format_decimal
from app.unidad2.exceptions import PivoteNulo
from app.unidad2.sistemas_de_ecuaciones.metodos_directos import gauss_jordan
from app.unidad3.ajuste_de_curvas.regresion_lineal import Punto
from app.unidad3.exceptions import PocosPuntos, PocosValoresX
from app.unidad3.utils import GRADO_MAX, GRADO_MIN, MetodoPolinomial, calcular_r


@dataclass(frozen=True)
class RegresionPolinomialParams:
    puntos: Sequence[Punto]
    tolerancia: float
    grado: int


@dataclass(frozen=True)
class RegresionPolinomialResult:
    metodo: MetodoPolinomial
    coeficientes: tuple[float, ...]
    funcion: str
    r: float
    aceptable: bool
    puntos: tuple[Punto, ...]
    tolerancia: float
    grado: int


def armar_funcion(coeficientes: Sequence[float]) -> str:
    terminos: list[str] = []
    decimales = 4

    for i in range(len(coeficientes) - 1, -1, -1):
        coef = round(coeficientes[i], decimales)
        if coef == 0:
            continue

        if i == 0:
            cuerpo = format_decimal(abs(coef), decimales)
        elif i == 1:
            cuerpo = f"{format_decimal(abs(coef), decimales)}x"
        else:
            cuerpo = f"{format_decimal(abs(coef), decimales)}x^{i}"

        if not terminos:
            terminos.append(("-" if coef < 0 else "") + cuerpo)
        else:
            terminos.append((" - " if coef < 0 else " + ") + cuerpo)

    cuerpo = "".join(terminos)
    return f"y = {cuerpo if cuerpo else '0'}"


def generar_matriz_polinomial(grado: int, puntos: Sequence[Punto]) -> list[list[float]]:
    dimension = grado + 1
    matriz = [[0.0] * (dimension + 1) for _ in range(dimension)]

    for abscisa, ordenada in puntos:
        for fila in range(dimension):
            for col in range(dimension):
                matriz[fila][col] += abscisa ** (fila + col)
            matriz[fila][dimension] += ordenada * abscisa ** fila

    return matriz


def resolver_sistema(matriz: list[list[float]]) -> list[float]:
    """Elige el pivote de cada columna ya reducida y resuelve con Gauss-Jordan.

    El pivote de la columna siguiente se ve después de eliminar la actual.
    Si se permutan todas las filas antes, puede dejar un cero en la diagonal.
    """
    aumentada = [fila[:] for fila in matriz]
    n = len(aumentada)
    ancho = n + 1

    for col in range(n):
        fila_pivote = max(range(col, n), key=lambda f: abs(aumentada[f][col]))
        if abs(aumentada[fila_pivote][col]) < 1e-12:
            raise PocosValoresX(grado=n - 1)
        aumentada[col], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[col]

        pivote = aumentada[col][col]
        for j in range(ancho):
            aumentada[col][j] /= pivote
        for fila in range(n):
            if fila == col:
                continue
            factor = aumentada[fila][col]
            for j in range(ancho):
                aumentada[fila][j] -= factor * aumentada[col][j]

    try:
        return gauss_jordan(aumentada)
    except PivoteNulo as exc:
        raise PocosValoresX(grado=n - 1) from exc


def calcular_regresion_polinomica(
    params: RegresionPolinomialParams,
) -> RegresionPolinomialResult:
    grado = params.grado
    if grado < GRADO_MIN or grado > GRADO_MAX:
        raise ValueError("grado fuera de rango")

    puntos = [(float(abscisa), float(ordenada)) for abscisa, ordenada in params.puntos]
    if len(puntos) < 2:
        raise PocosPuntos()
    if len({abscisa for abscisa, _ in puntos}) <= grado:
        raise PocosValoresX(grado=grado)

    matriz = generar_matriz_polinomial(grado, puntos)
    coeficientes = tuple(resolver_sistema(matriz))
    r = calcular_r(puntos, coeficientes)

    return RegresionPolinomialResult(
        metodo=MetodoPolinomial.REGRESION_POLINOMIAL,
        coeficientes=coeficientes,
        funcion=armar_funcion(coeficientes),
        r=r,
        aceptable=r > params.tolerancia,
        puntos=tuple(puntos),
        tolerancia=params.tolerancia,
        grado=grado,
    )
