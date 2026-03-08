import os
import typer

app = typer.Typer(help="Monolith V1.0 - Narzedzie deweloperskie do generowania kodu.")

def create_file_from_template(filepath: str, content: str):
    """Pomocnicza funkcja do zapisywania plikow."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  Utworzono: {filepath}")

@app.command()
def create_module(name: str):
    """
    Generuje kompletny modul w app/modules/{name} zawierajacy:
    routes.py, services.py, schemas.py oraz repository.py.
    """
    name_lower = name.lower()
    name_cap = name.capitalize()
    
    module_path = os.path.join("app", "modules", name_lower)
    
    if os.path.exists(module_path):
        typer.echo(f"Blad: Modul '{name_lower}' juz istnieje w {module_path}")
        raise typer.Exit(code=1)
        
    os.makedirs(module_path)
    typer.echo(f"Tworzenie modulu: {name_cap}...")

    # 1. SCHEMAS
    schemas_content = f"""
from pydantic import BaseModel
from typing import Optional

class {name_cap}Base(BaseModel):
    name: str
    description: Optional[str] = None

class {name_cap}Create({name_cap}Base):
    pass

class {name_cap}Response({name_cap}Base):
    id: int

    class Config:
        from_attributes = True
"""
    create_file_from_template(os.path.join(module_path, "schemas.py"), schemas_content)

    # 2. REPOSITORY
    repo_content = f"""
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class {name_cap}Model(Base):
    __tablename__ = "{name_lower}s"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
"""
    create_file_from_template(os.path.join(module_path, "repository.py"), repo_content)

    # 3. SERVICES
    services_content = f"""
from app.core.database import BaseRepository
from app.modules.{name_lower}.schemas import {name_cap}Create

class {name_cap}Service:
    def __init__(self, repo: BaseRepository):
        self.repo = repo
        
    async def get_all_{name_lower}s(self):
        return await self.repo.get_all()
        
    async def create_{name_lower}(self, data: {name_cap}Create):
        payload = data.model_dump()
        return await self.repo.create(payload)
"""
    create_file_from_template(os.path.join(module_path, "services.py"), services_content)

    # 4. ROUTES
    routes_content = f"""
from fastapi import APIRouter, Depends
from app.core.database import BaseRepository, get_repository
from app.modules.{name_lower}.schemas import {name_cap}Create, {name_cap}Response
from app.modules.{name_lower}.services import {name_cap}Service
from app.modules.{name_lower}.repository import {name_cap}Model

router = APIRouter()

def get_service(repo: BaseRepository = Depends(get_repository("{name_lower}s", {name_cap}Model))):
    return {name_cap}Service(repo)

@router.get("/", response_model=list[{name_cap}Response])
async def read_{name_lower}s(service: {name_cap}Service = Depends(get_service)):
    return await service.get_all_{name_lower}s()

@router.post("/", response_model={name_cap}Response)
async def create_{name_lower}(item: {name_cap}Create, service: {name_cap}Service = Depends(get_service)):
    return await service.create_{name_lower}(item)
"""
    create_file_from_template(os.path.join(module_path, "routes.py"), routes_content)

    # 5. INIT
    create_file_from_template(os.path.join(module_path, "__init__.py"), "")

    typer.echo(f"Modul '{name_cap}' wygenerowany pomyslnie.")
    typer.echo(f"Dodaj ENABLE_{name_cap.upper()}=True w pliku .env i zarejestruj w config.py.")

@app.command()
def create_plugin(name: str):
    """Generuje szkielet pluginu."""
    typer.echo(f"Tworzenie pluginu '{name}' - funkcja w przygotowaniu.")

if __name__ == "__main__":
    app()
