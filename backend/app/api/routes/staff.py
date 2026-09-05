from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...db import get_db
from ...models.models import Staff
from ...schemas.schemas import StaffCreate, StaffOut

router = APIRouter()


@router.get("", response_model=List[StaffOut])
def list_staff(db: Session = Depends(get_db)):
    return db.query(Staff).order_by(Staff.full_name).all()


@router.post("", response_model=StaffOut, status_code=status.HTTP_201_CREATED)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db)):
    staff = Staff(**payload.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.get("/{staff_id}", response_model=StaffOut)
def get_staff(staff_id: UUID, db: Session = Depends(get_db)):
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff no encontrado")
    return staff


@router.patch("/{staff_id}", response_model=StaffOut)
def update_staff(staff_id: UUID, payload: StaffCreate, db: Session = Depends(get_db)):
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff no encontrado")
    for key, value in payload.model_dump().items():
        setattr(staff, key, value)
    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: UUID, db: Session = Depends(get_db)):
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff no encontrado")
    db.delete(staff)
    db.commit()
