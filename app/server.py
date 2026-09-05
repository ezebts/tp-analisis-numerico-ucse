from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.settings import STATIC_DIR
from app.utils.handlers import request_validation_handler
from app.utils.templates import load_templates
from app.unidad1.views import router as unidad1_router


app = FastAPI(title="Métodos Numéricos UCSE")

app.include_router(unidad1_router)
app.add_exception_handler(RequestValidationError, request_validation_handler)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

view = load_templates(__file__)

@app.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request):
    return view.TemplateResponse(request, "index.html")
