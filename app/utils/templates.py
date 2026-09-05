from pathlib import Path
from typing import Callable, Optional

from fastapi.templating import Jinja2Templates

from app.settings import TEMPLATES_DIR
from app.utils.exceptions import Error, ValidationError


ERROR_MAPPINGS: dict[str, Callable] = {}
TEMPLATE_FILTERS: dict[str, Callable] = {}


def template_filter(fn: Callable) -> Callable:
    TEMPLATE_FILTERS[fn.__name__] = fn
    return fn


def error_mapping(fn: Callable) -> Callable:
    ERROR_MAPPINGS[fn.__name__] = fn
    return fn


@template_filter
def format_decimal(value: Optional[float], places: int = 6) -> str:
    if value is None:
        return "—"
    texto = f"{float(value):.{places}f}"
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto


@template_filter
def all_errors(value: object) -> list:
    if isinstance(value, ValidationError):
        return list(value.details.get("__all__") or [])
    if isinstance(value, Error):
        return [value]
    if value:
        return [Error("unexpected")]
    return []


@template_filter
def field_errors(value: object, field: str = "") -> list:
    if not isinstance(value, ValidationError) or not field:
        return []
    return list(value.details.get(field) or [])


@template_filter
def error_message(error: Error) -> str:
    mapper = ERROR_MAPPINGS.get(error.type) or ERROR_MAPPINGS.get("unexpected")
    if mapper is None:
        return "Ocurrió un error inesperado."
    return mapper(error.details or {})


def load_templates(module_file: str | None = None) -> Jinja2Templates:
    directories = [TEMPLATES_DIR]
    if module_file:
        directories.insert(0, Path(module_file).resolve().parent / "templates")
    templates = Jinja2Templates(directory=directories)
    templates.env.filters.update(TEMPLATE_FILTERS)
    return templates
