from math import isqrt


def inferir_dimension(cantidad: int) -> int | None:
    """ n tal que n * (n + 1) == cantidad (matriz aumentada). """
    if cantidad <= 0:
        return None

    disc = 1 + 4 * cantidad
    raiz = isqrt(disc)
    if raiz * raiz != disc:
        return None

    n = (-1 + raiz) // 2
    if n > 0 and n * (n + 1) == cantidad:
        return n
    return None


def redimensionar_aumentada(valores: list[float], dimension: int) -> list[list[float]]:
    """ Reescribe la aumentada a n x (n+1) conservando coeficientes y TI. """
    n_old = inferir_dimension(len(valores))
    if n_old is None:
        return [[0.0] * (dimension + 1) for _ in range(dimension)]

    filas = [
        list(valores[i * (n_old + 1):(i + 1) * (n_old + 1)])
        for i in range(n_old)
    ]

    resultado: list[list[float]] = []
    for i in range(dimension):
        if i >= n_old:
            resultado.append([0.0] * (dimension + 1))
            continue

        coeficientes = (filas[i][:n_old] + [0.0] * dimension)[:dimension]
        resultado.append(coeficientes + [filas[i][n_old]])

    return resultado


def plano_a_aumentada(valores: list[float], dimension: int) -> list[list[float]]:
    ancho = dimension + 1
    return [
        list(valores[i * ancho:(i + 1) * ancho])
        for i in range(dimension)
    ]
