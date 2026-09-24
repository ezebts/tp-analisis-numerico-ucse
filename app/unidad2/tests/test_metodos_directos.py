import pytest

from app.unidad2.exceptions import PivoteNulo
from app.unidad2.sistemas_de_ecuaciones.metodos_directos import (
    MetodoDirecto,
    MetodoDirectoParams,
    calcular_metodo_directo,
    gauss_jordan,
)
from app.unidad2.utils import inferir_dimension, redimensionar_aumentada


def test_gauss_jordan_converge():
    resultado = calcular_metodo_directo(
        MetodoDirectoParams(
            metodo=MetodoDirecto.GAUSS_JORDAN,
            matriz=[
                [2.0, 1.0, 5.0],
                [1.0, 3.0, 5.0],
            ],
        ),
    )

    assert resultado.converge
    assert resultado.solucion is not None
    assert resultado.dimension == 2
    assert abs(resultado.solucion[0] - 2.0) < 1e-9
    assert abs(resultado.solucion[1] - 1.0) < 1e-9


def test_gauss_jordan_ejemplo_enunciado():
    resultado = calcular_metodo_directo(
        MetodoDirectoParams(
            metodo=MetodoDirecto.GAUSS_JORDAN,
            matriz=[
                [3.0, 1.0, 2.0, 0.0],
                [5.0, 4.0, 3.0, 2.0],
                [1.0, 3.0, 9.0, 5.0],
            ],
        ),
    )

    assert resultado.converge
    assert resultado.solucion is not None
    assert abs(resultado.solucion[0] + 0.5081967213114754) < 1e-9
    assert abs(resultado.solucion[1] - 0.9016393442622951) < 1e-9
    assert abs(resultado.solucion[2] - 0.3114754098360656) < 1e-9


def test_gauss_jordan_pivote_nulo():
    with pytest.raises(PivoteNulo) as captured:
        gauss_jordan([
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
        ])

    assert captured.value.details["fila"] == 0

    resultado = calcular_metodo_directo(
        MetodoDirectoParams(
            metodo=MetodoDirecto.GAUSS_JORDAN,
            matriz=[
                [0.0, 1.0, 1.0],
                [1.0, 0.0, 1.0],
            ],
        ),
    )

    assert not resultado.converge
    assert resultado.solucion is None


def test_redimensionar_conserva_terminos_independientes():
    matriz = redimensionar_aumentada(
        [3.0, 1.0, 2.0, 0.0, 5.0, 4.0, 3.0, 2.0, 1.0, 3.0, 9.0, 5.0],
        4,
    )

    assert inferir_dimension(12) == 3
    assert len(matriz) == 4
    assert matriz[0] == [3.0, 1.0, 2.0, 0.0, 0.0]
    assert matriz[1] == [5.0, 4.0, 3.0, 0.0, 2.0]
    assert matriz[3] == [0.0, 0.0, 0.0, 0.0, 0.0]
