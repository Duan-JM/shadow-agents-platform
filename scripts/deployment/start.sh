#!/bin/bash

# Shadow Agents Platform 快速启动脚本

set -e

echo "==================================="
echo " Shadow Agents Platform 启动脚本"
echo "==================================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 进入 docker 目录
cd "$(dirname "$0")/docker"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，从模板复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑配置后重新运行"
    echo ""
    echo "必须配置的环境变量："
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo "  - OPENAI_API_KEY"
    echo ""
    exit 1
fi

# 检查必需的环境变量
source .env

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-change-in-production" ]; then
    echo "❌ 请在 .env 文件中配置 SECRET_KEY"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key" ]; then
    echo "❌ 请在 .env 文件中配置 OPENAI_API_KEY"
    exit 1
fi

echo "✅ 配置检查通过"
echo ""

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态："
docker-compose ps

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
docker-compose exec -T api flask db upgrade || true

echo ""
echo "==================================="
echo " ✅ 启动完成！"
echo "==================================="
echo ""
echo "访问地址："
echo "  - Web 界面: http://localhost:3000"
echo "  - API 接口: http://localhost:5000"
echo "  - Nginx 入口: http://localhost"
echo ""
echo "常用命令："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo ""
