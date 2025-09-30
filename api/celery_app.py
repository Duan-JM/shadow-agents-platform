"""
Celery 入口文件

用于启动 Celery Worker 和 Beat
"""
import os
from celery import Celery
from app_factory import create_app

# 创建 Flask 应用
flask_app = create_app()

# 创建 Celery 实例
celery = Celery(
    flask_app.import_name,
    broker=flask_app.config['CELERY_BROKER_URL'],
    backend=flask_app.config['CELERY_RESULT_BACKEND']
)

# 从 Flask 配置更新 Celery 配置
celery.conf.update(flask_app.config)

# 设置 Flask 应用上下文
class ContextTask(celery.Task):
    """带有 Flask 应用上下文的任务基类"""
    
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# 自动发现任务模块
celery.autodiscover_tasks(['tasks'])

if __name__ == '__main__':
    celery.start()
