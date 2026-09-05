from pydantic import ValidationError as PydanticValidationError
from fastapi.exceptions import RequestValidationError

from app.utils.exceptions import Error, ValidationError


def errors_from_pydantic(exc: PydanticValidationError | RequestValidationError) -> ValidationError:
    
    fields: dict[str, list[Error]] = {}
    form_errors: list[Error] = []
    
    for err in exc.errors():
        ptype = err["type"]
        ctx = dict(err.get("ctx") or {})
        field = err["loc"][-1] if err.get("loc") else None
        details = {"field": field, "value": err.get("input"), **ctx}

        if ptype in {"required", "missing"}:
            error = Error("required", field=ctx.get("field", field))
        
        elif ptype in {"decimal_parsing", "int_parsing", "float_parsing"}:
            code = "invalid_iterations" if field == "iteraciones" else "invalid_number"
            error = Error(code, **details)
        
        elif ptype == "enum" and field == "metodo":
            error = Error("invalid_method", **details)

        elif ptype == "greater_than" and field == "iteraciones":
            error = Error("invalid_iterations", **details)
        
        elif ptype in {"greater_than_equal", "less_than_equal", "greater_than", "less_than"}:
            error = Error(
                "out_of_range",
                field=field,
                value=err.get("input"),
                min=ctx.get("ge", ctx.get("gt")),
                max=ctx.get("le", ctx.get("lt")),
            )
        
        else:
            error = Error(ptype, **details)

        if field:
            fields.setdefault(field, []).append(error)
        else:
            form_errors.append(error)
    
    return ValidationError(*form_errors, **fields)
