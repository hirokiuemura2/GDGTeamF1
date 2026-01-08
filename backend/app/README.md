# Backend App — Contributor Guide

This guide explains the project layout and the recommended way to add new code (routes, services, repos, models, and dependencies) to keep things consistent.

## Overview
- FastAPI application with a clear separation of concerns:
  - Routers define HTTP endpoints and map requests to services
  - Services hold business logic and orchestrate data access
  - Repositories encapsulate data storage (Firestore)
  - Models define input/output schemas (Pydantic)
  - Infrastructure wraps external systems/SDKs (e.g., HTTP APIs)
  - Dependencies wire everything together via FastAPI `Depends`
  - Core holds cross‑cutting helpers (settings, HTTP client)

Request flow example: Router → Service → Repo/Infra → Service → Router response_model

## Directory Structure
- `main.py` — FastAPI app factory and router registration
- `routers/` — Route handlers using `APIRouter`
  - e.g., `expense_router.py`, `currency_router.py`
- `services/` — Business logic classes
  - e.g., `ExpenseService`, `CurrencyService`
- `repo/` — Data access (Firestore collections, queries, writes)
  - e.g., `ExpenseRepo`
- `models/` — Pydantic request/response models
  - e.g., `ExpenseCreate`, `ExpenseResponse`, `UserCreate`
- `infrastructure/` — External clients and provider wrappers
  - e.g., `CurrencyAPIClient`
- `dependencies/` — DI providers that compose settings/clients/services
  - e.g., `db.py`, `services.py`, `external.py`, `auth.py`
- `core/` — Shared utilities
  - `config.py` (Pydantic Settings), `http.py` (shared `httpx.AsyncClient`)

## Configuration
- Environment is loaded via `core/config.py` (`Settings`)
- Expected variables (via `.env`):
  - `currency_api_key` — for currency API calls
  - `gcp_project_id` — for Firestore client
- Access settings in DI with `Depends(get_settings)`


## Adding a New Feature (Endpoint)
Example: add a feature to manage “categories”.

1) Models (`models/category_models.py`)
- Define request/response schemas with Pydantic.

```python
# models/category_models.py
from pydantic import BaseModel, Field
from typing import Annotated

class CategoryCreate(BaseModel):
    name: Annotated[str, Field(strict=True, min_length=1)]

class CategoryResponse(CategoryCreate):
    id: str
```

2) Repo (`repo/category_repo.py`)
- Encapsulate Firestore access; keep methods synchronous.

```python
# repo/category_repo.py
from typing import Any, final
from google.cloud.firestore import Client

@final
class CategoryRepo:
    def __init__(self, db: Client, user_id: str):
        self.col = db.collection("users").document(user_id).collection("categories")

    def create(self, data: dict[str, Any]) -> str:
        doc_ref = self.col.document()
        doc_ref.set(data)
        return doc_ref.id
```


3) Service (`services/category_service.py`)
- Async boundary; use `run_in_threadpool` for repo calls.

```python
# services/category_service.py
from fastapi.concurrency import run_in_threadpool
from typing import final
from app.models.category_models import CategoryCreate, CategoryResponse
from app.repo.category_repo import CategoryRepo

@final
class CategoryService:
    def __init__(self, repo: CategoryRepo):
        self.repo = repo

    async def create(self, payload: CategoryCreate) -> CategoryResponse:
        data = {"name": payload.name}
        cid = await run_in_threadpool(self.repo.create, data)
        return CategoryResponse(id=cid, **data)
```


4) Dependency wiring (`dependencies/services.py`)
- Compose repo + service with DI providers.

```python
# dependencies/services.py
from typing import Annotated
from fastapi import Depends
from google.cloud import firestore

from app.dependencies.auth import get_current_user_id
from app.dependencies.db import get_firestore_client
from app.repo import ExpenseRepo, CategoryRepo  # NEW
from app.services.expense_service import ExpenseService
from app.services.category_service import CategoryService  # NEW

# existing get_expense_service(...)

def get_category_service(
    db: Annotated[firestore.Client, Depends(get_firestore_client)],
    user_id: Annotated[str, Depends(get_current_user_id)],
) -> CategoryService:
    return CategoryService(CategoryRepo(db, user_id))
```

5) Router (`routers/category_router.py`)
- Keep the router thin; specify `response_model`.

```python
# routers/category_router.py
from typing import Annotated
from fastapi import APIRouter, Depends

from app.models.category_models import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService
from app.dependencies.services import get_category_service

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    payload: CategoryCreate,
    svc: Annotated[CategoryService, Depends(get_category_service)],
) -> CategoryResponse:
    return await svc.create(payload)
```

6) Register the router (`main.py`)

```python
# main.py
from fastapi import FastAPI
from app.routers import currency_router, expense_router
from app.routers import category_router  # NEW

app = FastAPI()
app.include_router(currency_router.router)
app.include_router(expense_router.router)
app.include_router(category_router.router)  # NEW
```

## Working with Firestore
- Firestore client is provided via `dependencies/db.get_firestore_client`
- Configure `gcp_project_id` in `.env`
- Keep repo methods synchronous; call them from async services using `run_in_threadpool`
- Data shape stored should match your response models (minus server fields like `id`)

## External APIs
- Wrap the API in `infrastructure/` and inject `httpx.AsyncClient` from `core/http.py`
- Provide a DI factory in `dependencies/external.py` (e.g., `get_currency_api`)
- Surface HTTP errors explicitly in routers as `HTTPException` where appropriate

## Running Locally
- Create `.env` in project root with required variables:
  - `currency_api_key=...`
  - `gcp_project_id=...`
- Start the app: `uvicorn app.main:app --reload`
- Health check: `GET /healthcheck`
