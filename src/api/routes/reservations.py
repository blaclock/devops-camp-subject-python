from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from src.models.reservation import Reservation, ReservationCreate, ReservationUpdate
from src.db.database import get_session

router = APIRouter()


@router.get("/")
def get_reservations(session: Session = Depends(get_session)):
    reservations = session.exec(select(Reservation)).all()
    return reservations


@router.get("/{reservation_id}", status_code=status.HTTP_200_OK)
def get_reservation(reservation_id: int, session: Session = Depends(get_session)):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="予約が見つかりません")
    return reservation


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(reservation: ReservationCreate, session: Session = Depends(get_session)):
    db_reservation = Reservation(
        name=reservation.name,
        email=reservation.email,
        date=reservation.date,
        message=reservation.message,
    )
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)
    return db_reservation


@router.put("/{reservation_id}", status_code=status.HTTP_200_OK)
def update_reservation(
    reservation_id: int,
    reservation: ReservationUpdate,
    session: Session = Depends(get_session),
):
    db_reservation = session.get(Reservation, reservation_id)
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="予約が見つかりません")
    if reservation.name:
        db_reservation.name = reservation.name
    if reservation.email:
        db_reservation.email = reservation.email
    if reservation.date:
        db_reservation.date = reservation.date
    if reservation.message:
        db_reservation.message = reservation.message
    db_reservation.updated_at = datetime.now()
    session.add(db_reservation)
    session.commit()
    session.refresh(db_reservation)
    return db_reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
def delete_reservation(reservation_id: int, session: Session = Depends(get_session)):
    db_reservation = session.get(Reservation, reservation_id)
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="予約が見つかりません")
    session.delete(db_reservation)
    session.commit()
    return {"message": "予約が削除されました"}
