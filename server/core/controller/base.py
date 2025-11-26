from uuid import UUID
from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel

from server.core.database import Base, Propagation, Transactional
from server.core.exceptions import NotFoundException
from server.core.repository import BaseRepository

# 定义Controller的泛型类型变量
ModelType = TypeVar("ModelType", bound=Base)


class BaseController(Generic[ModelType]):
    """Data Controller base class. 泛型类"""

    def __init__(self, model: Type[ModelType], repository: BaseRepository) -> None:
        self.model_class = model
        self.repository = repository

    async def get_by_id(self, id_: int, join_: set[str] | None = None) -> ModelType:
        """
        根据ID获取模型实例。

        :param id_: 模型实例的ID。
        :param join_: 关联查询的关系名称集合。
        :return: 模型实例。
        """
        db_obj = await self.repository.get_by(
            field="id", value=id_, join_=join_, unique=True
        )
        if not db_obj:
            raise NotFoundException(f"{self.model_class.__tablename__.title()} with id: {id_} does not exist")

        return db_obj

    async def get_by_uuid(self, uuid: UUID, join_: set[str] | None = None) -> ModelType:
        """
        Returns the model instance matching the uuid.

        :param uuid: The uuid to match.
        :param join_: The joins to make.
        :return: The model instance.
        """

        db_obj = await self.repository.get_by(
            field="uuid", value=uuid, join_=join_, unique=True
        )
        if not db_obj:
            raise NotFoundException(
                f"{self.model_class.__tablename__.title()} with id: {uuid} does not exist"
            )
        return db_obj

    async def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """
        Returns a list of records based on pagination params.

        :param skip: The number of records to skip.
        :param limit: The number of records to return.
        :param join_: The joins to make.
        :return: A list of records.
        """

        response = await self.repository.get_all(skip, limit, join_)
        return response

    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """
        Creates a new Object in the DB.

        :param attributes: The attributes to create the object with.
        :return: The created object.
        """
        create = await self.repository.create(attributes)
        return create

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete(self, model: ModelType) -> bool:
        """
        Deletes the Object from the DB.

        :param model: The model to delete.
        :return: True if the object was deleted, False otherwise.
        """
        delete = await self.repository.delete(model)
        return delete

    @staticmethod
    def extract_attributes_from_schema(
        schema: BaseModel, excludes: set = None
    ) -> dict[str, Any]:
        """
        Extracts the attributes from the schema.

        :param schema: The schema to extract the attributes from.
        :param excludes: The attributes to exclude.
        :return: The attributes.
        """

        return schema.dict(exclude=excludes, exclude_unset=True)
