import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from server.core.database.session import engines, Base
import server.app.models

async def run_stmt(stmt):
    engine = engines["writer"]
    try:
        async with engine.begin() as conn:
            await conn.execute(text(stmt))
            print(f"Executed: {stmt[:50]}...")
    except Exception as e:
        print(f"Failed: {stmt[:50]}... Error: {e}")

async def create_tables():
    engine = engines["writer"]
    try:
        async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
        print("create_all executed")
    except Exception as e:
        print(f"create_all failed: {e}")

async def fix_db():
    print("Creating tables...")
    await create_tables()

    print("Patching user table...")
    await run_stmt("ALTER TABLE \"user\" ADD COLUMN last_name VARCHAR(255)")
    await run_stmt("ALTER TABLE \"user\" ADD COLUMN first_name VARCHAR(255)")

    print("Patching role table...")
    await run_stmt("ALTER TABLE role ADD COLUMN workspace_id UUID")
    await run_stmt("ALTER TABLE role ADD COLUMN is_system_role BOOLEAN DEFAULT FALSE")
    await run_stmt("ALTER TABLE role ADD COLUMN created_at TIMESTAMP DEFAULT NOW()")

if __name__ == "__main__":
    asyncio.run(fix_db())
