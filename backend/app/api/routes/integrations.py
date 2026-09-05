from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional

from ...db import get_db
from ...models.models import Reservation
from ...schemas.schemas import ReservationCreate, ReservationOut
from ...config import settings

router = APIRouter()


def _check_api_key(x_api_key: Optional[str] = Header(None)):
    """Autenticación por API key para sistemas externos (Ariadna)."""
    if not settings.API_KEY:
        # Sin API key configurada, se permite (modo desarrollo)
        return
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida")


@router.post(
    "/reservations",
    response_model=ReservationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_check_api_key)],
)
def create_reservation_from_ariadna(payload: ReservationCreate, db: Session = Depends(get_db)):
    """Recibe una reserva creada por Ariadna (teléfono, email, WhatsApp, Telegram...).

    Idempotente: si ya existe una reserva con el mismo `external_id` y `source`,
    se devuelve la existente en lugar de duplicarla.
    """
    # Idempotencia por external_id + source
    if payload.external_id:
        existing = (
            db.query(Reservation)
            .filter(
                Reservation.external_id == payload.external_id,
                Reservation.source == payload.source,
            )
            .first()
        )
        if existing:
            return existing

    data = payload.model_dump()
    # Forzar que la reserva quede marcada como creada por Ariadna
    data["created_by"] = "ariadna"
    if not data.get("source") or data["source"] == "manual":
        data["source"] = "ariadna"

    res = Reservation(**data)
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.get(
    "/reservations",
    response_model=list[ReservationOut],
    dependencies=[Depends(_check_api_key)],
)
def list_reservations_for_ariadna(
    source: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista reservas para que Ariadna pueda consultar el estado de la sala."""
    q = db.query(Reservation)
    if source:
        q = q.filter(Reservation.source == source)
    if status:
        q = q.filter(Reservation.status == status)
    return q.order_by(Reservation.reservation_date.desc()).all()
