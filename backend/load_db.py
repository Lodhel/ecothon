import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession


from loguru import logger

from backend.app.models import GeoData, GreenPlanting, PlantingStatus, Entry
from backend.app.orm_sender.manager_sqlalchemy import ManagerSQLAlchemy


class LoadDBManager(ManagerSQLAlchemy):
    file_path = 'mos_data.json'

    async def run(self, from_file: bool = True):
        data = self.load_data_from_file()   # TODO для автоматизации обновления данных логика будет расширена
        async with AsyncSession(self.engine, autoflush=False, expire_on_commit=False) as session:
            for row in data:
                await self.execute(session, row)

            await session.commit()

    def load_data_from_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data

    async def execute(self, session: AsyncSession, row: dict):
        logger.info(row)
        cells = row['Cells']
        geo_data = await self.create_instance_geo_data(session, cells)
        green_planting = await self.create_instance_green_planting(session, cells, geo_data)
        await self.create_instances_planting_statuses(session, cells, green_planting)
        await self.create_instance_entry(session, row, green_planting)

    @staticmethod
    async def create_instance_geo_data(session: AsyncSession, cells: dict) -> GeoData:
        geo_data = GeoData(
            coordinates=cells['geoData']['coordinates']
        )
        session.add(geo_data)
        await session.flush()

        return geo_data

    @staticmethod
    async def create_instance_green_planting(session: AsyncSession, cells: dict, geo_data: GeoData) -> GreenPlanting:
        green_planting = GreenPlanting(
            period=cells['Period'],
            global_id=cells['global_id'],
            adm_area=cells['AdmArea'],
            district=cells['District'],
            address=cells['Address'],
            geo_data_id=geo_data.id
        )
        session.add(green_planting)
        await session.flush()

        return green_planting

    @classmethod
    async def create_instances_planting_statuses(cls, session: AsyncSession, cells: dict, green_planting: GreenPlanting) -> None:
        for status in cells['Conditions']:
            await cls._create_instance_planting_status(session, status, green_planting)

    @staticmethod
    async def create_instance_entry(session: AsyncSession, row: dict, green_planting: GreenPlanting) -> None:
        entry = Entry(
            global_id=row['global_id'],
            number=row['Number'],
            green_planting_id=green_planting.id
        )
        session.add(entry)

    @staticmethod
    async def _create_instance_planting_status(session: AsyncSession, status: dict, green_planting: GreenPlanting):
        planting_status = PlantingStatus(
            status_name=status['ConditionName'],
            percent_value=status['PercentValue'],
            global_id=status['global_id'],
            is_deleted=status['is_deleted'],
            green_planting_id=green_planting.id
        )
        session.add(planting_status)


if __name__ == "__main__":
    load_db_manager = LoadDBManager()
    asyncio.run(load_db_manager.run())
