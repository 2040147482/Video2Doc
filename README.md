# Video2Doc - AI 视频内容智能分析工具

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.13+-green.svg)](https://python.org)
[![Node Version](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)

一个在线 AI 工具平台，用户上传视频或粘贴视频链接后，AI 自动识别视频中的语音与图像内容，并将其结构化生成为可编辑、可导出的文档格式，如 Markdown、PDF、HTML 或在线笔记等，适用于学习笔记、会议记录、视频摘要、内容归档等场景。

## ✨ 功能特点

### 🎯 核心功能
- **智能语音识别**: 支持多语言语音转文字，自动添加时间戳，按段落智能分割
- **图像内容分析**: 提取关键帧，OCR文字识别，图文内容智能匹配
- **多格式导出**: 支持 Markdown、PDF、HTML、TXT 等格式，一键批量导出

### 📹 视频输入
- **本地上传**: 支持 MP4、MOV、AVI、MKV、WEBM、FLV、WMV 格式，最大 2GB
- **在线链接**: 支持 YouTube、哔哩哔哩、Vimeo 等主流平台

### 🔧 技术特色
- **现代化架构**: FastAPI + Next.js，高性能异步处理
- **AI驱动**: 集成 OpenAI、Claude、Google Vision 等先进AI服务
- **响应式设计**: 支持桌面端和移动端，现代化UI/UX
- **实时进度**: WebSocket 实时反馈处理进度

## 🏗️ 技术架构

### 前端技术栈
- **框架**: Next.js 14 (App Router)
- **UI 库**: Tailwind CSS + Headless UI
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **文件上传**: react-dropzone
- **图标**: Heroicons
- **动画**: Framer Motion

### 后端技术栈
- **API 框架**: FastAPI (Python 3.13+)
- **数据验证**: Pydantic v2
- **异步处理**: Uvicorn + async/await
- **任务队列**: Celery + Redis
- **数据库**: PostgreSQL + SQLAlchemy 2.0
- **文件处理**: FFmpeg + aiofiles
- **AI 服务**: OpenAI, Anthropic, Google Vision

### AI & 服务集成
- **语音识别**: OpenAI Whisper, 腾讯云ASR, Deepgram
- **图像识别**: GPT-4V, Google Vision, 百度OCR
- **内容生成**: GPT-4 Turbo, Claude 3, Gemini
- **云存储**: AWS S3, Supabase, Firebase

## 🚀 快速开始

### 系统要求
- Python 3.13+
- Node.js 18+
- Redis (可选，用于任务队列)
- PostgreSQL (可选，生产环境)

### 1. 克隆项目
```bash
git clone https://github.com/your-username/Video2Doc.git
cd Video2Doc
```

### 2. 后端配置

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 环境配置
```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，配置必要的API密钥
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
```

#### 启动后端服务
```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 前端配置

#### 安装依赖
```bash
cd frontend
npm install
```

#### 环境配置
```bash
# 复制环境变量模板
cp env.local.example .env.local

# 配置API地址
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 启动前端服务
```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build
npm start
```

### 4. 使用 Docker（推荐）

#### 启动所有服务
```bash
# 启动完整服务栈
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 单独启动服务
```bash
# 仅启动后端
docker-compose up -d backend redis postgres

# 仅启动前端
docker-compose up -d frontend
```

## 📖 使用指南

### 基本使用流程

1. **上传视频**
   - 拖拽本地视频文件到上传区域
   - 或粘贴 YouTube、B站等平台的视频链接

2. **配置选项**
   - 选择视频语言（支持自动检测）
   - 选择输出格式（Markdown、PDF、HTML、TXT）

3. **AI 分析处理**
   - 系统自动提取音频进行语音识别
   - 提取关键帧进行图像识别
   - AI 生成结构化内容摘要

4. **下载结果**
   - 实时查看处理进度
   - 预览生成的文档内容
   - 下载所需格式的文件

### API 接口文档

启动后端服务后，访问以下地址查看完整API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 开发指南

### 项目结构
```
Video2Doc/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── config.py       # 应用配置
│   │   ├── main.py         # 应用入口
│   │   ├── models.py       # 数据模型
│   │   ├── exceptions.py   # 异常处理
│   │   ├── routers/        # API 路由
│   │   └── services/       # 业务逻辑
│   ├── requirements.txt    # Python 依赖
│   └── Dockerfile         # Docker 配置
├── frontend/               # Next.js 前端
│   ├── src/
│   │   ├── app/           # App Router 页面
│   │   ├── components/    # React 组件
│   │   └── lib/          # 工具函数
│   ├── package.json      # Node.js 依赖
│   └── Dockerfile       # Docker 配置
├── docker-compose.yml   # Docker Compose 配置
└── README.md           # 项目文档
```

### 开发建议

#### 后端开发
- 遵循 FastAPI 最佳实践
- 使用 async/await 进行异步编程
- 通过 Pydantic 进行数据验证
- 遵循 RESTful API 设计原则

#### 前端开发
- 使用 TypeScript 增强类型安全
- 遵循 React Hooks 最佳实践
- 使用 Tailwind CSS 进行样式开发
- 确保响应式设计兼容性

## 🧪 测试

### 后端测试
```bash
cd backend

# 运行API测试脚本
python ../test_api.py

# 单元测试
pytest tests/

# 代码格式检查
black . --check
flake8 .
```

### 前端测试
```bash
cd frontend

# 运行测试套件
npm test

# 构建检查
npm run build

# 代码格式检查
npm run lint
```

## 📦 部署

### 生产环境部署

#### 使用 Docker Compose（推荐）
```bash
# 生产环境配置
cp docker-compose.yml docker-compose.prod.yml

# 修改生产环境配置
# - 移除 volume 挂载
# - 配置环境变量
# - 使用生产数据库

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

#### 手动部署
```bash
# 后端部署
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 前端部署
cd frontend
npm run build
npm start
```

### 环境变量配置

关键环境变量说明：
- `OPENAI_API_KEY`: OpenAI API 密钥（必需）
- `DATABASE_URL`: 数据库连接字符串
- `REDIS_URL`: Redis 连接字符串
- `MAX_FILE_SIZE`: 最大文件大小限制
- `CORS_ORIGINS`: 允许的跨域源

## 🤝 贡献指南

欢迎提交 Pull Request 或创建 Issue！

### 开发流程
1. Fork 项目到您的 GitHub 账户
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

### 代码规范
- 后端代码遵循 PEP 8 规范
- 前端代码使用 ESLint + Prettier
- 提交信息使用 Conventional Commits 格式

## 📄 许可证

本项目基于 MIT 许可证开源。详情请查看 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- 项目地址: [https://github.com/your-username/Video2Doc](https://github.com/your-username/Video2Doc)
- 问题反馈: [GitHub Issues](https://github.com/your-username/Video2Doc/issues)
- 功能建议: [GitHub Discussions](https://github.com/your-username/Video2Doc/discussions)

## 🙏 致谢

感谢以下开源项目和服务：
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Next.js](https://nextjs.org/) - React 生产框架
- [OpenAI](https://openai.com/) - AI 语言模型服务
- [Tailwind CSS](https://tailwindcss.com/) - 实用工具优先的 CSS 框架

---

⭐ 如果这个项目对您有帮助，请给个星标支持！ 