# Nano Flow Backend

基于 FastAPI 的后端 API 服务，为 Nano Flow 可爱风格流程图生成提供核心功能。

## 技术栈

- **FastAPI** - 现代、高性能的 Web 框架
- **Pydantic** - 数据验证和设置管理
- **千问 LLM** - 智能提示词增强
- **GRSAI API** - Nano Banana Pro 图像生成（国内直连）
- **Loguru** - 日志管理

## 功能模块

### 核心功能 (P0) ✅

- ✅ 流程图生成 API (`POST /api/v1/generate`)
- ✅ VS 对比图生成 API (`POST /api/v1/generate-vs`)
- ✅ 任务状态查询 (`GET /api/v1/generate/{task_id}`)
- ✅ 自动生成步骤 (`POST /api/v1/generate/generate-steps`)
- ✅ 提示词智能增强（基于千问 LLM）
- ✅ 图像生成（GRSAI API + Nano Banana Pro）
- ✅ 实时进度跟踪
- ✅ 异步任务处理
- ✅ 健康检查接口

### 增强功能 (P1) - 待实现

- ⏳ 智能填充 (`POST /api/v1/smart-fill`)
- ⏳ 历史记录管理 (`GET /api/v1/history`)
- ⏳ 自定义提示词编辑 (`POST /api/v1/generate/custom-prompt`)
- ⏳ 图片下载和格式转换 (`GET /api/v1/download/{task_id}`)

## 目录结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   │
│   ├── api/                 # API 路由层
│   │   └── v1/
│   │       ├── generate.py     # 流程图生成接口
│   │       └── generate_vs.py  # VS 对比图生成接口
│   │
│   ├── schemas/             # Pydantic 数据模型
│   │   ├── common.py        # 通用模型
│   │   ├── generate.py      # 生成相关模型
│   │   ├── generate_vs.py   # VS 对比图模型
│   │   ├── task.py          # 任务状态模型
│   │   └── visual.py        # 视觉偏好模型
│   │
│   ├── services/            # 业务逻辑层
│   │   ├── llm_service.py       # LLM 服务（千问）
│   │   ├── prompt_builder.py    # 提示词构造器
│   │   └── image_generator.py   # 图像生成服务
│   │
│   └── core/                # 核心功能模块
│       └── task_manager.py  # 任务管理器
│
├── run.py                   # 启动脚本
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
├── example.http            # HTTP 请求示例
├── README.md
└── GENERATE_VS_API.md      # VS 对比图 API 文档
```

## 快速开始

### 1. 安装依赖

```bash
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

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 必填项 - API 密钥
QWEN_API_KEY=your_qwen_api_key_here
GRSAI_API_KEY=your_grsai_api_key_here

# 可选配置
APP_ENV=development
APP_DEBUG=True
APP_PORT=8000
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# GRSAI 图像生成配置（可选）
GRSAI_MODEL=nano-banana-pro
GRSAI_IMAGE_SIZE=1K
GRSAI_ASPECT_RATIO=auto
```

### 3. 启动服务

```bash
# 方式 1: 使用启动脚本（推荐）
python run.py

# 方式 2: 使用 uvicorn 直接启动
uvicorn app.main:app --reload --port 8000
```

服务将运行在 `http://localhost:8000`

### 4. 访问文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 使用示例

### 创建生成任务

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**响应：**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "正在分析需求... 🧠"
}
```

### 查询任务状态

```bash
curl "http://localhost:8000/api/v1/generate/550e8400-e29b-41d4-a716-446655440000"
```

**响应（处理中）：**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "message": "正在绘制可爱的角色... 🎨",
  "estimated_time": 30
}
```

**响应（完成）：**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "message": "生成完成！ ✨",
  "result": {
    "image_url": "https://cdn.example.com/images/xxx.png",
    "thumbnail_url": "https://cdn.example.com/images/xxx_thumb.png",
    "enhanced_prompt": "Process infographic: \"如何制作美味拿铁\"...",
    "metadata": {
      "resolution": "1344x768",
      "seed": 42,
      "model_version": "nano-banana-pro-v1",
      "cfg_scale": 7.5,
      "sampling_steps": 20
    }
  }
}
```

### VS 对比图生成

**创建 VS 对比图任务：**

```bash
curl -X POST "http://localhost:8000/api/v1/generate-vs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "不好的学习方法 vs 好的学习方法",
    "left_scenario": {
      "title": "不好的学习方法",
      "description": "被动、枯燥、混乱、疲惫"
    },
    "right_scenario": {
      "title": "好的学习方法",
      "description": "主动、清晰、轻松"
    },
    "actions": [
      "设定目标",
      "深度理解",
      "主动输出",
      "定期复盘"
    ],
    "visual_preferences": {
      "character": "bear",
      "color_scheme": "pastel",
      "custom_tags": ["kawaii", "flat"]
    }
  }'
```

**查询 VS 对比图任务状态：**

```bash
curl "http://localhost:8000/api/v1/generate-vs/550e8400-e29b-41d4-a716-446655440000"
```

> 详细的 VS 对比图 API 文档请参考 [GENERATE_VS_API.md](./GENERATE_VS_API.md)

### 健康检查

```bash
curl "http://localhost:8000/health"
```

**响应：**

```json
{
  "status": "healthy",
  "config": {
    "qwen_configured": true,
    "nano_banana_configured": true
  },
  "environment": "development"
}
```

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `QWEN_API_KEY` | 千问 API 密钥 | - | ✅ |
| `GRSAI_API_KEY` | GRSAI API 密钥 | - | ✅ |
| `QWEN_API_BASE` | 千问 API 基础 URL | https://dashscope.aliyuncs.com/compatible-mode/v1 | ❌ |
| `GRSAI_API_BASE` | GRSAI API 基础 URL | https://grsai.dakka.com.cn | ❌ |
| `GRSAI_MODEL` | GRSAI 模型名称 | nano-banana-pro | ❌ |
| `GRSAI_IMAGE_SIZE` | 图片大小 (1K/2K/4K) | 1K | ❌ |
| `GRSAI_ASPECT_RATIO` | 图片比例 | auto | ❌ |
| `APP_ENV` | 运行环境 | development | ❌ |
| `APP_DEBUG` | 调试模式 | True | ❌ |
| `APP_HOST` | 服务主机 | 0.0.0.0 | ❌ |
| `APP_PORT` | 服务端口 | 8000 | ❌ |
| `CORS_ORIGINS` | CORS 允许的源 | ["http://localhost:5173"] | ❌ |
| `DEFAULT_IMAGE_WIDTH` | 默认图片宽度 | 1344 | ❌ |
| `DEFAULT_IMAGE_HEIGHT` | 默认图片高度 | 768 | ❌ |
| `DEFAULT_STEPS` | 默认采样步数 | 20 | ❌ |
| `DEFAULT_CFG_SCALE` | 默认 CFG scale | 7.5 | ❌ |

### 视觉偏好选项

**角色类型（character）：**
- `bear` - 白色小熊
- `cat` - 橙色小猫
- `rabbit` - 粉色兔子
- `dog` - 棕色小狗
- `panda` - 熊猫
- `random` - 随机选择

**配色方案（color_scheme）：**
- `pastel` - 马卡龙色（柔和粉、蓝、绿、紫）
- `tech_blue` - 科技蓝（蓝、青、紫渐变）
- `warm_orange` - 暖橙色（橙、珊瑚、桃、黄）
- `mint_green` - 薄荷绿（薄荷、青、鼠尾草、青柠）
- `pink_purple` - 粉紫色（粉、品红、紫、紫罗兰）
- `random` - 随机选择

## 架构设计

### 异步任务流程

```
客户端 → POST /api/v1/generate
         ↓
    创建任务（返回 task_id）
         ↓
    后台任务开始处理：
    1. 解析用户输入
    2. LLM 增强提示词
    3. 调用图像生成 API
    4. 创建缩略图
    5. 更新任务状态
         ↓
客户端 ← GET /api/v1/generate/{task_id}
    （轮询获取进度和结果）
```

### 提示词构造流程

```
用户输入（标题 + 步骤）
    ↓
LLM 增强每个步骤的视觉描述
    ↓
组装完整提示词：
  - 布局提示（horizontal/grid）
  - 风格标签（kawaii, flat）
  - 角色和配色
  - 质量标签
    ↓
生成图像
```

## 开发指南

### 添加新的 API 端点

1. **定义数据模型** (`app/schemas/`)
   ```python
   class NewFeatureRequest(BaseModel):
       field1: str
       field2: int
   ```

2. **实现业务逻辑** (`app/services/`)
   ```python
   class NewFeatureService:
       async def process(self, data):
           # 业务逻辑
           pass
   ```

3. **创建路由处理器** (`app/api/v1/`)
   ```python
   @router.post("/new-feature")
   async def new_feature(request: NewFeatureRequest):
       # 处理请求
       pass
   ```

4. **注册路由** (`app/main.py`)
   ```python
   from .api.v1 import new_feature
   app.include_router(new_feature.router, prefix="/api/v1")
   ```

### 代码规范

- ✅ 使用类型注解（Type Hints）
- ✅ 编写清晰的文档字符串（Docstrings）
- ✅ 保持函数简洁（单一职责原则）
- ✅ 使用 `logger` 记录关键操作和错误
- ✅ 异常处理要完善（try-except）
- ✅ 配置项使用环境变量管理

### 测试

```bash
# 运行测试（待实现）
pytest tests/

# 测试覆盖率
pytest --cov=app tests/
```

## 故障排查

### 常见问题

**Q: 启动时报错 "Field required"**

A: 检查 `.env` 文件是否正确配置了必填的 API 密钥（`QWEN_API_KEY` 和 `NANO_BANANA_API_KEY`）

**Q: 生成任务一直处于 processing 状态**

A: 
1. 检查网络连接是否正常
2. 验证 API 密钥是否有效
3. 查看控制台日志获取详细错误信息
4. 确认 API 配额是否充足

**Q: 图片生成失败（status: failed）**

A:
1. 检查 GRSAI 账户积分余额
2. 验证提示词是否包含违规内容
3. 查看错误详情：`GET /api/v1/generate/{task_id}` 中的 `error` 字段
4. 常见错误：
   - `输出内容违规` - 修改提示词
   - `输入内容违规` - 检查提示词
   - `任务超时` - 重试或减小图片尺寸

**Q: CORS 错误**

A: 在 `.env` 中添加前端 URL 到 `CORS_ORIGINS`：
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

**Q: 端口被占用**

A: 修改 `.env` 中的 `APP_PORT` 或使用其他端口启动：
```bash
uvicorn app.main:app --port 8001
```

### 日志查看

应用使用 `loguru` 进行日志记录，日志会输出到控制台。关键日志包括：

- 🚀 应用启动信息
- 📝 任务创建和状态更新
- 🎨 LLM 调用和提示词生成
- 🖼️ 图像生成过程
- ❌ 错误和异常信息

## 性能优化

当前实现使用内存存储任务状态，适合开发和小规模部署。对于生产环境，建议：

1. **使用 Redis** 存储任务状态（替换 `TaskManager`）
2. **使用 Celery** 处理异步任务（替换 `BackgroundTasks`）
3. **使用数据库** 持久化历史记录
4. **使用 CDN** 存储生成的图片
5. **添加缓存** 避免重复生成相同内容

## 下一步计划

- [ ] 实现 P1 功能（智能填充、历史记录等）
- [ ] 添加用户认证和授权
- [ ] 集成 Redis 和 Celery
- [ ] 添加数据库支持（PostgreSQL）
- [ ] 实现图片上传到 OSS/CDN
- [ ] 添加单元测试和集成测试
- [ ] 性能监控和日志分析
- [ ] Docker 容器化部署

## License

MIT
