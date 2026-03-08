import os
import importlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Modular Monolith API based on Template V1.0",
    docs_url="/docs",
    version="1.0.0"
)

if settings.ENABLE_GLOBAL_ERROR_HANDLER:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal Server Error",
                "details": str(exc) if settings.ENVIRONMENT == "dev" else None
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "message": "Validation Error",
                "details": exc.errors() if settings.ENABLE_STANDARD_RESPONSE else None
            }
        )

if settings.ENABLE_HEALTH_CHECK:
    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "ok", "project": settings.PROJECT_NAME}

def load_modules():
    modules_path = os.path.join(os.path.dirname(__file__), "modules")
    if not os.path.exists(modules_path):
        return

    for module_name in os.listdir(modules_path):
        module_dir = os.path.join(modules_path, module_name)
        if os.path.isdir(module_dir) and not module_name.startswith("__"):
            setting_flag = f"ENABLE_{module_name.upper()}"
            is_enabled = getattr(settings, setting_flag, False)
            
            if is_enabled:
                try:
                    module = importlib.import_module(f"app.modules.{module_name}.routes")
                    if hasattr(module, "router"):
                        prefix = f"{settings.API_V1_STR}/{module_name}"
                        app.include_router(module.router, prefix=prefix, tags=[module_name.capitalize()])
                        print(f"[Capability Registry] Moduł załadowany: {module_name} ({prefix})")
                except Exception as e:
                    print(f"[Capability Registry] Błąd ładowania modułu {module_name}: {e}")

load_modules()
