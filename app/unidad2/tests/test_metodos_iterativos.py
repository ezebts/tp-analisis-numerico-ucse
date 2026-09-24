from app.unidad1.utils import Tolerance
from app.unidad2.sistemas_de_ecuaciones.metodos_iterativos import (
    MetodoIterativo,
    MetodoIterativoParams,
    calcular_metodo_iterativo,
)


def test_gauss_seidel_converge():
    resultado = calcular_metodo_iterativo(
        MetodoIterativoParams(
            metodo=MetodoIterativo.GAUSS_SEIDEL,
            matriz=[
                [10.0, 1.0, 1.0, 12.0],
                [1.0, 10.0, 1.0, 12.0],
                [1.0, 1.0, 10.0, 12.0],
            ],
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
        ),
    )

    assert resultado.converge
    assert resultado.solucion is not None
    assert resultado.iteraciones <= resultado.max_iteraciones
    assert abs(resultado.solucion[0] - 1.0) < 1e-3
    assert abs(resultado.solucion[1] - 1.0) < 1e-3
    assert abs(resultado.solucion[2] - 1.0) < 1e-3


def test_gauss_seidel_sistema_2x2():
    resultado = calcular_metodo_iterativo(
        MetodoIterativoParams(
            metodo=MetodoIterativo.GAUSS_SEIDEL,
            matriz=[
                [4.0, 1.0, 1.0],
                [1.0, 3.0, 2.0],
            ],
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
        ),
    )

    assert resultado.converge
    assert resultado.solucion is not None
    assert abs(resultado.solucion[0] - (1.0 / 11.0)) < 1e-3
    assert abs(resultado.solucion[1] - (7.0 / 11.0)) < 1e-3


def test_gauss_seidel_pivote_nulo():
    resultado = calcular_metodo_iterativo(
        MetodoIterativoParams(
            metodo=MetodoIterativo.GAUSS_SEIDEL,
            matriz=[
                [0.0, 1.0, 1.0],
                [1.0, 3.0, 2.0],
            ],
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
        ),
    )

    assert not resultado.converge
    assert resultado.solucion is None


def test_gauss_seidel_supera_iteraciones():
    resultado = calcular_metodo_iterativo(
        MetodoIterativoParams(
            metodo=MetodoIterativo.GAUSS_SEIDEL,
            matriz=[
                [1.0, 2.0, 3.0],
                [2.0, 1.0, 3.0],
            ],
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
        ),
    )

    assert not resultado.converge
    assert resultado.iteraciones > resultado.max_iteraciones


def test_gauss_seidel_respeta_iteraciones_de_la_vista():
    resultado = calcular_metodo_iterativo(
        MetodoIterativoParams(
            metodo=MetodoIterativo.GAUSS_SEIDEL,
            matriz=[
                [10.0, 1.0, 1.0, 12.0],
                [1.0, 10.0, 1.0, 12.0],
                [1.0, 1.0, 10.0, 12.0],
            ],
            max_iteraciones=1,
            tolerancia=Tolerance(0.0001),
        ),
    )

    assert not resultado.converge
    assert resultado.max_iteraciones == 1
    assert resultado.iteraciones > 1
