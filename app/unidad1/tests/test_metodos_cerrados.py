from math import sqrt

from app.utils.parser import parse_expression
from app.unidad1.utils import Interval, Tolerance
from app.unidad1.raices_de_funciones.metodos_cerrados import (
    MetodoCerrado,
    MetodoCerradoParams,
    calcular_metodo_cerrado,
)


def test_biseccion_converge():
    resultado = calcular_metodo_cerrado(
        MetodoCerradoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoCerrado.BISECCION,
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
            interval=Interval(1.0, 2.0),
        ),
    )

    assert resultado.converge
    assert resultado.raiz is not None
    assert abs(resultado.raiz - sqrt(2)) < 1e-3
    assert resultado.iteraciones < resultado.max_iteraciones


def test_biseccion_diverge():
    resultado = calcular_metodo_cerrado(
        MetodoCerradoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoCerrado.BISECCION,
            max_iteraciones=2,
            tolerancia=Tolerance(0.0001),
            interval=Interval(1.0, 2.0),
        ),
    )

    assert not resultado.converge
    assert resultado.raiz is None
    assert resultado.iteraciones == 2


def test_regla_falsa_converge():
    resultado = calcular_metodo_cerrado(
        MetodoCerradoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoCerrado.REGLA_FALSA,
            max_iteraciones=100,
            tolerancia=Tolerance(0.0001),
            interval=Interval(1.0, 2.0),
        ),
    )

    assert resultado.converge
    assert resultado.raiz is not None
    assert abs(resultado.raiz - sqrt(2)) < 1e-3
    assert resultado.iteraciones < resultado.max_iteraciones


def test_regla_falsa_diverge():
    resultado = calcular_metodo_cerrado(
        MetodoCerradoParams(
            func=parse_expression("x^2 - 2"),
            metodo=MetodoCerrado.REGLA_FALSA,
            max_iteraciones=2,
            tolerancia=Tolerance(0.0001),
            interval=Interval(1.0, 2.0),
        ),
    )

    assert not resultado.converge
    assert resultado.raiz is None
    assert resultado.iteraciones == 2
