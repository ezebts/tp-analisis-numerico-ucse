from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.utils.exceptions import Error, ValidationError
from app.utils.graph import Grafico
from app.utils.interval import intervalo_valido
from app.utils.parser import parse_expression
from app.utils.templates import format_decimal, load_templates
from app.unidad4.exceptions import PocosSubintervalos, SubintervalosImpares
from app.unidad4.forms import CalcularForm, IntegracionForm
from app.unidad4.integracion.metodos import (
    NOMBRES_METODO,
    IntegracionParams,
    MetodoIntegracion,
    calcular_integral,
    requiere_n,
)
from app.unidad4.utils import DECIMALES_AREA, integral_exacta


logger = getLogger(__name__)

view = load_templates(__file__)

router = APIRouter(prefix="/unidad-4", tags=["Unidad 4"])

METODOS = list(MetodoIntegracion)
NOMBRES = {metodo.value: nombre for metodo, nombre in NOMBRES_METODO.items()}
METODOS_CON_N = [metodo.value for metodo in METODOS if requiere_n(metodo)]


def _valores_iniciales() -> dict:
    return {
        "funcion": "1/x + x",
        "metodo": MetodoIntegracion.TRAPECIOS_MULTIPLE,
        "xi": "0.5",
        "xd": "3.5",
        "xmin": "0.5",
        "xmax": "3.5",
        "n": "10",
    }


def _contexto(input: IntegracionForm) -> dict:
    return {
        "errores": [],
        "resultado": None,
        "grafico": None,
        "exacto": None,
        "funcion": input.funcion,
        "metodo": input.metodo,
        "metodos": METODOS,
        "nombres": NOMBRES,
        "metodos_con_n": METODOS_CON_N,
        "decimales": DECIMALES_AREA,
        "valores": {
            "funcion": input.funcion,
            "metodo": input.metodo,
            "xi": input.xi,
            "xd": input.xd,
            "xmin": input.xmin,
            "xmax": input.xmax,
            "n": "" if input.n is None else input.n,
        },
        "swap_form": True,
    }


@router.get("", response_class=HTMLResponse, name="unidad4")
async def index(request: Request):
    return view.TemplateResponse(
        request,
        "index.html",
        {
            "metodos": METODOS,
            "nombres": NOMBRES,
            "metodos_con_n": METODOS_CON_N,
            "decimales": DECIMALES_AREA,
            "valores": _valores_iniciales(),
        },
    )


@router.post("/calcular", response_class=HTMLResponse, name="unidad4_calcular")
async def calcular(
    request: Request,
    input: Annotated[CalcularForm, Form()],
):
    ctx = _contexto(input)
    try:
        func = parse_expression(input.funcion)
        intervalo = intervalo_valido(input.xi, input.xd, "xi")
        escala = intervalo_valido(input.xmin, input.xmax, "xmin")
        n = input.n if requiere_n(input.metodo) else None
        resultado = calcular_integral(
            IntegracionParams(
                func=func,
                metodo=input.metodo,
                interval=intervalo,
                n=n,
            )
        )
        ctx["resultado"] = resultado
        ctx["exacto"] = integral_exacta(func, intervalo)
        ctx["grafico"] = Grafico.de_funcion(
            func,
            escala,
            misma_escala=True,
            titulo_y="y",
            places=DECIMALES_AREA,
            area=resultado.paneles,
            etiqueta_area=f"A ≈ {format_decimal(resultado.area, DECIMALES_AREA)}",
        )
    except (SubintervalosImpares, PocosSubintervalos) as exc:
        ctx["errores"] = ValidationError(n=exc)
    except Error as exc:
        ctx["errores"] = exc
    except Exception as exc:
        logger.exception("Error al calcular la integral")
        ctx["errores"] = exc

    return view.TemplateResponse(request, "partials/calculo.html", ctx)


@router.post("/graficar", response_class=HTMLResponse, name="unidad4_graficar")
async def graficar(
    request: Request,
    input: Annotated[IntegracionForm, Form()],
):
    ctx = _contexto(input)
    try:
        func = parse_expression(input.funcion)
        escala = intervalo_valido(input.xmin, input.xmax, "xmin")
        ctx["grafico"] = Grafico.de_funcion(
            func,
            escala,
            misma_escala=True,
            titulo_y="y",
            places=DECIMALES_AREA,
        )
    except Error as exc:
        ctx["errores"] = exc
    except Exception as exc:
        logger.exception("Error al graficar la función")
        ctx["errores"] = exc

    return view.TemplateResponse(request, "partials/calculo.html", ctx)
