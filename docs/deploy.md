# FastAPI服务（后端）部署
## 部署环境要求
- 操作系统 Linux（推荐Ubuntu 20.04+或 Centos7/8）
- Python 3.12+
- 依赖项（见`pyproject.toml`）
- 数据库/缓存（MySQL、PostgreSQL或Redis等）
- Web服务器 Nginx（反向代理 & 静态文件服务）
- 应用服务器 Gunicorn + Uvicorn（ASGI 服务器）
- 进程管理 Systemd（或 Supervisor）
- 容器化（可选）Docker或Kubernetes


