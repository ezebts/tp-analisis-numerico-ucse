from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.utils.templates import load_templates
from app.utils.exceptions import Error

from app.unidad1.utils import Tolerance
from app.unidad2.forms import CalcularForm, GenerarForm, MetodoSistema
from app.unidad2.utils import redimensionar_aumentada
from app.unidad2.sistemas_de_ecuaciones.metodos_directos import (
    MetodoDirecto,
    MetodoDirectoParams,
    calcular_metodo_directo,
)
from app.unidad2.sistemas_de_ecuaciones.metodos_iterativos import (
    MetodoIterativo,
    MetodoIterativoParams,
    calcular_metodo_iterativo,
)


logger = getLogger(__name__)

view = load_templates(__file__)

router = APIRouter(prefix="/unidad-2", tags=["Unidad 2"])

DEFAULT_ITERACIONES = 100
DEFAULT_TOLERANCIA = 0.0001
DEFAULT_MATRIZ = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]


def _contexto_vista(
    *,
    dimension: int,
    metodo: MetodoSistema,
    matriz: list[list[float]],
    errores=None,
    resultado=None,
    iteraciones: int = DEFAULT_ITERACIONES,
    tolerancia: float = DEFAULT_TOLERANCIA,
    swap_form: bool = False,
    swap_matriz: bool = False,
) -> dict:
    return {
        "errores": errores or [],
        "resultado": resultado,
        "metodo": metodo,
        "metodos": [*MetodoDirecto, *MetodoIterativo],
        "dimension": dimension,
        "matriz": matriz,
        "valores": {
            "dimension": str(dimension),
            "metodo": metodo,
            "iteraciones": str(iteraciones),
            "tolerancia": str(tolerancia),
        },
        "swap_form": swap_form,
        "swap_matriz": swap_matriz,
    }


def _contexto_inicial(**extra) -> dict:
    return _contexto_vista(
        dimension=len(DEFAULT_MATRIZ),
        metodo=MetodoDirecto.GAUSS_JORDAN,
        matriz=[fila[:] for fila in DEFAULT_MATRIZ],
        **extra,
    )


@router.get("", response_class=HTMLResponse, name="unidad2")
async def index(request: Request):
    return view.TemplateResponse(request, "index.html", _contexto_inicial())


@router.post("/generar", response_class=HTMLResponse, name="unidad2_generar")
async def generar(
    request: Request,
    input: Annotated[GenerarForm, Form()],
):
    return view.TemplateResponse(
        request,
        "partials/generar.html",
        _contexto_vista(
            dimension=input.dimension,
            metodo=input.metodo,
            matriz=redimensionar_aumentada(input.matriz, input.dimension),
            swap_matriz=True,
        ),
    )


@router.get("/limpiar", response_class=HTMLResponse, name="unidad2_limpiar")
async def limpiar(request: Request):
    return view.TemplateResponse(
        request,
        "partials/calculo.html",
        _contexto_inicial(swap_form=True),
    )


@router.post("/calcular", response_class=HTMLResponse, name="unidad2_calcular")
async def calcular(
    request: Request,
    input: Annotated[CalcularForm, Form()],
):
    matriz = redimensionar_aumentada(input.matriz, input.dimension)
    iteraciones = input.iteraciones if input.iteraciones is not None else DEFAULT_ITERACIONES
    tolerancia = input.tolerancia if input.tolerancia is not None else DEFAULT_TOLERANCIA
    ctx = _contexto_vista(
        dimension=input.dimension,
        metodo=input.metodo,
        matriz=matriz,
        iteraciones=iteraciones,
        tolerancia=tolerancia,
        swap_form=True,
    )

    try:
        if isinstance(input.metodo, MetodoIterativo):
            ctx["resultado"] = calcular_metodo_iterativo(
                MetodoIterativoParams(
                    metodo=input.metodo,
                    matriz=matriz,
                    max_iteraciones=iteraciones,
                    tolerancia=Tolerance(tolerancia),
                )
            )
        else:
            ctx["resultado"] = calcular_metodo_directo(
                MetodoDirectoParams(
                    metodo=input.metodo,
                    matriz=matriz,
                )
            )
    except Error as exc:
        ctx["errores"] = exc
    except Exception as exc:
        logger.exception("Error al calcular")
        ctx["errores"] = exc

    return view.TemplateResponse(request, "partials/calculo.html", ctx)
