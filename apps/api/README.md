# COOP Saving API

```bash
cp .env.example .env
uv sync
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```
