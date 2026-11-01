from app.utils.exceptions import Error


class PocosPuntos(Error):
    """Menos de dos puntos: no hay recta posible."""

    def __init__(self):
        super().__init__()


class EquisConstantes(Error):
    """Todos los X son iguales: la pendiente no está definida."""

    def __init__(self):
        super().__init__()


class OrdenadasConstantes(Error):
    """Todos los Y son iguales: st vale 0 y r no se puede calcular."""

    def __init__(self):
        super().__init__()


class AjustePeorQuePromedio(Error):
    """sr supera a st: la recta ajusta peor que el promedio de Y."""

    def __init__(self):
        super().__init__()


class PocosValoresX(Error):
    """No hay suficientes valores de X distintos para el grado pedido."""

    def __init__(self, grado: int):
        super().__init__(grado=grado)
