from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.controllers import account_controller, user_controller
from app.services.exceptions import BusinessRuleError, ConflictError, NotFoundError

app = FastAPI(
    title="Simple Bank API",
    description="Simple banking REST API backed by a MySQL database.",
    version="1.0.0",
)

app.include_router(user_controller.router)
app.include_router(account_controller.router)


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(BusinessRuleError)
async def handle_business_rule(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def handle_conflict(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Simple Bank API is running. Visit /docs to try it out."}