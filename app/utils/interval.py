from dataclasses import dataclass

from app.utils.exceptions import Error, ValidationError


@dataclass(frozen=True)
class Interval:
    """Representa un intervalo [xi, xd]."""

    xi: float
    xd: float

    def __post_init__(self):
        if self.xi >= self.xd:
            raise ValidationError(Error("invalid_interval", interval=self))

    def __str__(self):
        return f"[{self.xi}, {self.xd}]"
