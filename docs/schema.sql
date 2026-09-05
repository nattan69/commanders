-- ============================================================
-- Commanders TPV — Esquema de referencia (PostgreSQL)
-- Generado a partir de los modelos SQLAlchemy (app/models/models.py)
-- ============================================================

-- PERSONAL
CREATE TABLE staff (
    id          UUID PRIMARY KEY,
    full_name   VARCHAR NOT NULL,
    email       VARCHAR UNIQUE,
    phone       VARCHAR,
    role        VARCHAR NOT NULL,          -- admin, manager, waiter, kitchen, bar
    pin         VARCHAR,                   -- PIN de acceso rápido (hash en producción)
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- ÁREAS
CREATE TABLE areas (
    id                UUID PRIMARY KEY,
    name              VARCHAR NOT NULL,    -- terraza, interior, barra...
    position_x        INTEGER DEFAULT 0,
    position_y        INTEGER DEFAULT 0,
    surcharge_percent NUMERIC(5,2) DEFAULT 0,
    created_at        TIMESTAMPTZ DEFAULT now()
);

-- MESAS
CREATE TABLE tables (
    id         UUID PRIMARY KEY,
    area_id    UUID REFERENCES areas(id) ON DELETE SET NULL,
    number     VARCHAR NOT NULL,
    seats      INTEGER DEFAULT 4,
    position_x INTEGER DEFAULT 0,
    position_y INTEGER DEFAULT 0,
    shape      VARCHAR DEFAULT 'square',   -- square, round, rectangle
    status     VARCHAR DEFAULT 'available',-- available, occupied, reserved, needs_cleaning, blocked
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- CATEGORÍAS DE MENÚ
CREATE TABLE menu_categories (
    id         UUID PRIMARY KEY,
    name       VARCHAR NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ARTÍCULOS DE MENÚ
CREATE TABLE menu_items (
    id              UUID PRIMARY KEY,
    category_id     UUID REFERENCES menu_categories(id) ON DELETE SET NULL,
    name            VARCHAR NOT NULL,
    description     TEXT,
    price           NUMERIC(10,2) NOT NULL,
    vat_rate        NUMERIC(5,2) DEFAULT 10.0,  -- IVA: 10% hostelería, 21% alcohol
    kitchen_station VARCHAR DEFAULT 'main',     -- main, grill, fry, bar, dessert
    allergens       JSONB,
    is_available    BOOLEAN NOT NULL DEFAULT TRUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- RESERVAS
CREATE TABLE reservations (
    id               UUID PRIMARY KEY,
    table_id         UUID REFERENCES tables(id) ON DELETE SET NULL,
    customer_name    VARCHAR NOT NULL,
    customer_phone   VARCHAR,
    customer_email   VARCHAR,
    party_size       INTEGER NOT NULL DEFAULT 2,
    reservation_date DATE NOT NULL,
    reservation_time VARCHAR NOT NULL,     -- "20:30"
    status           VARCHAR DEFAULT 'confirmed', -- pending, confirmed, seated, cancelled, no_show
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- COMANDAS
CREATE TABLE orders (
    id              UUID PRIMARY KEY,
    table_id        UUID REFERENCES tables(id) ON DELETE SET NULL,
    staff_id        UUID REFERENCES staff(id) ON DELETE SET NULL,
    order_type      VARCHAR DEFAULT 'dine_in',  -- dine_in, takeaway, delivery
    status          VARCHAR DEFAULT 'open',     -- open, sent_to_kitchen, served, paid, cancelled
    total_amount    NUMERIC(10,2) DEFAULT 0,
    discount_amount NUMERIC(10,2) DEFAULT 0,
    notes           TEXT,
    opened_at       TIMESTAMPTZ DEFAULT now(),
    closed_at       TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- LÍNEAS DE COMANDA
CREATE TABLE order_items (
    id             UUID PRIMARY KEY,
    order_id       UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    menu_item_id   UUID REFERENCES menu_items(id) ON DELETE SET NULL,
    name_snapshot  VARCHAR,                -- nombre en el momento del pedido
    price_snapshot NUMERIC(10,2),          -- precio en el momento del pedido
    quantity       INTEGER NOT NULL DEFAULT 1,
    vat_rate       NUMERIC(5,2) DEFAULT 10.0,
    status         VARCHAR DEFAULT 'pending', -- pending, sent, preparing, ready, served, cancelled
    modifications  JSONB,                  -- ["sin cebolla", "poco hecho", ...]
    seat_number    INTEGER,                -- división de cuenta por comensal
    created_at     TIMESTAMPTZ DEFAULT now()
);

-- PAGOS
CREATE TABLE payments (
    id         UUID PRIMARY KEY,
    order_id   UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    method     VARCHAR NOT NULL,           -- cash, card, bizum, split
    amount     NUMERIC(10,2) NOT NULL,
    status     VARCHAR DEFAULT 'completed',-- pending, completed, refunded, failed
    paid_at    TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- REGISTRO FISCAL (VeriFactu)
CREATE TABLE fiscal_records (
    id                  UUID PRIMARY KEY,
    order_id            UUID REFERENCES orders(id) ON DELETE SET NULL,
    record_id           VARCHAR UNIQUE NOT NULL,
    chain_hash          VARCHAR NOT NULL,  -- SHA256(previous_hash + payload_canonico)
    previous_chain_hash VARCHAR,
    payload_json        JSONB NOT NULL,
    record_type         VARCHAR DEFAULT 'alta', -- alta, anulacion, rectificacion
    issued_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    signature           VARCHAR,           -- firma electrónica (producción)
    created_at          TIMESTAMPTZ DEFAULT now()
);
