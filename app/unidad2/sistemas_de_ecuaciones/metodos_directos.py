"""
Implementación de los metodos directos para sistemas de ecuaciones.
"""

from enum import StrEnum
from typing import Optional
from dataclasses import dataclass

from app.utils.exceptions import ValidationError, Error
from app.unidad2.exceptions import PivoteNulo


class MetodoDirecto(StrEnum):
    GAUSS_JORDAN = "gauss_jordan"


@dataclass(frozen=True)
class MetodoDirectoParams:
    metodo: MetodoDirecto
    matriz: list[list[float]]

    def get_metodo(self):
        if self.metodo == MetodoDirecto.GAUSS_JORDAN:
            return gauss_jordan

        raise ValidationError(
            Error("invalid_method", value=self.metodo)
        )


@dataclass(frozen=True)
class MetodoDirectoResult:
    metodo: MetodoDirecto
    dimension: int
    converge: bool
    solucion: Optional[list[float]]


def gauss_jordan(matriz: list[list[float]]) -> list[float]:
    """ Estrategia de Gauss-Jordan sobre la matriz aumentada n x (n+1). """
    n = len(matriz)

    for fila_diag in range(n):
        coeficiente_diagonal = matriz[fila_diag][fila_diag]
        if coeficiente_diagonal == 0:
            raise PivoteNulo(fila=fila_diag)

        for col in range(n + 1):
            matriz[fila_diag][col] = matriz[fila_diag][col] / coeficiente_diagonal

        for fila in range(n):
            if fila_diag == fila:
                continue

            coeficiente_cero = matriz[fila][fila_diag]
            for col in range(n + 1):
                matriz[fila][col] = (
                    matriz[fila][col] - (coeficiente_cero * matriz[fila_diag][col])
                )

    return [matriz[i][n] for i in range(n)]


def calcular_metodo_directo(params: MetodoDirectoParams) -> MetodoDirectoResult:
    calcular = params.get_metodo()
    aumentada = [fila[:] for fila in params.matriz]
    dimension = len(aumentada)

    try:
        solucion = calcular(aumentada)
    except PivoteNulo:
        solucion = None
    except (ZeroDivisionError, OverflowError, ValueError):
        solucion = None

    return MetodoDirectoResult(
        metodo=params.metodo,
        dimension=dimension,
        converge=solucion is not None,
        solucion=solucion,
    )
