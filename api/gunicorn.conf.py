"""
Gunicorn 配置文件

用于生产环境启动
"""
import os
import multiprocessing

# 绑定地址和端口
bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"

# Worker 配置
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000

# 超时配置
timeout = 200
graceful_timeout = 30
keepalive = 5

# 日志配置
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程名称
proc_name = 'shadow-agents-api'

# 预加载应用
preload_app = True

# 启用线程
threads = 2

def on_starting(server):
    """服务启动时的回调"""
    print("Gunicorn server is starting...")

def when_ready(server):
    """服务就绪时的回调"""
    print("Gunicorn server is ready. Spawning workers...")

def on_exit(server):
    """服务退出时的回调"""
    print("Gunicorn server is shutting down...")
