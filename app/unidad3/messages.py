from app.utils.templates import error_mapping


@error_mapping
def PocosPuntos(_d: dict) -> str:
    return "Se necesitan al menos 2 puntos."


@error_mapping
def EquisConstantes(_d: dict) -> str:
    return "Todos los valores de X son iguales: no se puede calcular la recta."


@error_mapping
def OrdenadasConstantes(_d: dict) -> str:
    return "Todos los valores de Y son iguales: no se puede calcular r."


@error_mapping
def AjustePeorQuePromedio(_d: dict) -> str:
    return "La curva ajusta peor que el promedio de Y: no se puede calcular r."


@error_mapping
def PocosValoresX(d: dict) -> str:
    grado = d.get("grado")
    return (
        f"Para grado {grado} se necesitan al menos {grado + 1} "
        "valores de X distintos."
    )


@error_mapping
def out_of_range(d: dict) -> str:
    field = d.get("field")
    if field == "tolerancia":
        etiqueta = "La tolerancia"
    elif field == "grado":
        etiqueta = "El grado"
    else:
        etiqueta = "El valor"
    return (
        f"{etiqueta} debe estar entre {d.get('min')} y {d.get('max')} "
        f"(recibido {d.get('value')})."
    )


@error_mapping
def cantidad_puntos(d: dict) -> str:
    return f"Ingrese entre {d.get('min')} y {d.get('max')} puntos."
