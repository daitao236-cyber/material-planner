# spiders/base.py
# 爬虫基类定义

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TrendItem:
    """热门趋势条目"""
    platform: str
    keyword: str
    heat: float = 0.0
    videos: int = 0
    trend: str = "stable"
    related_elements: List[str] = field(default_factory=list)
    example_content: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)
    url: str = ""  # 视频/内容链接

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "keyword": self.keyword,
            "heat": self.heat,
            "videos": self.videos,
            "trend": self.trend,
            "related_elements": self.related_elements,
            "example_content": self.example_content,
            "fetched_at": self.fetched_at.isoformat(),
            "url": self.url
        }


class BaseSpider(ABC):
    """爬虫基类"""

    # 请求间隔（秒）- 遵守爬虫礼仪
    REQUEST_DELAY = 1.0

    # 超时时间（秒）
    TIMEOUT = 30

    # 最大重试次数
    MAX_RETRIES = 3

    def __init__(self, platform_name: str = ""):
        """
        初始化爬虫

        Args:
            platform_name: 平台名称
        """
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def fetch(
        self,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取趋势数据

        Args:
            keywords: 关键词列表
            max_items: 最大条目数

        Returns:
            List[TrendItem]: 趋势数据列表
        """
        pass

    @abstractmethod
    async def _fetch_platform_trends(
        self,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        从平台获取趋势数据（子类实现）

        Args:
            keywords: 关键词列表

        Returns:
            List[Dict]: 原始趋势数据
        """
        pass

    def _parse_raw_trends(
        self,
        raw_data: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[TrendItem]:
        """
        解析原始数据为TrendItem

        Args:
            raw_data: 原始数据列表
            keywords: 关键词列表（用于标记关联性）

        Returns:
            List[TrendItem]: 解析后的趋势数据
        """
        trends = []

        for item in raw_data:
            keyword = item.get("keyword", item.get("title", ""))

            # 不再做严格过滤，保留所有数据让用户自己筛选
            # 只标记是否与关键词相关
            is_related = False
            if keywords and any(kw in keyword for kw in keywords):
                is_related = True

            trend = TrendItem(
                platform=self.platform_name,
                keyword=keyword,
                heat=item.get("heat", item.get("hot_value", 0)),
                videos=item.get("videos", item.get("video_count", 0)),
                trend=item.get("trend", "stable"),
                related_elements=item.get("related", item.get("tags", [])),
                example_content=item.get("example", item.get("content", "")),
                fetched_at=datetime.now(),
                url=item.get("url", "")
            )
            trends.append(trend)

        return trends

    async def _delay(self):
        """请求间隔延迟"""
        await asyncio.sleep(self.REQUEST_DELAY)

    async def _fetch_with_retry(
        self,
        fetch_func,
        *args,
        **kwargs
    ) -> Any:
        """
        带重试的抓取

        Args:
            fetch_func: 抓取函数
            *args, **kwargs: 函数参数

        Returns:
            抓取结果
        """
        last_error = None

        for attempt in range(self.MAX_RETRIES):
            try:
                return await fetch_func(*args, **kwargs)
            except Exception as e:
                last_error = e
                self.logger.warning(f"抓取失败 (尝试 {attempt + 1}/{self.MAX_RETRIES}): {e}")
                
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.REQUEST_DELAY * (attempt + 1))

        raise last_error or Exception("抓取失败")

    def _match_keywords(
        self,
        text: str,
        keywords: List[str]
    ) -> bool:
        """
        匹配关键词

        Args:
            text: 文本
            keywords: 关键词列表

        Returns:
            bool: 是否匹配
        """
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)

    def _normalize_trend(self, heat: float) -> str:
        """
        规范化趋势方向

        Args:
            heat: 热度值

        Returns:
            str: 趋势方向 (up/down/stable)
        """
        if heat > 10000:
            return "up"
        elif heat < 1000:
            return "down"
        else:
            return "stable"