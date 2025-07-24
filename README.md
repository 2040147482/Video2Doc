# Video2Doc - 视频内容AI分析工具

一个在线 AI 工具平台，用户上传视频或粘贴视频链接后，AI 自动识别视频中的语音与图像内容，并将其结构化生成为可编辑、可导出的文档格式，如 Markdown、PDF、HTML 或在线笔记等。

## 功能特点

- 🎥 **视频输入**：支持本地上传或在线链接
- 🎯 **AI分析**：语音识别、图像识别、内容理解
- 📝 **智能摘要**：自动生成结构化摘要
- 📄 **多格式输出**：支持Markdown、PDF、HTML等格式
- 🌐 **现代化界面**：基于Next.js的响应式Web界面

## 技术栈

- **前端**：Next.js + Tailwind CSS
- **后端**：FastAPI (Python)
- **视频处理**：FFmpeg
- **语音识别**：Whisper、腾讯云、Deepgram
- **图像识别**：GPT-4V、Google Vision、Baidu OCR
- **AI摘要**：GPT-4 Turbo、Claude 3、Gemini
- **存储**：Supabase/Firebase/AWS S3

## 快速开始

### 前置要求

- Node.js 18+
- Python 3.9+
- FFmpeg

### 安装依赖

```bash
# 前端
cd frontend
npm install

# 后端
cd backend
pip install -r requirements.txt
```

### 环境配置

复制并配置环境变量：

```bash
# 前端
cp frontend/.env.example frontend/.env.local

# 后端
cp backend/.env.example backend/.env
```

### 运行项目

```bash
# 启动后端
cd backend
uvicorn main:app --reload

# 启动前端
cd frontend
npm run dev
```

## 项目结构

```
Video2Doc/
├── frontend/          # Next.js 前端
├── backend/           # FastAPI 后端
├── docs/             # 文档
├── .taskmaster/      # 任务管理配置
└── README.md
```

## 开发进度

本项目使用 TaskMaster-AI 进行任务管理。主要开发任务包括：

1. ✅ 项目基础架构搭建
2. ⏳ 视频上传功能实现
3. ⏳ 视频处理模块开发
4. ⏳ 语音识别服务集成
5. ⏳ 图像识别功能开发
6. ⏳ AI摘要生成服务
7. ⏳ 多格式输出功能
8. ⏳ 用户界面设计与开发
9. ⏳ 文件存储系统
10. ⏳ 任务队列系统

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！ 