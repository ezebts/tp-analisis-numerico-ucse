from app.utils.templates import error_mapping


@error_mapping
def PivoteNulo(d: dict) -> str:
    fila = d.get("fila")
    extra = f" en la fila {fila + 1}" if isinstance(fila, int) else ""
    return (
        f"El sistema no tiene solución única (pivote nulo{extra} en la diagonal)."
    )
