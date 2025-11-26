from typing import Generic, Type, TypeVar

from server.core.database import Base, Propagation, Transactional
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
