"""Verificación end-to-end del backend Commanders con TestClient.

Prueba el flujo completo: crear área → mesa → categoría → artículo →
staff → comanda con items → emitir registro fiscal (hash encadenado).
"""
from fastapi.testclient import TestClient
from app.main import app
from app.db import engine
from sqlalchemy import inspect


def main():
    with TestClient(app) as client:
        # Health
        r = client.get("/health")
        assert r.status_code == 200, r.text
        print("health:", r.json())

        # Área
        r = client.post("/api/v1/tables/areas", json={"name": "Terraza"})
        assert r.status_code == 201, r.text
        area_id = r.json()["id"]
        print("area:", r.json()["name"])

        # Mesa
        r = client.post("/api/v1/tables", json={"area_id": area_id, "number": "1", "seats": 4})
        assert r.status_code == 201, r.text
        table_id = r.json()["id"]
        print("mesa:", r.json()["number"])

        # Categoría
        r = client.post("/api/v1/menu/categories", json={"name": "Bebidas"})
        assert r.status_code == 201, r.text
        cat_id = r.json()["id"]

        # Artículo
        r = client.post("/api/v1/menu/items", json={
            "category_id": cat_id, "name": "Café", "price": 1.5, "vat_rate": 10.0
        })
        assert r.status_code == 201, r.text
        item_id = r.json()["id"]
        print("artículo:", r.json()["name"], r.json()["price"])

        # Staff
        r = client.post("/api/v1/staff", json={"full_name": "Pep", "role": "waiter"})
        assert r.status_code == 201, r.text
        staff_id = r.json()["id"]

        # Comanda con items (snapshot automático desde el menú)
        r = client.post("/api/v1/orders", json={
            "table_id": table_id,
            "staff_id": staff_id,
            "items": [
                {"menu_item_id": item_id, "quantity": 2},
                {"name_snapshot": "Croissant", "price_snapshot": 2.0, "quantity": 1},
            ],
        })
        assert r.status_code == 201, r.text
        order = r.json()
        order_id = order["id"]
        print("comanda total:", order["total_amount"], "items:", len(order["items"]))

        # Emitir registro fiscal (hash encadenado)
        r = client.post(f"/api/v1/fiscal/{order_id}/issue")
        assert r.status_code == 201, r.text
        fiscal = r.json()
        print("fiscal record_id:", fiscal["record_id"])
        print("fiscal chain_hash:", fiscal["chain_hash"][:16], "...")
        print("fiscal previous:", fiscal["previous_chain_hash"])

        # Segundo registro para verificar el encadenamiento
        r2 = client.post("/api/v1/orders", json={
            "table_id": table_id, "staff_id": staff_id,
            "items": [{"name_snapshot": "Agua", "price_snapshot": 1.0, "quantity": 1}],
        })
        order2_id = r2.json()["id"]
        r = client.post(f"/api/v1/fiscal/{order2_id}/issue")
        fiscal2 = r.json()
        assert fiscal2["previous_chain_hash"] == fiscal["chain_hash"], "¡Cadena rota!"
        print("cadena verificada: previous == hash anterior ✓")

    # Verificar tablas creadas
    insp = inspect(engine)
    tables = sorted(insp.get_table_names())
    print("\nTablas creadas:", tables)
    assert "staff" in tables and "orders" in tables and "fiscal_records" in tables
    print("\n✅ TODO OK")


if __name__ == "__main__":
    main()
