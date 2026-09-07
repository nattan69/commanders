# Comanda — TPV para bar/restaurante

Sistema de punto de venta (TPV) para bares y restaurantes, con gestión de
reservas, comandas, mesas y personal. Proyecto independiente de Jornals y
Ariadna, siguiendo el mismo patrón de arquitectura (backend FastAPI +
frontend Next.js desacoplados, contrato REST + WebSocket).

## Módulos

| Módulo | Descripción |
|---|---|
| **Reservas** | Gestión de reservas con preferencias del cliente, tamaño de grupo, estado (pendiente/confirmada/sentada/cancelada/no-show) |
| **Comandas** | Toma de pedidos a mesa, envío a cocina, modificadores, división de cuenta por comensal |
| **Mesas** | Plano de sala visual, estado en tiempo real, áreas (terraza/interior/barra) |
| **Personal** | Cambreros, roles, PIN de acceso rápido, turnos |

## Stack

- **Backend**: Python + FastAPI + SQLAlchemy (SQLite en dev, PostgreSQL en producción)
- **Frontend**: Next.js (React)
- **Tiempo real**: WebSocket (comandas → cocina, estado de mesas)
- **Fiscal**: preparado para VeriFactu (registro de facturación con hash encadenado SHA-256)

## Cumplimiento fiscal (VeriFactu)

Desde 2026, todo TPV que emita tiques/facturas en España debe cumplir
VeriFactu (registro de facturación inalterable). El backend ya incluye la
tabla `fiscal_records` con hash encadenado (SHA-256 del hash anterior +
payload canónico), preparada para la firma electrónica en producción.

## Estructura

```
Comanda/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── main.py           # Punto de entrada, routers, CORS
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── db.py             # Engine, SessionLocal, Base
│   │   ├── models/           # Modelos SQLAlchemy
│   │   ├── schemas/          # Schemas Pydantic
│   │   └── api/routes/       # Routers REST (tables, menu, reservations, orders, staff, fiscal)
│   ├── requirements.txt
│   └── verify_e2e.py         # Verificación end-to-end con TestClient
├── frontend/         # Next.js (pendiente — na Flavia)
└── docs/             # Documentación
```

## API (contrato REST)

Base: `/api/v1`

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Health check |
| GET/POST | `/tables` | Listar/crear mesas |
| GET/PATCH/DELETE | `/tables/{id}` | Detalle/actualizar/borrar mesa |
| GET/POST | `/tables/areas` | Listar/crear áreas |
| GET/POST | `/menu/categories` | Listar/crear categorías |
| GET/POST | `/menu/items` | Listar/crear artículos |
| GET/PATCH/DELETE | `/menu/items/{id}` | Detalle/actualizar/borrar artículo |
| GET/POST | `/reservations` | Listar/crear reservas |
| GET/PATCH/DELETE | `/reservations/{id}` | Detalle/actualizar/borrar reserva |
| GET/POST | `/orders` | Listar/crear comandas |
| GET | `/orders/{id}` | Detalle de comanda (con items) |
| POST | `/orders/{id}/items` | Añadir item a comanda |
| PATCH | `/orders/{id}/status` | Cambiar estado de comanda |
| GET/POST | `/staff` | Listar/crear personal |
| GET/PATCH/DELETE | `/staff/{id}` | Detalle/actualizar/borrar personal |
| GET | `/fiscal` | Listar registros fiscales |
| POST | `/fiscal/{order_id}/issue` | Emitir registro fiscal (hash encadenado) |

## Estado

- [x] Backend base (modelos, schemas, rutas CRUD, fiscal con hash encadenado)
- [x] Verificación end-to-end con TestClient
- [ ] Frontend Next.js (na Flavia)
- [ ] WebSocket tiempo real (comandas → cocina)
- [ ] Firma electrónica VeriFactu (producción)
