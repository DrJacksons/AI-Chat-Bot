import multiprocessing

bind = "127.0.0.1:8000"  # 仅监听本地，由 Nginx 代理
workers = multiprocessing.cpu_count() * 2 + 1  # 推荐 worker 数量
worker_class = "uvicorn.workers.UvicornWorker"  # 使用 Uvicorn 的 worker
timeout = 120
keepalive = 5
accesslog = "./logs/gunicorn_access.log"
errorlog = "./logs/gunicorn_error.log"
loglevel = "info"
