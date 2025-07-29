"""
模拟AI摘要服务
"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Any
import logging

from app.services.summary.base import (
    BaseSummaryService, 
    SummaryResult, 
    SummaryChapter, 
    SummarySection,
    KeyPoint
)

logger = logging.getLogger(__name__)


class MockSummaryService(BaseSummaryService):
    """模拟AI摘要服务实现"""
    
    async def generate_summary(
        self, 
        task_id: str,
        transcription: Optional[Dict[str, Any]] = None,
        image_analysis: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> SummaryResult:
        """
        生成内容摘要
        
        Args:
            task_id: 任务ID
            transcription: 语音识别结果
            image_analysis: 图像分析结果
            metadata: 视频元数据
            options: 摘要选项
            
        Returns:
            摘要结果
        """
        logger.info(f"生成摘要: {task_id}")
        
        # 模拟处理时间
        start_time = time.time()
        await asyncio.sleep(1.5)
        
        # 获取选项
        options = options or {}
        language = options.get("language", "zh-cn")
        detail_level = options.get("detail_level", "medium")
        
        # 提取视频时长
        content_duration = 0.0
        if metadata and "duration" in metadata:
            content_duration = metadata["duration"]
        elif transcription and "duration" in transcription:
            content_duration = transcription["duration"]
        
        # 生成模拟标题
        title = "视频内容分析报告"
        if transcription and "text" in transcription:
            # 从转录中提取一些内容作为标题
            text = transcription["text"]
            words = text.split()
            if len(words) > 5:
                title = " ".join(words[:5]) + "..."
        
        # 生成模拟概述
        overview = "这是一个自动生成的视频内容摘要。"
        if transcription and "text" in transcription:
            # 从转录中提取一些内容作为概述
            text = transcription["text"]
            if len(text) > 200:
                overview = text[:200] + "..."
            else:
                overview = text
        
        # 生成模拟章节
        chapters = []
        if content_duration > 0:
            # 基于内容时长创建章节
            num_chapters = min(max(int(content_duration / 60), 1), 5)
            chapter_duration = content_duration / num_chapters
            
            for i in range(num_chapters):
                start_time_sec = i * chapter_duration
                end_time_sec = (i + 1) * chapter_duration
                
                # 创建章节
                chapter = SummaryChapter(
                    title=f"第{i+1}章: {self._generate_mock_title()}",
                    start_time=start_time_sec,
                    end_time=end_time_sec,
                    sections=[]
                )
                
                # 为章节添加小节
                num_sections = random.randint(2, 4)
                section_duration = chapter_duration / num_sections
                
                for j in range(num_sections):
                    section_start = start_time_sec + j * section_duration
                    timestamps = [section_start + random.random() * section_duration 
                                 for _ in range(random.randint(1, 3))]
                    
                    section = SummarySection(
                        title=f"小节 {i+1}.{j+1}: {self._generate_mock_title()}",
                        content=self._generate_mock_content(),
                        source_timestamps=timestamps,
                        source_frames=[random.randint(100, 10000) for _ in range(len(timestamps))],
                        importance=random.random(),
                        keywords=self._generate_mock_keywords()
                    )
                    chapter.sections.append(section)
                
                chapters.append(chapter)
        
        # 生成关键点
        key_points = await self.extract_key_points("", max_points=5)
        
        # 创建摘要结果
        result = SummaryResult(
            title=title,
            overview=overview,
            key_points=key_points,
            chapters=chapters,
            topics=self._generate_mock_topics(),
            keywords=self._generate_mock_keywords(),
            model_used="MockSummaryService",
            processing_time=time.time() - start_time,
            content_duration=content_duration
        )
        
        return result
    
    async def generate_title(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        生成标题
        
        Args:
            content: 内容文本
            options: 选项
            
        Returns:
            生成的标题
        """
        await asyncio.sleep(0.2)  # 模拟处理时间
        
        if not content:
            return "未提供内容"
        
        # 简单地从内容中提取一部分作为标题
        words = content.split()
        if len(words) > 5:
            return " ".join(words[:5]) + "..."
        return content
    
    async def extract_key_points(
        self, 
        content: str, 
        max_points: int = 5,
        options: Optional[Dict[str, Any]] = None
    ) -> List[KeyPoint]:
        """
        提取关键点
        
        Args:
            content: 内容文本
            max_points: 最大关键点数量
            options: 选项
            
        Returns:
            关键点列表
        """
        await asyncio.sleep(0.3)  # 模拟处理时间
        
        # 生成模拟关键点
        key_points = []
        num_points = min(max_points, random.randint(3, 7))
        
        for i in range(num_points):
            source_type = random.choice(["audio", "video", "combined"])
            
            key_point = KeyPoint(
                content=f"关键点 {i+1}: {self._generate_mock_content(short=True)}",
                timestamp=random.random() * 300 if random.random() > 0.3 else None,
                frame_number=random.randint(100, 10000) if source_type in ["video", "combined"] else None,
                source_type=source_type,
                importance=random.random()
            )
            key_points.append(key_point)
        
        # 按重要性排序
        key_points.sort(key=lambda x: x.importance, reverse=True)
        return key_points
    
    def _generate_mock_title(self) -> str:
        """生成模拟标题"""
        titles = [
            "项目介绍与背景",
            "技术分析与比较",
            "市场趋势分析",
            "用户需求调研",
            "解决方案设计",
            "实施计划与时间表",
            "成本与收益分析",
            "风险评估与管理",
            "团队组织与分工",
            "未来展望与规划"
        ]
        return random.choice(titles)
    
    def _generate_mock_content(self, short: bool = False) -> str:
        """生成模拟内容"""
        if short:
            contents = [
                "该项目旨在提高用户体验和系统效率。",
                "数据分析显示市场需求持续增长。",
                "技术架构采用了最新的微服务设计。",
                "用户反馈表明界面简洁度有待提高。",
                "成本控制是项目成功的关键因素。",
                "团队协作需要进一步加强。",
                "测试结果显示系统稳定性良好。",
                "安全性问题需要特别关注。",
                "未来将扩展更多功能模块。",
                "竞品分析提供了宝贵的参考。"
            ]
        else:
            contents = [
                "该项目旨在通过创新技术提高用户体验和系统效率。我们分析了当前市场趋势和用户需求，设计了一套完整的解决方案。初步实施结果表明，系统性能提升了30%，用户满意度显著提高。",
                "数据分析显示，近三年来市场需求持续增长，年均增长率达到15%。我们的产品定位准确，功能设计符合目标用户群体的核心需求。竞品分析表明，我们在技术创新方面具有明显优势。",
                "技术架构采用了最新的微服务设计，提高了系统的可扩展性和容错能力。我们使用了容器化部署，简化了开发和运维流程。性能测试显示，系统能够稳定支持10000并发用户访问。",
                "用户反馈表明，产品界面设计简洁直观，功能操作流畅，但在某些复杂功能的引导方面还有提升空间。我们计划在下一版本中优化用户引导流程，提供更多上下文帮助信息。",
                "成本控制是项目成功的关键因素。通过优化资源配置和技术选型，我们将开发成本控制在预算范围内，同时保证了产品质量。运维成本也比行业平均水平低15%。"
            ]
        return random.choice(contents)
    
    def _generate_mock_keywords(self) -> List[str]:
        """生成模拟关键词"""
        all_keywords = [
            "人工智能", "机器学习", "深度学习", "数据分析", 
            "云计算", "大数据", "区块链", "物联网",
            "微服务", "容器化", "DevOps", "敏捷开发",
            "用户体验", "界面设计", "响应式设计", "移动优先",
            "安全性", "性能优化", "可扩展性", "高可用性"
        ]
        
        # 随机选择3-7个关键词
        num_keywords = random.randint(3, 7)
        return random.sample(all_keywords, min(num_keywords, len(all_keywords)))
    
    def _generate_mock_topics(self) -> List[str]:
        """生成模拟主题"""
        all_topics = [
            "技术创新", "产品设计", "市场分析", "用户研究",
            "项目管理", "团队协作", "资源规划", "风险控制",
            "成本效益", "未来展望"
        ]
        
        # 随机选择2-5个主题
        num_topics = random.randint(2, 5)
        return random.sample(all_topics, min(num_topics, len(all_topics))) 