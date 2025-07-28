"""
直接测试图像识别服务，绕过API
"""

import asyncio
from PIL import Image, ImageDraw

async def test_direct_image_analysis():
    """直接测试图像识别服务"""
    print("=== 直接图像识别测试 ===")
    
    # 创建测试图像
    image = Image.new('RGB', (200, 150), color='white')
    draw = ImageDraw.Draw(image)
    draw.text((20, 20), "Hello World", fill='black')
    draw.text((20, 50), "测试图像", fill='blue')
    draw.rectangle([50, 80, 150, 120], outline='red', width=2)
    
    image_path = "direct_test.jpg"
    image.save(image_path, "JPEG")
    print(f"测试图像已创建: {image_path}")
    
    try:
        # 导入服务
        from app.services.image_recognition import default_service
        print(f"服务类型: {type(default_service)}")
        
        # 直接调用分析
        print("开始图像分析...")
        result = await default_service.analyze_image(image_path)
        
        # 输出结果
        print("✅ 分析成功!")
        print(f"模型: {result.model_used}")
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"OCR文本: {result.extracted_text}")
        print(f"场景描述: {result.scene_analysis.description}")
        print(f"场景标签: {', '.join(result.scene_analysis.tags)}")
        print(f"检测对象数量: {len(result.objects)}")
        
        for i, obj in enumerate(result.objects[:3]):
            print(f"  对象{i+1}: {obj.label} (置信度: {obj.confidence:.2f})")
        
        # 测试字典转换
        result_dict = result.to_dict()
        print(f"字典转换成功，包含 {len(result_dict)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        import os
        if os.path.exists(image_path):
            os.remove(image_path)
            print("已清理测试文件")

if __name__ == "__main__":
    success = asyncio.run(test_direct_image_analysis())
    if success:
        print("\n✅ 直接测试通过!")
    else:
        print("\n❌ 直接测试失败!") 