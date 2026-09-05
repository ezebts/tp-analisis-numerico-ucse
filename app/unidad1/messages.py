from app.utils.templates import error_mapping


@error_mapping
def invalid_interval(d: dict) -> str:
    return (
        f"El intervalo debe ser [xi, xd] con xi < xd (recibido {d.get('interval')})."
    )


@error_mapping
def out_of_range(d: dict) -> str:
    return (
        f"La tolerancia debe estar entre {d.get('min')} y {d.get('max')} "
        f"(recibido {d.get('value')})."
    )


@error_mapping
def invalid_iterations(d: dict) -> str:
    value = d.get("value")
    extra = f' (recibido "{value}")' if value not in (None, "") else ""
    return f"Las iteraciones deben ser un entero mayor que 0{extra}."


@error_mapping
def invalid_method(d: dict) -> str:
    value = d.get("value")
    extra = f' (recibido "{value}")' if value not in (None, "") else ""
    return f"Seleccione un método válido{extra}."


@error_mapping
def IntervalDoesntCrossZero(d: dict) -> str:
    return (
        f"El intervalo {d.get('interval')} no cruza el eje x. "
        "f(xi) y f(xd) deben tener signos opuestos."
    )
