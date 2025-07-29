# Video2Doc 测试套件

这个目录包含了Video2Doc项目的所有测试脚本，按功能模块分类组织。

## 📁 测试文件组织结构

### 🎯 导出功能测试 (Export Tests)
- `test_export.py` - 完整的多格式导出功能测试
- `test_export_quick.py` - 快速导出API测试

### 📝 摘要生成测试 (Summary Tests)
- `test_summary_simple.py` - 简化的摘要生成测试
- `test_complete_summary.py` - 完整的摘要生成流程测试

### 🗣️ 语音识别测试 (Speech Recognition Tests)
- `test_speech.py` - 完整的语音识别功能测试
- `test_speech_detailed.py` - 详细的语音识别测试
- `test_ultra_simple.py` - 最简化的语音识别测试

### 🖼️ 图像识别测试 (Image Recognition Tests)
- `test_image_recognition.py` - 完整的图像识别测试
- `test_simple_image.py` - 简化的图像识别测试
- `test_direct_image.py` - 直接图像处理测试

### 🎥 视频处理测试 (Video Processing Tests)
- `test_video_upload.py` - 视频上传功能测试

### 🌐 API集成测试 (API Tests)
- `test_api.py` - 通用API接口测试

### ⚙️ 队列管理测试 (Queue Management Tests)
- `test_queue_simple.py` - 简化的队列系统测试
- `test_queue_full.py` - 完整的队列系统测试 (待实现)

### 💳 支付功能测试 (Payment Tests)
- `test_payments.py` - Creem支付集成测试

### ☁️ 云存储测试 (Cloud Storage Tests)
- `test_cloud_storage.py` - 云存储功能测试
- `test_simple_storage.py` - 简化的存储测试
- `test_storage_api.py` - 存储API接口测试

### 🐛 调试和诊断测试 (Debug Tests)
- `test_app_debug.py` - 应用程序调试测试
- `test_debug_with_logs.py` - 带日志的调试测试
- `test_structure.py` - 测试文件结构验证

## 🚀 如何运行测试

### 运行所有测试
```bash
cd backend
python tests/run_all_tests.py
```

### 运行特定测试
```bash
cd backend
# 导出功能测试
python tests/test_export.py

# 支付功能测试
python tests/test_payments.py

# 语音识别测试
python tests/test_speech.py

# 图像识别测试
python tests/test_image_recognition.py

# 摘要生成测试
python tests/test_summary_simple.py

# 云存储测试
python tests/test_cloud_storage.py

# 队列管理测试
python tests/test_queue_simple.py
```

### 快速测试（推荐用于开发调试）
```bash
cd backend
# 快速导出测试
python tests/test_export_quick.py

# 快速API测试
python tests/test_export_quick.py
python tests/test_summary_simple.py
python tests/test_speech_ultra_simple.py 

# 快速队列测试
python tests/test_queue_simple.py

# 快速支付测试
python tests/test_payments.py
```

## 📋 测试前准备

### 1. 环境准备
确保后端服务正在运行：
```bash
cd backend
# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# 启动后端服务
python main.py
```

### 2. 配置文件
确保以下配置文件正确设置：
- `.env` - 环境变量配置（包含API密钥等）
- `app/config.py` - 应用配置

### 3. 支付测试配置
支付功能测试需要Creem API密钥：
```bash
# 在.env文件中设置
CREEM_API_KEY=your-creem-api-key
CREEM_WEBHOOK_SECRET=your-webhook-secret
```

## 🎯 测试覆盖说明

- ✅ **基础API接口测试** - 所有核心API端点
- ✅ **文件上传测试** - 视频文件上传功能
- ✅ **语音识别测试** - 音频转文字功能
- ✅ **图像识别测试** - 关键帧提取功能
- ✅ **摘要生成测试** - AI摘要生成功能
- ✅ **多格式导出测试** - Markdown/PDF/HTML/TXT/ZIP导出
- ✅ **云存储测试** - 本地和S3存储功能
- ✅ **任务队列测试** - Celery异步任务处理
- ✅ **支付集成测试** - Creem支付平台集成
- ⏳ **用户认证测试** - 待实现
- ⏳ **权限管理测试** - 待实现

## 🔧 故障排除

### 常见问题

1. **服务未启动**
   ```
   Error: ConnectionError or HTTPConnectionPool
   ```
   解决：确保后端服务在 http://localhost:8000 运行

2. **依赖包缺失**
   ```
   Error: ModuleNotFoundError
   ```
   解决：运行 `pip install -r requirements.txt`

3. **API密钥未配置**
   ```
   Error: 支付服务错误
   ```
   解决：在.env文件中配置正确的API密钥

4. **端口被占用**
   ```
   Error: Address already in use
   ```
   解决：更改端口或停止占用端口的进程

### 获取帮助
如果遇到测试问题，请检查：
1. 后端服务日志
2. 测试脚本输出的详细错误信息
3. 网络连接和防火墙设置
4. API密钥和配置文件

## 📊 测试报告
运行 `run_all_tests.py` 后会生成测试报告，包含：
- 测试通过/失败统计
- 执行时间
- 错误详情
- 性能指标 