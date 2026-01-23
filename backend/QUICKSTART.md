# Nano Flow Backend - 快速开始指南

本指南将帮助你在 5 分钟内启动并测试 Nano Flow 后端服务。

## 前置要求

- Python 3.10 或更高版本
- 千问 API 密钥（从阿里云 DashScope 获取）
- Nano Banana Pro API 密钥

## 步骤 1: 安装依赖

```bash
# 进入 backend 目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 步骤 2: 配置 API 密钥

1. 复制环境变量示例文件：

```bash
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API 密钥：

```env
# 必填项 - 请替换为你的真实 API 密钥
QWEN_API_KEY=sk-xxxxxxxxxxxxx
NANO_BANANA_API_KEY=sk-xxxxxxxxxxxxx

# 其他配置保持默认即可
APP_ENV=development
APP_DEBUG=True
APP_PORT=8000
```

### 如何获取 API 密钥？

**千问 API 密钥：**
1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册/登录账号
3. 在控制台创建 API Key

**Nano Banana Pro API 密钥：**
1. 访问 Nano Banana 官网
2. 注册账号并申请 API 访问权限
3. 在控制台获取 API Key

## 步骤 3: 启动服务

```bash
# 方式 1: 使用启动脚本（推荐）
python run.py

# 方式 2: 使用 uvicorn
uvicorn app.main:app --reload
```

看到以下输出表示启动成功：

```
============================================================
🚀 Nano Flow API Starting...
Environment: development
Debug Mode: True
Host: 0.0.0.0:8000
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 步骤 4: 验证安装

### 方法 1: 使用测试脚本（推荐）

打开新的终端窗口，运行测试脚本：

```bash
python test_api.py
```

这个脚本会自动测试：
1. 健康检查接口
2. 创建生成任务
3. 查询任务状态

### 方法 2: 使用浏览器

1. 打开浏览器访问 http://localhost:8000/docs
2. 你会看到 Swagger UI 交互式 API 文档
3. 尝试调用 `/health` 接口验证服务状态

### 方法 3: 使用 curl

```bash
# 健康检查
curl http://localhost:8000/health

# 创建生成任务
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "如何制作咖啡",
    "steps": [
      {"title": "研磨咖啡豆", "description": "选择新鲜豆子"},
      {"title": "萃取咖啡", "description": "使用咖啡机萃取"}
    ],
    "visual_preferences": {
      "character": "bear",
      "color_scheme": "pastel"
    }
  }'

# 查询任务状态（替换 {task_id} 为上一步返回的 task_id）
curl http://localhost:8000/api/v1/generate/{task_id}
```

## 完整测试示例

使用 Swagger UI 进行完整测试：

1. 访问 http://localhost:8000/docs

2. 点击 `POST /api/v1/generate` 展开

3. 点击 "Try it out" 按钮

4. 修改请求体（或使用默认值）：

```json
{
  "title": "如何制作美味拿铁",
  "steps": [
    {
      "title": "研磨咖啡豆",
      "description": "选择新鲜的中深烘焙豆子"
    },
    {
      "title": "萃取浓缩",
      "description": "使用咖啡机萃取双份Espresso"
    },
    {
      "title": "打奶泡",
      "description": "将牛奶加热并打出细腻奶泡"
    },
    {
      "title": "组合完成",
      "description": "将奶泡倒入浓缩咖啡中"
    }
  ],
  "visual_preferences": {
    "character": "bear",
    "color_scheme": "pastel",
    "custom_tags": ["kawaii", "flat"]
  }
}
```

5. 点击 "Execute" 按钮

6. 复制响应中的 `task_id`

7. 使用 `GET /api/v1/generate/{task_id}` 查询生成进度

8. 轮询查询直到 `status` 为 `completed` 或 `failed`

## 常见问题

### Q: 启动失败，提示 "Field required"

**A:** 检查 `.env` 文件是否存在，且包含必填的 API 密钥：
- `QWEN_API_KEY`
- `NANO_BANANA_API_KEY`

### Q: 端口被占用

**A:** 修改 `.env` 中的 `APP_PORT` 为其他端口（如 8001）

### Q: 任务一直处于 processing 状态

**A:** 可能的原因：
1. API 密钥无效 - 检查密钥是否正确
2. 网络问题 - 检查能否访问外部 API
3. API 配额不足 - 检查账户余额/配额

查看终端日志获取详细错误信息。

### Q: 生成的图片无法显示

**A:** 当前版本返回的可能是 base64 编码的 data URL。在生产环境中应该：
1. 将图片上传到 OSS/CDN
2. 返回永久的图片 URL

## 下一步

- 查看 [README.md](README.md) 了解完整的 API 文档
- 查看 [backend_api_design.md](../backend_api_design_aeef649e.plan.md) 了解架构设计
- 开始集成前端应用

## 需要帮助？

- 查看终端日志获取错误详情
- 访问 API 文档：http://localhost:8000/docs
- 检查配置文件是否正确

祝你使用愉快！🎉
