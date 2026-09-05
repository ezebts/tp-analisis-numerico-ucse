from pathlib import Path

from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    implicit_application,
    function_exponentiation
)


BASE_DIR = Path(__file__).parent


STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


SYMPY_PARSER = standard_transformations + (
    implicit_multiplication_application, 
    convert_xor,
    implicit_application,
    function_exponentiation
)
