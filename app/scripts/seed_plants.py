#初始化数据脚本

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.plant import Plant


PLANTS = [
    {
        "name": "龟背竹",
        "category": "经典植物",
        "is_special_offer": True,
        "price": 8,
        "water": 3,
        "light": 2,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "琴叶榕",
        "category": "经典植物",
        "is_special_offer": False,
        "price": 12,
        "water": 2,
        "light": 3,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "银斑葛",
        "category": "经典植物",
        "is_special_offer": True,
        "price": 3,
        "water": 2,
        "light": 1,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "丝兰",
        "category": "经典植物",
        "is_special_offer": True,
        "price": 10,
        "water": 1,
        "light": 3,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "橄榄树",
        "category": "户外植物",
        "is_special_offer": False,
        "price": 18,
        "water": 1,
        "light": 1,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "天竺葵",
        "category": "户外植物",
        "is_special_offer": False,
        "price": 9,
        "water": 2,
        "light": 3,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "罗勒",
        "category": "户外植物",
        "is_special_offer": True,
        "price": 5,
        "water": 2,
        "light": 2,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "芦荟",
        "category": "多肉植物",
        "is_special_offer": False,
        "price": 25,
        "water": 1,
        "light": 1,
        "cover": "/static/images/monstera.jpg",
    },
    {
        "name": "生石花",
        "category": "多肉植物",
        "is_special_offer": True,
        "price": 11,
        "water": 3,
        "light": 1,
        "cover": "/static/images/monstera.jpg",
    },
]


def seed_plants() -> None:
    with SessionLocal() as db:
        for plant_data in PLANTS:
            statement = select(Plant).where(
                Plant.name == plant_data["name"]
            )
            existing_plant = db.scalar(statement)

            if existing_plant is None:
                db.add(Plant(**plant_data))
            else:
                for field, value in plant_data.items():
                    setattr(existing_plant, field, value)

        db.commit()

    print(f"成功同步 {len(PLANTS)} 条植物数据")


if __name__ == "__main__":
    seed_plants()