import requests
import json
import wave
import numpy as np
import os

def create_test_audio():
    # 创建一个简单的WAV文件
    duration = 1.0
    sample_rate = 16000
    num_samples = int(duration * sample_rate)
    
    t = np.linspace(0, duration, num_samples)
    audio = np.sin(2 * np.pi * 440 * t) * 0.5
    
    with wave.open("ultra_test_audio.wav", 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    return "ultra_test_audio.wav"

def test_basic():
    """测试基本端点"""
    print("=== 1. 测试基本端点 ===")
    try:
        response = requests.post("http://localhost:8000/api/speech-ultra-simple/test")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"基本测试失败: {e}")
        return False

def test_file_upload():
    """测试文件上传"""
    print("\n=== 2. 测试文件上传 ===")
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-ultra-simple/file-upload-test",
                files=files
            )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"文件上传测试失败: {e}")
        return False
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def test_file_service():
    """测试文件服务"""
    print("\n=== 3. 测试文件服务 ===")
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-ultra-simple/file-service-test",
                files=files
            )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应")
        
        return response.status_code == 200
    except Exception as e:
        print(f"文件服务测试失败: {e}")
        return False
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def test_speech_service():
    """测试语音服务"""
    print("\n=== 4. 测试语音服务 ===")
    audio_file = create_test_audio()
    
    try:
        with open(audio_file, "rb") as f:
            files = {"file": (audio_file, f, "audio/wav")}
            response = requests.post(
                "http://localhost:8000/api/speech-ultra-simple/speech-service-test",
                files=files
            )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应")
        
        return response.status_code == 200
    except Exception as e:
        print(f"语音服务测试失败: {e}")
        return False
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def main():
    print("开始超级简化端点诊断测试...")
    
    tests = [
        ("基本端点", test_basic),
        ("文件上传", test_file_upload),
        ("文件服务", test_file_service),
        ("语音服务", test_speech_service)
    ]
    
    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))
        
        if not success:
            print(f"\n❌ {name} 测试失败，停止后续测试")
            break
        else:
            print(f"✅ {name} 测试通过")
    
    print("\n" + "="*50)
    print("诊断结果摘要:")
    print("="*50)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    # 找到失败的第一个测试
    for i, (name, success) in enumerate(results):
        if not success:
            print(f"\n问题出现在: {name}")
            break
    else:
        print("\n✅ 所有测试都通过了！")

if __name__ == "__main__":
    main() 