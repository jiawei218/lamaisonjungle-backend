import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Plant


@pytest.fixture
def plant(db_session: Session) -> Plant:
    model = Plant(
        name="测试植物",
        category="测试分类",
        is_special_offer=True,
        price=10,
        water=2,
        light=3,
        cover="/static/images/test.jpg",
    )

    db_session.add(model)
    db_session.flush()
    db_session.refresh(model)

    return model


def test_read_plants(
    client: TestClient,
    plant: Plant,
) -> None:
    response = client.get("/api/plants")

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["code"] == plant.code
    assert body[0]["name"] == "测试植物"
    assert body[0]["isSpecialOffer"] is True


def test_find_plant_by_code(
    client: TestClient,
    plant: Plant,
) -> None:
    response = client.get(f"/api/plants/{plant.code}")

    assert response.status_code == 200
    assert response.json()["code"] == plant.code


def test_find_unknown_plant_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/api/plants/not-exists")

    assert response.status_code == 404
    assert response.json() == {"detail": "植物不存在"}
