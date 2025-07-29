"""
图像识别功能测试脚本
"""

import requests
import json
import time
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

API_BASE_URL = "http://localhost:8000"

def create_test_image():
    """创建测试图像文件"""
    # 创建一个简单的测试图像
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 绘制一些文本和图形
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()
    
    # 添加中英文文本
    draw.text((20, 20), "测试图像 Test Image", fill='black', font=font)
    draw.text((20, 60), "Video2Doc AI Tool", fill='blue', font=font)
    draw.text((20, 100), "图像识别功能测试", fill='red', font=font)
    
    # 绘制一些几何图形
    draw.rectangle([50, 150, 150, 200], outline='green', width=3)
    # 绘制圆形（使用ellipse）
    draw.ellipse([270, 150, 330, 210], outline='purple', width=3)
    draw.line([200, 220, 350, 250], fill='orange', width=5)
    
    # 保存图像
    image_path = "test_image.jpg"
    image.save(image_path, "JPEG")
    print(f"测试图像已创建: {image_path}")
    return image_path

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ 健康检查测试通过")
            print(f"状态: {data.get('status')}")
            print(f"版本: {data.get('version')}")
            return True
        else:
            print(f"❌ 健康检查测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查测试失败: {str(e)}")
        return False

def test_image_analysis(image_path):
    """测试图像分析"""
    print("\n=== 测试图像分析 ===")
    try:
        with open(image_path, "rb") as f:
            files = {"file": (image_path, f, "image/jpeg")}
            data = {
                "enable_ocr": True,
                "enable_scene_analysis": True,
                "enable_object_detection": True,
                "language": "auto",
                "detail_level": "medium"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/image-recognition/analyze",
                files=files,
                data=data
            )
        
        print(f"上传响应状态: {response.status_code}")
        print(f"上传响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            if task_id:
                print(f"✅ 图像分析任务已启动，任务ID: {task_id}")
                
                # 轮询任务状态
                return poll_task_status(task_id, "图像分析")
            else:
                print("❌ 图像分析测试失败: 未返回任务ID")
                return False
        else:
            print(f"❌ 图像分析测试失败: {response.status_code}")
            try:
                error_data = response.json()
                print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("无法解析错误响应")
            return False
            
    except Exception as e:
        print(f"❌ 图像分析测试失败: {str(e)}")
        return False

def test_batch_analysis():
    """测试批量图像分析"""
    print("\n=== 测试批量图像分析 ===")
    try:
        # 创建多个测试图像
        image_paths = []
        for i in range(3):
            image_path = f"test_frame_{i}.jpg"
            image = Image.new('RGB', (200, 150), color=('red', 'green', 'blue')[i])
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), f"Frame {i}", fill='white')
            image.save(image_path, "JPEG")
            image_paths.append(os.path.abspath(image_path))
        
        print(f"创建了 {len(image_paths)} 个测试帧")
        
        # 发送批量分析请求
        request_data = {
            "frame_paths": image_paths,
            "analysis_options": {
                "enable_ocr": True,
                "enable_scene_analysis": True,
                "enable_object_detection": False,
                "language": "en",
                "detail_level": "low"
            }
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/image-recognition/batch-analyze",
            json=request_data
        )
        
        print(f"批量分析响应状态: {response.status_code}")
        print(f"批量分析响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            task_id = data.get('task_id')
            total_frames = data.get('total_frames')
            
            if task_id:
                print(f"✅ 批量分析任务已启动，任务ID: {task_id}，总帧数: {total_frames}")
                
                # 轮询任务状态
                success = poll_task_status(task_id, "批量分析", max_wait_time=30)
                
                # 清理测试文件
                for image_path in image_paths:
                    try:
                        os.remove(image_path)
                    except:
                        pass
                
                return success
            else:
                print("❌ 批量分析测试失败: 未返回任务ID")
                return False
        else:
            print(f"❌ 批量分析测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 批量分析测试失败: {str(e)}")
        return False

def poll_task_status(task_id, task_name, max_wait_time=15):
    """轮询任务状态"""
    print(f"等待{task_name}任务完成...")
    
    max_retries = max_wait_time  # 最多等待时间（秒）
    for i in range(max_retries):
        try:
            time.sleep(1)
            response = requests.get(f"{API_BASE_URL}/api/image-recognition/status/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                
                print(f"任务状态: {status}, 进度: {progress:.1f}%")
                
                if status == 'completed':
                    result = data.get('result')
                    if result:
                        print(f"✅ {task_name}测试通过")
                        print("=== 分析结果摘要 ===")
                        
                        # 单张图像结果
                        if isinstance(result, dict):
                            print_analysis_result(result)
                        # 批量结果
                        elif isinstance(result, list):
                            print(f"批量分析完成，共处理 {len(result)} 帧")
                            for idx, frame_result in enumerate(result[:2]):  # 只显示前2个结果
                                print(f"\n--- 帧 {idx+1} ---")
                                print_analysis_result(frame_result)
                            if len(result) > 2:
                                print(f"... 还有 {len(result)-2} 个结果")
                    else:
                        print(f"✅ {task_name}测试通过（无详细结果）")
                    
                    return True
                    
                elif status == 'failed':
                    error = data.get('error', '未知错误')
                    print(f"❌ {task_name}测试失败: {error}")
                    return False
                    
                elif status == 'cancelled':
                    print(f"⚠️ {task_name}任务已取消")
                    return False
                    
            else:
                print(f"获取任务状态失败: {response.status_code}")
                
        except Exception as e:
            print(f"轮询任务状态时出错: {str(e)}")
    
    print(f"❌ {task_name}测试超时")
    return False

def print_analysis_result(result):
    """打印分析结果摘要"""
    if not result or not isinstance(result, dict):
        print("无效的结果格式")
        return
    
    # OCR结果
    extracted_text = result.get('extracted_text', '')
    if extracted_text:
        print(f"OCR文本: {extracted_text[:100]}...")
    
    # 场景分析
    scene_analysis = result.get('scene_analysis', {})
    if scene_analysis:
        description = scene_analysis.get('description', '')
        confidence = scene_analysis.get('confidence', 0)
        tags = scene_analysis.get('tags', [])
        print(f"场景描述: {description}")
        print(f"置信度: {confidence:.2f}")
        print(f"标签: {', '.join(tags)}")
    
    # 对象检测
    objects = result.get('objects', [])
    if objects:
        print(f"检测到 {len(objects)} 个对象:")
        for obj in objects[:3]:  # 只显示前3个
            label = obj.get('label', '')
            confidence = obj.get('confidence', 0)
            print(f"  - {label} (置信度: {confidence:.2f})")
    
    # 处理时间
    processing_time = result.get('processing_time', 0)
    print(f"处理时间: {processing_time:.2f}秒")

def cleanup():
    """清理测试文件"""
    test_files = ["test_image.jpg"] + [f"test_frame_{i}.jpg" for i in range(3)]
    for file_path in test_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除测试文件: {file_path}")
        except Exception as e:
            print(f"删除测试文件失败 {file_path}: {str(e)}")

def main():
    """主测试函数"""
    print("="*50)
    print("图像识别功能测试")
    print("="*50)
    
    # 测试列表
    tests = [
        ("健康检查", test_health),
        ("图像分析", lambda: test_image_analysis(create_test_image())),
        ("批量分析", test_batch_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n测试: {test_name}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}测试通过")
            else:
                print(f"❌ {test_name}测试失败")
                
        except Exception as e:
            print(f"❌ {test_name}测试异常: {str(e)}")
            results.append((test_name, False))
    
    # 清理测试文件
    cleanup()
    
    # 输出测试摘要
    print("\n" + "="*50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"测试完成: {passed} 通过, {total - passed} 失败")
    print("="*50)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    return passed == total

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        cleanup() 