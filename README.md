# Shadow Agents Platform

<div align="center">
  <h3>🤖 影子智能体平台</h3>
  <p>基于 Dify 架构的开源 AI 应用开发平台</p>
  <p>
    <a href="#特性">特性</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#文档">文档</a> •
    <a href="#技术栈">技术栈</a>
  </p>
</div>

---

## 📖 简介

Shadow Agents Platform（影子智能体平台）是一个开源的 AI 应用开发平台，参考 Dify 1.9.1 架构设计，专注于提供：

- 🎯 **应用管理**：支持聊天、补全、Agent、工作流等多种应用类型
- 🔄 **工作流引擎**：可视化流程编排，支持条件分支、循环迭代
- 📚 **知识库系统**：RAG（检索增强生成）支持，多格式文档处理
- 🤖 **模型集成**：支持 OpenAI、Anthropic 等多个模型提供商
- 🛠️ **工具系统**：内置和自定义工具支持

## ✨ 特性

### 核心功能

- [x] **用户认证系统**
  - JWT Token 认证
  - 多租户支持
  - API Key 管理

- [x] **应用系统**
  - Chat 应用（多轮对话）
  - Completion 应用（文本生成）
  - Agent 应用（工具调用）
  - Workflow 应用（流程编排）

- [x] **工作流引擎**
  - 可视化节点编辑器
  - 多种节点类型（LLM、Code、HTTP、条件、循环等）
  - 并行执行和流程控制
  - 调试和日志

- [x] **知识库系统（RAG）**
  - 多格式文档支持（PDF、Word、Markdown 等）
  - 文本分段和向量化
  - 语义检索和混合检索
  - 重排序（Rerank）

- [x] **模型管理**
  - 多模型提供商支持
  - 统一的模型接口
  - 流式响应
  - Token 追踪

### 技术特性

- 🐍 **Python 3.11** + **Flask 3.1** 后端
- ⚛️ **Next.js 15** + **React 19** 前端
- 🗄️ **PostgreSQL 15** 主数据库
- 🔴 **Redis 6** 缓存和队列
- 🔍 **Milvus** 向量数据库
- 🐳 **Docker Compose** 一键部署

## 快速开始

### 方式一：使用快速启动脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/your-org/shadow-agents-platform.git
cd shadow-agents-platform

# 运行快速启动脚本
bash scripts/deployment/start.sh
```

### 方式二：手动启动

```bash
# 克隆项目
git clone https://github.com/your-org/shadow-agents-platform.git
cd shadow-agents-platform

# 使用 Docker Compose 启动
cd docker
cp .env.example .env
vim .env  # 编辑配置（必须配置 SECRET_KEY, OPENAI_API_KEY 等）
docker-compose up -d

# 初始化数据库
docker-compose exec api flask db upgrade
```

访问：
- **Web 界面**: http://localhost:3000
- **API 文档**: http://localhost:5000/api/docs
- **Nginx 入口**: http://localhost

## 文档

### 架构文档
- [架构分析总览](docs/architecture/00-README.md)
- [系统架构设计](docs/architecture/01-system-architecture.md)
- [后端架构设计](docs/architecture/02-backend-structure.md)
- [前端架构设计](docs/architecture/03-frontend-structure.md)
- [技术栈清单](docs/architecture/04-technology-stack.md)
- [功能模块清单](docs/architecture/05-feature-modules.md)

### 开发文档
- [开发指南](docs/guides/development.md)
- [部署指南](docs/guides/deployment.md)
- [数据库设计](docs/database/schema.md)

### 组件文档
- [后端 API 文档](api/README.md)
- [前端文档](web/README.md)
- [Docker 部署文档](docker/README.md)

## 🛠️ 技术栈

### 后端

- **框架**: Flask 3.1.2
- **异步任务**: Celery 5.5.2
- **ORM**: SQLAlchemy 2.0.29
- **数据库**: PostgreSQL 15, Redis 6
- **向量数据库**: Milvus
- **AI SDK**: OpenAI, Anthropic, 等

### 前端

- **框架**: Next.js 15.5.0
- **UI 库**: React 19.1.1
- **类型系统**: TypeScript
- **样式**: Tailwind CSS
- **状态管理**: SWR, Context
- **流程图**: ReactFlow 11

### 基础设施

- **容器化**: Docker, Docker Compose
- **Web 服务器**: Nginx
- **代码沙箱**: DifySandbox

## 📁 项目结构

```
shadow-agents-platform/
├── api/                  # 后端 API 服务
│   ├── controllers/     # 控制器层
│   ├── core/            # 核心业务逻辑
│   ├── models/          # 数据模型
│   ├── services/        # 服务层
│   └── ...
├── web/                 # 前端应用
│   ├── app/             # Next.js App Router
│   ├── components/      # React 组件
│   ├── hooks/           # 自定义 Hooks
│   └── ...
├── docker/              # Docker 配置
│   ├── docker-compose.yml
│   ├── nginx/
│   └── ...
├── docs/                # 项目文档
└── scripts/             # 脚本工具
```

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](./CONTRIBUTING.md)。

## 📄 许可证

本项目采用 [MIT License](./LICENSE)。

## 🙏 致谢

本项目参考了以下优秀的开源项目：

- [Dify](https://github.com/langgenius/dify) - AI 应用开发平台
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [ReactFlow](https://github.com/wbkd/react-flow) - 流程图库

## 📮 联系方式

- Issue: [GitHub Issues](https://github.com/Duan-JM/shadow-agents-platform/issues)
- Email: your-email@example.com

---

<div align="center">
  <sub>Built with ❤️ by the Shadow Agents Platform Team</sub>
</div>
