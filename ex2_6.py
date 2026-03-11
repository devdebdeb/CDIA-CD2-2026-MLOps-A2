from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            'erro': 'Dados Inválidos'
            ,'detalhes': exc.errors
            ,'path': str(request.url)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code
        ,content={
            'erro': exc.detail
            ,'status': exc.status_code
            ,'path': str(request.url)
        }
    )