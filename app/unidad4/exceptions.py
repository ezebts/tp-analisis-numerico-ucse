from app.utils.exceptions import Error


class PocosSubintervalos(Error):
    """La cantidad de subintervalos no alcanza para el método."""

    def __init__(self, n: int, minimo: int):
        super().__init__(n=n, minimo=minimo)


class SubintervalosImpares(Error):
    """Simpson 1/3 múltiple exige una cantidad par de subintervalos."""

    def __init__(self, n: int):
        super().__init__(n=n)
