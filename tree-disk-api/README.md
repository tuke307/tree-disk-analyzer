# Tree Disk Analyzer API

## Development
general setup
```bash
poetry config virtualenvs.in-project true
poetry env use python
```

install dependencies
```bash
poetry install
eval $(poetry env activate)
```

download models
```bash
python -m src.config.preparation
```

## Usage Examples

### start server (dev)
```bash
uvicorn src.main:app --reload
```

### start server (prod)
```bash
gunicorn src.main:app -c gunicorn.conf.py
```

### test
```bash
pytest
```
