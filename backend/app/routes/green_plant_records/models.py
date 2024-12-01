from pydantic import BaseModel, Field
from fastapi import Query
from typing import Optional, List


class GreenPlantFilterModel(BaseModel):
    response_format: str = Query(
        "json",
        enum=["json", "xlsx"],
        description="Формат ответа: 'json' или 'xlsx'"
    )
    name_filter: Optional[str] = Query(
        None,
        description="Фильтр по наименованию пород"
    )


class GreenPlantRecordModel(BaseModel):
    row_number: str = Field(..., description="Номер строки в ведомости")
    name: str = Field(..., description="Наименование пород")
    tree_count: int = Field(..., description="Количество деревьев")
    shrub_count: int = Field(..., description="Количество кустарников")
    width: str = Field(..., description="Диаметр дерева/кустарника (в см)")
    height: str = Field(..., description="Высота дерева/кустарника (в м)")
    condition_description: str = Field(..., description="Характеристика состояния насаждений")


class GreenPlantResponseModel(BaseModel):
    status: str = Field(..., description="Статус операции (успех или ошибка)")
    data: Optional[List[GreenPlantRecordModel]] = Field(
        None, description="Список записей перечетной ведомости"
    )
    message: Optional[str] = Field(None, description="Сообщение об ошибке")


class GreenPlantImageUploadResponseModel(BaseModel):
    status: str = Field(..., description="Статус операции")
    data: List[dict] = Field(..., description="Извлеченные данные из изображения")
