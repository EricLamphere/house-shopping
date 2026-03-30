# Architecture

## Overview

House Shopping is a local-first web application built on FastAPI (Python) with a server-rendered frontend using Jinja2 templates, HTMX, and TailwindCSS. All data is stored in files on the local filesystem — no database required.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn (Python 3.11) |
| Templates | Jinja2 |
| Dynamic UI | HTMX v2 |
| Styling | TailwindCSS (CDN) |
| Drag & Drop | SortableJS (CDN) |
| Storage | JSON (houses, links) + YAML (assets) |
| Infrastructure | Docker Compose + Taskfile |

## Project Structure

```
house-shopping/
├── app/
│   ├── main.py               # FastAPI app factory
│   ├── config.py             # MEMORY_DIR path config
│   ├── models/               # Pydantic data models
│   ├── routes/               # API endpoints (FastAPI routers)
│   ├── services/             # Business logic (pure functions)
│   ├── storage/              # File-based persistence
│   ├── templates/            # Jinja2 HTML templates
│   │   └── partials/         # Reusable template fragments (HTMX targets)
│   └── static/               # CSS and JS
├── memory/                   # Volume-mounted runtime data
│   ├── houses.json           # House listings (gitignored)
│   ├── links.json            # Saved links (gitignored)
│   └── assets.yml            # Financial profile (gitignored)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                     # This folder
├── Dockerfile
├── docker-compose.yml
└── Taskfile.yml
```

## Layers

### Routes

Each router in `app/routes/` handles a domain:

| File | Prefix | Responsibility |
|------|--------|----------------|
| `home.py` | `/` | Render homepage |
| `houses.py` | `/houses` | House CRUD, favorites, reordering |
| `cost_estimator.py` | `/cost-estimator` | Cost calculator form and results |
| `assets.py` | `/assets` | User financial profile |
| `links.py` | `/links` | Saved links CRUD and reordering |

Routes return either full HTML pages or partial HTML fragments for HTMX swaps.

### Models

Pydantic models in `app/models/` define the data schema and handle validation:

- **`House`** — a saved listing, contains nested `ZillowData` plus user-entered costs, notes, and favorites metadata
- **`ZillowData`** — listing specifics: address, price, beds, baths, sqft, image URL
- **`Link`** — a saved link with display text, URL, and sort order
- **`UserAssets`** — user's financial profile: salary, savings, loan preferences
- **`CostEstimateInput`** / **`CostEstimateResult`** — input and output for cost calculations

### Services

Pure functions with no side effects, in `app/services/`:

- **`cost_calculator.py`** — mortgage amortization, PMI, closing costs, full estimate
- **`zillow_scraper.py`** — Zillow HTML parsing and URL address extraction
- **`image_proxy.py`** — async HTTP fetch for proxying listing images

### Storage

File-based persistence in `app/storage/`:

- **`HouseStore`** — reads/writes `houses.json`; thread-safe with a mutex lock; atomic writes via temp file + rename
- **`LinkStore`** — reads/writes `links.json`; same thread-safety and atomic write pattern as `HouseStore`
- **`AssetsStore`** — reads/writes `assets.yml`; YAML format for human editability

All updates use Pydantic's `model_copy(update=...)` — objects are never mutated in place.

## Request Flow

### Add House

1. User opens modal, pastes Zillow URL
2. JS parses address from URL slug (client-side, no network request)
3. User fills in price, beds, baths, sqft; submits form
4. HTMX POSTs to `/houses`; backend validates, writes to `houses.json`
5. Response includes `X-House-Added: true` header
6. JS detects header, closes modal, reloads page

### Edit House

1. User clicks Edit on a tile
2. JS fetches `/houses/{id}/edit` — returns pre-filled HTML form
3. Form is injected into the edit modal, modal opens
4. User submits; JS sends `PATCH /houses/{id}` via `fetch`
5. On `204`, JS closes modal and reloads

### Cost Estimator

1. User clicks "Estimate Costs" on a house tile
2. Browser navigates to `/cost-estimator/{house_id}`
3. House-specific data (utilities, taxes, insurance, PMI) pre-fills the form
4. User fills remaining fields and clicks Calculate
5. HTMX POSTs to `/cost-estimator/calculate`; response is a partial HTML fragment
6. HTMX swaps the results panel — no full page reload

### Links

1. User visits `/links`; server renders the full page with the current list
2. User types display text + URL, submits the add form
3. HTMX POSTs to `/links`; backend appends to `links.json` with `sort_order` = current max + 1
4. Response is the full `link_list.html` partial; HTMX swaps the `<ul>` with `outerHTML`
5. SortableJS re-initialises on `htmx:afterSettle`
6. Edit: clicking the pencil fires `GET /links/{id}/edit`; the row swaps to an inline form
7. Save: form PATCHes `/links/{id}`; response is the restored read-only row
8. Cancel: `GET /links/{id}/row` returns the read-only row without saving
9. Drag reorder: SortableJS `onEnd` sends `PUT /links/order` with the new ordered ID array
10. Delete: HTMX DELETE replaces the entire list with the updated partial

### Favorites & Reordering

- Star toggle: HTMX PATCH to `/houses/{id}/favorite`, then `window.location.reload()`
- Drag reorder: SortableJS captures new order on drag end, `fetch` PUT to `/houses/favorites/order` with ordered IDs

## Storage Design

### houses.json

Array of serialized `House` objects. Written atomically:

1. Serialize to a temp file in the same directory
2. `Path(tmp).replace(target)` — atomic rename (POSIX guarantee)
3. If write fails, temp file is deleted, original is untouched

A `threading.Lock` ensures only one read/write occurs at a time.

### assets.yml

Single YAML document matching the `UserAssets` schema. Human-editable. Defaults to zero values if the file is missing.

## Frontend Approach

The frontend is server-rendered HTML with targeted partial updates via HTMX. There is no client-side framework.

- **Full pages** are returned for navigation (`GET /`, `GET /cost-estimator`)
- **Partial fragments** are returned for in-page updates (form validation errors, cost results)
- **JS is minimal** — modal management, SortableJS init, address extraction from URL slugs, and one `fetch` call for edit submission

HTMX attributes on HTML elements declare the behavior:
- `hx-post`, `hx-patch`, `hx-delete` — method
- `hx-target` — where to swap the response
- `hx-swap` — how to swap (e.g. `innerHTML`)
- `hx-indicator` — element to show as a loading spinner

## Configuration

`app/config.py` reads `MEMORY_DIR` from the environment (defaults to `./memory`). Docker Compose sets `MEMORY_DIR=/app/memory` and mounts `./memory` as a volume, so data persists across container restarts.

Static files use cache-busting query strings (e.g. `app.js?v=5`) to force browser refreshes after deploys.
