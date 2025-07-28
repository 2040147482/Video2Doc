"""
图像识别服务调试脚本
"""

import sys
import asyncio
import traceback
from PIL import Image, ImageDraw

def test_imports():
    """测试导入"""
    print("=== 测试导入 ===")
    try:
        from app.services.image_recognition import default_service
        print("✅ 图像识别服务导入成功")
        print(f"服务类型: {type(default_service)}")
        print(f"服务名称: {default_service.model_name}")
        return True
    except Exception as e:
        print(f"❌ 图像识别服务导入失败: {e}")
        traceback.print_exc()
        return False

def create_simple_test_image():
    """创建简单的测试图像"""
    try:
        image = Image.new('RGB', (100, 100), color='white')
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), "Test", fill='black')
        
        image_path = "simple_test.jpg"
        image.save(image_path, "JPEG")
        print(f"✅ 测试图像已创建: {image_path}")
        return image_path
    except Exception as e:
        print(f"❌ 创建测试图像失败: {e}")
        return None

async def test_image_service():
    """测试图像识别服务"""
    print("\n=== 测试图像识别服务 ===")
    try:
        from app.services.image_recognition import default_service
        
        # 创建测试图像
        image_path = create_simple_test_image()
        if not image_path:
            return False
        
        # 测试单独的方法
        print("测试OCR...")
        ocr_results = await default_service.extract_text(image_path)
        print(f"OCR结果: {len(ocr_results)} 个文本块")
        
        print("测试场景分析...")
        scene_result = await default_service.describe_scene(image_path)
        print(f"场景分析: {scene_result.description}")
        
        print("测试对象检测...")
        objects = await default_service.detect_objects(image_path)
        print(f"对象检测: 检测到 {len(objects)} 个对象")
        
        print("测试完整分析...")
        full_result = await default_service.analyze_image(image_path)
        print(f"完整分析成功: {full_result.model_used}")
        
        # 清理
        import os
        os.unlink(image_path)
        print("✅ 图像识别服务测试成功")
        return True
        
    except Exception as e:
        print(f"❌ 图像识别服务测试失败: {e}")
        traceback.print_exc()
        return False

async def test_queue_service():
    """测试队列服务"""
    print("\n=== 测试队列服务 ===")
    try:
        from app.services.queue_service import queue_service
        
        # 测试创建任务
        test_task = {
            "task_id": "test_queue_123",
            "type": "test",
            "status": "pending"
        }
        
        task_id = queue_service.create_task(test_task)
        print(f"✅ 队列任务创建成功: {task_id}")
        
        # 测试获取任务
        task = queue_service.get_task(task_id)
        if task:
            print(f"✅ 队列任务获取成功: {task['status']}")
        else:
            print("❌ 队列任务获取失败")
            return False
        
        # 测试更新任务
        queue_service.update_task_status(task_id, "completed", 100.0)
        updated_task = queue_service.get_task(task_id)
        if updated_task and updated_task['status'] == 'completed':
            print("✅ 队列任务更新成功")
        else:
            print("❌ 队列任务更新失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 队列服务测试失败: {e}")
        traceback.print_exc()
        return False

async def test_file_service():
    """测试文件服务"""
    print("\n=== 测试文件服务 ===")
    try:
        from app.services.file_service import file_service
        print("✅ 文件服务导入成功")
        print(f"上传目录: {file_service.upload_dir}")
        return True
    except Exception as e:
        print(f"❌ 文件服务测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("开始图像识别服务调试...")
    
    # 测试导入
    if not test_imports():
        print("导入测试失败，停止调试")
        return
    
    # 测试文件服务
    if not await test_file_service():
        print("文件服务测试失败")
    
    # 测试队列服务
    if not await test_queue_service():
        print("队列服务测试失败")
    
    # 测试图像识别服务
    if not await test_image_service():
        print("图像识别服务测试失败")
        return
    
    print("\n✅ 所有测试都通过了！")

if __name__ == "__main__":
    asyncio.run(main()) 