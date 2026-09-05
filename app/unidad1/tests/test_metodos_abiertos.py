from math import sqrt

from app.utils.parser import parse_expression
from app.unidad1.utils import Tolerance
from app.unidad1.raices_de_funciones.metodos_abiertos import (
    PASO_DERIVADA,
    MetodoAbierto,
    MetodoAbiertoParams,
    calcular_metodo_abierto,
    derivada_tangente,
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


def test_derivada_tangente_simbolica():
    f = lambda x: x * x - 2
    df = lambda x: 2 * x
    assert derivada_tangente(1.0, -1.0, f, df) == 2.0


def test_derivada_tangente_aproximada_si_falla_simbolica():
    f = lambda x: x * x - 2
    fxi = -1.0

    def df(_x):
        raise ValueError

    assert derivada_tangente(1.0, fxi, f, df) == (f(1.0 + PASO_DERIVADA) - fxi) / PASO_DERIVADA
