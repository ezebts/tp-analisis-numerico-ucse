from logging import getLogger
from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.utils.exceptions import Error, GradoExcedido, NoEsPolinomio, ValidationError
from app.utils.graph import Grafico
from app.utils.interval import intervalo_valido
from app.utils.templates import format_decimal, load_templates
from app.unidad3.ajuste_de_curvas.regresion_lineal import (
    RegresionLinealParams,
    calcular_regresion_lineal,
)
from app.unidad3.ajuste_de_curvas.regresion_polinomica import (
    RegresionPolinomialParams,
    calcular_regresion_polinomica,
)
from app.unidad3.exceptions import (
    AjustePeorQuePromedio,
    EquisConstantes,
    OrdenadasConstantes,
    PocosPuntos,
    PocosValoresX,
)
from app.unidad3.forms import PuntosForm, QuitarPuntoForm, RectaModificadaForm
from app.unidad3.utils import (
    GRADO_INICIAL,
    MetodoLineal,
    MetodoPolinomial,
    PUNTOS_INICIALES,
    PUNTOS_MAX,
    PUNTOS_MIN,
    agregar_punto,
    quitar_punto,
    r_funcion_modificada,
)


logger = getLogger(__name__)

view = load_templates(__file__)

router = APIRouter(prefix="/unidad-3", tags=["Unidad 3"])

DEFAULT_TOLERANCIA = 80.0
ERRORES_PUNTOS = (PocosPuntos, EquisConstantes, OrdenadasConstantes, PocosValoresX)


def _grafico_desde_resultado(resultado, escala):
    if hasattr(resultado, "coeficientes"):
        coeficientes = resultado.coeficientes
    else:
        coeficientes = (resultado.a0, resultado.a1)
    return Grafico.de_ajuste(resultado.puntos, escala, coeficientes)


def _contexto_vista(
    *,
    metodo: MetodoLineal | MetodoPolinomial,
    xs: list[float],
    ys: list[float],
    tolerancia: float,
    xmin: float,
    xmax: float,
    grado: int = GRADO_INICIAL,
    errores=None,
    resultado=None,
    modificada=None,
    grafico=None,
    funcion_modificada: str = "",
    swap_form: bool = False,
    swap_puntos: bool = False,
    swap_modificada: bool = False,
) -> dict:
    return {
        "errores": errores or [],
        "resultado": resultado,
        "modificada": modificada,
        "grafico": grafico,
        "metodos": [*MetodoLineal, *MetodoPolinomial],
        "xs": xs,
        "ys": ys,
        "puntos_min": PUNTOS_MIN,
        "puntos_max": PUNTOS_MAX,
        "valores": {
            "metodo": metodo,
            "tolerancia": format_decimal(tolerancia),
            "grado": grado,
            "xmin": xmin,
            "xmax": xmax,
        },
        "funcion_modificada": funcion_modificada,
        "swap_form": swap_form,
        "swap_puntos": swap_puntos,
        "swap_modificada": swap_modificada,
    }


def _contexto_inicial(**extra) -> dict:
    return _contexto_vista(
        metodo=MetodoLineal.REGRESION_LINEAL,
        xs=[0.0] * PUNTOS_INICIALES,
        ys=[0.0] * PUNTOS_INICIALES,
        tolerancia=DEFAULT_TOLERANCIA,
        xmin=-10.0,
        xmax=10.0,
        grado=GRADO_INICIAL,
        **extra,
    )


@router.get("", response_class=HTMLResponse, name="unidad3")
async def index(request: Request):
    return view.TemplateResponse(request, "index.html", _contexto_inicial())


@router.post("/agregar-punto", response_class=HTMLResponse, name="unidad3_agregar_punto")
async def agregar(
    request: Request,
    input: Annotated[PuntosForm, Form()],
):
    errores = None
    if len(input.xs) >= PUNTOS_MAX:
        errores = ValidationError(
            puntos=Error(
                "cantidad_puntos",
                min=PUNTOS_MIN,
                max=PUNTOS_MAX,
                value=len(input.xs),
            )
        )
    xs, ys = agregar_punto(input.xs, input.ys)
    return view.TemplateResponse(
        request,
        "partials/puntos_respuesta.html",
        _contexto_vista(
            metodo=input.metodo,
            xs=xs,
            ys=ys,
            tolerancia=input.tolerancia,
            xmin=input.xmin,
            xmax=input.xmax,
            grado=input.grado,
            errores=errores,
            swap_puntos=True,
        ),
    )


@router.post("/quitar-punto", response_class=HTMLResponse, name="unidad3_quitar_punto")
async def quitar(
    request: Request,
    input: Annotated[QuitarPuntoForm, Form()],
):
    xs, ys = quitar_punto(input.xs, input.ys, input.indice)
    return view.TemplateResponse(
        request,
        "partials/puntos_respuesta.html",
        _contexto_vista(
            metodo=input.metodo,
            xs=xs,
            ys=ys,
            tolerancia=input.tolerancia,
            xmin=input.xmin,
            xmax=input.xmax,
            grado=input.grado,
            swap_puntos=True,
        ),
    )


@router.get("/limpiar", response_class=HTMLResponse, name="unidad3_limpiar")
async def limpiar(request: Request):
    return view.TemplateResponse(
        request,
        "partials/calculo.html",
        _contexto_inicial(swap_form=True),
    )


@router.post("/graficar", response_class=HTMLResponse, name="unidad3_graficar")
async def graficar(
    request: Request,
    input: Annotated[PuntosForm, Form()],
):
    ctx = _contexto_vista(
        metodo=input.metodo,
        xs=input.xs,
        ys=input.ys,
        tolerancia=input.tolerancia,
        xmin=input.xmin,
        xmax=input.xmax,
        grado=input.grado,
        swap_form=True,
    )
    try:
        escala = intervalo_valido(input.xmin, input.xmax, "xmin")
    except Error as exc:
        ctx["errores"] = exc
    else:
        ctx["grafico"] = Grafico.de_ajuste(input.puntos(), escala)
    return view.TemplateResponse(request, "partials/calculo.html", ctx)


@router.post("/calcular", response_class=HTMLResponse, name="unidad3_calcular")
async def calcular(
    request: Request,
    input: Annotated[PuntosForm, Form()],
):
    ctx = _contexto_vista(
        metodo=input.metodo,
        xs=input.xs,
        ys=input.ys,
        tolerancia=input.tolerancia,
        xmin=input.xmin,
        xmax=input.xmax,
        grado=input.grado,
        swap_form=True,
    )

    try:
        escala = intervalo_valido(input.xmin, input.xmax, "xmin")
        if input.metodo == MetodoPolinomial.REGRESION_POLINOMIAL:
            resultado = calcular_regresion_polinomica(
                RegresionPolinomialParams(
                    puntos=input.puntos(),
                    tolerancia=input.tolerancia,
                    grado=input.grado,
                )
            )
        else:
            resultado = calcular_regresion_lineal(
                RegresionLinealParams(
                    puntos=input.puntos(),
                    tolerancia=input.tolerancia,
                )
            )
    except ERRORES_PUNTOS as exc:
        ctx["errores"] = ValidationError(puntos=exc)
    except Error as exc:
        ctx["errores"] = exc
    except Exception as exc:
        logger.exception("Error al calcular")
        ctx["errores"] = exc
    else:
        ctx["resultado"] = resultado
        ctx["funcion_modificada"] = resultado.funcion
        ctx["grafico"] = _grafico_desde_resultado(resultado, escala)
        grado = input.grado if input.metodo == MetodoPolinomial.REGRESION_POLINOMIAL else 1
        
        try:
            ctx["modificada"] = r_funcion_modificada(
                resultado.puntos,
                resultado.funcion,
                input.tolerancia,
                grado,
            )
        except Error:
            logger.exception("No se pudo evaluar la función obtenida como modificación")

    return view.TemplateResponse(request, "partials/calculo.html", ctx)


@router.post("/recalcular-r", response_class=HTMLResponse, name="unidad3_recalcular")
async def recalcular(
    request: Request,
    input: Annotated[RectaModificadaForm, Form()],
):
    ctx = _contexto_vista(
        metodo=input.metodo,
        xs=input.xs,
        ys=input.ys,
        tolerancia=input.tolerancia,
        xmin=input.xmin,
        xmax=input.xmax,
        grado=input.grado,
        funcion_modificada=input.funcion_modificada,
        swap_modificada=True,
    )

    try:
        grado = (
            input.grado
            if input.metodo == MetodoPolinomial.REGRESION_POLINOMIAL
            else 1
        )
        ctx["modificada"] = r_funcion_modificada(
            input.puntos(),
            input.funcion_modificada,
            input.tolerancia,
            grado,
        )
    except ValidationError as exc:
        errores = [error for items in exc.details.values() for error in items]
        for error in errores:
            error.details["field"] = "funcion_modificada"
        ctx["errores"] = ValidationError(funcion_modificada=errores)
    except (NoEsPolinomio, GradoExcedido, AjustePeorQuePromedio) as exc:
        ctx["errores"] = ValidationError(funcion_modificada=exc)
    except ERRORES_PUNTOS as exc:
        ctx["errores"] = ValidationError(puntos=exc)
    except Error as exc:
        ctx["errores"] = exc
    except Exception as exc:
        logger.exception("Error al recalcular r")
        ctx["errores"] = exc

    return view.TemplateResponse(request, "partials/recalcular.html", ctx)
