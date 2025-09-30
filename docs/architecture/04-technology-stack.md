# Dify 技术栈清单

## 后端技术栈

### 核心框架

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Python | 3.11+ | 编程语言 | https://www.python.org/ |
| Flask | 3.1.2 | Web 框架 | https://flask.palletsprojects.com/ |
| Gunicorn | 23.0.0 | WSGI HTTP 服务器 | https://gunicorn.org/ |
| Gevent | 25.9.1 | 协程库 | http://www.gevent.org/ |

### 数据库和缓存

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| PostgreSQL | 15+ | 关系型数据库 | https://www.postgresql.org/ |
| Redis | 6+ | 缓存和消息队列 | https://redis.io/ |
| SQLAlchemy | 2.0.29 | Python ORM | https://www.sqlalchemy.org/ |
| Flask-SQLAlchemy | 3.1.1 | Flask SQLAlchemy 集成 | https://flask-sqlalchemy.palletsprojects.com/ |
| psycopg2-binary | 2.9.6 | PostgreSQL 驱动 | https://www.psycopg.org/ |

### 异步任务

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Celery | 5.5.2 | 分布式任务队列 | https://docs.celeryproject.org/ |
| redis-py | 6.1.0 | Redis Python 客户端 | https://github.com/redis/redis-py |

### AI 和机器学习

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| OpenAI | 1.61.0 | OpenAI API 客户端 | https://github.com/openai/openai-python |
| Transformers | 4.56.1 | Hugging Face 模型库 | https://huggingface.co/docs/transformers |
| TikToken | 0.9.0 | OpenAI Token 计数 | https://github.com/openai/tiktoken |
| LangSmith | 0.1.77 | LangChain 追踪 | https://smith.langchain.com/ |
| LangFuse | 2.51.3 | LLM 工程平台 | https://langfuse.com/ |

### 数据处理

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Pandas | 2.2.2 | 数据分析 | https://pandas.pydata.org/ |
| NumPy | 1.26.4 | 数值计算 | https://numpy.org/ |
| Pydantic | 2.11.4 | 数据验证 | https://docs.pydantic.dev/ |
| PyYAML | 6.0.1 | YAML 解析 | https://pyyaml.org/ |

### 文档处理

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| BeautifulSoup4 | 4.12.2 | HTML 解析 | https://www.crummy.com/software/BeautifulSoup/ |
| pypdfium2 | 4.30.0 | PDF 处理 | https://pypdfium2.readthedocs.io/ |
| python-docx | 1.1.0 | Word 文档处理 | https://python-docx.readthedocs.io/ |
| openpyxl | 3.1.5 | Excel 处理 | https://openpyxl.readthedocs.io/ |
| Markdown | 3.5.1 | Markdown 处理 | https://python-markdown.github.io/ |
| Unstructured | 0.16.1 | 文档解析 | https://unstructured.io/ |

### HTTP 客户端

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| httpx | 0.27.0 | 异步 HTTP 客户端 | https://www.python-httpx.org/ |
| Requests | (通过 httpx) | HTTP 请求 | - |

### 认证和安全

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| PyJWT | 2.10.1 | JWT Token | https://pyjwt.readthedocs.io/ |
| authlib | 1.6.4 | OAuth 认证 | https://docs.authlib.org/ |
| pycryptodome | 3.19.1 | 加密库 | https://www.pycryptodome.org/ |
| Flask-Login | 0.6.3 | 用户会话管理 | https://flask-login.readthedocs.io/ |
| Flask-CORS | 6.0.0 | CORS 支持 | https://flask-cors.readthedocs.io/ |

### 云服务集成

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| boto3 | 1.35.99 | AWS SDK | https://boto3.amazonaws.com/ |
| azure-identity | 1.16.1 | Azure 认证 | https://docs.microsoft.com/azure/identity |
| azure-storage-blob | 12.13.0 | Azure Blob 存储 | https://docs.microsoft.com/azure/storage |
| google-cloud-storage | 2.16.0 | Google Cloud 存储 | https://cloud.google.com/storage |
| google-cloud-aiplatform | 1.49.0 | Google AI Platform | https://cloud.google.com/ai-platform |

### 向量数据库

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| pymilvus | 2.5.0 | Milvus Python SDK | https://milvus.io/ |
| qdrant-client | 1.9.0 | Qdrant Python SDK | https://qdrant.tech/ |
| weaviate-client | 3.24.0 | Weaviate Python SDK | https://weaviate.io/ |
| chromadb | 0.5.20 | Chroma 向量数据库 | https://www.trychroma.com/ |
| pgvector | 0.2.5 | PostgreSQL 向量扩展 | https://github.com/pgvector/pgvector |
| elasticsearch | 8.14.0 | Elasticsearch | https://www.elastic.co/ |
| opensearch-py | 2.4.0 | OpenSearch | https://opensearch.org/ |

### 监控和日志

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Sentry SDK | 2.28.0 | 错误追踪 | https://sentry.io/ |
| OpenTelemetry | 1.27.0 | 可观测性 | https://opentelemetry.io/ |

### 邮件服务

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Resend | 2.9.0 | 邮件发送 | https://resend.com/ |
| SendGrid | 6.12.3 | 邮件发送 | https://sendgrid.com/ |

### 其他工具

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| python-dotenv | 1.0.1 | 环境变量管理 | https://github.com/theskumar/python-dotenv |
| jieba | 0.42.1 | 中文分词 | https://github.com/fxsjy/jieba |
| chardet | 5.1.0 | 字符编码检测 | https://github.com/chardet/chardet |
| cachetools | 5.3.0 | 缓存工具 | https://github.com/tkem/cachetools |

---

## 前端技术栈

### 核心框架

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Next.js | 15.5.0 | React SSR 框架 | https://nextjs.org/ |
| React | 19.1.1 | UI 框架 | https://react.dev/ |
| React DOM | 19.1.1 | React DOM 渲染 | https://react.dev/ |
| TypeScript | (Latest) | 静态类型 | https://www.typescriptlang.org/ |

### 状态管理

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| SWR | 2.3.0 | 数据获取和缓存 | https://swr.vercel.app/ |
| use-context-selector | 2.0.0 | Context 性能优化 | https://github.com/dai-shi/use-context-selector |
| ahooks | 3.8.4 | React Hooks 工具库 | https://ahooks.js.org/ |
| immer | 9.0.19 | 不可变数据 | https://immerjs.github.io/immer/ |

### UI 组件

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| @headlessui/react | 2.2.1 | 无样式组件 | https://headlessui.com/ |
| @heroicons/react | 2.0.16 | 图标库 | https://heroicons.com/ |
| @remixicon/react | 4.5.0 | 图标库 | https://remixicon.com/ |
| @emoji-mart/data | 1.2.1 | Emoji 数据 | https://github.com/missive/emoji-mart |
| emoji-mart | 5.5.2 | Emoji 选择器 | https://github.com/missive/emoji-mart |

### 样式

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Tailwind CSS | (Latest) | CSS 框架 | https://tailwindcss.com/ |
| @tailwindcss/typography | 0.5.15 | 排版插件 | https://tailwindcss.com/docs/typography-plugin |
| tailwind-merge | 2.5.4 | 样式合并 | https://github.com/dcastil/tailwind-merge |
| class-variance-authority | 0.7.0 | 样式变体 | https://cva.style/ |
| classnames | 2.5.1 | 类名拼接 | https://github.com/JedWatson/classnames |
| next-themes | 0.4.3 | 主题切换 | https://github.com/pacocoursey/next-themes |

### 表单处理

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| react-hook-form | 7.53.1 | 表单管理 | https://react-hook-form.com/ |
| @hookform/resolvers | 3.9.0 | 表单验证解析器 | https://github.com/react-hook-form/resolvers |
| zod | 3.23.8 | Schema 验证 | https://zod.dev/ |
| @tanstack/react-form | 1.3.3 | 表单库 | https://tanstack.com/form |

### 数据可视化

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| reactflow | 11.11.3 | 流程图/节点编辑器 | https://reactflow.dev/ |
| @dagrejs/dagre | 1.1.4 | 图布局算法 | https://github.com/dagrejs/dagre |
| elkjs | 0.9.3 | 图布局引擎 | https://github.com/kieler/elkjs |
| echarts | 5.5.1 | 图表库 | https://echarts.apache.org/ |
| echarts-for-react | 3.0.2 | ECharts React 封装 | https://github.com/hustcc/echarts-for-react |
| mermaid | 11.10.0 | 流程图渲染 | https://mermaid.js.org/ |
| abcjs | 6.5.2 | 乐谱渲染 | https://www.abcjs.net/ |

### 编辑器

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| @monaco-editor/react | 4.6.0 | Monaco 代码编辑器 | https://microsoft.github.io/monaco-editor/ |
| lexical | 0.30.0 | Meta 富文本编辑器 | https://lexical.dev/ |
| @lexical/react | 0.30.0 | Lexical React 绑定 | https://lexical.dev/ |

### Markdown 和富文本

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| react-markdown | 9.0.1 | Markdown 渲染 | https://github.com/remarkjs/react-markdown |
| remark-gfm | 4.0.0 | GitHub Flavored Markdown | https://github.com/remarkjs/remark-gfm |
| remark-math | 6.0.0 | 数学公式支持 | https://github.com/remarkjs/remark-math |
| rehype-katex | 7.0.1 | KaTeX 渲染 | https://github.com/remarkjs/rehype-katex |
| rehype-raw | 7.0.0 | 原始 HTML 支持 | https://github.com/rehypejs/rehype-raw |
| katex | 0.16.21 | 数学公式渲染 | https://katex.org/ |

### HTTP 和数据请求

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| ky | 1.7.2 | HTTP 客户端 | https://github.com/sindresorhus/ky |
| @tanstack/react-query | 5.60.5 | 数据同步 | https://tanstack.com/query |
| @tanstack/react-query-devtools | 5.60.5 | Query DevTools | https://tanstack.com/query |
| qs | 6.13.0 | 查询字符串解析 | https://github.com/ljharb/qs |

### 国际化

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| i18next | 23.16.4 | 国际化框架 | https://www.i18next.com/ |
| react-i18next | 15.1.0 | React i18next 集成 | https://react.i18next.com/ |
| i18next-resources-to-backend | 1.2.1 | 资源懒加载 | https://github.com/i18next/i18next-resources-to-backend |
| @formatjs/intl-localematcher | 0.5.6 | 语言匹配 | https://formatjs.io/ |
| negotiator | 1.0.0 | 内容协商 | https://github.com/jshttp/negotiator |
| pinyin-pro | 3.25.0 | 拼音转换 | https://github.com/zh-lx/pinyin-pro |

### 工具库

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| lodash-es | 4.17.21 | 工具函数库 | https://lodash.com/ |
| dayjs | 1.11.13 | 日期处理 | https://day.js.org/ |
| uuid | 10.0.0 | UUID 生成 | https://github.com/uuidjs/uuid |
| fast-deep-equal | 3.1.3 | 深度比较 | https://github.com/epoberezkin/fast-deep-equal |
| decimal.js | 10.4.3 | 精确计算 | https://github.com/MikeMcl/decimal.js |
| semver | 7.6.3 | 版本号解析 | https://github.com/npm/node-semver |
| mime | 4.0.4 | MIME 类型 | https://github.com/broofa/mime |
| tldts | 7.0.9 | 域名解析 | https://github.com/remusao/tldts |

### UI 增强

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| react-tooltip | 5.8.3 | 工具提示 | https://react-tooltip.com/ |
| @floating-ui/react | 0.26.25 | 浮动 UI 定位 | https://floating-ui.com/ |
| react-hotkeys-hook | 4.6.1 | 快捷键 | https://github.com/JohannesKlauss/react-hotkeys-hook |
| cmdk | 1.1.1 | 命令面板 | https://cmdk.paco.me/ |
| react-infinite-scroll-component | 6.1.0 | 无限滚动 | https://github.com/ankeetmaini/react-infinite-scroll-component |
| react-window | 1.8.10 | 虚拟列表 | https://github.com/bvaughn/react-window |
| react-window-infinite-loader | 1.0.9 | 虚拟列表加载器 | https://github.com/bvaughn/react-window-infinite-loader |

### 文件处理

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| react-easy-crop | 5.1.0 | 图片裁剪 | https://github.com/ValentinH/react-easy-crop |
| html-to-image | 1.11.11 | HTML 转图片 | https://github.com/bubkoo/html-to-image |
| copy-to-clipboard | 3.3.3 | 复制到剪贴板 | https://github.com/sudodoki/copy-to-clipboard |
| react-papaparse | 4.4.0 | CSV 解析 | https://github.com/Bunlong/react-papaparse |
| react-pdf-highlighter | 8.0.0-rc.0 | PDF 高亮 | https://github.com/agentcooper/react-pdf-highlighter |
| qrcode.react | 4.2.0 | 二维码生成 | https://github.com/zpao/qrcode.react |

### 多媒体

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| js-audio-recorder | 1.0.7 | 音频录制 | https://github.com/2fps/recorder |
| recordrtc | 5.6.2 | 录音录屏 | https://recordrtc.org/ |
| lamejs | 1.2.1 | MP3 编码 | https://github.com/zhuker/lamejs |

### 拖拽和排序

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| sortablejs | 1.15.0 | 拖拽排序 | https://sortablejs.github.io/Sortable/ |
| react-sortablejs | 6.1.4 | SortableJS React 封装 | https://github.com/SortableJS/react-sortablejs |

### 安全

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| dompurify | 3.2.4 | XSS 防护 | https://github.com/cure53/DOMPurify |
| crypto-js | 4.2.0 | 加密库 | https://github.com/brix/crypto-js |
| jwt-decode | 4.0.0 | JWT 解析 | https://github.com/auth0/jwt-decode |
| js-cookie | 3.0.5 | Cookie 操作 | https://github.com/js-cookie/js-cookie |

### 监控和错误追踪

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| @sentry/react | 8.54.0 | 错误追踪 | https://sentry.io/ |
| @sentry/utils | 8.54.0 | Sentry 工具 | https://sentry.io/ |

### 其他

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| react-error-boundary | 4.1.2 | 错误边界 | https://github.com/bvaughn/react-error-boundary |
| mitt | 3.0.1 | 事件总线 | https://github.com/developit/mitt |
| scheduler | 0.26.0 | React 调度器 | https://github.com/facebook/react |
| sharp | 0.33.2 | 图片处理 | https://sharp.pixelplumbing.com/ |
| shave | 5.0.4 | 文本截断 | https://github.com/dollarshaveclub/shave |
| line-clamp | 1.0.0 | 行数限制 | https://github.com/styled-components/polished |

---

## 基础设施

### 容器和编排

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Docker | Latest | 容器化 | https://www.docker.com/ |
| Docker Compose | Latest | 容器编排 | https://docs.docker.com/compose/ |

### Web 服务器

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Nginx | Latest | 反向代理 | https://nginx.org/ |

### 代码沙箱

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| DifySandbox | 0.2.12 | 代码安全执行 | - |
| Golang | Latest | Sandbox 实现语言 | https://go.dev/ |

### 插件系统

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| Plugin Daemon | 0.3.0-local | 插件运行时 | - |

---

## 开发工具

### 包管理器

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| uv | Latest | Python 包管理器 | https://github.com/astral-sh/uv |
| pnpm | 10.17.1 | Node.js 包管理器 | https://pnpm.io/ |

### 代码质量

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| ESLint | Latest | JavaScript 代码检查 | https://eslint.org/ |
| Ruff | 0.12.3 | Python 代码检查 | https://github.com/astral-sh/ruff |
| basedpyright | 1.31.0 | Python 类型检查 | https://github.com/DetachHead/basedpyright |
| MyPy | 1.17.1 | Python 类型检查 | https://mypy-lang.org/ |

### 测试

| 技术 | 版本 | 用途 | 官网 |
|------|------|------|------|
| pytest | 8.3.2 | Python 测试框架 | https://pytest.org/ |
| Jest | Latest | JavaScript 测试框架 | https://jestjs.io/ |

---

**文档版本**: v1.0  
**最后更新**: 2025-09-30  
**基于 Dify 版本**: 1.9.1
