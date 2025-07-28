"""
测试语音识别功能
"""

import os
import sys
import asyncio
import requests
import json
import time
from pathlib import Path

# 测试配置
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_URL = "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"  # 公开测试音频
TEST_AUDIO_FILE = "test_audio.mp3"  # 本地测试文件名

def create_test_audio():
    """创建测试音频文件"""
    if os.path.exists(TEST_AUDIO_FILE):
        print(f"测试音频文件已存在: {TEST_AUDIO_FILE}")
        return True
    
    try:
        # 下载测试音频
        print(f"下载测试音频: {TEST_AUDIO_URL}")
        response = requests.get(TEST_AUDIO_URL)
        if response.status_code != 200:
            print(f"下载测试音频失败: {response.status_code}")
            return False
        
        # 保存为本地文件
        with open(TEST_AUDIO_FILE, "wb") as f:
            f.write(response.content)
        
        print(f"测试音频文件已创建: {TEST_AUDIO_FILE}")
        return True
    except Exception as e:
        print(f"创建测试音频文件失败: {str(e)}")
        return False

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查测试通过")
            return True
        else:
            print(f"❌ 健康检查测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查测试异常: {str(e)}")
        return False

def test_transcribe_file():
    """测试文件转录"""
    try:
        if not os.path.exists(TEST_AUDIO_FILE):
            print(f"❌ 测试音频文件不存在: {TEST_AUDIO_FILE}")
            return False
        
        print(f"上传音频文件: {TEST_AUDIO_FILE}")
        with open(TEST_AUDIO_FILE, "rb") as f:
            files = {"file": (TEST_AUDIO_FILE, f, "audio/mpeg")}
            data = {
                "language": None,
                "model": "whisper-1",
                "with_timestamps": "true"
            }
            response = requests.post(
                f"{API_BASE_URL}/api/speech/transcribe", 
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"转录任务已创建: {task_id}")
            
            # 轮询任务状态
            max_retries = 10
            for i in range(max_retries):
                time.sleep(2)  # 等待2秒
                status_response = requests.get(f"{API_BASE_URL}/api/speech/transcribe/{task_id}")
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get("text") != "转录中...":
                        print(f"转录完成: {status_result.get('text')[:50]}...")
                        print(f"✅ 文件转录测试通过")
                        return True
                    print(f"转录进行中... ({i+1}/{max_retries})")
                else:
                    print(f"❌ 获取转录状态失败: {status_response.status_code}")
                    return False
            
            print("❌ 转录超时")
            return False
        else:
            print(f"❌ 文件转录测试失败: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 文件转录测试异常: {str(e)}")
        return False

def test_transcribe_url():
    """测试URL转录"""
    try:
        print(f"转录音频URL: {TEST_AUDIO_URL}")
        data = {
            "url": TEST_AUDIO_URL
        }
        response = requests.post(f"{API_BASE_URL}/api/speech/transcribe/url", data=data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"转录任务已创建: {task_id}")
            
            # 轮询任务状态
            max_retries = 10
            for i in range(max_retries):
                time.sleep(2)  # 等待2秒
                status_response = requests.get(f"{API_BASE_URL}/api/speech/transcribe/{task_id}")
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get("text") != "转录中...":
                        print(f"转录完成: {status_result.get('text')[:50]}...")
                        print(f"✅ URL转录测试通过")
                        return True
                    print(f"转录进行中... ({i+1}/{max_retries})")
                else:
                    print(f"❌ 获取转录状态失败: {status_response.status_code}")
                    return False
            
            print("❌ 转录超时")
            return False
        else:
            print(f"❌ URL转录测试失败: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ URL转录测试异常: {str(e)}")
        return False

def test_detect_language():
    """测试语言检测"""
    try:
        if not os.path.exists(TEST_AUDIO_FILE):
            print(f"❌ 测试音频文件不存在: {TEST_AUDIO_FILE}")
            return False
        
        print(f"上传音频文件进行语言检测: {TEST_AUDIO_FILE}")
        with open(TEST_AUDIO_FILE, "rb") as f:
            files = {"file": (TEST_AUDIO_FILE, f, "audio/mpeg")}
            response = requests.post(f"{API_BASE_URL}/api/speech/detect-language", files=files)
        
        if response.status_code == 200:
            result = response.json()
            language = result.get("language")
            print(f"检测到的语言: {language}")
            print(f"✅ 语言检测测试通过")
            return True
        else:
            print(f"❌ 语言检测测试失败: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 语言检测测试异常: {str(e)}")
        return False

def cleanup():
    """清理测试文件"""
    try:
        if os.path.exists(TEST_AUDIO_FILE):
            os.remove(TEST_AUDIO_FILE)
            print(f"已删除测试音频文件: {TEST_AUDIO_FILE}")
    except Exception as e:
        print(f"清理测试文件失败: {str(e)}")

def main():
    """主函数"""
    print("=" * 50)
    print("语音识别功能测试")
    print("=" * 50)
    
    # 创建测试音频文件
    if not create_test_audio():
        print("创建测试音频文件失败，测试终止")
        return
    
    # 运行测试
    tests = [
        ("健康检查", test_health),
        ("文件转录", test_transcribe_file),
        ("URL转录", test_transcribe_url),
        ("语言检测", test_detect_language)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print("\n" + "-" * 30)
        print(f"测试: {name}")
        print("-" * 30)
        
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            failed += 1
    
    # 清理测试文件
    cleanup()
    
    # 打印测试结果
    print("\n" + "=" * 50)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    # 返回退出码
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 