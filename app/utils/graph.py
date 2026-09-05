from dataclasses import dataclass, field
from typing import Optional, Protocol

from sympy import Expr, lambdify, symbols


class GraphInterval(Protocol):
    xi: float
    xd: float


@dataclass
class Graph:
    func: Expr
    interval: GraphInterval
    raiz: Optional[float] = None
    n: int = 240
    xs: list[float] = field(init=False)
    ys: list[Optional[float]] = field(init=False)

    def __post_init__(self) -> None:
        f = lambdify(symbols("x"), self.func, modules="math")
        x_min = self.interval.xi
        x_max = self.interval.xd
        paso = (x_max - x_min) / (self.n - 1) if self.n > 1 else 0
        xs: list[float] = []
        ys: list[Optional[float]] = []
        for i in range(self.n):
            x = x_min + paso * i
            xs.append(x)
            try:
                y = float(f(x))
                if y != y or abs(y) > 1e6:
                    ys.append(None)
                else:
                    ys.append(y)
            except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                ys.append(None)
        self.xs = xs
        self.ys = ys
