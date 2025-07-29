"""
快速导出测试
"""

import requests
import json

def test_formats():
    """测试获取支持的格式"""
    try:
        response = requests.get("http://localhost:8000/api/export/formats", timeout=5)
        print(f"支持的格式: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"格式获取失败: {e}")
        return False

def test_templates():
    """测试获取可用模板"""
    try:
        response = requests.get("http://localhost:8000/api/export/templates", timeout=5)
        print(f"可用模板: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"模板获取失败: {e}")
        return False

def main():
    """快速测试"""
    print("=== 快速导出功能测试 ===")
    
    if test_formats() and test_templates():
        print("✅ 基础API测试通过!")
    else:
        print("❌ 基础API测试失败!")

if __name__ == "__main__":
    main() 