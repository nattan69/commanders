# Commanders TPV — Guió d'estat i pròximes passes

> Actualitzat: 06/09/2026 (nit)
> Projecte: TPV per bar/restaurant — `D:/projectes/Commanders`
> Repo: `github.com/nattan69/commanders`

---

## 1. Què és Commanders

TPV (punt de venda) per a bars i restaurants, amb 4 mòduls principals:

1. **Reserves** (de taules)
2. **Comandes** (tauló, cuina, KDS)
3. **Taules** (pla de sala, obertes, pagament fraccionat)
4. **Cambrers** (gestió de personal, sessions per dispositiu)

**Equip:**
- **Maria** (jo) → backend + supervisió/coordinació
- **Flavia** → frontend (Next.js)
- **Gemma4** → suport (feina feixuga de codi)

**Stack:** FastAPI (backend) + Next.js 15 (frontend), SQLite en dev / PostgreSQL en producció, WebSocket per temps real (pendent).

---

## 2. Què duim fet

### Backend (FastAPI) — complet i verificat end-to-end

**Models (11):**
- `Staff` — cambrers (amb `pin` per login)
- `DeviceSession` — sessió per dispositiu (PDA/mòbil/tablet)
- `Area` — zones de la sala (terrassa, interior, barra...)
- `Table` — taules (número, seients, posició, estat)
- `MenuCategory` / `MenuItem` — carta (preu, IVA, estació de cuina, al·lèrgens)
- `Reservation` — reserves (amb `source`, `external_id`, `created_by`)
- `Order` / `OrderItem` — comandes (snapshot de preu/nom, modificadors, seient)
- `Payment` — pagaments (efectiu, targeta, bizum, split)
- `FiscalRecord` — registre fiscal VeriFactu (hash encadenat)

**Rutes REST (7 routers):**
- `/api/v1/tables` — àrees + taules (CRUD)
- `/api/v1/menu` — categories + articles (CRUD)
- `/api/v1/reservations` — reserves (CRUD)
- `/api/v1/orders` — comandes (amb items, càlcul total, divisió de compte)
- `/api/v1/staff` — personal + **login/logout per PIN**
- `/api/v1/fiscal` — emissió de registre fiscal (hash encadenat)
- `/api/v1/integrations` — **endpoint per a n'Ariadna** (reserves multicanal)

**Funcionalitats clau implementades:**
- ✅ **Autenticació per PIN** — cada cambrer fa login al seu dispositiu, sessió independent amb token
- ✅ **Integració Ariadna** — endpoint dedicat amb API key, idempotent per `external_id`
- ✅ **Hash encadenat VeriFactu** — registre fiscal inalterable (SHA-256 encadenat)
- ✅ **Snapshot de preu/nom** als items (el tique conserva el preu del moment)
- ✅ **Divisió de compte** per comensal (`seat_number`)

### Frontend (Next.js) — esquelet fet per na Flavia

- Next 15 + App Router, trilingüe ca/es/en
- `lib/api.ts` — client API amb fallback al mock
- `app/sala` — pla de sala visual (taules per àrea, estat lliure/ocupada)
- `app/comandes` — presa de comandes (taula + carta + items)
- Paleta de marca: crema + tinta + or (estètica de carta/tiquet)

### Promo web

- `sapedrera.eu/comanda.html` — redissenyada amb estètica de carta/tiquet
- Targeta a la portada (🍽️ Comanda · TPV Restaurant)

### Commits al repo

```
43850de  Autenticación por PIN: DeviceSession + /staff/login + /staff/logout
35ba87e  feat(frontend): esquelet Next.js (sala + comandes)  [Flavia]
8c9b56f  Integración con Ariadna: /integrations/reservations
51708d4  Backend base TPV: models, schemas, rutas CRUD + fiscal VeriFactu
```

---

## 3. Pròximes passes

### Immediates (demà)

1. **Connectar frontend ↔ backend** contra el contracte d'API
   - Na Flavia connecta `lib/api.ts` al backend real (ja té el contracte)
   - Verificar el flux: login PIN → pla de sala → presa de comanda → enviar a cuina

2. **Contracte exacte de crida Ariadna ↔ TPV**
   - Definir com n'Ariadna crida `/integrations/reservations` (payload exacte, API key)
   - Coordinar amb el projecte Ariadna

### Properes (a curt termini)

3. **WebSocket per temps real** — comandes → cuina (KDS), estat de taules en viu
4. **Autenticació completa** — validar el token a cada crida (ara el login retorna token però les rutes encara no l'exigeixen)
5. **KDS (Kitchen Display System)** — pantalla de cuina amb encaminament per estacions
6. **Divisió de comptes** — UI per dividir per comensal/article/percentatge

### A mitjà termini

7. **Firma electrònica VeriFactu** — certificat digital per a producció
8. **PostgreSQL** — migració de SQLite a Postgres per a producció
9. **Alembic** — migracions de BD (ara fem `create_all` idempotent)

### Decisions pendents de l'usuari (en Tomeu)

- **Dispositiu principal**: tauleta tàctil / PC de barra / ambdós
- **VeriFactu**: Fase 0 sense firma / des del principi / ja ho veurem
- **Stack**: confirmar FastAPI + Next.js (proposat i assumit)

---

## 4. Notes tècniques importants

- **Rutes de col·lecció amb `""`** (no `"/"`) per evitar el redirect 307 de Starlette
- **Codi en castellà** (convenció per a Gemma4 i el projecte)
- **Gemma4 no commiteja** — Maria revisa, verifica amb TestClient, commiteja i puja
- **Verificació**: `backend/verify_e2e.py` (TestClient) — passa tot el flux end-to-end
- **BD dev**: `backend/commanders.db` (SQLite, esborrable per a proves)
