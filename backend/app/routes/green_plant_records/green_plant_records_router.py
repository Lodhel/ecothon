import datetime
import json
import tempfile
from typing import Optional

from fastapi import Depends, UploadFile, File, Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models import GreenPlantRecord, GreenPlantFiles
from backend.app.orm_sender.manager_sqlalchemy import ManagerSQLAlchemy
from backend.app.process_image import ClientProcessingImage
from backend.app.routes.green_plant_records.create_xlsx import ManagerXLSX
from backend.app.routes.green_plant_records.models import GreenPlantResponseModel, GreenPlantRecordModel
from backend.app.routes.main import MainRouterMIXIN

from io import BytesIO
from openpyxl import Workbook


green_plant_records_router = InferringRouter()
green_plant_records_tags = ["green_plant_records_router"]


@cbv(green_plant_records_router)
class GreenPlantRouter(MainRouterMIXIN, ManagerSQLAlchemy):
    client_process_image = ClientProcessingImage
    manager_xlsx = ManagerXLSX

    @green_plant_records_router.get(
        "/records/",
        name="get_green_plant_records",
        response_model=GreenPlantResponseModel,
        description="Выгрузка перечетной ведомости в формате JSON или XLSX",
        tags=green_plant_records_tags,
    )
    async def get(
        self,
        request: Request,
        green_plant_record_id: int = Query(None, description="id объекта"),
        response_format: str = Query("json", enum=["json", "xlsx"], description="Формат ответа"),
        name_filter: Optional[str] = Query(None, description="Фильтр по наименованию пород"),
    ):
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            query = select(GreenPlantRecord)
            if name_filter:
                query = query.where(GreenPlantRecord.name == name_filter)
            if green_plant_record_id:
                query = query.where(GreenPlantRecord.id == green_plant_record_id)

            result = await session.execute(query)
            records = result.scalars().all()

            if response_format == "json":
                return GreenPlantResponseModel(
                    status="success",
                    data=[
                        GreenPlantRecordModel(
                            row_number=record.row_number,
                            name=record.name,
                            tree_count=record.tree_count,
                            shrub_count=record.shrub_count,
                            width=record.width,
                            height=record.height,
                            condition_description=record.condition_description,
                        )
                        for record in records
                    ],
                )

            elif response_format == "xlsx":
                data = [
                    [
                        record.row_number,
                        record.name,
                        f"{record.tree_count or 0} / {record.shrub_count or 0}",
                        record.width,
                        record.height,
                        record.condition_description,
                    ]
                    for record in records
                ]
                wb: Workbook = self.manager_xlsx().create(data)

                file_stream = BytesIO()
                wb.save(file_stream)
                file_stream.seek(0)
                file_name: str = f'ПЕРЕЧЕТНАЯ_ВЕДОМОСТЬ_{datetime.date.today().month}-{datetime.date.today().year}'
                return StreamingResponse(
                    file_stream,
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={
                        "Content-Disposition": f"attachment; filename*=utf-8''{file_name}.xlsx"
                    },
                )

    @green_plant_records_router.post(
        "/process-image/",
        name="process_image",
        description="Обработка изображения перечетной ведомости",
        tags=green_plant_records_tags,
    )
    async def post(self, image: UploadFile = File(...)):
        results: list = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(await image.read())
            temp_file_path = temp_file.name

        client_process_image = self.client_process_image()
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            async for data_tree in client_process_image.make_generator_tree_data_by_image(temp_file_path):
                is_shrub = data_tree['tree_type'].lower() == 'куст'
                results.append(data_tree)

                existing_record = await session.execute(
                    select(GreenPlantRecord).where(
                        GreenPlantRecord.row_number == data_tree['class_id'],
                        GreenPlantRecord.name == data_tree['tree_type']
                    )
                )
                existing_record = existing_record.scalars().first()

                if existing_record:
                    if is_shrub:
                        existing_record.shrub_count += 1
                    else:
                        existing_record.tree_count += 1
                else:
                    green_plant_records = GreenPlantRecord(
                        row_number=data_tree['class_id'],
                        name=data_tree['tree_type'],
                        tree_count=1 if not is_shrub else 0,
                        shrub_count=1 if is_shrub else 0,
                        width=str(data_tree['width']),
                        height=str(data_tree['height']),
                        condition_description='удовлетворит.',
                    )
                    session.add(green_plant_records)

            if results:
                green_plant_files = GreenPlantFiles(
                    data=results,
                    file_path=temp_file_path
                )
                session.add(green_plant_files)

                await session.commit()

        data = self.get_data(results)
        return data
