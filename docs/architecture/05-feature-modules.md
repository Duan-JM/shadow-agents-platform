# Dify 核心功能模块清单

## 一、用户认证系统

### 1.1 用户注册登录

**功能清单**:
- ✅ 邮箱注册
- ✅ 邮箱登录
- ✅ OAuth 登录 (GitHub, Google)
- ✅ 密码找回
- ✅ 邮箱验证
- ✅ 账户激活

**技术实现**:
- JWT Token 认证
- Session 管理 (Redis)
- OAuth 2.0 集成
- 邮件发送 (Resend/SendGrid)

**API 端点**:
```
POST   /api/login                    # 登录
POST   /api/logout                   # 登出
POST   /api/register                 # 注册
POST   /api/forgot-password          # 忘记密码
POST   /api/reset-password           # 重置密码
GET    /api/oauth/authorize/:provider # OAuth 授权
GET    /api/oauth/callback/:provider  # OAuth 回调
```

### 1.2 多租户管理

**功能清单**:
- ✅ 租户创建
- ✅ 租户成员管理
- ✅ 角色权限
- ✅ 资源配额
- ✅ 邀请机制

**角色类型**:
- **Owner**: 所有者 (最高权限)
- **Admin**: 管理员
- **Editor**: 编辑者
- **Viewer**: 查看者

### 1.3 API Key 管理

**功能清单**:
- ✅ API Key 创建
- ✅ API Key 删除
- ✅ API Key 权限控制
- ✅ API Key 使用统计

---

## 二、应用管理系统

### 2.1 应用类型

#### 2.1.1 Chat 应用
**特性**:
- 多轮对话
- 上下文记忆
- 对话历史
- 流式响应
- 文件上传
- 语音输入

#### 2.1.2 Completion 应用
**特性**:
- 单次文本生成
- 批量处理
- 自定义输入输出
- 表单模式

#### 2.1.3 Agent 应用
**特性**:
- 工具调用
- 多步推理
- ReAct 模式
- Function Calling
- 自主决策

#### 2.1.4 Workflow 应用
**特性**:
- 可视化流程编排
- 多种节点类型
- 条件分支
- 循环迭代
- 并行执行
- 调试运行

### 2.2 应用配置

**基础配置**:
- 应用名称和图标
- 应用描述
- 应用类型
- 发布状态

**模型配置**:
- 模型提供商选择
- 模型参数调整
  - Temperature
  - Top P
  - Max Tokens
  - Presence Penalty
  - Frequency Penalty

**Prompt 配置**:
- 系统提示词
- 用户输入变量
- 上下文变量
- Jinja2 模板

**高级功能**:
- 开场白 (Opening Statement)
- 建议问题 (Suggested Questions)
- 引用归属 (Citation)
- 内容审核 (Moderation)
- 语音转文字 (Speech to Text)
- 文字转语音 (Text to Speech)

### 2.3 应用发布

**功能清单**:
- ✅ WebApp 发布
- ✅ API 发布
- ✅ 嵌入式集成
- ✅ 版本管理
- ✅ 回滚功能

**分享选项**:
- 公开链接
- 私有访问
- 密码保护
- IP 白名单

### 2.4 应用监控

**监控指标**:
- 使用次数
- Token 消耗
- 平均响应时间
- 错误率
- 用户反馈

**日志查看**:
- 对话日志
- 执行日志
- 调试日志
- 错误日志

---

## 三、工作流系统

### 3.1 工作流节点

#### 3.1.1 基础节点

| 节点类型 | 功能说明 | 输入 | 输出 |
|---------|---------|------|------|
| Start | 开始节点 | 用户输入 | 输入变量 |
| End | 结束节点 | 任意变量 | 最终输出 |
| Answer | 答案输出 | 文本内容 | 用户可见内容 |

#### 3.1.2 模型节点

| 节点类型 | 功能说明 | 输入 | 输出 |
|---------|---------|------|------|
| LLM | 大语言模型调用 | Prompt + 变量 | 生成文本 |
| Knowledge Retrieval | 知识库检索 | 查询文本 | 相关文档 |

#### 3.1.3 逻辑节点

| 节点类型 | 功能说明 | 输入 | 输出 |
|---------|---------|------|------|
| Condition (If/Else) | 条件判断 | 条件表达式 | 分支路径 |
| Loop | 循环迭代 | 列表数据 | 迭代结果 |
| Code | 代码执行 | Python/JavaScript | 执行结果 |
| Template Transform | 模板转换 | Jinja2 模板 | 格式化文本 |

#### 3.1.4 工具节点

| 节点类型 | 功能说明 | 输入 | 输出 |
|---------|---------|------|------|
| HTTP Request | HTTP 请求 | URL + 参数 | 响应数据 |
| Tool | 工具调用 | 工具参数 | 工具结果 |
| Question Classifier | 问题分类 | 问题文本 | 分类结果 |
| Parameter Extractor | 参数提取 | 文本 + Schema | 结构化数据 |
| Document Extractor | 文档提取 | 文件 | 文本内容 |

#### 3.1.5 数据节点

| 节点类型 | 功能说明 | 输入 | 输出 |
|---------|---------|------|------|
| Variable Assigner | 变量赋值 | 变量值 | 更新后变量 |
| List Operator | 列表操作 | 列表数据 | 处理后列表 |

### 3.2 工作流功能

**编辑功能**:
- ✅ 节点拖拽
- ✅ 连线管理
- ✅ 自动布局
- ✅ 缩放和平移
- ✅ 快捷键支持
- ✅ 撤销/重做

**调试功能**:
- ✅ 单步执行
- ✅ 断点调试
- ✅ 变量查看
- ✅ 日志输出
- ✅ 错误定位

**高级特性**:
- ✅ 并行执行
- ✅ 条件分支
- ✅ 循环迭代 (最多 100 次)
- ✅ 变量传递
- ✅ 环境变量
- ✅ 全局异常处理

### 3.3 工作流模板

**内置模板**:
- 客服对话
- 内容生成
- 数据分析
- 文档处理
- 多轮问答
- ...

---

## 四、知识库系统 (RAG)

### 4.1 知识库管理

**功能清单**:
- ✅ 知识库创建
- ✅ 知识库编辑
- ✅ 知识库删除
- ✅ 知识库权限
- ✅ 知识库统计

**知识库类型**:
- 文档知识库
- 外部数据源
- 网页抓取

### 4.2 文档管理

**支持的文档类型**:
- 📄 PDF
- 📄 Word (DOC, DOCX)
- 📄 Markdown
- 📄 TXT
- 📄 HTML
- 📄 Excel (XLS, XLSX)
- 📄 PPT (PPTX)
- 📄 EPUB

**文档操作**:
- ✅ 批量上传
- ✅ 在线编辑
- ✅ 版本管理
- ✅ 文档预览
- ✅ 文档删除
- ✅ 元数据管理

### 4.3 文档处理

**文本分段**:
- 自动分段
- 自定义分隔符
- 分段长度控制
- 重叠设置

**分段策略**:
- 固定长度分段
- 递归字符分段
- Markdown 分段
- 自定义规则

### 4.4 向量化

**Embedding 模型**:
- OpenAI text-embedding-ada-002
- OpenAI text-embedding-3-small
- OpenAI text-embedding-3-large
- Azure OpenAI
- Cohere Embeddings
- 本地 Embedding 模型
- ...50+ 模型

**向量化配置**:
- 批量大小
- 并发数
- 重试策略

### 4.5 检索

**检索模式**:
- 向量检索 (语义检索)
- 全文检索 (关键词检索)
- 混合检索 (向量 + 全文)

**检索配置**:
- Top K (返回数量)
- Score Threshold (相关性阈值)
- 重排序 (Rerank)
- 引用归属

**Rerank 模型**:
- Cohere Rerank
- Jina Rerank
- BGE Reranker
- Cross-encoder

### 4.6 外部数据源

**支持的数据源**:
- 🔌 Notion
- 🔌 Google Drive
- 🔌 GitHub
- 🔌 Web Scraping
- 🔌 API 集成

---

## 五、模型管理系统

### 5.1 模型提供商

**支持的提供商** (50+):

**国际提供商**:
- OpenAI (GPT-3.5, GPT-4, GPT-4o)
- Anthropic (Claude 2, Claude 3)
- Google (Gemini, PaLM)
- Cohere
- Hugging Face
- Replicate
- Azure OpenAI
- AWS Bedrock
- Mistral AI
- Groq
- ...

**国内提供商**:
- 智谱 AI (GLM-4)
- 百度 (文心一言)
- 阿里云 (通义千问)
- 讯飞星火
- 字节跳动 (豆包)
- 腾讯混元
- MiniMax
- 月之暗面 (Kimi)
- 零一万物
- ...

### 5.2 模型类型

1. **LLM (大语言模型)**
   - 文本生成
   - 对话
   - 指令遵循

2. **Text Embedding**
   - 文本向量化
   - 语义搜索

3. **Rerank**
   - 结果重排序
   - 相关性打分

4. **Speech2Text**
   - 语音识别
   - 音频转文字

5. **Text2Speech**
   - 语音合成
   - 文字转音频

### 5.3 模型配置

**凭证管理**:
- API Key 配置
- 多凭证支持
- 凭证池管理
- 负载均衡

**参数配置**:
- Temperature (随机性)
- Top P (核采样)
- Max Tokens (最大长度)
- Presence Penalty (重复惩罚)
- Frequency Penalty (频率惩罚)
- Stop Sequences (停止序列)

### 5.4 费用追踪

**统计指标**:
- Token 使用量
- API 调用次数
- 费用计算
- 配额管理

---

## 六、工具系统

### 6.1 内置工具

**搜索工具**:
- Google Search
- DuckDuckGo
- Bing Search
- Wikipedia

**知识工具**:
- Knowledge Retrieval (知识库检索)
- Web Scraper (网页抓取)

**数据工具**:
- Calculator (计算器)
- JSON Parser
- CSV Parser
- XML Parser

**图像工具**:
- DALL-E
- Stable Diffusion
- Image Analysis

**编程工具**:
- Code Interpreter
- Python Executor
- JavaScript Executor

### 6.2 自定义工具

**工具类型**:
- API 工具
- OpenAPI 工具
- Python 插件
- 工作流工具

**工具定义**:
```yaml
name: custom_tool
description: Tool description
parameters:
  - name: param1
    type: string
    required: true
    description: Parameter description
```

### 6.3 工具市场

**功能**:
- 工具搜索
- 工具安装
- 工具评分
- 工具分享

---

## 七、插件系统

### 7.1 插件类型

1. **模型插件**
   - 自定义模型提供商
   - 模型适配器

2. **工具插件**
   - 第三方服务集成
   - 自定义功能

3. **数据源插件**
   - 外部数据接入
   - 实时数据同步

### 7.2 插件管理

**功能清单**:
- ✅ 插件安装
- ✅ 插件卸载
- ✅ 插件配置
- ✅ 插件更新
- ✅ 插件调试

### 7.3 插件开发

**开发语言**:
- Python
- TypeScript

**插件 SDK**:
- Dify Plugin SDK

---

## 八、对话管理

### 8.1 对话功能

**基础功能**:
- ✅ 创建对话
- ✅ 消息发送
- ✅ 消息接收
- ✅ 流式响应
- ✅ 对话历史
- ✅ 对话删除

**高级功能**:
- ✅ 多轮对话
- ✅ 上下文管理
- ✅ 对话分支
- ✅ 对话标注
- ✅ 对话导出

### 8.2 消息类型

**文本消息**:
- 纯文本
- Markdown
- 代码块

**多模态消息**:
- 图片
- 音频
- 视频
- 文件

**特殊消息**:
- 系统消息
- 工具调用
- 错误消息

### 8.3 消息反馈

**反馈类型**:
- 👍 点赞
- 👎 点踩
- 💬 评论
- ⭐ 评分

**标注功能**:
- 消息标注
- 答案修改
- 质量评分

---

## 九、监控和日志

### 9.1 应用监控

**监控指标**:
- 使用量统计
- Token 消耗
- 响应时间
- 错误率
- 用户活跃度

**可视化**:
- 折线图
- 柱状图
- 饼图
- 热力图

### 9.2 日志管理

**日志类型**:
- 对话日志
- 执行日志
- 错误日志
- 审计日志

**日志功能**:
- 日志查询
- 日志过滤
- 日志导出
- 日志分析

### 9.3 错误追踪

**集成方案**:
- Sentry
- 自定义错误追踪

---

## 十、系统管理

### 10.1 租户管理

**功能清单**:
- 租户创建
- 租户配置
- 成员管理
- 权限控制
- 配额管理

### 10.2 模型管理

**功能清单**:
- 提供商管理
- 模型列表
- 凭证配置
- 模型测试

### 10.3 系统设置

**功能清单**:
- 基础设置
- 邮件配置
- 存储配置
- 安全配置
- 功能开关

---

## 十一、数据管理

### 11.1 数据导入导出

**导出格式**:
- JSON
- CSV
- Excel
- DSL (工作流定义)

**导入功能**:
- 批量导入
- 模板导入
- DSL 导入

### 11.2 数据备份

**备份内容**:
- 应用配置
- 知识库数据
- 对话历史
- 用户数据

---

## 十二、API 服务

### 12.1 Service API

**功能清单**:
- 对话 API
- 补全 API
- 工作流执行 API
- 反馈 API
- 文件上传 API

### 12.2 Console API

**功能清单**:
- 应用管理 API
- 知识库管理 API
- 模型管理 API
- 日志查询 API

### 12.3 API 文档

**文档格式**:
- OpenAPI (Swagger)
- 交互式文档
- SDK 示例

---

## 十三、安全和合规

### 13.1 内容安全

**功能清单**:
- 敏感词过滤
- 内容审核
- NSFW 检测

**审核提供商**:
- OpenAI Moderation
- 自定义规则

### 13.2 数据安全

**功能清单**:
- 数据加密
- 访问控制
- 审计日志
- 隐私保护

### 13.3 SSRF 防护

**防护机制**:
- URL 白名单
- IP 黑名单
- 代理服务器
- 请求过滤

---

**文档版本**: v1.0  
**最后更新**: 2025-09-30  
**基于 Dify 版本**: 1.9.1
