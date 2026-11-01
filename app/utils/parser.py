import re

import sympy
from sympy import Poly, symbols
from sympy.parsing.sympy_parser import parse_expr

from app.settings import SYMPY_PARSER
from app.utils.exceptions import Error, GradoExcedido, NoEsPolinomio, ValidationError

x = symbols("x")


def parse_expression(expression: str) -> sympy.Expr:
    
    expresion = expression.strip()
    
    if not expresion:
        raise ValidationError(funcion=[Error("required")])
    
    try:
        func = parse_expr(expresion, transformations=SYMPY_PARSER)
    except Exception as exc:
        raise ValidationError(
            funcion=[Error("invalid_function", value=expresion)]
        ) from exc
    
    if len(func.free_symbols) > 1:
        raise ValidationError(
            funcion=[
                Error(
                    "single_variable",
                    variables=list(func.free_symbols),
                )
            ]
        )
    
    return func


def polinomio(funcion: str, grado: int | None = None) -> Poly:
    """Polinomio en x a partir de un texto. Si grado no es None, lo exige como máximo."""
    texto = (funcion or "").strip().replace(",", ".")
    if "=" in texto:
        texto = texto.split("=", 1)[1].strip()

    try:
        expr = parse_expression(texto)
    except ValidationError:
        # "recta" se parte en r*e*c*t*a por la multiplicación implícita.
        if re.fullmatch(r"[A-Za-z]+", texto):
            raise ValidationError(
                funcion=[Error("invalid_function", value=funcion)]
            ) from None
        raise

    if expr.free_symbols - {x} or not expr.is_polynomial(x):
        raise NoEsPolinomio(value=funcion)

    resultado = Poly(expr.expand(), x)
    if grado is not None and resultado.degree() > grado:
        raise GradoExcedido(grado=grado, value=funcion)
    return resultado
