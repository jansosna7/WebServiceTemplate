import os
import importlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings

# 1. Inicjalizacja instancji FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Modular Monolith API based on Template V1.0",
    docs_url="/docs",  # OpenAPI zawsze aktywne pod /docs[cite: 6]
    version="1.0.0"
)

# ==========================================================
# 2. GLOBAL ERROR HANDLER & STANDARD RESPONSE[cite: 6, 7]
# ==========================================================
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

# ==========================================================
# 3. OPCJONALNE ENDPOINTY SYSTEMOWE[cite: 6]
# ==========================================================
if settings.ENABLE_HEALTH_CHECK:
    @app.get("/health", tags=["System"])
    async def health_check():
        return {
            "status": "ok", 
            "project": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT
        }

if settings.ENABLE_METRICS:
    @app.get("/metrics", tags=["System"])
    async def get_metrics():
        # Miejsce na integrację np. z Prometheus w przyszłości[cite: 6]
        return {"metrics": "Not implemented yet"}

# ==========================================================
# 4. CAPABILITY REGISTRY - DYNAMICZNE ŁADOWANIE MODUŁÓW[cite: 6, 7]
# ==========================================================
def load_modules():
    """
    Funkcja skanuje folder app/modules/ i ładuje moduły,
    które są włączone w config.py (settings.ENABLE_...).
    Wymaga, aby w folderze modułu istniał plik routes.py z obiektem `router`.[cite: 6, 7]
    """
    modules_path = os.path.join(os.path.dirname(__file__), "modules")
    
    # Jeśli folder modules nie istnieje, pomiń
    if not os.path.exists(modules_path):
        return

    # Iteracja po wszystkich podfolderach w app/modules/[cite: 7]
    for module_name in os.listdir(modules_path):
        module_dir = os.path.join(modules_path, module_name)
        
        # Interesują nas tylko foldery, które nie są plikami ukrytymi (jak np. __pycache__)
        if os.path.isdir(module_dir) and not module_name.startswith("__"):
            
            # Mapowanie nazwy folderu na nazwę flagi w ustawieniach (np. "wallet" -> "ENABLE_WALLET")[cite: 7]
            setting_flag = f"ENABLE_{module_name.upper()}"
            
            # Sprawdzanie czy flaga istnieje w settings i czy jest ustawiona na True[cite: 6, 7]
            is_enabled = getattr(settings, setting_flag, False)
            
            if is_enabled:
                try:
                    # Dynamiczny import pliku routes.py z danego modułu[cite: 7]
                    # Przykład: import app.modules.wallet.routes
                    module = importlib.import_module(f"app.modules.{module_name}.routes")
                    
                    # Pobranie obiektu router (APIRouter) z pliku routes.py[cite: 7]
                    if hasattr(module, "router"):
                        prefix = f"{settings.API_V1_STR}/{module_name}"
                        app.include_router(
                            module.router, 
                            prefix=prefix, 
                            tags=[module_name.capitalize()]
                        )
                        print(f"[Capability Registry] Moduł załadowany: {module_name} ({prefix})")[cite: 6]
                except Exception as e:
                    print(f"[Capability Registry] Błąd ładowania modułu {module_name}: {e}")

# Odpalenie loadera podczas startu aplikacji
load_modules()

# ==========================================================
# 5. ŁADOWANIE WEB UI (Opcjonalnie)[cite: 6]
# ==========================================================
if settings.ENABLE_ADMIN_PANEL:
    # Zakładając, że plik web/routes.py ma obiekt admin_router[cite: 6]
    try:
        from app.web.routes import admin_router
        app.include_router(admin_router, prefix="/admin", tags=["Web UI"])
        print("[Capability Registry] Web Admin Panel załadowany.")
    except ImportError:
        pass # Plik app/web/routes.py może jeszcze nie istnieć na tym etapie
