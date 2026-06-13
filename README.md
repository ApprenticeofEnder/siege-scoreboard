# Siege Scoreboard

Scaffold for a rewrite of the [Siege](https://github.com/0xd13a/siege) defense-competition scoreboard. Domain logic is not implemented yet; see [`DATA_MODEL.md`](DATA_MODEL.md) for the target data model.

## Stack

- **Backend:** FastAPI + Jinja2
- **Frontend:** [shadcn-htmx](https://github.com/productdevbook/shadcn-htmx) (Jinja2 macros) + HTMX v4 SSE
- **CSS:** Tailwind CSS v4
- **Dev environment:** [devenv](https://devenv.sh) with `languages.python` (uv) and `languages.javascript` (pnpm)

## Prerequisites

- [devenv](https://devenv.sh/getting-started/)
- [direnv](https://direnv.net/) (recommended)

Node, pnpm, Python 3.13, and uv are provided by devenv language modules — no separate install needed.

## Setup

```sh
direnv allow          # runs uv sync + pnpm install on first enter
pnpm dlx shadcn-htmx init --flavour jinja
pnpm dlx shadcn-htmx add button card table badge theme-toggle
```

Components land in [`templates/components/`](templates/components/).

## Development

```sh
devenv up
```

Starts three things:

1. **`css:build` task** — compiles Tailwind once before processes start
2. **`tailwind` process** — watches templates and rebuilds CSS
3. **`api` process** — FastAPI on port 8000 with reload

Useful scripts:

```sh
devenv shell
pnpm run build:css   # one-off CSS build
uv run ruff check .
uv run ruff format .
```

## URLs

| Path | Description |
|------|-------------|
| `/` | Redirects to `/demo` |
| `/demo` | HTMX SSE event log demo |
| `/events` | SSE stream (synthetic score events) |
| `/health` | Health check |

## Project layout

```
app/main.py              FastAPI app
templates/               Jinja2 pages + shadcn-htmx macros
templates/components/    shadcn-htmx CLI output (do not hand-edit)
assets/input.css         Tailwind entry + theme tokens
app/static/styles.css    compiled CSS (gitignored, built by Tailwind)
```

## Next steps

Implement entities from [`DATA_MODEL.md`](DATA_MODEL.md): tick result ingestion, scoring policy, SQLite persistence, leaderboard views, and D3 chart.
