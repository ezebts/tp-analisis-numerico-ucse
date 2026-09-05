from app.utils.templates import error_mapping


@error_mapping
def required(d: dict) -> str:
    field = d.get("field")
    return f"Complete el campo {field}." if field else "Complete todos los campos."


@error_mapping
def unexpected(_d: dict) -> str:
    return "Ocurrió un error al calcular."


@error_mapping
def invalid_number(d: dict) -> str:
    field = d.get("field")
    value = d.get("value")
    
    if not field:
        return "Ingrese un número válido."
    
    extra = f' (recibido "{value}")' if value not in (None, "") else ""
    
    return f"Ingrese un número válido en {field}{extra}."


@error_mapping
def invalid_function(d: dict) -> str:
    value = d.get("value")
    extra = f' "{value}"' if value else ""
    
    return (
        f"No se pudo interpretar la función{extra}. "
        "Use una expresión en x, por ejemplo x^2 - 2."
    )


@error_mapping
def single_variable(d: dict) -> str:
    variables = d.get("variables") or []
    
    if not variables:
        return "La función debe depender de una sola variable (x)."
    
    nombres = ", ".join(str(symbol) for symbol in variables)
    
    return (
        "La función debe depender de una sola variable (x). "
        f"Variables encontradas: {nombres}."
    )


@error_mapping
def ImageNotReal(d: dict) -> str:
    x = d.get("x")
    extra = f" en x = {x}" if x is not None else ""
    return (
        f"f(x) no es un número real{extra}. "
        "Use un punto donde la función esté definida."
    )
