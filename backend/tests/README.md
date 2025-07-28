# Video2Doc 测试脚本

本目录包含用于测试 Video2Doc 后端 API 的各种测试脚本。

## 测试脚本列表

1. **test_api.py** - 基本 API 功能测试
   - 健康检查
   - 支持的格式
   - 处理视频 URL
   - 上传视频文件
   - 任务列表

2. **test_speech.py** - 语音识别功能测试
   - 健康检查
   - 文件转录
   - URL 转录
   - 语言检测

3. **test_speech_detailed.py** - 详细的语音识别功能测试
   - 与 test_speech.py 类似，但提供更详细的日志和结果检查

4. **test_video_upload.py** - 视频上传功能测试
   - 健康检查
   - 支持的格式
   - 处理视频 URL
   - 上传视频文件
   - 任务列表

## 运行测试

确保后端服务器正在运行（默认在 http://localhost:8000）。

### 运行单个测试脚本

```bash
# 激活虚拟环境
cd backend
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac

# 运行测试
python tests/test_api.py
python tests/test_speech.py
python tests/test_speech_detailed.py
python tests/test_video_upload.py
```

### 依赖项

测试脚本依赖以下 Python 包：

- requests
- numpy (用于生成测试音频)

如果缺少这些依赖项，请使用以下命令安装：

```bash
pip install requests numpy
```

## 注意事项

- 测试脚本会创建临时文件用于测试，测试完成后会自动清理
- 某些测试可能需要互联网连接（如 URL 处理测试）
- 确保后端服务器已正确配置并运行 