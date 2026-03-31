# House Shopping

A local-first app for tracking houses you're considering buying. Add listings, favorite and sort them, take notes, and estimate monthly costs.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Task](https://taskfile.dev/installation/)

## Usage

```bash
task start        # build, start (detached), open browser
task stop         # stop the app
task logs         # tail logs
task test         # run tests with coverage
task lint         # run ruff linter
```

Or with live logs:

```bash
task start -- debug
```

The app runs at **http://localhost:8000**.

## Data

All data is stored locally in `memory/`:

- `houses.json` — your saved listings (gitignored)
- `assets.yml` — your financial profile for cost estimates (committed with zero defaults)

## Features

- Add houses by pasting a Zillow URL (address auto-filled from URL) or entering details manually
- Favorite houses and drag to reorder them
- Edit listings and add notes
- Estimate monthly mortgage, taxes, insurance, PMI, and utilities per house
