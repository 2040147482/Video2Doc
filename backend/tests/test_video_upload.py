import os
import time
import requests
import tempfile

# 配置
API_BASE_URL = "http://localhost:8000"
TEST_VIDEO_FILE = "test_video.mp4"

def create_test_video():
    """创建测试视频文件"""
    print("创建测试视频文件...")
    
    # 创建一个简单的文件，模拟视频
    with open(TEST_VIDEO_FILE, "wb") as f:
        f.write(b"This is a test video file content")
    
    print(f"测试视频文件已创建: {TEST_VIDEO_FILE}")
    return os.path.abspath(TEST_VIDEO_FILE)

def cleanup():
    """清理测试文件"""
    try:
        if os.path.exists(TEST_VIDEO_FILE):
            os.remove(TEST_VIDEO_FILE)
            print(f"已删除测试视频文件: {TEST_VIDEO_FILE}")
    except Exception as e:
        print(f"清理文件时出错: {e}")

def test_health():
    """测试健康检查端点"""
    print("\n------------------------------")
    print("测试: 健康检查")
    print("------------------------------")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"状态: {data.get('status')}")
            print(f"版本: {data.get('version')}")
            print("✅ 健康检查测试通过")
            return True
        else:
            print(f"❌ 健康检查测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查测试失败: {str(e)}")
        return False

def test_supported_formats():
    """测试支持的格式端点"""
    print("\n------------------------------")
    print("测试: 支持的格式")
    print("------------------------------")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/video/supported-formats")
        if response.status_code == 200:
            data = response.json()
            print(f"支持的输入格式: {', '.join(data.get('input_formats', []))}")
            print(f"支持的输出格式: {', '.join(data.get('output_formats', []))}")
            print("✅ 支持的格式测试通过")
            return True
        else:
            print(f"❌ 支持的格式测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 支持的格式测试失败: {str(e)}")
        return False

def test_process_url():
    """测试处理视频URL端点"""
    print("\n------------------------------")
    print("测试: 处理视频URL")
    print("------------------------------")
    
    try:
        # 使用示例URL
        data = {
            "url": "https://example.com/sample-video.mp4",
            "options": {
                "output_format": "markdown",
                "extract_audio": True,
                "extract_frames": True,
                "frame_interval": 5,
                "language": "auto"
            }
        }
        
        response = requests.post(f"{API_BASE_URL}/api/video/process-url", json=data)
        
        if response.status_code == 200 or response.status_code == 202:
            result = response.json()
            print(f"任务ID: {result.get('task_id')}")
            print(f"状态: {result.get('status')}")
            print("✅ 处理视频URL测试通过")
            return True
        else:
            print(f"❌ 处理视频URL测试失败: {response.status_code}")
            if response.text:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 处理视频URL测试失败: {str(e)}")
        return False

def test_upload_file(video_path):
    """测试上传视频文件端点"""
    print("\n------------------------------")
    print("测试: 上传视频文件")
    print("------------------------------")
    
    try:
        print(f"上传视频文件: {os.path.basename(video_path)}")
        
        with open(video_path, "rb") as video_file:
            files = {"file": (os.path.basename(video_path), video_file, "video/mp4")}
            data = {
                "output_format": "markdown",
                "extract_audio": "true",
                "extract_frames": "true",
                "frame_interval": "5",
                "language": "auto"
            }
            response = requests.post(
                f"{API_BASE_URL}/api/video/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"任务ID: {result.get('task_id')}")
            print(f"状态: {result.get('status')}")
            print("✅ 上传视频文件测试通过")
            return True
        else:
            print(f"❌ 上传视频文件测试失败: {response.status_code}")
            if response.text:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 上传视频文件测试失败: {str(e)}")
        return False

def test_tasks():
    """测试任务列表端点"""
    print("\n------------------------------")
    print("测试: 任务列表")
    print("------------------------------")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/processing/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"任务数量: {len(tasks)}")
            if tasks:
                print(f"示例任务: ID={tasks[0].get('id')}, 状态={tasks[0].get('status')}")
            print("✅ 任务列表测试通过")
            return True
        else:
            print(f"❌ 任务列表测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 任务列表测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("视频上传功能测试")
    print("="*50)
    
    # 创建测试视频
    video_path = create_test_video()
    
    # 运行测试
    results = []
    results.append(("健康检查", test_health()))
    results.append(("支持的格式", test_supported_formats()))
    results.append(("处理视频URL", test_process_url()))
    results.append(("上传视频文件", test_upload_file(video_path)))
    results.append(("任务列表", test_tasks()))
    
    # 清理
    cleanup()
    
    # 显示结果
    print("\n"+"="*50)
    print("测试结果摘要:")
    print("="*50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        if result:
            status = "✅ 通过"
            passed += 1
        else:
            status = "❌ 失败"
            failed += 1
        
        print(f"{name}: {status}")
    
    print("\n"+"="*50)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    print("="*50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 