from functools import reduce
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from server.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Data Repository base class. 泛型类"""

    def __init__(self, model: Type[ModelType], db_session: AsyncSession) -> None:
        self.model_class = model
        self.session = db_session

    
