from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_reservations():
    # Act
    response = client.get("/reservations/")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) > 1
    assert response.json()[0]["id"] is not None
    assert response.json()[0]["name"] is not None
    assert response.json()[0]["email"] is not None
    assert response.json()[0]["date"] is not None
    assert response.json()[0]["status"] is not None
    assert response.json()[0]["message"] is not None
    assert response.json()[0]["created_at"] is not None
    assert response.json()[0]["updated_at"] is not None
    assert response.json()[1]["id"] is not None
    assert response.json()[1]["name"] is not None
    assert response.json()[1]["email"] is not None
    assert response.json()[1]["date"] is not None
    assert response.json()[1]["status"] is not None
    assert response.json()[1]["message"] is not None
    assert response.json()[1]["created_at"] is not None
    assert response.json()[1]["updated_at"] is not None


def test_get_reservation():
    # Act
    response = client.get("/reservations/2")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == 2
    assert response.json()["name"] == "test"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["date"] == "2027-01-01T10:00:00"
    assert response.json()["status"] is not None
    assert response.json()["message"] == "test message"
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is not None


def test_create_reservation():
    # Act
    response = client.post(
        "/reservations/",
        json={
            "id": 1,
            "name": "test",
            "email": "test@example.com",
            "date": "2027-01-01 10:00:00",
            "status": "pending",
            "message": "test message",
        },
    )

    # Assert
    assert response.status_code == 201
    assert response.json()["id"] is not None
    assert response.json()["name"] == "test"
    assert response.json()["email"] == "test@example.com"
    assert response.json()["date"] == "2027-01-01T10:00:00"
    assert response.json()["status"] == "pending"
    assert response.json()["message"] == "test message"
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is not None


def test_update_reservation():
    # Act
    response = client.put(
        "/reservations/1",
        json={
            "name": "test二郎",
            "email": "test3_mail_update@test.com",
            "date": "2028-01-01 10:00:00",
            "status": "confirmed",
            "message": "テスト予約3updateです",
        },
    )
    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "test二郎"
    assert response.json()["email"] == "test3_mail_update@test.com"
    assert response.json()["date"] == "2028-01-01T10:00:00"
    assert response.json()["status"] == "confirmed"
    assert response.json()["message"] == "テスト予約3updateです"
    assert response.json()["created_at"] is not None
    assert response.json()["updated_at"] is not None


def test_delete_reservation():
    # Act
    response = client.delete("/reservations/1")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "予約が削除されました"
