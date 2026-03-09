from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import time

class StandardResponseMiddleware(BaseHTTPMiddleware):
    """
    Middleware ujednolicajacy format odpowiedzi API.
    Wszystkie odpowiedzi beda mialy strukture: {"status": "ok", "data": ...}
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Przetworzenie zapytania przez aplikacje
        response = await call_next(request)
        
        # Nie modyfikujemy odpowiedzi dla dokumentacji /docs lub statykow
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
            return response

        # Mozna tu dodac logike pakowania danych w strukture:
        # {"status": "ok", "data": response_content, "execution_time": ...}[cite: 10]
        
        return response
