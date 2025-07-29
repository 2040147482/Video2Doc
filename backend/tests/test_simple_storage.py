"""
简化的云存储测试脚本
测试基本的存储功能
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.cloud_storage.local_storage import LocalStorage
    print("✅ 成功导入LocalStorage")
except ImportError as e:
    print(f"❌ 导入LocalStorage失败: {e}")
    sys.exit(1)


def create_test_file(content: str = "测试文件内容", filename: str = "test.txt") -> Path:
    """创建测试文件"""
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / filename
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 创建测试文件: {test_file}")
    return test_file


async def test_basic_storage():
    """基础存储测试"""
    print("\n🔧 开始基础存储测试...")
    
    try:
        # 创建本地存储实例
        storage = LocalStorage(
            bucket_name="test-bucket",
            base_path="./test_storage"
        )
        print("✅ 创建本地存储实例成功")
        
        # 创建测试文件
        test_file = create_test_file("Hello, Storage Test!", "storage_test.txt")
        
        # 测试上传
        print("📤 测试文件上传...")
        storage_object = await storage.upload_file(
            file_path=test_file,
            key="test/storage_test.txt"
        )
        print(f"✅ 上传成功: {storage_object.key}")
        
        # 测试文件存在检查
        print("🔍 测试文件存在检查...")
        exists = await storage.file_exists("test/storage_test.txt")
        print(f"✅ 文件存在: {exists}")
        
        # 测试文件列表
        print("📄 测试文件列表...")
        files = await storage.list_files(prefix="test/")
        print(f"✅ 找到 {len(files)} 个文件")
        
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()
        
        print("✅ 基础存储测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 基础存储测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🎯 云存储系统简化测试")
    print("=" * 50)
    
    # 运行基础测试
    result = await test_basic_storage()
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 测试通过！云存储基础功能正常！")
    else:
        print("⚠️ 测试失败，请检查错误信息")
    
    return result


if __name__ == "__main__":
    print("开始运行测试...")
    try:
        result = asyncio.run(main())
        print(f"测试完成，结果: {'成功' if result else '失败'}")
    except Exception as e:
        print(f"测试执行异常: {e}")
        import traceback
        traceback.print_exc() 