import pytest

from app.unidad3.ajuste_de_curvas.regresion_polinomica import (
    RegresionPolinomialParams,
    calcular_regresion_polinomica,
    resolver_sistema,
)
from app.unidad3.exceptions import PocosValoresX
from app.utils.graph import Grafico
from app.utils.interval import Interval

EJEMPLO_1 = [
    (-1.0, 6.0),
    (0.0, 4.0),
    (2.0, 1.0),
    (3.0, 1.0),
    (5.0, 2.0),
    (6.0, 5.0),
]

EJEMPLO_2 = [
    (-3.2, 4.8),
    (-2.75, -4.05),
    (-1.0, 0.0),
    (0.0, 3.0),
    (0.5, 2.0),
    (1.5, -1.4),
    (2.0, 0.0),
    (2.33, 4.0),
]


def _params(puntos, grado=2, tolerancia=80.0):
    return RegresionPolinomialParams(
        puntos=puntos,
        tolerancia=tolerancia,
        grado=grado,
    )


def test_ejemplo_apunte_grado_2():
    resultado = calcular_regresion_polinomica(_params(EJEMPLO_1, grado=2))

    assert resultado.funcion == "y = 0.375x^2 - 2.1017x + 3.7333"
    assert resultado.r == pytest.approx(98.5516, abs=0.0001)
    assert resultado.aceptable
    assert resultado.grado == 2
    assert len(resultado.coeficientes) == 3


def test_ejemplo_apunte_grado_4():
    resultado = calcular_regresion_polinomica(_params(EJEMPLO_2, grado=4))

    assert resultado.funcion == (
        "y = 0.5085x^4 + 0.5102x^3 - 3.5586x^2 - 0.4989x + 3.0355"
    )
    assert resultado.r == pytest.approx(99.9973, abs=0.0001)
    assert resultado.aceptable


def test_pivote_inicial_en_cero():
    assert resolver_sistema([[0.0, 1.0, 1.0], [1.0, 0.0, 2.0]]) == pytest.approx([2.0, 1.0])


def test_pocos_valores_x_distintos():
    with pytest.raises(PocosValoresX):
        calcular_regresion_polinomica(
            _params([(1.0, 2.0), (2.0, 4.0), (1.0, 5.0)], grado=2)
        )


def test_grafico_evalua_polinomio():
    resultado = calcular_regresion_polinomica(_params(EJEMPLO_1, grado=2))
    grafico = Grafico.de_ajuste(resultado.puntos, Interval(-2, 8), resultado.coeficientes)

    assert grafico.xs[0] == -2
    assert grafico.ys[0] == pytest.approx(
        sum(c * grafico.xs[0] ** i for i, c in enumerate(resultado.coeficientes))
    )
