from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from models.reservation import Reservation, ReservationCreate
from db.database import get_session

router = APIRouter()


@router.get("/")
def get_reservations():
    return {"message": "Hello, World!"}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: ReservationCreate, session: Session = Depends(get_session)
):
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
