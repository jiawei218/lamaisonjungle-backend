# 定义API返回模型

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PlantBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    category: str = Field(
        min_length=1,
        max_length=100,
    )

    is_special_offer: bool = False
    price: int = Field(ge=0)
    water: int = Field(ge=1, le=3)
    light: int = Field(ge=1, le=3)
    cover: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_chinese_name(cls, value: str) -> str:
        normalized_name = value.strip()

        if not re.fullmatch(
            r"[\u4e00-\u9fff0-9（）()]+",
            normalized_name,
        ):
            raise ValueError("产品名称只能包含中文、数字和括号")

        return normalized_name


class PlantCreate(PlantBase):
    pass


class PlantRead(PlantBase):
    id: int
    code: str
    name: str
    category: str

    isSpecialOffer:bool = Field(
        validation_alias="is_special_offer"
    )
    price: int
    water: int
    light: int
    cover: str
#允许 Pydantic 直接读取 SQLAlchemy 对象
    model_config = ConfigDict(from_attributes=True)