"""
Implementación de los metodos iterativos para sistemas de ecuaciones.
"""

from enum import StrEnum
from typing import Optional
from dataclasses import dataclass

from app.utils.exceptions import ValidationError, Error
from app.unidad1.utils import Tolerance
from app.unidad2.exceptions import PivoteNulo


class MetodoIterativo(StrEnum):
    GAUSS_SEIDEL = "gauss_seidel"


@dataclass(frozen=True)
class MetodoIterativoParams:
    metodo: MetodoIterativo
    matriz: list[list[float]]
    max_iteraciones: int
    tolerancia: Tolerance

    def get_metodo(self):
        if self.metodo == MetodoIterativo.GAUSS_SEIDEL:
            return gauss_seidel

        raise ValidationError(
            Error("invalid_method", value=self.metodo)
        )


@dataclass(frozen=True)
class MetodoIterativoResult:
    metodo: MetodoIterativo
    dimension: int
    converge: bool
    solucion: Optional[list[float]]
    iteraciones: int
    max_iteraciones: int
    tolerancia: Tolerance


def gauss_seidel(
    matriz: list[list[float]],
    tolerancia: float,
    max_iteraciones: int,
) -> tuple[list[float], int, bool]:
    """ Estrategia de Gauss-Seidel (Von Mises) sobre la matriz aumentada. """
    contador = 0
    dimension = len(matriz)
    es_solucion = False
    vector_resultado = [0.0] * dimension
    vector_anterior = [0.0] * dimension

    while contador <= max_iteraciones and not es_solucion:
        contador += 1
        if contador > 1:
            vector_anterior = vector_resultado[:]

        for fila in range(dimension):
            resultado = matriz[fila][dimension]
            coeficiente_incognita = matriz[fila][fila]
            if coeficiente_incognita == 0:
                raise PivoteNulo(fila=fila)

            for col in range(dimension):
                if fila != col:
                    resultado = resultado - (matriz[fila][col] * vector_resultado[col])

            vector_resultado[fila] = resultado / coeficiente_incognita

        contador_mismo_resultado = 0
        for i in range(dimension):
            actual = vector_resultado[i]
            if actual != 0:
                error_relativo = abs((actual - vector_anterior[i]) / actual)
            else:
                error_relativo = abs(actual - vector_anterior[i])

            if error_relativo < tolerancia:
                contador_mismo_resultado += 1

        es_solucion = contador_mismo_resultado == dimension

    return vector_resultado, contador, es_solucion and contador <= max_iteraciones


def calcular_metodo_iterativo(params: MetodoIterativoParams) -> MetodoIterativoResult:
    calcular = params.get_metodo()
    aumentada = [fila[:] for fila in params.matriz]
    dimension = len(aumentada)

    try:
        solucion, iteraciones, converge = calcular(
            aumentada,
            params.tolerancia.value,
            params.max_iteraciones,
        )
    except PivoteNulo:
        return MetodoIterativoResult(
            metodo=params.metodo,
            dimension=dimension,
            converge=False,
            solucion=None,
            iteraciones=0,
            max_iteraciones=params.max_iteraciones,
            tolerancia=params.tolerancia,
        )
    except (ZeroDivisionError, OverflowError, ValueError):
        return MetodoIterativoResult(
            metodo=params.metodo,
            dimension=dimension,
            converge=False,
            solucion=None,
            iteraciones=0,
            max_iteraciones=params.max_iteraciones,
            tolerancia=params.tolerancia,
        )

    return MetodoIterativoResult(
        metodo=params.metodo,
        dimension=dimension,
        converge=converge,
        solucion=solucion,
        iteraciones=iteraciones,
        max_iteraciones=params.max_iteraciones,
        tolerancia=params.tolerancia,
    )
