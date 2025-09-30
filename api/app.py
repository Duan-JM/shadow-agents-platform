"""
应用入口文件

启动 Flask 应用
"""
import os
from app_factory import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发环境直接运行
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'false').lower() == 'true'
    )
