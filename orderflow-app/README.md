# OrderFlow — Phase 1

Simple Order Management API used as the application foundation for the platform-engineering project.

## Phase 1 scope

- FastAPI REST API
- PostgreSQL persistence
- SQLAlchemy 2.x
- Alembic migrations
- Pydantic request/response validation
- Health and readiness endpoints
- Pytest API tests

The application intentionally contains very little business logic. The platform is the primary project focus.

## Project structure

```text
orderflow-app/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   └── orders.py
│   │   └── router.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   └── order.py
│   ├── schemas/
│   │   └── order.py
│   └── main.py
├── migrations/
│   ├── versions/
│   │   └── 0001_create_orders_table.py
│   ├── env.py
│   └── script.py.mako
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## API

```text
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{id}
PATCH  /api/v1/orders/{id}/status
DELETE /api/v1/orders/{id}
GET    /health
GET    /ready
```

`/health` verifies that the process is running. `/ready` verifies that the application can reach its database. This distinction will map directly to Kubernetes probes later.

## 1. Create virtual environment

Python 3.12+ is recommended for local development.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start PostgreSQL

For a quick local development database, run PostgreSQL separately from the application:

```bash
docker run --name orderflow-postgres \
  -e POSTGRES_USER=orderflow \
  -e POSTGRES_PASSWORD=orderflow \
  -e POSTGRES_DB=orderflow \
  -p 5432:5432 \
  -d postgres:17-alpine
```

If the container already exists:

```bash
docker start orderflow-postgres
```

## 3. Configure the application

```bash
cp .env.example .env
```

The `.env` file is intentionally ignored by Git. In later phases, the same configuration pattern will become Kubernetes Secrets/ConfigMaps and eventually AWS secret management.

## 4. Run database migration

```bash
alembic upgrade head
```

## 5. Start the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## 6. Run tests

```bash
pytest -q
```

By default the tests use an isolated SQLite database so the test suite is fast and requires no external service. To exercise the same SQLAlchemy model against PostgreSQL, set `TEST_DATABASE_URL` before running pytest:

```bash
export TEST_DATABASE_URL='postgresql+psycopg://orderflow:orderflow@localhost:5432/orderflow'
pytest -q
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_id": "CUST-1001",
    "product": "Laptop",
    "quantity": 1,
    "amount": 75000
  }'
```

Example response shape:

```json
{
  "order_id": "ORD-XXXXXXXXXX",
  "customer_id": "CUST-1001",
  "product": "Laptop",
  "quantity": 1,
  "amount": "75000.00",
  "status": "CREATED",
  "created_at": "2026-10-01T12:00:00Z",
  "updated_at": "2026-10-01T12:00:00Z"
}
```

## Architecture decision

### Problem
We need a small business application that can demonstrate the platform without spending most of the project on domain logic.

### Decision
Keep one FastAPI service, one PostgreSQL database, one order resource, and a small set of operational endpoints.

### Result
The application is small enough to understand quickly while exposing the interfaces required by later Docker, CI, Kubernetes, GitOps, observability, AWS, and service-mesh phases.

### Trade-off
The service is intentionally not split into multiple business services yet. That complexity will be introduced only in Phase 9 when the Payment API is added for service-mesh and canary demonstrations.
