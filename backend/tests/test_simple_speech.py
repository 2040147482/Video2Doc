import requests
import json
import wave
import numpy as np
import os

def create_test_audio():
    # 创建一个简单的WAV文件
    duration = 1.0  # 秒
    sample_rate = 16000  # 采样率
    num_samples = int(duration * sample_rate)
    
    # 生成一个简单的音调 (440Hz)
    t = np.linspace(0, duration, num_samples)
    audio = np.sin(2 * np.pi * 440 * t) * 0.5
    
    # 保存为WAV文件
    with wave.open("simple_test_audio.wav", 'w') as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16位
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    return "simple_test_audio.wav"

def test_simple_transcribe():
    """测试简化的文件转录端点"""
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-simple/transcribe",
                files=files
            )
        
        print(f"简化转录测试: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"转录文本: {data.get('text')}")
            print(f"语言: {data.get('language')}")
            print(f"状态: {data.get('status')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应为JSON")
            return False
    except Exception as e:
        print(f"简化转录测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(audio_file):
            os.remove(audio_file)

def test_simple_language_detection():
    """测试简化的语言检测端点"""
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-simple/detect-language",
                files=files
            )
        
        print(f"\n简化语言检测测试: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"检测到的语言: {data.get('language')}")
            print(f"置信度: {data.get('confidence')}")
            return True
        else:
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应为JSON")
            return False
    except Exception as e:
        print(f"简化语言检测测试失败: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    print("开始测试简化的语音识别端点...")
    
    success1 = test_simple_transcribe()
    success2 = test_simple_language_detection()
    
    if success1 and success2:
        print("\n✅ 所有简化端点测试通过！")
    else:
        print("\n❌ 部分简化端点测试失败") 