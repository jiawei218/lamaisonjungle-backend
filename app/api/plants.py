from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Plant
from app.schemas.plant import PlantRead

router = APIRouter(
    prefix="/api/plants",
    tags=["plants"],
)


@router.get("",response_model=list[PlantRead])
async def read_plants(
        #注入数据库session，无需前端调用，
        db: Session = Depends(get_db),
) -> list[Plant]:
    statement = select(Plant).order_by(Plant.id)
    plants = db.scalars(statement).all()

    return list(plants)



@router.get("/{plant_code}",response_model=PlantRead)
async def find_plant_by_code(
        plant_code: str,
        db:Session = Depends(get_db),
)-> Plant:
    statement = select(Plant).where(
        Plant.code == plant_code
    )
    plant = db.scalar(statement)

    if plant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="植物不存在",
        )
    return plant