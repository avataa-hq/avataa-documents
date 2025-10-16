from fastapi.exceptions import RequestValidationError


def exception_formatter(exc: RequestValidationError):
    result = []
    minimal_len = min([len(err["loc"]) for err in exc.errors()])
    for err in exc.errors():
        if len(err["loc"]) != minimal_len:
            continue
        formatted = f"""[{" -> ".join([str(e) for e in err["loc"][1:]])}] {err["msg"]} ({err["type"]})"""
        result.append(formatted)
    return "\n".join(result)
