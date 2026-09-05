from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app.utils.graph import Graph
from app.utils.parser import parse_expression
from app.utils.templates import load_templates

from app.unidad1.forms import CalcularForm, MetodoAbierto, MetodoCerrado
from app.unidad1.utils import Interval, Tolerance

from app.unidad1.raices_de_funciones.metodos_abiertos import (
    MetodoAbiertoParams,
    calcular_metodo_abierto,
)
from app.unidad1.raices_de_funciones.metodos_cerrados import (
    MetodoCerradoParams,
    calcular_metodo_cerrado,
)


view = load_templates(__file__)

router = APIRouter(prefix="/unidad-1", tags=["Unidad 1"])


@router.get("", response_class=HTMLResponse, name="unidad1")
async def index(request: Request):
    return view.TemplateResponse(
        request,
        "index.html",
        {
            "metodos": [*MetodoCerrado, *MetodoAbierto],
            "valores": {
                "funcion": "x^2 - 2",
                "metodo": MetodoCerrado.BISECCION,
                "iteraciones": "100",
                "tolerancia": "0.0001",
                "xi": "1.0",
                "xd": "2.0",
                "xmin": "-2.0",
                "xmax": "4.0",
            },
        },
    )


@router.post("/calcular", response_class=HTMLResponse, name="unidad1_calcular")
async def calcular(
    request: Request,
    input: Annotated[CalcularForm, Form()],
):
    ctx = {
        "errores": [],
        "resultado": None,
        "grafico": None,
        "funcion": input.funcion,
        "metodo": input.metodo,
        "metodos": [*MetodoCerrado, *MetodoAbierto],
        "valores": {
            "funcion": input.funcion,
            "metodo": input.metodo,
            "iteraciones": input.iteraciones,
            "tolerancia": input.tolerancia,
            "xi": input.xi,
            "xd": input.xd if input.xd is not None else "",
            "xmin": input.xmin,
            "xmax": input.xmax,
        },
        "swap_form": True,
    }
    
    try:
    
        func = parse_expression(input.funcion)
        
        if isinstance(input.metodo, MetodoAbierto):
            resultado = calcular_metodo_abierto(
                MetodoAbiertoParams(
                    func=func,
                    metodo=input.metodo,
                    max_iteraciones=input.iteraciones,
                    tolerancia=Tolerance(input.tolerancia),
                    xi=input.xi,
                    xd=input.xd,
                )
            )
        else:
            resultado = calcular_metodo_cerrado(
                MetodoCerradoParams(
                    func=func,
                    metodo=input.metodo,
                    max_iteraciones=input.iteraciones,
                    tolerancia=Tolerance(input.tolerancia),
                    interval=Interval(input.xi, input.xd),
                )
            )
        
        ctx["grafico"] = Graph(
            func,
            Interval(input.xmin, input.xmax),
            resultado.raiz,
        )
        
        ctx["resultado"] = resultado
    
    except Exception as exc:
        ctx["errores"] = exc
    
    return view.TemplateResponse(request, "partials/calculo.html", ctx)
