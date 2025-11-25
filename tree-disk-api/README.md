# Tree Disk Analyzer API

## Development
general setup
```bash
uv venv .venv
source .venv/bin/activate
```

install dependencies
```bash
uv sync
```

download models
```bash
uv run python -m src.config.preparation
```

## Usage Examples

### start server (dev)
```bash
uv run uvicorn src.main:app --reload
```

### start server (prod)
```bash
uv run gunicorn src.main:app -c gunicorn.conf.py
```

### test
```bash
uv run pytest
```
