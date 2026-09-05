from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...db import get_db
from ...models.models import Reservation
from ...schemas.schemas import ReservationCreate, ReservationOut

router = APIRouter()


@router.get("", response_model=List[ReservationOut])
def list_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.reservation_date.desc()).all()


@router.post("", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    res = Reservation(**payload.model_dump())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


@router.get("/{reservation_id}", response_model=ReservationOut)
def get_reservation(reservation_id: UUID, db: Session = Depends(get_db)):
    res = db.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return res


@router.patch("/{reservation_id}", response_model=ReservationOut)
def update_reservation(reservation_id: UUID, payload: ReservationCreate, db: Session = Depends(get_db)):
    res = db.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    for key, value in payload.model_dump().items():
        setattr(res, key, value)
    db.commit()
    db.refresh(res)
    return res


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(reservation_id: UUID, db: Session = Depends(get_db)):
    res = db.get(Reservation, reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(res)
    db.commit()
