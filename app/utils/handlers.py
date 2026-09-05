from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler

import app.utils.messages
from app.utils.forms import errors_from_pydantic
from app.utils.templates import load_templates


view = load_templates()


async def request_validation_handler(request: Request, exc: RequestValidationError):
    
    if request.headers.get("hx-request") != "true":
        return await request_validation_exception_handler(request, exc)
    
    return view.TemplateResponse(
        request,
        "partials/errores.html",
        {"errores": errors_from_pydantic(exc)},
    )
