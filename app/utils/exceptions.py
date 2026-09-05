from typing import Any, Iterator
from dataclasses import dataclass, field


@dataclass
class Error(Exception):
    """
    Clase base para todas las excepciones
    """

    type: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __init__(self, type: str | None = None, **details: Any):
        self.type = type or self.__class__.__name__
        self.details = details
        super().__init__(self.type, self.details)

    @staticmethod
    def create(value: "Error | str") -> "Error":
        return value if isinstance(value, Error) else Error(str(value))

    def __iter__(self) -> Iterator["Error"]:
        yield self


class ValidationError(Error, ValueError):
    """
    Excepción lanzada cuando los datos de entrada no son válidos.
    """

    details: dict[str, list[Error]]

    def __init__(self, *errors: Error | str, **fields: list[Error] | Error | str):
        
        grouped: dict[str, list[Error]] = {}
        form_errors = [Error.create(error) for error in errors]
        
        if form_errors:
            grouped["__all__"] = form_errors
        
        for name, value in fields.items():
            items = value if isinstance(value, list) else [value]
            grouped[name] = [Error.create(item) for item in items]
            
            if name != "__all__":
                for error in grouped[name]:
                    error.details.setdefault("field", name)
        
        Error.__init__(self, self.__class__.__name__)
        self.details = grouped

    def __iter__(self) -> Iterator[Error]:
        
        details = self.details or {}
        
        for error in details.get("__all__", []):
            yield from error
        
        for name, items in details.items():
            
            if name == "__all__":
                continue
            
            for error in items:
                yield from error
