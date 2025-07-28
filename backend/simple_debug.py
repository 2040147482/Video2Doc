import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """测试所有导入"""
    print("测试导入...")
    
    try:
        from app.services.file_service import file_service
        print("✅ file_service 导入成功")
    except Exception as e:
        print(f"❌ file_service 导入失败: {e}")
        return False
    
    try:
        from app.services.speech_recognition import default_service
        print("✅ speech_recognition 导入成功")
    except Exception as e:
        print(f"❌ speech_recognition 导入失败: {e}")
        return False
    
    try:
        from app.services.queue_service import queue_service
        print("✅ queue_service 导入成功")
    except Exception as e:
        print(f"❌ queue_service 导入失败: {e}")
        return False
    
    try:
        from app.config import get_settings
        settings = get_settings()
        print("✅ settings 导入成功")
    except Exception as e:
        print(f"❌ settings 导入失败: {e}")
        return False
    
    return True

async def test_speech_service():
    """测试语音识别服务"""
    print("\n测试语音识别服务...")
    
    try:
        from app.services.speech_recognition import default_service
        
        # 创建测试音频文件
        import wave
        import numpy as np
        
        # 创建一个简单的WAV文件
        duration = 1.0  # 秒
        sample_rate = 16000  # 采样率
        num_samples = int(duration * sample_rate)
        
        # 生成一个简单的音调 (440Hz)
        t = np.linspace(0, duration, num_samples)
        audio = np.sin(2 * np.pi * 440 * t) * 0.5
        
        # 保存为WAV文件
        test_file = "simple_test.wav"
        with wave.open(test_file, 'w') as wf:
            wf.setnchannels(1)  # 单声道
            wf.setsampwidth(2)  # 16位
            wf.setframerate(sample_rate)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        
        print(f"✅ 创建测试音频文件: {test_file}")
        
        # 测试转录
        result = await default_service.transcribe(test_file)
        print(f"✅ 转录成功: {result.text}")
        
        # 清理文件
        os.unlink(test_file)
        print("✅ 清理测试文件")
        
        return True
    except Exception as e:
        print(f"❌ 语音识别服务测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("开始简单调试测试...")
    
    if not await test_imports():
        print("导入测试失败，停止")
        return
    
    if not await test_speech_service():
        print("语音识别服务测试失败")
        return
    
    print("\n✅ 所有测试通过！")

if __name__ == "__main__":
    asyncio.run(main()) 