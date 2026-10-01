from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers import account_controller, audit_controller, auth_controller, dashboard_controller, user_controller
from app.services.exceptions import (
    BusinessRuleError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)

app = FastAPI(
    title="Simple Bank API",
    description="Simple banking REST API backed by MongoDB Atlas.",
    version="1.0.0",
)

# Let the React app (running on port 5173) call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(account_controller.router)
app.include_router(audit_controller.router)
app.include_router(dashboard_controller.router)


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

@app.exception_handler(UnauthorizedError)
async def handle_unauthorized(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=401, content={"detail": str(exc)},
                        headers={"WWW-Authenticate": "Bearer"})


@app.exception_handler(ForbiddenError)
async def handle_forbidden(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})
