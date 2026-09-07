# Arquitectura — Comanda TPV

## Visión general

```
┌─────────────┐     REST/WS      ┌─────────────┐
│  Frontend   │ ◄──────────────► │   Backend   │
│  Next.js    │                  │   FastAPI   │
│  (Flavia)   │                  │  (Maria)    │
└─────────────┘                  └──────┬──────┘
                                        │
                                   ┌────▼────┐
                                   │   BD    │
                                   │ SQLite/ │
                                   │ Postgres│
                                   └─────────┘
```

## Capas del backend

```
app/
├── main.py          # FastAPI app, lifespan (create_all), CORS, routers
├── config.py        # Settings con pydantic-settings (.env)
├── db.py            # Engine, SessionLocal, Base, get_db
├── models/          # Modelos SQLAlchemy (ORM)
├── schemas/         # Schemas Pydantic (validación entrada/salida)
└── api/routes/      # Routers REST por dominio
```

## Modelo de datos

Entidades principales:

- **staff** — personal (cambreros, cocina, barra, managers)
- **areas** — zonas de la sala (terraza, interior, barra)
- **tables** — mesas (pertenecen a un área)
- **menu_categories** / **menu_items** — carta
- **reservations** — reservas (ligadas a mesa)
- **orders** / **order_items** — comandas y sus líneas
- **payments** — pagos (cash, card, bizum, split)
- **fiscal_records** — registro fiscal VeriFactu (hash encadenado)

## Decisiones clave

1. **UUID como PK** — compatible SQLite y PostgreSQL, evita colisiones al sincronizar.
2. **Snapshot de precio/nombre** en `order_items` — el tique conserva el precio
   del momento del pedido aunque la carta cambie después.
3. **Hash encadenado VeriFactu** — `chain_hash = SHA256(previous_hash + payload_canonico)`.
   El payload se serializa con claves ordenadas (JSON canónico) para garantizar
   determinismo.
4. **Rutas de colección sin barra final** (`""` en vez de `"/"`) — evita el
   redirect 307 de Starlette que rompe `fetch`/curl (lección aprendida en Ariadna).
5. **`create_all` en lifespan** — Fase 0 sin migraciones Alembic; se añadirán
   cuando el esquema se estabilice.

## Cumplimiento fiscal (VeriFactu)

- `fiscal_records.record_id` — identificador único del registro.
- `fiscal_records.chain_hash` — hash encadenado (integridad de la cadena).
- `fiscal_records.previous_chain_hash` — enlace al registro anterior.
- `fiscal_records.payload_json` — datos canónicos del tique.
- `fiscal_records.signature` — firma electrónica (pendiente en producción).

## Pendiente

- WebSocket para tiempo real (comandas → cocina, estado de mesas).
- Autenticación (PIN del personal, JWT para managers).
- Firma electrónica VeriFactu con certificado.
- Migraciones Alembic.
