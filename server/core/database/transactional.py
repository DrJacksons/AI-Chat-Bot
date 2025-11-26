from enum import Enum
from functools import wraps

from server.setting import config
from .session import session



class Propagation(Enum):
    REQUIRED = "required"
    REQUIRED_NEW = "required_new"


class Transactional:
    """
    事务装饰器，用于在函数执行时开启数据库事务。
    """
    def __init__(self, propagation: Propagation = Propagation.REQUIRED):
        self.propagation = propagation
    
    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwagrs):
            try:
                if self.propagation == Propagation.REQUIRED:
                    result = await self._run_required(
                        function,
                        args=args,
                        kwargs=kwagrs,
                    )
                elif self.propagation == Propagation.REQUIRED_NEW:
                    result = await self._run_required_new(
                        function,
                        args=args,
                        kwargs=kwagrs,
                    )
                else:
                    result = await self._run_required(
                        function,
                        args=args,
                        kwargs=kwagrs,
                    )
            except Exception as ex:
                await session.rollback()
                raise ex

            return result
        
        return decorator
    
    async def _run_required(self, function, args, kwargs):
        """
        REQUIRED 行为的事务提交
        """
        result = await function(*args, **kwargs)
        await session.commit()
        return result

    async def _run_required_new(self, function, args, kwargs):
        """
        REQUIRED_NEW 行为的事务提交
        """
        session.begin()
        result = await function(*args, **kwargs)
        await session.commit()
        return result
