"""
存储API测试脚本
测试云存储相关的API接口
"""

import requests
import tempfile
from pathlib import Path

# API基础URL
BASE_URL = "http://localhost:8000/api"


def create_test_file(content: str = "API测试文件内容", filename: str = "api_test.txt") -> Path:
    """创建测试文件"""
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / filename
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return test_file


def test_storage_health():
    """测试存储健康检查"""
    print("🔍 测试存储健康检查...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 存储健康检查通过: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ 存储健康检查失败: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 存储健康检查连接失败: {e}")
        return False


def test_storage_stats():
    """测试存储统计"""
    print("📊 测试存储统计...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 存储统计成功: {data.get('storage_type')}, 文件数: {data.get('total_files', 0)}")
            return True
        else:
            print(f"❌ 存储统计失败: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 存储统计连接失败: {e}")
        return False


def test_file_list():
    """测试文件列表"""
    print("📄 测试文件列表...")
    
    try:
        response = requests.get(f"{BASE_URL}/files?limit=10", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            file_count = data.get('total_count', 0)
            print(f"✅ 文件列表成功: 找到 {file_count} 个文件")
            return True
        else:
            print(f"❌ 文件列表失败: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 文件列表连接失败: {e}")
        return False


def test_file_upload():
    """测试文件上传"""
    print("📤 测试文件上传...")
    
    try:
        # 创建测试文件
        test_file = create_test_file("Storage API Test Content", "storage_api_test.txt")
        
        # 准备上传
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {'task_id': 'storage_api_test_001'}
            
            response = requests.post(
                f"{BASE_URL}/upload",
                files=files,
                data=data,
                timeout=30
            )
        
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        
        if response.status_code == 200:
            data = response.json()
            storage_key = data.get('storage_key')
            print(f"✅ 文件上传成功: {storage_key}")
            return True, storage_key
        else:
            print(f"❌ 文件上传失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   响应内容: {response.text}")
            return False, None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 文件上传连接失败: {e}")
        return False, None
    except Exception as e:
        print(f"❌ 文件上传异常: {e}")
        return False, None


def main():
    """主测试函数"""
    print("🎯 存储API测试")
    print("=" * 50)
    
    results = []
    
    # 运行测试
    test_functions = [
        ("存储健康检查", test_storage_health),
        ("存储统计", test_storage_stats),
        ("文件列表", test_file_list),
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n🧪 测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常 {test_name}: {e}")
            results.append((test_name, False))
    
    # 文件上传测试（特殊处理）
    print(f"\n🧪 测试: 文件上传")
    try:
        upload_result, storage_key = test_file_upload()
        results.append(("文件上传", upload_result))
    except Exception as e:
        print(f"❌ 文件上传测试异常: {e}")
        results.append(("文件上传", False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📋 测试结果:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有API测试通过！")
    else:
        print("⚠️ 部分API测试失败")
        print("💡 提示: 确保后端服务器正在运行 (python -m uvicorn main:app --host 0.0.0.0 --port 8000)")


if __name__ == "__main__":
    main() 