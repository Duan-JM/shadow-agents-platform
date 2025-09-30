# 贡献指南

感谢您对 Shadow Agents Platform 的关注！我们欢迎任何形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现 bug 或有功能建议：

1. 在 [Issues](https://github.com/Duan-JM/shadow-agents-platform/issues) 中搜索，确认问题未被报告
2. 创建新 Issue，详细描述问题或建议
3. 使用适当的标签（bug、enhancement、question 等）

### 提交代码

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目
   git clone https://github.com/your-username/shadow-agents-platform.git
   cd shadow-agents-platform
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **开发和测试**
   - 遵循项目代码规范
   - 编写必要的测试
   - 确保所有测试通过

4. **提交变更**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   # 或
   git commit -m "fix: 修复某个 bug"
   ```

   **提交信息规范**：
   - `feat`: 新功能
   - `fix`: Bug 修复
   - `docs`: 文档更新
   - `style`: 代码格式调整
   - `refactor`: 代码重构
   - `test`: 测试相关
   - `chore`: 构建过程或辅助工具变动

5. **推送到 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 填写 PR 模板，描述变更内容
   - 等待代码审查

## 📝 开发规范

### 代码风格

**Python**：
- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 最大行长度 120 字符
- 使用 Black 进行代码格式化
- 使用 Ruff 进行代码检查

**TypeScript/JavaScript**：
- 使用 2 空格缩进
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化

### 注释规范

- 所有文档和注释使用**中文**
- 函数和类需要添加文档字符串
- 复杂逻辑需要添加行内注释

**Python 示例**：
```python
def calculate_embedding(text: str) -> list[float]:
    """
    计算文本的向量表示
    
    参数:
        text: 输入文本
        
    返回:
        向量表示，浮点数列表
        
    异常:
        ValueError: 当文本为空时抛出
    """
    if not text:
        raise ValueError("文本不能为空")
    # 实现逻辑...
```

**TypeScript 示例**:
```typescript
/**
 * 获取应用列表
 * @param page 页码
 * @param pageSize 每页数量
 * @returns 应用列表数据
 */
async function fetchApps(page: number, pageSize: number): Promise<AppListResponse> {
  // 实现逻辑...
}
```

### 测试要求

- 新功能必须包含单元测试
- Bug 修复需要包含回归测试
- 测试覆盖率不低于 80%

**运行测试**：
```bash
# 后端测试
cd api
pytest

# 前端测试
cd web
npm test
```

## 🏗️ 项目结构

详见 [项目文档](./docs/architecture/)。

## 📖 文档

- 修改代码时，同步更新相关文档
- 新功能需要更新用户文档和 API 文档
- 文档使用中文编写

## ❓ 问题和帮助

如有任何问题：

1. 查看 [文档](./docs/)
2. 搜索 [Issues](https://github.com/Duan-JM/shadow-agents-platform/issues)
3. 创建新 Issue 提问
4. 联系维护者

## 📄 许可证

提交代码即表示您同意您的贡献将在 [MIT License](./LICENSE) 下发布。

---

再次感谢您的贡献！🎉
