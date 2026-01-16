#!/bin/bash
DIR=$(cd "$(dirname "$0")" && cd .. && pwd)
echo "进入项目目录"
echo $DIR

# 检查并终止当前问数服务的进程（gunicorn server.core.server:app）
echo "正在查找并终止当前问数服务进程..."
for pid in $(ps -ef | grep "gunicorn" | grep "server.core.server:app" | grep -v grep | awk '{print $2}'); do
    echo "终止问数服务进程，PID: $pid"
    kill -9 "$pid" 2>/dev/null
done
echo "当前问数服务进程已终止（如存在）"

echo "正在启动问数服务..."

# 检查并删除旧的gunicorn.pid文件
if [ -f "gunicorn.pid" ]; then
    echo "发现旧的gunicorn.pid文件，正在删除..."
    rm gunicorn.pid
fi

# 在后台启动服务，同时将输出重定向到日志文件和终端
gunicorn --config gunicorn_conf.py server.core.server:app >/dev/null 2>&1 &
SERVER_PID=$!

echo "等待 Web 服务启动并健康检测..."
until curl -f http://127.0.0.1:8000/monitoring/health >/dev/null 2>&1; do
    echo "服务尚未就绪，等待中..."
    sleep 3   
done

echo "服务已在后台启动，PID: $SERVER_PID"

# 检查服务是否正常启动
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "----------------------------------------"
    echo "✅ 服务启动成功！"
    echo "服务PID: $SERVER_PID"
    echo "如需查看完整日志，请运行: tail -f logs/app.log"
    echo "如需停止服务，请运行: kill $SERVER_PID"
else
    echo "----------------------------------------"
    echo "❌ 服务启动失败，请检查日志文件: $LOG_FILE"
fi

echo "脚本执行完成，终端已释放"