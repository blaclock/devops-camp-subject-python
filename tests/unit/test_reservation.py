from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from api.routes.reservations import get_reservation, create_reservation, update_reservation, delete_reservation

from models.reservation import Reservation, ReservationCreate, ReservationUpdate
from datetime import datetime


def test_get_reservation_unit():
    # Arrange
    mock_session = MagicMock()
    mock_session.get.return_value = Reservation(
        id=1,
        name="test",
        email="test@example.com",
        date="2027-01-01 10:00:00",
        message="test message",
    )

    # Act
    result = get_reservation(reservation_id=1, session=mock_session)

    # Assert
    assert result.id == 1
    assert result.name == "test"
    assert result.email == "test@example.com"
    assert result.date == "2027-01-01 10:00:00"
    assert result.message == "test message"

    mock_session.get.assert_called_once_with(Reservation, 1)


def test_get_reservation_not_found_raises_http_exception():
    # Arrange
    mock_session = MagicMock()
    mock_session.get.return_value = None
    # Act / Assert
    with pytest.raises(HTTPException) as exc:
        get_reservation(reservation_id=999, session=mock_session)
    assert exc.value.status_code == 404
    assert exc.value.detail == "予約が見つかりません"
    mock_session.get.assert_called_once_with(Reservation, 999)


def test_create_reservation():
    # Arrange
    mock_session = MagicMock()
    mock_session.add.return_value = Reservation(
        name="test",
        email="test@example.com",
        date=datetime(2026, 1, 1, 10, 0),
        message="test message",
    )
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    result = create_reservation(
        reservation=ReservationCreate(
            name="test", email="test@example.com", date=datetime(2026, 1, 1, 10, 0), message="test message"
        ),
        session=mock_session,
    )

    # Assert
    assert result.name == "test"
    assert result.email == "test@example.com"
    assert result.date == datetime(2026, 1, 1, 10, 0)
    assert result.message == "test message"
    mock_session.add.assert_called_once_with(
        Reservation(name="test", email="test@example.com", date=datetime(2026, 1, 1, 10, 0), message="test message")
    )
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_update_reservation():
    # Arrange
    mock_session = MagicMock()
    mock_session.get.return_value = Reservation(
        name="test2",
        email="test2@example.com",
        date=datetime(2026, 1, 1, 10, 0),
        message="test message",
    )
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    result = update_reservation(
        reservation_id=1,
        reservation=ReservationUpdate(
            name="test2", email="test2@example.com", date=datetime(2026, 1, 1, 10, 0), message="test message"
        ),
        session=mock_session,
    )

    # Assert
    assert result.name == "test2"
    assert result.email == "test2@example.com"
    assert result.date == datetime(2026, 1, 1, 10, 0)
    assert result.message == "test message"
    mock_session.get.assert_called_once_with(Reservation, 1)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


def test_delete_reservation():
    # Arrange
    mock_session = MagicMock()
    mock_session.get.return_value = Reservation(
        id=1,
        name="test",
        email="test@example.com",
        date="2027-01-01 10:00:00",
        message="test message",
    )
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    # Act
    result = delete_reservation(reservation_id=1, session=mock_session)

    # Assert
    assert result["message"] == "予約が削除されました"
    mock_session.get.assert_called_once_with(Reservation, 1)
    mock_session.commit.assert_called_once()
    # mock_session.refresh.assert_called_once()
