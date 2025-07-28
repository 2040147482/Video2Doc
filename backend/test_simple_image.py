"""
简化的图像识别API测试
"""

import requests
import json
import time
from PIL import Image, ImageDraw

def create_simple_image():
    """创建简单测试图像"""
    image = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Test", fill='black')
    
    image_path = "simple_test.jpg"
    image.save(image_path, "JPEG")
    return image_path

def test_simple_image_analysis():
    """测试简单图像分析"""
    print("=== 简化图像分析测试 ===")
    
    image_path = create_simple_image()
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = requests.post(
                "http://localhost:8000/api/image-recognition/analyze",
                files=files
            )
        
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            
            if task_id:
                print(f"任务已启动: {task_id}")
                
                # 简单等待并检查状态
                for i in range(10):
                    time.sleep(1)
                    
                    status_response = requests.get(
                        f"http://localhost:8000/api/image-recognition/status/{task_id}"
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get('status')
                        progress = status_data.get('progress', 0)
                        
                        print(f"第{i+1}次检查: 状态={status}, 进度={progress}")
                        
                        if status == 'completed':
                            result = status_data.get('result')
                            print("✅ 分析成功!")
                            if result:
                                print(f"OCR文本: {result.get('extracted_text', 'N/A')}")
                                scene = result.get('scene_analysis', {})
                                if scene:
                                    print(f"场景描述: {scene.get('description', 'N/A')}")
                            return True
                        elif status == 'failed':
                            error = status_data.get('error', '未知错误')
                            print(f"❌ 分析失败: {error}")
                            return False
                    else:
                        print(f"获取状态失败: {status_response.status_code}")
                
                print("❌ 分析超时")
                return False
            else:
                print("❌ 未返回任务ID")
                return False
        else:
            print(f"❌ 上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        import os
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    success = test_simple_image_analysis()
    if success:
        print("\n✅ 测试通过!")
    else:
        print("\n❌ 测试失败!") 