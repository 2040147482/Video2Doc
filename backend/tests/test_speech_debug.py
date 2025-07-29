import requests
import json

# 创建测试音频文件
import wave
import numpy as np

def create_test_audio():
    # 创建一个简单的WAV文件
    duration = 3.0  # 秒
    sample_rate = 16000  # 采样率
    num_samples = int(duration * sample_rate)
    
    # 生成一个简单的音调 (440Hz)
    t = np.linspace(0, duration, num_samples)
    audio = np.sin(2 * np.pi * 440 * t) * 0.5
    
    # 保存为WAV文件
    with wave.open("debug_audio.wav", 'w') as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16位
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    return "debug_audio.wav"

def test_health():
    """测试健康检查端点"""
    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"健康检查: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_transcribe():
    """测试文件转录端点"""
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech/transcribe",
                files=files
            )
        
        print(f"转录测试: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code != 200:
            # 尝试获取详细错误信息
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应为JSON")
        
        return response.status_code == 200
    except Exception as e:
        print(f"转录测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        import os
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    print("开始调试语音识别端点...")
    
    if test_health():
        print("健康检查通过，继续测试转录...")
        test_transcribe()
    else:
        print("健康检查失败，停止测试") 