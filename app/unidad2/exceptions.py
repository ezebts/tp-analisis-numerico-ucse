from app.utils.exceptions import Error


class PivoteNulo(Error):
    """
    Excepción lanzada cuando el pivote de la diagonal es 0.
    """

    def __init__(self, fila: int):
        super().__init__(fila=fila)
