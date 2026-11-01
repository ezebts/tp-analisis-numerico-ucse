from math import log

import pytest

from app.utils.interval import Interval
from app.utils.parser import parse_expression
from app.unidad4.exceptions import PocosSubintervalos, SubintervalosImpares
from app.unidad4.integracion.metodos import (
    IntegracionParams,
    MetodoIntegracion,
    calcular_integral,
)
from app.unidad4.utils import integral_exacta


def _area(funcion: str, metodo: MetodoIntegracion, xi: float, xd: float, n: int | None = None) -> float:
    resultado = calcular_integral(
        IntegracionParams(
            func=parse_expression(funcion),
            metodo=metodo,
            interval=Interval(xi, xd),
            n=n,
        )
    )
    return resultado.area


def test_trapecios_multiples_del_mockup():
    area = _area("1/x + x", MetodoIntegracion.TRAPECIOS_MULTIPLE, 0.5, 3.5, 10)
    assert area == pytest.approx(7.974358391960803)
    assert round(area, 4) == 7.9744


def test_integral_exacta_del_mockup():
    exacto = integral_exacta(parse_expression("1/x + x"), Interval(0.5, 3.5))
    assert exacto == pytest.approx(log(7) + 6)
    assert round(exacto, 4) == 7.9459


def test_trapecios_simple_ignora_n():
    sin_n = _area("x", MetodoIntegracion.TRAPECIOS_SIMPLE, 0, 2)
    con_n = _area("x", MetodoIntegracion.TRAPECIOS_SIMPLE, 0, 2, 10)
    assert sin_n == pytest.approx(2)
    assert con_n == pytest.approx(sin_n)


def test_simpson_13_simple_es_exacto_en_grado_2():
    assert _area("x^2", MetodoIntegracion.SIMPSON_13_SIMPLE, 0, 2) == pytest.approx(8 / 3)


def test_simpson_38_es_exacto_en_grado_3():
    assert _area("x^3", MetodoIntegracion.SIMPSON_38, 0, 3) == pytest.approx(81 / 4)


def test_simpson_13_multiple_rechaza_n_impar():
    with pytest.raises(SubintervalosImpares):
        _area("x^2", MetodoIntegracion.SIMPSON_13_MULTIPLE, 0, 2, 3)


def test_combinado_rechaza_un_subintervalo():
    with pytest.raises(PocosSubintervalos):
        _area("x^2", MetodoIntegracion.SIMPSON_COMBINADO, 0, 1, 1)


def test_combinado_par_coincide_con_simpson_13():
    combinado = _area("x^2", MetodoIntegracion.SIMPSON_COMBINADO, 0, 2, 4)
    multiple = _area("x^2", MetodoIntegracion.SIMPSON_13_MULTIPLE, 0, 2, 4)
    assert combinado == pytest.approx(multiple)
    assert combinado == pytest.approx(8 / 3)


def test_combinado_impar_es_exacto_en_un_cubico():
    assert _area("x^3", MetodoIntegracion.SIMPSON_COMBINADO, 0, 1, 5) == pytest.approx(0.25)


def test_paneles_de_trapecios_pasan_por_los_extremos():
    resultado = calcular_integral(
        IntegracionParams(
            func=parse_expression("1/x + x"),
            metodo=MetodoIntegracion.TRAPECIOS_MULTIPLE,
            interval=Interval(0.5, 3.5),
            n=10,
        )
    )
    assert len(resultado.paneles) == 11
    assert resultado.paneles[0][0] == pytest.approx(0.5)
    assert resultado.paneles[-1][0] == pytest.approx(3.5)
