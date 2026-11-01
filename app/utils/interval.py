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


def intervalo_valido(xi: float, xd: float, campo: str) -> Interval:
    """Intervalo con xi < xd. El error queda asociado al campo de la UI."""
    try:
        return Interval(xi, xd)
    except ValidationError as exc:
        raise ValidationError(**{campo: list(exc)}) from exc
