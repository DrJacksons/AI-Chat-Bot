from server.app.models import Connector, ConnectorType, Dataset, DatasetSpace
from server.core.repository import BaseRepository
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional


class DatasetRepository(BaseRepository[Dataset]):
    """
    Dataset repository provides all the database operations for the Dataset model.
    """

    async def create_dataset(
        self,
        user_id: str,
        name: str,
        connector_type: ConnectorType,
        config,
        head: dict,
        description: str = "",
        field_descriptions: List[dict] = [{}],
        filterable_columns: Optional[List[str]] = None,
    ):
        connector = Connector(type=connector_type.value, config=config, user_id=user_id)
        self.session.add(connector)
        await self.session.flush()

        dataset = Dataset(
            name=name,
            table_name=name,
            head=head,
            user_id=user_id,
            connector_id=connector.id,
            description=description,
            field_descriptions={"columns": field_descriptions},
            filterable_columns={"columns": filterable_columns},
        )

        self.session.add(dataset)
        await self.session.flush()
        return dataset


    async def get_all_by_workspace_id(self, workspace_id: UUID):
        result = await self.session.execute(
            select(Dataset).join(DatasetSpace).where(DatasetSpace.workspace_id == workspace_id)
        )
        datasets = result.scalars().all()
        return datasets
    

    async def update_dataset(self, dataset):
        self.session.add(dataset)
        await self.session.commit()
        await self.session.refresh(dataset)

        return dataset


    async def get_user_datasets(self, user_id: int, connector_type: ConnectorType = None):
        if connector_type:
            result = await self.session.execute(
                select(Dataset)
                .options(
                    joinedload(Dataset.connector)
                )
                .where(
                    Dataset.user_id == user_id,
                    Connector.type == connector_type.value,
                )
                .order_by(Dataset.created_at.desc())
            )
        else:
            result = await self.session.execute(
                select(Dataset)
                .options(
                    joinedload(Dataset.connector)
                )
                .where(Dataset.user_id == user_id)
                .order_by(Dataset.created_at.desc())
            )
        return result.unique().scalars().all()
