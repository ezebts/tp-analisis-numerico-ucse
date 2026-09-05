import sympy
from sympy.parsing.sympy_parser import parse_expr

from app.settings import SYMPY_PARSER
from app.utils.exceptions import Error, ValidationError


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
