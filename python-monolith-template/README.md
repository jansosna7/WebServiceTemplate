# Python Modular Monolith Template V1.0

Uniwersalny szkielet usługi webowej w Pythonie, zaprojektowany jako modularny monolit. Gotowy do rozszerzania przez pluginy, w pełni konfigurowalny i przygotowany do wdrożenia (deploymentu) zarówno w środowisku deweloperskim, jak i produkcyjnym.

## Główne funkcje

* **Backend Asynchroniczny**: Oparty na FastAPI z automatyczną walidacją schematów (Pydantic).
* **Capability Registry**: Moduły można włączać i wyłączać za pomocą jednej flagi w pliku `.env` i `config.py`.
* **Wbudowane CLI**: Narzędzie do automatycznego generowania boilerplate'u (endpointy, serwisy, repozytoria) dla nowych modułów.
* **Podwójny silnik bazy danych**: Automatyczny fallback do plików CSV, jeśli baza SQL (PostgreSQL) jest wyłączona. Idealne do szybkiego prototypowania.
* **Event Bus**: Wewnętrzny, asynchroniczny system zdarzeń pozwalający na luźną komunikację między modułami.
* **Standard Response Middleware**: Gwarantuje jednolity format odpowiedzi JSON z całego API.
* **Web Admin Panel**: Wbudowany, lekki interfejs użytkownika zbudowany z użyciem szablonów Jinja2 i HTMX (dający wrażenie działania aplikacji SPA bez pisania kodu w JS).
* **Gotowość na Docker**: Skonfigurowany plik `docker-compose.yml` i `Dockerfile`.

---

## Szybki start (Lokalnie)

### 1. Instalacja zależności
Upewnij się, że masz zainstalowanego Pythona 3.11+. Utwórz wirtualne środowisko i zainstaluj biblioteki:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Konfiguracja środowiska
Skopiuj przykładowy plik konfiguracyjny i dostosuj go do swoich potrzeb:

```bash
cp .env.example .env
```

### 3. Uruchomienie serwera
Uruchom aplikację w trybie deweloperskim (z automatycznym przeładowywaniem po zmianie kodu):

```bash
uvicorn app.main:app --reload
```

* **Dokumentacja API (Swagger):** http://127.0.0.1:8000/docs
* **Panel Admina (Web):** http://127.0.0.1:8000/admin/

---

## Narzędzie CLI (Generowanie Modułów)

Szablon zawiera wbudowane narzędzie wiersza poleceń, które przyspiesza tworzenie nowych funkcji.

### Tworzenie nowego modułu API
Aby wygenerować kompletny szkielet dla nowego zasobu (np. `orders`), wpisz:

```bash
python app/cli.py create-module orders
```

To polecenie utworzy folder `app/modules/orders` zawierający gotowe pliki:
* `routes.py` (Endpointy FastAPI)
* `services.py` (Logika biznesowa)
* `repository.py` (Modele bazodanowe i warstwa dostępu do danych)
* `schemas.py` (Modele walidacji Pydantic)

### Aktywacja modułu
Po wygenerowaniu modułu, musisz go zarejestrować w systemie:
1. Otwórz plik `app/config.py` i dodaj flagę: `ENABLE_ORDERS: bool = True`
2. Otwórz plik `.env` i dodaj: `ENABLE_ORDERS=True`

---

## Architektura i Przepływ Danych (Pipeline)

Aplikacja wymusza czysty podział odpowiedzialności. Typowe zapytanie HTTP przechodzi przez następujące warstwy:

1. **Router (routes.py):** Przyjmuje zapytanie, weryfikuje token (Auth) i wstrzykuje odpowiedni serwis (Dependency Injection).
2. **Schematy (schemas.py):** Pydantic automatycznie waliduje ciało zapytania.
3. **Serwis (services.py):** Wykonuje logikę biznesową i (opcjonalnie) publikuje zdarzenia na globalnej szynie `EventBus`.
4. **Repozytorium (repository.py):** Komunikuje się z trwałym nośnikiem danych (SQLAlchemy dla bazy danych lub pandas dla plików CSV).

---

## Wdrożenie (Docker)

Aby uruchomić cały stos (Aplikacja + Redis + opcjonalnie Baza Danych) w kontenerach:

```bash
docker-compose up -d --build
```

Jeśli chcesz włączyć bazę PostgreSQL, odkomentuj sekcję `db` w pliku `docker-compose.yml` oraz zmień `USE_DB=True` w pliku `.env`.