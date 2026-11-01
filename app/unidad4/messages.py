from app.utils.templates import error_mapping


@error_mapping
def PocosSubintervalos(d: dict) -> str:
    return (
        f"Se necesitan al menos {d.get('minimo')} subintervalos "
        f"(recibido {d.get('n')})."
    )


@error_mapping
def SubintervalosImpares(d: dict) -> str:
    return (
        "Simpson 1/3 múltiple necesita una cantidad par de subintervalos "
        f"(recibido {d.get('n')})."
    )
