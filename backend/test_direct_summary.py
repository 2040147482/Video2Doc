"""
直接测试摘要服务，绕过API
"""

import asyncio
import json
from typing import Dict, Any

async def test_direct_summary():
    """直接测试摘要服务"""
    print("=== 直接摘要服务测试 ===")
    
    try:
        # 导入摘要服务
        from app.services.summary import default_service
        print(f"服务类型: {type(default_service)}")
        
        # 创建模拟转录结果
        transcription = {
            "text": "这是一段测试视频的转录文本。在这个视频中，我们讨论了人工智能技术的最新发展和应用场景。"
                   "深度学习模型在图像识别、自然语言处理和推荐系统等领域取得了显著进展。"
                   "我们还探讨了AI伦理问题和未来发展方向。",
            "language": "zh-cn",
            "duration": 180.5,
            "segments": [
                {"start": 0.0, "end": 10.5, "text": "这是一段测试视频的转录文本。"},
                {"start": 11.0, "end": 30.2, "text": "在这个视频中，我们讨论了人工智能技术的最新发展和应用场景。"},
                {"start": 31.0, "end": 60.5, "text": "深度学习模型在图像识别、自然语言处理和推荐系统等领域取得了显著进展。"},
                {"start": 61.0, "end": 90.0, "text": "我们还探讨了AI伦理问题和未来发展方向。"}
            ]
        }
        
        # 创建模拟图像分析结果
        image_analysis = {
            "frames": [
                {
                    "timestamp": 10.0,
                    "frame_number": 300,
                    "scene_description": "演讲者站在舞台上展示幻灯片",
                    "objects": ["person", "screen", "podium"],
                    "text_content": "AI技术发展"
                },
                {
                    "timestamp": 45.0,
                    "frame_number": 1350,
                    "scene_description": "深度学习架构图示",
                    "objects": ["diagram", "text", "graph"],
                    "text_content": "深度神经网络"
                },
                {
                    "timestamp": 75.0,
                    "frame_number": 2250,
                    "scene_description": "应用案例展示",
                    "objects": ["chart", "image", "text"],
                    "text_content": "应用场景分析"
                }
            ]
        }
        
        # 创建模拟元数据
        metadata = {
            "title": "AI技术发展概述",
            "duration": 180.5,
            "resolution": "1920x1080",
            "fps": 30,
            "created_at": "2023-07-15T10:30:00Z"
        }
        
        # 创建选项
        options = {
            "language": "zh-cn",
            "detail_level": "medium",
            "include_chapters": True,
            "include_key_points": True,
            "max_key_points": 5
        }
        
        # 直接调用摘要生成
        print("开始生成摘要...")
        result = await default_service.generate_summary(
            task_id="test_direct_123",
            transcription=transcription,
            image_analysis=image_analysis,
            metadata=metadata,
            options=options
        )
        
        # 输出结果
        print("\n✅ 摘要生成成功!")
        print(f"标题: {result.title}")
        print(f"概述: {result.overview[:150]}...")
        print(f"使用模型: {result.model_used}")
        print(f"处理时间: {result.processing_time:.2f}秒")
        print(f"内容时长: {result.content_duration:.1f}秒")
        
        # 输出关键点
        print("\n关键点:")
        for i, point in enumerate(result.key_points):
            print(f"  {i+1}. {point.content}")
            if point.timestamp:
                print(f"     时间戳: {point.timestamp:.1f}秒")
            if point.source_type:
                print(f"     来源: {point.source_type}")
        
        # 输出章节
        if result.chapters:
            print("\n章节结构:")
            for i, chapter in enumerate(result.chapters):
                print(f"  第{i+1}章: {chapter.title}")
                print(f"    时间范围: {chapter.start_time:.1f}秒 - {chapter.end_time:.1f}秒")
                
                for j, section in enumerate(chapter.sections):
                    print(f"    {i+1}.{j+1} {section.title}")
                    print(f"      内容: {section.content[:50]}...")
                    print(f"      关键词: {', '.join(section.keywords[:3])}")
        
        # 测试字典转换
        result_dict = result.to_dict()
        print(f"\n字典转换成功，包含 {len(result_dict)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"❌ 摘要生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_direct_summary())
    if success:
        print("\n✅ 直接测试通过!")
    else:
        print("\n❌ 直接测试失败!") 