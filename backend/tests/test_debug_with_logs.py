"""
调试脚本：启动服务器并捕获详细日志
"""
import asyncio
import subprocess
import time
import requests
import json
import wave
import numpy as np
import os
from pathlib import Path

def create_test_audio():
    """创建测试音频文件"""
    duration = 1.0
    sample_rate = 16000
    num_samples = int(duration * sample_rate)
    
    t = np.linspace(0, duration, num_samples)
    audio = np.sin(2 * np.pi * 440 * t) * 0.5
    
    with wave.open("debug_test.wav", 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    return "debug_test.wav"

def test_endpoints():
    """测试各个端点"""
    print("等待服务器启动...")
    time.sleep(3)
    
    # 测试健康检查
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"健康检查: {response.status_code}")
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {response.text}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 测试简化的语音转录
    print("\n=== 测试简化语音转录 ===")
    audio_file = create_test_audio()
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-simple/transcribe",
                files=files,
                timeout=10
            )
        
        print(f"简化转录: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 转录成功: {data.get('text')}")
        else:
            print(f"❌ 转录失败: {response.text}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                pass
    except Exception as e:
        print(f"❌ 转录异常: {e}")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)
    
    # 测试原始语音转录
    print("\n=== 测试原始语音转录 ===")
    audio_file = create_test_audio()
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech/transcribe",
                files=files,
                timeout=10
            )
        
        print(f"原始转录: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 转录成功: {data.get('text')}")
        else:
            print(f"❌ 转录失败: {response.text}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                pass
    except Exception as e:
        print(f"❌ 转录异常: {e}")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def main():
    """主函数"""
    print("开始调试会话...")
    print("请在另一个终端中运行服务器:")
    print("cd backend")
    print(".\\venv\\Scripts\\Activate.ps1")
    print("python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level debug")
    print("\n按 Enter 键开始测试...")
    input()
    
    test_endpoints()
    
    print("\n调试完成！")

if __name__ == "__main__":
    main() 