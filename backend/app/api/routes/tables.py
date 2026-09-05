from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...db import get_db
from ...models.models import Area, Table
from ...schemas.schemas import AreaCreate, AreaOut, TableCreate, TableUpdate, TableOut

router = APIRouter()


# ============================================================
# ÁREAS
# ============================================================
@router.get("/areas", response_model=List[AreaOut])
def list_areas(db: Session = Depends(get_db)):
    return db.query(Area).order_by(Area.name).all()


@router.post("/areas", response_model=AreaOut, status_code=status.HTTP_201_CREATED)
def create_area(payload: AreaCreate, db: Session = Depends(get_db)):
    area = Area(**payload.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


# ============================================================
# MESAS
# ============================================================
@router.get("", response_model=List[TableOut])
def list_tables(db: Session = Depends(get_db)):
    return db.query(Table).order_by(Table.number).all()


@router.post("", response_model=TableOut, status_code=status.HTTP_201_CREATED)
def create_table(payload: TableCreate, db: Session = Depends(get_db)):
    table = Table(**payload.model_dump())
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


@router.get("/{table_id}", response_model=TableOut)
def get_table(table_id: UUID, db: Session = Depends(get_db)):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    return table


@router.patch("/{table_id}", response_model=TableOut)
def update_table(table_id: UUID, payload: TableUpdate, db: Session = Depends(get_db)):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(table, key, value)
    db.commit()
    db.refresh(table)
    return table


@router.delete("/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_table(table_id: UUID, db: Session = Depends(get_db)):
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Mesa no encontrada")
    db.delete(table)
    db.commit()
