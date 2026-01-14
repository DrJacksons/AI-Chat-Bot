from contextvars import ContextVar, Token
from typing import Union
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.sql.expression import Delete, Insert, Update
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from server.setting import config


session_context: ContextVar[str] = ContextVar("session_context")

def get_session_context() -> str:
    return session_context.get()

def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)

def reset_session_context(context: Token) -> None:
    session_context.reset(context)

# 定义“写”数据库引擎和“读”数据库引擎（读写分离）
if config.DATABASE_SCHEMA:
    engines = {
        "writer": create_async_engine(
            config.DATABASE_URL,
            pool_recycle=3600,
            echo=bool(config.SHOW_SQL_ALCHEMY_QUERIES),
            connect_args={"server_settings": {"search_path": config.DATABASE_SCHEMA}},
        ),
        "reader": create_async_engine(
            config.DATABASE_URL,
            pool_recycle=3600,
            echo=bool(config.SHOW_SQL_ALCHEMY_QUERIES),
            connect_args={"server_settings": {"search_path": config.DATABASE_SCHEMA}},
        ),
    }
else:
    engines = {
        "writer": create_async_engine(config.DATABASE_URL, pool_recycle=3600, echo=bool(config.SHOW_SQL_ALCHEMY_QUERIES)),
        "reader": create_async_engine(config.DATABASE_URL, pool_recycle=3600, echo=bool(config.SHOW_SQL_ALCHEMY_QUERIES)),
    }

class RoutingSession(Session):
    # 查询类操作走只读连接，写入类操作走写连接
    def get_bind(self, mapper=None, clause=None, **kwargs):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        return engines["reader"].sync_engine

async_session_factory = sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)

# scoped_session-->线程安全的session
session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)


async def get_session():
    """
    获取数据库会话。
    可用于依赖注入。

    :return: The database session.
    """
    try:
        yield session
    finally:
        await session.close()


# 定义数据库模型的基类
if config.DATABASE_SCHEMA:
    print(f"Using schema: {config.DATABASE_SCHEMA}")
    from sqlalchemy import MetaData
    metadata = MetaData(schema=config.DATABASE_SCHEMA)
    Base = declarative_base(metadata=metadata)
else:
    Base = declarative_base()
