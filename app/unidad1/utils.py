from math import floor, log10
from dataclasses import dataclass

from app.utils.exceptions import Error, ValidationError


@dataclass(frozen=True)
class Interval:
    """
    Rpresenta un intervalo [xi, xd]
    """
    xi: float
    xd: float

    def __post_init__(self):
        if self.xi >= self.xd:
            raise ValidationError(Error("invalid_interval", interval=self))

    def __str__(self):
        return f"[{self.xi}, {self.xd}]"


@dataclass(frozen=True)
class Tolerance:
    """
    Representa una tolerancia o precisión.
    """
    value: float

    def __post_init__(self):
        if self.value < 0 or self.value > 1:
            raise ValidationError(
                Error("out_of_range", min=0, max=1, value=self.value)
            )

    def __str__(self):
        return f"{self.value:.{self.places}f}".rstrip("0").rstrip(".") or "0"

    @property
    def places(self) -> int:
        if self.value <= 0:
            return 0
        return max(0, -floor(log10(self.value)))

    def acepts(self, value: float) -> bool:
        return abs(self.value - value) <= self.value
