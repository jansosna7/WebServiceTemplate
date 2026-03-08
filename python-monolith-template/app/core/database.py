import os
import pandas as pd
from typing import Any, List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from fastapi import Depends

from app.config import settings

# =================================================================
# 1. BAZA DANYCH SQLALCHEMY (PostgreSQL / Inne wspierane async)
# =================================================================
Base = declarative_base()

# Tworzymy silnik i sesję tylko jeśli flaga USE_DB jest True i podano URL[cite: 9]
engine = None
AsyncSessionLocal = None

if settings.USE_DB and settings.DATABASE_URL:
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

async def get_db_session() -> AsyncSession:
    """Dependency do wstrzykiwania sesji SQLAlchemy."""
    if not AsyncSessionLocal:
        raise Exception("Database is not configured. Check USE_DB and DATABASE_URL in .env")
    async with AsyncSessionLocal() as session:
        yield session

# =================================================================
# 2. INTERFEJS REPOZYTORIUM (Abstract Base Class)[cite: 9]
# =================================================================
class BaseRepository(ABC):
    """
    Abstrakcyjna klasa wymuszająca implementację metod CRUD.
    Dzięki niej Service Layer nie musi wiedzieć, z jakim silnikiem gada.
    """
    @abstractmethod
    async def get_all(self) -> List[dict]:
        pass

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[dict]:
        pass

    @abstractmethod
    async def create(self, data: dict) -> dict:
        pass


# =================================================================
# 3. IMPLEMENTACJA FALLBACK: PANDAS (CSV Storage)[cite: 8, 9]
# =================================================================
class CSVRepository(BaseRepository):
    """
    Implementacja zapisu danych do plików CSV. Brak relacji. Idealne do prototypu.[cite: 8, 9]
    """
    def __init__(self, table_name: str):
        self.table_name = table_name
        # Dane lądują w storage/permanent/[cite: 8, 9]
        self.file_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "storage", "permanent", f"{table_name}.csv"
        )
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            # Tworzy pusty DataFrame jeśli plik nie istnieje
            df = pd.DataFrame(columns=["id"]) 
            df.to_csv(self.file_path, index=False)

    async def get_all(self) -> List[dict]:
        df = pd.read_csv(self.file_path)
        return df.to_dict(orient="records")

    async def get_by_id(self, id: Any) -> Optional[dict]:
        df = pd.read_csv(self.file_path)
        # Zakładamy, że kolumna 'id' istnieje
        if "id" not in df.columns:
            return None
        
        # Filtrujemy by znaleźć wiersz
        record = df[df["id"] == id]
        if record.empty:
            return None
        return record.iloc[0].to_dict()

    async def create(self, data: dict) -> dict:
        df = pd.read_csv(self.file_path)
        
        # Generowanie prostego ID jeśli nie podano
        if "id" not in data:
            data["id"] = int(df["id"].max()) + 1 if not df.empty and "id" in df.columns else 1
            
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        return data


# =================================================================
# 4. IMPLEMENTACJA BAZY DANYCH: SQLALCHEMY[cite: 9]
# =================================================================
class SQLRepository(BaseRepository):
    """
    Implementacja komunikacji z prawdziwą bazą relacyjną.[cite: 8, 9]
    """
    def __init__(self, session: AsyncSession, model: Base):
        self.session = session
        self.model = model

    async def get_all(self) -> List[dict]:
        # Tu w docelowym serwisie znajdzie się zapytanie np. select(self.model)
        # Przykład tymczasowy, dopóki deweloper nie zdefiniuje schematu[cite: 8]
        return [{"info": "SQLRepository get_all called"}]

    async def get_by_id(self, id: Any) -> Optional[dict]:
        # Oczekuje implementacji np. await self.session.get(self.model, id)
        pass

    async def create(self, data: dict) -> dict:
        # Oczekuje implementacji obj = self.model(**data); session.add(obj); itp.
        pass


# =================================================================
# 5. DEPENDENCY INJECTION DO WSTRZYKIWANIA W ROUTERACH FastAPI
# =================================================================
async def get_optional_db_session():
    """Bezpieczne dependency, które zarządza cyklem życia sesji."""
    if settings.USE_DB and AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        yield None

def get_repository(table_name: str, model: Any = None):
    """
    Zwraca odpowiednią klasę repozytorium na podstawie config.USE_DB.
    """
    async def _get_repo(session = Depends(get_optional_db_session)):
        if settings.USE_DB:
            if not session:
                raise Exception("Baza włączona (USE_DB=True), ale brak połączenia.")
            return SQLRepository(session, model)
        else:
            return CSVRepository(table_name)
            
    return _get_repo
