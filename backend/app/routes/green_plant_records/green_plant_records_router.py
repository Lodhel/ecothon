import tempfile

from fastapi import Depends, UploadFile, File
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models import GreenPlantRecord
from backend.app.orm_sender.manager_sqlalchemy import ManagerSQLAlchemy
from backend.app.process_image import ClientProcessingImage
from backend.app.routes.green_plant_records.models import GreenPlantResponseModel, GreenPlantRecordModel, \
    GreenPlantImageUploadResponseModel
from backend.app.routes.main import MainRouterMIXIN

from io import BytesIO
from openpyxl import Workbook


green_plant_records_router = InferringRouter()
green_plant_records_tags = ["green_plant_records_router"]


@cbv(green_plant_records_router)
class GreenPlantRouter(MainRouterMIXIN, ManagerSQLAlchemy):
    client_process_image = ClientProcessingImage

    # @green_plant_records_router.get(
    #     "/records/",
    #     name="get_green_plant_records",
    #     response_model=GreenPlantResponseModel,
    #     description="Выгрузка перечетной ведомости в формате JSON или XLSX",
    #     tags=["Green Plant Records"],
    # )
    # async def get(
    #     self,
    #     request: Request,
    #     response_format: str = Query("json", enum=["json", "xlsx"], description="Формат ответа"),
    #     name_filter: Optional[str] = Query(None, description="Фильтр по наименованию пород"),
    # ):
    #     """
    #     Get green plant records in JSON or XLSX format based on query parameters.
    #     """
    #     async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
    #         query = session.query(GreenPlantRecord)
    #         if name_filter:
    #             query = query.filter(GreenPlantRecord.name == name_filter)
    #
    #         records = await query.all()
    #
    #         if response_format == "json":
    #             return GreenPlantResponseModel(
    #                 status="success",
    #                 data=[
    #                     GreenPlantRecordModel(
    #                         row_number=record.row_number,
    #                         name=record.name,
    #                         tree_count=record.tree_count,
    #                         shrub_count=record.shrub_count,
    #                         diameter_cm=record.diameter_cm,
    #                         height_m=record.height_m,
    #                         condition_description=record.condition_description,
    #                     )
    #                     for record in records
    #                 ],
    #             )
    #
    #         elif response_format == "xlsx":
    #             wb = Workbook()
    #             ws = wb.active
    #             ws.title = "Filtered Data"
    #             headers = [
    #                 "№ п/п", "Наименование пород", "Кол-во в шт.", "Диаметр, Р, см",
    #                 "Высота, м", "Характеристика состояния зеленых насаждений",
    #             ]
    #             ws.append(headers)
    #             for record in records:
    #                 ws.append(
    #                     [
    #                         record.row_number,
    #                         record.name,
    #                         f"{record.tree_count or 0} / {record.shrub_count or 0}",
    #                         record.diameter_cm,
    #                         record.height_m,
    #                         record.condition_description,
    #                     ]
    #                 )
    #             file_stream = BytesIO()
    #             wb.save(file_stream)
    #             file_stream.seek(0)
    #             return StreamingResponse(
    #                 file_stream,
    #                 media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    #                 headers={"Content-Disposition": "attachment; filename=filtered_data.xlsx"},
    #             )

    @green_plant_records_router.post(
        "/process-image/",
        name="process_image",
        # response_model=GreenPlantImageUploadResponseModel,
        description="Обработка изображения перечетной ведомости",
        tags=["Green Plant Records"],
    )
    async def post(self, image: UploadFile = File(...)):
        results: list = []
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(await image.read())
            temp_file_path = temp_file.name

        client_process_image = self.client_process_image()
        async for data_tree in client_process_image.make_generator_tree_data_by_image(temp_file_path):
            # {'x_point': 55.5, 'y_point': 250.0, 'width': 103.0, 'height': 56.0, 'confidence': 0.6297429800033569, 'tree_type': 'Ель'}
            results.append(data_tree)
            GreenPlantRecordModel(
                **{
                    'row_number': data_tree['class_id'],
                    'name': data_tree['tree_type'],
                    'tree_count': 1,
                    'shrub_count': 1,
                    'width': data_tree['width'],
                    'height': data_tree['height'],
                    'condition_description': 'удовлетворит.'
                }
            )

        # extracted_data = [
        #     {
        #         "row_number": "23a",
        #         "name": "кустарник разный",
        #         "tree_count": 1,
        #         "shrub_count": 18,
        #         "diameter_cm": "до 2",
        #         "height_m": "12",
        #         "condition_description": "барбарис, стрижены",
        #     },
        #     {
        #         "row_number": "24",
        #         "name": "Липа",
        #         "tree_count": 1,
        #         "shrub_count": 0,
        #         "diameter_cm": "26",
        #         "height_m": "12",
        #         "condition_description": "удовлетворит.",
        #     },
        # ]

        data = self.get_data(results)
        return data
