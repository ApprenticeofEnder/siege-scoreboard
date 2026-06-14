# Agent Instructions

Test command: `uv run pytest --nf --lf`
Type check command: `uv run basedpyright .`
Lint command: `uv run ruff check .`
Format command: `uv run ruff format .`

## Rules

- Do not strip type hints; only add or modify if needed to resolve type checking issues.
