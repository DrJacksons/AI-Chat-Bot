from typing import List
from server.app.models import Logs
from server.app.schemas.responses.logs import LogResponse
from server.core.repository import BaseRepository
from server.core.database import Propagation, Transactional
from sqlalchemy import func
from sqlalchemy.future import select


class LogsRepository(BaseRepository[Logs]):
    
    @Transactional(propagation=Propagation.REQUIRED)
    async def add_log(
        self, user_id: str, json_log: str, query: str, 
        success: bool = True, execution_time: float = 0.0,
        exhausted_tokens: int = 0
    ):  
        new_log = Logs(
            user_id=user_id,
            json_log=json_log,
            query=query,
            success=success,
            execution_time=execution_time,
            exhausted_tokens=exhausted_tokens
        )
        self.session.add(new_log)
        return new_log

    async def get_user_logs(self, user_id: str, skip: int = 0, limit: int = 10) -> List[LogResponse]:
        query = select(Logs).where(Logs.user_id == user_id).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_logs_count(self, user_id: str) -> int:
        query = select(func.count(Logs.id)).where(Logs.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_tokens_count(self, user_id: str) -> int:
        query = select(func.sum(Logs.exhausted_tokens)).where(Logs.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one()
