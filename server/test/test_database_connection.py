import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from server.core.database.session import engines


@pytest.mark.asyncio
async def test_database_writer_connection():
    engine: AsyncEngine = engines["writer"]
    async with engine.connect() as connection:
        result = await connection.execute("SELECT 1")
        value = result.scalar_one()
        assert value == 1

