from math import sqrt

from app.utils.parser import parse_expression
from app.unidad1.utils import Tolerance
from app.unidad1.raices_de_funciones.metodos_abiertos import (
    MetodoAbierto,
    MetodoAbiertoParams,
    calcular_metodo_abierto,
)


def test_tangente_converge():
    resultado = calcular_metodo_abierto(
        MetodoAbiertoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoAbierto.TANGENTE,
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
            xi=1.0,
        ),
    )

    assert resultado.converge
    assert resultado.raiz is not None
    assert abs(resultado.raiz - sqrt(2)) < 1e-3
    assert resultado.iteraciones < resultado.max_iteraciones
    assert resultado.xd is None


def test_tangente_diverge():
    resultado = calcular_metodo_abierto(
        MetodoAbiertoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoAbierto.TANGENTE,
            max_iteraciones=2,
            tolerancia=Tolerance(0.0001),
            xi=1.0,
        ),
    )

    assert not resultado.converge
    assert resultado.raiz is not None
    assert resultado.iteraciones == 2


def test_secante_converge():
    resultado = calcular_metodo_abierto(
        MetodoAbiertoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoAbierto.SECANTE,
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
            xi=1.0,
            xd=2.0,
        ),
    )

    assert resultado.converge
    assert resultado.raiz is not None
    assert abs(resultado.raiz - sqrt(2)) < 1e-3
    assert resultado.iteraciones < resultado.max_iteraciones


def test_secante_diverge():
    resultado = calcular_metodo_abierto(
        MetodoAbiertoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoAbierto.SECANTE,
            max_iteraciones=2,
            tolerancia=Tolerance(0.0001),
            xi=1.0,
            xd=2.0,
        ),
    )

    assert not resultado.converge
    assert resultado.raiz is not None
    assert resultado.iteraciones == 2


def test_tangente_converge_con_derivada_numerica():
    resultado = calcular_metodo_abierto(
        MetodoAbiertoParams(
            func=parse_expression("abs(x^2 - 2)"),
            metodo=MetodoAbierto.TANGENTE,
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
            xi=1.0,
        ),
    )

    assert resultado.converge
    assert resultado.raiz is not None
    assert abs(resultado.raiz - sqrt(2)) < 1e-3
