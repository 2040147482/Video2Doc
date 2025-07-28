import os
import requests
import tempfile

# 配置
API_BASE_URL = "http://localhost:8000"
TEMP_FILE = "test_video.mp4"

def test_health():
    """测试健康检查端点"""
    print("\n------------------------------")
    print("测试: 健康检查")
    print("------------------------------")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
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
            formats = response.json()
            print(f"支持的输入格式: {formats.get('input_formats')}")
            print(f"支持的输出格式: {formats.get('output_formats')}")
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
        # 使用示例URL (不是真实视频)
        data = {"url": "https://example.com/sample-video.mp4"}
        response = requests.post(f"{API_BASE_URL}/api/video/process-url", json=data)
        
        if response.status_code == 200 or response.status_code == 202:
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

def test_upload_file():
    """测试上传视频文件端点"""
    print("\n------------------------------")
    print("测试: 上传视频文件")
    print("------------------------------")
    
    try:
        # 创建一个临时视频文件
        with open(TEMP_FILE, "wb") as f:
            f.write(b"This is a test video file")
        
        print(f"创建测试文件: {TEMP_FILE}")
        
        with open(TEMP_FILE, "rb") as f:
            files = {"file": (TEMP_FILE, f, "video/mp4")}
            response = requests.post(f"{API_BASE_URL}/api/video/upload", files=files)
        
        # 删除临时文件
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
            print(f"已删除测试文件: {TEMP_FILE}")
        
        if response.status_code == 200:
            print("✅ 上传视频文件测试通过")
            return True
        else:
            print(f"❌ 上传视频文件测试失败: {response.status_code}")
            if response.text:
                print(response.text)
            return False
    except Exception as e:
        print(f"❌ 上传视频文件测试失败: {str(e)}")
        # 确保清理临时文件
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
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
    print("API功能测试")
    print("="*50)
    
    # 运行测试
    tests_passed = 0
    tests_failed = 0
    
    # 测试健康检查
    if test_health():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 测试支持的格式
    if test_supported_formats():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 测试处理视频URL
    if test_process_url():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 测试上传视频文件
    if test_upload_file():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 测试任务列表
    if test_tasks():
        tests_passed += 1
    else:
        tests_failed += 1
    
    print("\n" + "="*50)
    print(f"测试完成: {tests_passed} 通过, {tests_failed} 失败")
    print("="*50)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 