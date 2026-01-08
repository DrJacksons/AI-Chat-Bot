# AI-Chat-Bot
Intelligent chatbot based on documents and structured data

# Usage
1. Clone the repository
```shell
git clone https://gitee.com/dong-jiakai/AI-Chat-Bot.git
```
2. Install the required dependencies
```shell
# 创建虚拟环境
uv venv .venv
# 激活虚拟环境
source .venv/bin/activate
# 同步安装依赖
uv sync
```
3. Run the chatbot script
```shell
python main.py
```
4. Database migration
使用 alembic 进行数据库迁移：
```shell
# 初始化alembic异步模板配置（生成 alembic.ini 和 migrations/ 目录）
alembic init -t async migrations
# 修改 alembic.ini 中的 sqlalchemy.url 为实际数据库连接字符串
sqlalchemy.url = postgresql+asyncpg://root:123456@127.0.0.1:5432/test
# 修改 migrations/env.py 中的 target_metadata 为实际数据库模型的元数据
from server.app.models import Base
target_metadata = Base.metadata
# 创建数据库迁移文件
alembic revision -m "create table"
# 数据库迁移
alembic upgrade head
```
