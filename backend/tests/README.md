# 测试文件说明

本目录包含Video2Doc项目的所有测试文件，按功能模块进行分类组织。

## 📁 测试文件分类

### 🔄 导出功能测试 (Export Tests)
- `test_export.py` - 完整的导出功能测试，包含多格式导出、状态跟踪、文件下载
- `test_export_quick.py` - 快速的导出API基础测试

### 📝 摘要功能测试 (Summary Tests)  
- `test_summary.py` - 完整的摘要服务测试
- `test_simple_summary.py` - 摘要服务集成测试
- `test_complete_summary.py` - 完整工作流测试
- `test_direct_summary.py` - 直接摘要服务调用测试
- `test_summary_simple.py` - 简化的摘要API测试
- `test_summary_debug.py` - 摘要功能调试测试

### 🎤 语音识别测试 (Speech Tests)
- `test_speech.py` - 语音识别主要测试
- `test_speech_detailed.py` - 详细的语音识别测试
- `test_simple_speech.py` - 简化的语音识别测试
- `test_speech_ultra_simple.py` - 超简化的语音识别测试
- `test_speech_debug.py` - 语音识别调试测试

### 🖼️ 图像识别测试 (Image Tests)
- `test_image_recognition.py` - 完整的图像识别测试
- `test_direct_image.py` - 直接图像服务调用测试
- `test_simple_image.py` - 简化的图像识别测试
- `test_image_debug.py` - 图像识别调试测试

### 📤 视频上传测试 (Upload Tests)
- `test_video_upload.py` - 视频上传功能测试

### 🌐 API集成测试 (API Tests)
- `test_api.py` - 通用API接口测试

### 🐛 调试和诊断测试 (Debug Tests)
- `test_app_debug.py` - 应用程序调试测试
- `test_debug_with_logs.py` - 带日志的调试测试
- `test_simple_debug.py` - 简单调试测试

### 📂 测试资源 (Test Assets)
- `test_assets/` - 包含测试用的音频、视频等资源文件
  - `test_audio.wav` - 测试音频文件
  - `test_video.mp4` - 测试视频文件 (如存在)

### 🔧 测试工具 (Test Utilities)
- `run_all_tests.py` - 批量运行所有测试的脚本
- `__init__.py` - Python包初始化文件

## 🚀 运行测试

### 运行所有测试
```bash
python run_all_tests.py
```

### 运行特定功能测试
```bash
# 导出功能测试
python test_export.py

# 摘要功能测试  
python test_summary.py

# 语音识别测试
python test_speech.py

# 图像识别测试
python test_image_recognition.py
```

### 快速验证测试
```bash
# 快速API测试
python test_export_quick.py
python test_summary_simple.py
python test_speech_ultra_simple.py
```

## 📋 测试规范

### 新增测试文件命名规范
- **主要功能测试**: `test_{功能名}.py` (如 `test_export.py`)
- **简化测试**: `test_{功能名}_simple.py` 
- **调试测试**: `test_{功能名}_debug.py`
- **直接服务测试**: `test_direct_{功能名}.py`
- **快速测试**: `test_{功能名}_quick.py`

### 测试文件结构要求
1. 每个测试文件应包含详细的文档字符串
2. 包含必要的错误处理和日志输出
3. 测试结果应有明确的成功/失败指示
4. 包含适当的超时设置防止测试挂起

### 测试资源管理
- 所有测试用的媒体文件放在 `test_assets/` 目录
- 测试生成的临时文件应在测试结束后清理
- 避免测试文件过大，影响代码仓库体积

## 🔍 测试状态

| 功能模块 | 主要测试 | 状态 | 说明 |
|---------|---------|------|-----|
| 导出功能 | test_export.py | ✅ | 多格式导出已通过测试 |
| 摘要服务 | test_summary.py | ✅ | AI摘要生成已通过测试 |
| 语音识别 | test_speech.py | ✅ | 语音转文字已通过测试 |
| 图像识别 | test_image_recognition.py | ✅ | 图像分析已通过测试 |
| 视频上传 | test_video_upload.py | ✅ | 文件上传已通过测试 |
| API接口 | test_api.py | ✅ | 基础API已通过测试 |

## 🎯 持续改进

- 定期更新测试用例覆盖新功能
- 优化测试执行效率
- 增加边界情况和错误场景测试
- 维护测试数据的时效性 