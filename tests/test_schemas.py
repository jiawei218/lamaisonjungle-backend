import pytest
from pydantic import ValidationError

from app.schemas.plant import PlantCreate


def make_plant(**overrides: object) -> PlantCreate:
    data: dict[str, object] = {
        "name": "龟背竹",
        "category": "经典植物",
        "price": 10,
        "water": 2,
        "light": 3,
        "cover": "/static/images/monstera.jpg",
    }
    data.update(overrides)
    return PlantCreate.model_validate(data)


def test_plant_name_is_trimmed() -> None:
    plant = make_plant(name="  龟背竹  ")

    assert plant.name == "龟背竹"


def test_plant_name_rejects_english() -> None:
    with pytest.raises(ValidationError):
        make_plant(name="Monstera")


@pytest.mark.parametrize("water", [0, 4])
def test_water_must_be_between_1_and_3(water: int) -> None:
    with pytest.raises(ValidationError):
        make_plant(water=water)


def test_price_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        make_plant(price=-1)
