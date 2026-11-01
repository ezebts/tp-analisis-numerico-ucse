from app.utils.templates import error_mapping


@error_mapping
def required(d: dict) -> str:
    field = d.get("field")
    if field == "matriz":
        return "Complete todos los coeficientes de la matriz."
    if field in {"xs", "ys", "puntos"}:
        return "Complete las coordenadas de todos los puntos."
    if field == "funcion_modificada":
        return "Ingrese la función. Ejemplo: y = 2.5x - 1.3."
    if field == "n":
        return "Ingrese la cantidad de subintervalos."
    return f"Complete el campo {field}." if field else "Complete todos los campos."


@error_mapping
def unexpected(_d: dict) -> str:
    return "Ocurrió un error al calcular."


@error_mapping
def invalid_number(d: dict) -> str:
    field = d.get("field")
    value = d.get("value")
    
    if field == "matriz":
        field = "la matriz"
    elif field in {"xs", "ys", "puntos"}:
        field = "los puntos"
    elif field == "n":
        field = "subintervalos"

    if not field:
        return "Ingrese un número válido."
    
    extra = f' (recibido "{value}")' if value not in (None, "") else ""
    
    return f"Ingrese un número válido en {field}{extra}."


@error_mapping
def NoEsPolinomio(_d: dict) -> str:
    return "Se espera un polinomio en x. Ejemplo: y = 2.5x - 1.3."


@error_mapping
def GradoExcedido(d: dict) -> str:
    grado = d.get("grado")
    if grado == 1:
        return "Se espera una recta (grado 1). Ejemplo: y = 2.5x - 1.3."
    return f"Se espera un polinomio de grado a lo sumo {grado}."


@error_mapping
def invalid_function(d: dict) -> str:
    value = d.get("value")
    extra = f' "{value}"' if value else ""
    ejemplo = (
        "y = 2.5x - 1.3"
        if d.get("field") == "funcion_modificada"
        else "x^2 - 2"
    )

    return (
        f"No se pudo interpretar la función{extra}. "
        f"Use una expresión en x, por ejemplo {ejemplo}."
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
def invalid_interval(d: dict) -> str:
    return (
        f"El intervalo debe ser [xi, xd] con xi < xd (recibido {d.get('interval')})."
    )


@error_mapping
def ImageNotReal(d: dict) -> str:
    x = d.get("x")
    extra = f" en x = {x}" if x is not None else ""
    return (
        f"f(x) no es un número real{extra}. "
        "Use un punto donde la función esté definida."
    )
