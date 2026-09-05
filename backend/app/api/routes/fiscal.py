from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import hashlib
import json
from datetime import datetime, timezone

from ...db import get_db
from ...models.models import Order, FiscalRecord
from ...schemas.schemas import FiscalRecordOut

router = APIRouter()


def _canonical_json(payload: dict) -> str:
    """Serialización canónica (claves ordenadas) para el hash VeriFactu."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _chain_hash(previous_hash: str | None, payload_json: str) -> str:
    """Hash encadenado: SHA-256 del hash anterior + payload canónico."""
    data = (previous_hash or "") + payload_json
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@router.get("", response_model=List[FiscalRecordOut])
def list_fiscal_records(db: Session = Depends(get_db)):
    return db.query(FiscalRecord).order_by(FiscalRecord.issued_at.desc()).all()


@router.post("/{order_id}/issue", response_model=FiscalRecordOut, status_code=status.HTTP_201_CREATED)
def issue_fiscal_record(order_id: UUID, db: Session = Depends(get_db)):
    """Emite un registro de facturación (tique) para una comanda cerrada.

    Genera el hash encadenado VeriFactu: el hash del registro anterior
    se concatena con el payload canónico de este registro y se aplica SHA-256.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Comanda no encontrada")

    # El registro anterior en la cadena (último emitido)
    last = (
        db.query(FiscalRecord)
        .order_by(FiscalRecord.issued_at.desc())
        .first()
    )
    previous_hash = last.chain_hash if last else None

    # Payload canónico del tique
    payload = {
        "order_id": str(order.id),
        "total_amount": str(order.total_amount),
        "discount_amount": str(order.discount_amount),
        "order_type": order.order_type,
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }
    payload_json = _canonical_json(payload)

    record_id = f"CMD-{order.id.hex[:12].upper()}"
    chain_hash = _chain_hash(previous_hash, payload_json)

    record = FiscalRecord(
        order_id=order.id,
        record_id=record_id,
        chain_hash=chain_hash,
        previous_chain_hash=previous_hash,
        payload_json=payload,
        record_type="alta",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=FiscalRecordOut)
def get_fiscal_record(record_id: UUID, db: Session = Depends(get_db)):
    record = db.get(FiscalRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro fiscal no encontrado")
    return record
