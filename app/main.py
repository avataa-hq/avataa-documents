from http.client import responses

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse, JSONResponse

import settings
from init_app import create_app
from routers import (
    document_router,
    document_specification_router,
    content_router,
)
from routers.other_routers import inventory_router, security_router
from schemas.exception import ExceptionModel
from security import security_config
from settings import PREFIX, ROOT_PREFIX, API_VERSION
from utils.exception_formatter import exception_formatter

app_version = "4.0.0"
app_title = "Documents"
description = (
    "TMF667 Document API describes the meta-data of a Document, such as the name, creationDate and "
    + "lifecycle status. The (typically binary) body of this document (such as a Word.doc, PDF, Video clip, "
    + "or Image) will be held in the associated Attachment(s) either by Ref or Value. If by value - the "
    + "binary content is held in the Attachment.content. If by reference, the Attachment.url might point to "
    + "a (file:) or remote (http:) pointer to the Document media.\n\n A Document may be associated with a "
    + "DocumentSpecification, which will detail the characteristics of that type of Document (an Image may "
    + "have a width, height and format; a Video may have a length and format).\n A Document has a "
    + "collection of RelatedParty's, for roles such as author, reviewer, publisher, and a lifecycle status "
    + "to take the document through a simple set of production stages."
)


app = create_app(
    root_path=ROOT_PREFIX,
    openapi_url=f"{ROOT_PREFIX}/openapi.json",
    docs_url=f"{ROOT_PREFIX}/docs",
)

if settings.DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app_v1 = create_app(
    root_path=f"{ROOT_PREFIX}/v{API_VERSION}",
    title=app_title,
    version=app_version,
    description=description,
)

app_v1.include_router(content_router.router)
app_v1.include_router(document_router.router)
app_v1.include_router(document_specification_router.router)
app_v1.include_router(inventory_router.router)
if security_config.SECURITY_TYPE != "DISABLE":
    app_v1.include_router(security_router.router)
# app.include_router(hub_router.router, prefix=PREFIX)
# app.include_router(listener_router.router, prefix=PREFIX)
app.mount(PREFIX, app_v1)


@app.get(PREFIX, include_in_schema=False)
async def redirect():
    response = RedirectResponse(url=f"{PREFIX}/docs")
    return response


@app.exception_handler(HTTPException)
async def catch_http_exception(request: Request, exc: HTTPException):
    exception_response = ExceptionModel(
        code=exc.status_code,
        reason=responses[exc.status_code],
        message=exc.detail,
        status=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exception_response.dict(by_alias=True, exclude_none=True),
    )


# @app.exception_handler(Exception)
# async def catch_exception(request: Request, exc: Exception):
#     message = ''
#     if exc.args:
#         message = '\n'.join(exc.args)
#     exception_response = ExceptionModel(code=500,
#                                         reason=responses[500],
#                                         message=message,
#                                         status=500)
#     return JSONResponse(status_code=500, content=exception_response.dict(by_alias=True, exclude_none=True))


@app.exception_handler(RequestValidationError)
async def catch_validation_error(request: Request, exc: RequestValidationError):
    f_exception = exception_formatter(exc)
    exception_response = ExceptionModel(
        code=422, reason=responses[422], message=f_exception, status=422
    )
    return JSONResponse(
        status_code=422,
        content=exception_response.dict(by_alias=True, exclude_none=True),
    )
