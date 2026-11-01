import math

import pytest

from app.utils.exceptions import GradoExcedido, NoEsPolinomio, ValidationError
from app.utils.graph import Grafico
from app.utils.interval import Interval
from app.utils.parser import polinomio
from app.unidad3.ajuste_de_curvas.regresion_lineal import (
    RegresionLinealParams,
    calcular_regresion_lineal,
)
from app.unidad3.exceptions import (
    AjustePeorQuePromedio,
    EquisConstantes,
    OrdenadasConstantes,
    PocosPuntos,
)
from app.unidad3.utils import (
    PUNTOS_MAX,
    agregar_punto,
    quitar_punto,
    r_funcion_modificada,
)

PUNTOS = [(1.0, 2.0), (2.0, 4.0), (3.0, 5.0), (4.0, 4.0), (5.0, 5.0)]


def _params(puntos=PUNTOS, tolerancia=80.0):
    return RegresionLinealParams(puntos=puntos, tolerancia=tolerancia)


def test_ejemplo_apunte():
    resultado = calcular_regresion_lineal(_params())

    assert resultado.a1 == pytest.approx(0.6)
    assert resultado.a0 == pytest.approx(2.2)
    assert resultado.funcion == "y = 0.6x + 2.2"
    assert resultado.r == pytest.approx(math.sqrt((6 - 2.4) / 6) * 100)
    assert resultado.r == pytest.approx(77.46, abs=0.01)
    assert not resultado.aceptable
    assert resultado.puntos == tuple(PUNTOS)


def test_recta_modificada():
    modificada = r_funcion_modificada(PUNTOS, "y = 0.5x + 2.5", 80, 1)

    assert modificada.coeficientes[1] == pytest.approx(0.5)
    assert modificada.coeficientes[0] == pytest.approx(2.5)
    assert modificada.r == pytest.approx(math.sqrt((6 - 2.5) / 6) * 100)
    assert modificada.r == pytest.approx(76.38, abs=0.01)
    assert not modificada.aceptable


def test_recta_modificada_acepta_coma():
    modificada = r_funcion_modificada(PUNTOS, "y = 0,5x + 2,5", 80, 1)
    assert modificada.r == pytest.approx(76.38, abs=0.01)


def test_aceptable_si_r_supera_la_tolerancia():
    resultado = calcular_regresion_lineal(_params(tolerancia=70))
    assert resultado.aceptable

    estricto = calcular_regresion_lineal(_params(tolerancia=resultado.r))
    assert not estricto.aceptable


def test_funcion_con_ordenada_negativa():
    resultado = calcular_regresion_lineal(
        _params(puntos=[(0.0, -3.0), (2.0, 0.0)])
    )
    assert resultado.funcion == "y = 1.5x - 3"

    resultado = calcular_regresion_lineal(
        _params(puntos=[(0.0, -3.0), (1.0, -1.0)])
    )
    assert resultado.funcion == "y = 2x - 3"


def test_pocos_puntos():
    with pytest.raises(PocosPuntos):
        calcular_regresion_lineal(_params(puntos=[(1.0, 2.0)]))


def test_x_constantes():
    with pytest.raises(EquisConstantes):
        calcular_regresion_lineal(_params(puntos=[(2.0, 1.0), (2.0, 4.0)]))


def test_y_constantes():
    with pytest.raises(OrdenadasConstantes):
        calcular_regresion_lineal(_params(puntos=[(1.0, 3.0), (2.0, 3.0), (4.0, 3.0)]))


def test_recta_sin_prefijo_y():
    modificada = r_funcion_modificada(PUNTOS, "0.5x + 2.5", 80, 1)
    assert modificada.coeficientes[1] == pytest.approx(0.5)
    assert modificada.coeficientes[0] == pytest.approx(2.5)
    assert modificada.r == pytest.approx(76.38, abs=0.01)


def test_coeficientes_formas_flexibles():
    identidad = r_funcion_modificada([(0.0, 1.0), (2.0, 3.0)], "y = x + 1", 80, 1)
    assert (identidad.coeficientes[1], identidad.coeficientes[0]) == (1.0, 1.0)

    negativa = r_funcion_modificada([(0.0, 3.0), (2.0, 1.0)], "y = -x + 3", 80, 1)
    assert (negativa.coeficientes[1], negativa.coeficientes[0]) == (-1.0, 3.0)

    constante = r_funcion_modificada([(0.0, 2.0), (1.0, 4.0)], "y = 3", 80, 1)
    assert (constante.coeficientes[1], constante.coeficientes[0]) == (0.0, 3.0)


def test_funcion_invalida():
    with pytest.raises(ValidationError) as capturado:
        r_funcion_modificada(PUNTOS, "recta", 80, 1)
    assert capturado.value.details["funcion"][0].type == "invalid_function"
    with pytest.raises(ValidationError):
        r_funcion_modificada(PUNTOS, "   ", 80, 1)
    with pytest.raises(ValidationError):
        r_funcion_modificada(PUNTOS, "y =", 80, 1)


def test_se_espera_recta():
    with pytest.raises(GradoExcedido):
        r_funcion_modificada(PUNTOS, "y = x^2 + 1", 80, 1)
    with pytest.raises(NoEsPolinomio):
        r_funcion_modificada(PUNTOS, "sin(x)", 80, 1)
    assert polinomio("x^2 + 1").degree() == 2


def test_recta_peor_que_el_promedio():
    with pytest.raises(AjustePeorQuePromedio):
        r_funcion_modificada(PUNTOS, "y = 10x + 10", 80, 1)


def test_grafico_usa_la_escala_indicada():
    grafico = Grafico.de_ajuste(PUNTOS, Interval(0, 8), (2.2, 0.6))

    assert grafico.puntos_x == [1, 2, 3, 4, 5]
    assert grafico.xmin == 0
    assert grafico.xmax == 8
    assert grafico.misma_escala is True
    assert grafico.xs[0] == 0
    assert grafico.xs[-1] == 8
    assert grafico.ys[0] == pytest.approx(2.2)


def test_agregar_y_quitar_puntos():
    xs, ys = agregar_punto([1.0, 2.0], [3.0, 4.0])
    assert xs == [1.0, 2.0, 0.0]
    assert ys == [3.0, 4.0, 0.0]

    llenos = [float(i) for i in range(PUNTOS_MAX)]
    assert agregar_punto(llenos, llenos)[0] == llenos

    xs, ys = quitar_punto([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], 1)
    assert xs == [1.0, 3.0]
    assert ys == [4.0, 6.0]
    assert quitar_punto([1.0, 2.0], [3.0, 4.0], 0) == ([1.0, 2.0], [3.0, 4.0])
