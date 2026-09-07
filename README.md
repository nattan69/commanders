# Comanda 🍽️

TPV (punto de venta) para bares y restaurantes: reservas, comandas, mesas y
personal. Backend FastAPI + frontend Next.js, preparado para VeriFactu.

## Arranque rápido (backend)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check: `http://localhost:8000/health`

Verificación end-to-end:

```bash
.venv/bin/python verify_e2e.py
```

## Documentación

- [docs/PROJECTE.md](docs/PROJECTE.md) — visión general y estado
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — arquitectura y decisiones
