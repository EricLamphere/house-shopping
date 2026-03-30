# House Shopping App

## Overview
A local-first house shopping app that stores Zillow links with previews, supports favoriting/sorting, and includes a cost estimator for monthly payments and upfront costs.

## Tech Stack
- **Backend**: FastAPI (Python 3.11+), Uvicorn
- **Frontend**: Jinja2 templates + HTMX + TailwindCSS (CDN) + SortableJS (CDN)
- **Storage**: JSON/YAML files in `memory/` volume
- **Infrastructure**: Docker Compose + Taskfile

## Commands
- `task start` - Build and start app (detached), open browser
- `task start -- --debug` - Start with live logs in terminal
- `task stop` - Stop the app
- `task logs` - Tail logs
- `task test` - Run tests with coverage
- `task lint` - Run ruff linter

## Project Structure
- `app/` - FastAPI application
  - `models/` - Pydantic data models
  - `services/` - Business logic (scraper, calculator, image proxy)
  - `storage/` - File-based persistence (JSON/YAML)
  - `routes/` - API endpoints
  - `templates/` - Jinja2 HTML templates
  - `static/` - CSS and JS
- `memory/` - Volume-mounted data directory
  - `assets.yml` - User finance data (committed with zero defaults)
  - `houses.json` - House listings (gitignored, runtime-generated)
- `tests/` - pytest test suite

## Conventions
- Immutable data patterns: never mutate, always create new objects
- Atomic file writes: write to temp file, then rename
- HTMX partials in `templates/partials/` for dynamic updates
- Pure functions in services (no side effects in calculators)
- All user input validated via Pydantic models
