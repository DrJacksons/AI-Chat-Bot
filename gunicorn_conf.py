# gunicorn_config.py
import os

wsgi_app = "flask_demo:app"
# Server Socket
# 服务器绑定地址和端口
bind = "0.0.0.0:8090"

# 工作进程数量
# 建议设置为 CPU 核心数 * 2 + 1
workers = 2
# 工作进程类型
worker_class = "gevent"
# 工作进程连接数
worker_connections = 1000
# 超时设置
timeout = 300
keepalive = 5
# 最大请求数，防止内存泄漏
max_requests = 1000
max_requests_jitter = 100

# PID文件
pidfile = "gunicorn.pid"

# 日志级别
loglevel = "info"
# 访问日志和错误日志
accesslog = True
errorlog = True

# 日志格式（如果启用Gunicorn日志）
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 开发模式设置
reload = False  # 生产环境设置为False
reload_extra_files = []

# 临时目录
tmp_upload_dir = None

# Hooks
def post_fork(server, worker):
   server.log.info("Worker spawned (pid: %s)", worker.pid)
def pre_fork(server, worker):
   pass
def pre_exec(server):
   server.log.info("Forked child, re-executing.")
def when_ready(server):
   server.log.info("Server is ready. Spawning workers")
def worker_int(worker):
   worker.log.info("worker received INT or QUIT signal")