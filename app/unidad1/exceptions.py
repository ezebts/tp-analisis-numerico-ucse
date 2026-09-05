from app.utils.exceptions import Error
from app.unidad1.utils import Interval


class IntervalDoesntCrossZero(Error):
    """
    Excepción lanzada cuando el intervalo no cruza el eje x
    """

    def __init__(self, interval: Interval):
        super().__init__(interval=interval)
