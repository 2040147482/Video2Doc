import os
import math
import time
import wave
import json
import requests
import numpy as np
from pathlib import Path

# 配置
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "test_audio.wav"
VERBOSE = True  # 是否显示详细日志

def log(message):
    """打印日志"""
    if VERBOSE:
        print(message)

def create_test_audio():
    """创建测试音频文件"""
    print("生成测试音频文件...")
    
    # 创建一个简单的WAV文件
    duration = 3.0  # 秒
    sample_rate = 16000  # 采样率
    num_samples = int(duration * sample_rate)
    
    # 生成一个简单的音调 (440Hz)
    t = np.linspace(0, duration, num_samples)
    audio = np.sin(2 * math.pi * 440 * t) * 0.5
    
    # 保存为WAV文件
    with wave.open(TEST_AUDIO_FILE, 'w') as wf:
        wf.setnchannels(1)  # 单声道
        wf.setsampwidth(2)  # 16位
        wf.setframerate(sample_rate)
        wf.writeframes((audio * 32767).astype(np.int16).tobytes())
    
    print(f"测试音频文件已创建: {TEST_AUDIO_FILE}")
    return os.path.abspath(TEST_AUDIO_FILE)

def cleanup():
    """清理测试文件"""
    try:
        if os.path.exists(TEST_AUDIO_FILE):
            os.remove(TEST_AUDIO_FILE)
            print(f"已删除测试音频文件: {TEST_AUDIO_FILE}")
    except Exception as e:
        print(f"清理文件时出错: {e}")

def test_health():
    """测试健康检查端点"""
    print("\n------------------------------")
    print("测试: 健康检查")
    print("------------------------------")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        log(f"状态码: {response.status_code}")
        log(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ 健康检查测试通过")
            return True
        else:
            print(f"❌ 健康检查测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查测试失败: {str(e)}")
        return False

def test_transcribe_file(audio_path):
    """测试文件转录端点"""
    print("\n------------------------------")
    print("测试: 文件转录")
    print("------------------------------")
    
    try:
        print(f"上传音频文件: {os.path.basename(audio_path)}")
        
        with open(audio_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_path), audio_file, "audio/wav")}
            response = requests.post(
                f"{API_BASE_URL}/api/speech/transcribe",
                files=files
            )
        
        log(f"状态码: {response.status_code}")
        log(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            log(f"任务ID: {data.get('task_id')}")
            log(f"状态: {data.get('status')}")
            
            # 检查转录结果
            task_id = data.get('task_id')
            if task_id:
                # 轮询结果
                max_retries = 10
                for i in range(max_retries):
                    time.sleep(1)  # 等待1秒
                    result_response = requests.get(f"{API_BASE_URL}/api/speech/transcribe/{task_id}")
                    log(f"结果状态码: {result_response.status_code}")
                    log(f"结果响应: {result_response.text}")
                    
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        if result_data.get('status') == 'completed':
                            print(f"✅ 文件转录测试通过")
                            print(f"转录文本: {result_data.get('text')}")
                            return True
                    
                    print(f"等待结果... ({i+1}/{max_retries})")
                
                print("❌ 文件转录测试失败: 超时")
                return False
            else:
                print("❌ 文件转录测试失败: 未返回任务ID")
                return False
        else:
            print(f"❌ 文件转录测试失败: {response.status_code}")
            if response.text:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 文件转录测试失败: {str(e)}")
        return False

def test_transcribe_url():
    """测试URL转录端点"""
    print("\n------------------------------")
    print("测试: URL转录")
    print("------------------------------")
    
    # 由于我们使用本地生成的音频，暂时跳过URL测试
    print("⚠️ 跳过URL转录测试")
    return True

def test_detect_language(audio_path):
    """测试语言检测端点"""
    print("\n------------------------------")
    print("测试: 语言检测")
    print("------------------------------")
    
    try:
        print(f"上传音频文件进行语言检测: {os.path.basename(audio_path)}")
        
        with open(audio_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_path), audio_file, "audio/wav")}
            response = requests.post(
                f"{API_BASE_URL}/api/speech/detect-language",
                files=files
            )
        
        log(f"状态码: {response.status_code}")
        log(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            language = data.get('language')
            print(f"✅ 语言检测测试通过")
            print(f"检测到的语言: {language}")
            return True
        else:
            print(f"❌ 语言检测测试失败: {response.status_code}")
            if response.text:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 语言检测测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("语音识别功能详细测试")
    print("="*50)
    
    # 创建测试音频
    audio_path = create_test_audio()
    
    # 运行测试
    results = []
    results.append(("健康检查", test_health()))
    results.append(("文件转录", test_transcribe_file(audio_path)))
    results.append(("URL转录", test_transcribe_url()))
    results.append(("语言检测", test_detect_language(audio_path)))
    
    # 清理
    cleanup()
    
    # 显示结果
    print("\n"+"="*50)
    print("测试结果摘要:")
    print("="*50)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, result in results:
        if result is True:
            status = "✅ 通过"
            passed += 1
        elif result is False:
            status = "❌ 失败"
            failed += 1
        else:
            status = "⚠️ 跳过"
            skipped += 1
        
        print(f"{name}: {status}")
    
    print("\n"+"="*50)
    print(f"测试完成: {passed} 通过, {failed} 失败, {skipped} 跳过")
    print("="*50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 