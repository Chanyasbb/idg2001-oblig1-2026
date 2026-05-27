# Olympics API

REST API for querying Olympic Games data (2008–2016).
Built with FastAPI + SQLite. Token-based access control.

## Live on Render

**Base URL:** `<RENDER_URL>`

Interactive docs: `<RENDER_URL>/docs`

## Dataset

The bundled dataset covers 2008–2016 (Summer + Winter Olympics, ~49k rows).
Original full dataset (120 years) available on [Kaggle](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results).

## Run locally

```bash
cd olympics_api
python -m venv ../venv && source ../venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Endpoints

### Admin (no auth required)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/user` | Register a new user |
| GET | `/v1/user` | List all users |
| GET | `/v1/user/<id>` | Get a user |
| PUT / PATCH | `/v1/user/<id>` | Update email and/or password |
| DELETE | `/v1/user/<id>` | Delete a user |
| POST | `/v1/tokens` | Add tokens to a user |

### Data (requires `X-User-Id` header, costs 1 token per call)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/athlete/<id>` | Athlete record by row ID |
| GET | `/v1/athlete?name=<name>` | Search athletes by name (partial match) |
| GET | `/v1/country/<noc>` | Medal summary by country NOC code (e.g. `NOR`) |
| GET | `/v1/sport/<sport>` | Sport results with optional filters |
| POST | `/v1/event` | Add a new participation record |

All data endpoints accept `?format=json` (default) or `?format=xml`.

#### Sport endpoint filters

```
GET /v1/sport/ski-jumping?country=NOR&year=2014&medals=gold
```

- `country` — NOC code, e.g. `NOR`
- `year` — e.g. `2014`
- `medals` — `gold`, `silver`, or `bronze`
- `format` — `json` or `xml`

Sport slugs are normalized: `ski-jumping` matches `"Ski Jumping"` in the DB.

## Auth

Data endpoints require an `X-User-Id: <user_id>` header.
Each call deducts 1 token. New users start with 100 tokens.

## Tests

```bash
cd olympics_api
pytest                  # all tests with coverage report
flake8 app tests        # PEP 8 style check
mypy app                # static type check
```
