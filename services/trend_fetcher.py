# services/trend_fetcher.py
# 趋势抓取服务

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import asdict
import asyncio

from domain.models import TrendItem
from spiders import DouyinSpider, BilibiliSpider, KuaishouSpider, XiaohongshuSpider, WeiboSpider

logger = logging.getLogger(__name__)


class TrendFetcher:
    """趋势抓取服务"""

    def __init__(self):
        self.spiders = {
            "douyin": DouyinSpider(),
            "bilibili": BilibiliSpider(),
            "kuaishou": KuaishouSpider(),
            "xiaohongshu": XiaohongshuSpider(),
            "weibo": WeiboSpider()
        }
        self._trends_cache: Dict[str, List[TrendItem]] = {}
        self.version_keywords: List[str] = []

    def set_version_context(self, version_content: dict):
        """设置版本上下文，生成更精准的搜索关键词

        Args:
            version_content: 版本内容字典，包含商业化、新干员、新地图等活动内容
        """
        keywords = []
        
        # 从商业化内容中提取关键词
        if version_content.get('commercial'):
            keywords.extend(self._extract_keywords(version_content['commercial']))
        
        # 从新干员/角色中提取关键词
        if version_content.get('new_operators'):
            keywords.extend(self._extract_keywords(version_content['new_operators']))
        
        # 从新地图/玩法中提取关键词
        if version_content.get('new_content'):
            keywords.extend(self._extract_keywords(version_content['new_content']))
        
        # 从活动内容中提取关键词
        if version_content.get('activities'):
            keywords.extend(self._extract_keywords(version_content['activities']))
        
        # 从拉新专项中提取关键词
        if version_content.get('user_acquisition'):
            keywords.extend(self._extract_keywords(version_content['user_acquisition']))
        
        # 添加版本名称作为关键词
        if version_content.get('version_name'):
            keywords.append(version_content['version_name'])
        
        # 添加版本类型作为关键词
        if version_content.get('game_type'):
            keywords.append(version_content['game_type'])
        
        # 去重
        self.version_keywords = list(set(keywords))
        logger.info(f"设置版本上下文，提取关键词: {self.version_keywords}")

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词

        Args:
            text: 输入文本

        Returns:
            List[str]: 提取的关键词列表
        """
        if not text:
            return []
        
        # 常见分隔符
        separators = ['\n', '、', ',', '，', ';', '；', '-', '—']
        
        keywords = []
        for sep in separators:
            if sep in text:
                parts = text.split(sep)
                for part in parts:
                    part = part.strip()
                    if part and len(part) >= 2:
                        keywords.append(part)
                break
        
        # 如果没有分隔符，尝试按行分割
        if not keywords:
            for line in text.split('\n'):
                line = line.strip()
                if line and len(line) >= 2:
                    keywords.append(line)
        
        # 过滤掉太短的词
        keywords = [kw for kw in keywords if len(kw) >= 2]
        
        return keywords

    def get_version_keywords(self) -> List[str]:
        """获取版本关键词列表

        Returns:
            List[str]: 版本关键词列表
        """
        return self.version_keywords

    async def fetch_trends(
        self,
        platform: str,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取指定平台的趋势

        Args:
            platform: 平台名称
            keywords: 关键词列表
            max_items: 最大条目数

        Returns:
            List[TrendItem]: 趋势数据列表
        """
        spider = self.spiders.get(platform)
        if not spider:
            logger.warning(f"未找到爬虫: {platform}")
            return []

        try:
            trends = await spider.fetch(keywords, max_items)
            self._trends_cache[platform] = trends
            logger.info(f"抓取 {platform} 完成，共 {len(trends)} 条")
            return trends

        except Exception as e:
            logger.error(f"抓取 {platform} 失败: {e}")
            return []

    async def fetch_all(
        self,
        keywords: List[str],
        platforms: Optional[List[str]] = None,
        max_items_per_platform: int = 20
    ) -> List[TrendItem]:
        """
        并发抓取所有指定平台

        Args:
            keywords: 关键词列表
            platforms: 平台列表，默认所有平台
            max_items_per_platform: 每个平台最大条目数

        Returns:
            List[TrendItem]: 所有趋势数据
        """
        if platforms is None:
            platforms = list(self.spiders.keys())

        # 并发抓取所有平台
        tasks = [
            self.fetch_trends(platform, keywords, max_items_per_platform)
            for platform in platforms
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_trends = []
        for result in results:
            if isinstance(result, list):
                all_trends.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"抓取异常: {result}")

        return all_trends

    def get_cached_trends(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取缓存的趋势数据

        Args:
            platform: 平台名称，如果为None则返回所有

        Returns:
            List[Dict[str, Any]]: 趋势数据字典列表
        """
        if platform:
            trends = self._trends_cache.get(platform, [])
        else:
            trends = []
            for t in self._trends_cache.values():
                trends.extend(t)

        return [asdict(t) for t in trends]

    def filter_trends(
        self,
        trends: List[TrendItem],
        keywords: Optional[List[str]] = None,
        min_heat: float = 0,
        platforms: Optional[List[str]] = None
    ) -> List[TrendItem]:
        """
        过滤趋势数据

        Args:
            trends: 趋势数据
            keywords: 关键词列表
            min_heat: 最小热度
            platforms: 平台列表

        Returns:
            List[TrendItem]: 过滤后的趋势
        """
        filtered = trends

        # 关键词过滤
        if keywords:
            filtered = [
                t for t in filtered
                if any(kw.lower() in t.keyword.lower() for kw in keywords)
            ]

        # 热度过滤
        if min_heat > 0:
            filtered = [t for t in filtered if t.heat >= min_heat]

        # 平台过滤
        if platforms:
            filtered = [t for t in filtered if t.platform in platforms]

        return filtered

    def sort_trends(
        self,
        trends: List[TrendItem],
        by: str = "heat",
        ascending: bool = False
    ) -> List[TrendItem]:
        """
        排序趋势数据

        Args:
            trends: 趋势数据
            by: 排序字段 (heat/videos/trend)
            ascending: 是否升序

        Returns:
            List[TrendItem]: 排序后的趋势
        """
        if by == "heat":
            return sorted(trends, key=lambda t: t.heat, reverse=not ascending)
        elif by == "videos":
            return sorted(trends, key=lambda t: t.videos, reverse=not ascending)
        elif by == "keyword":
            return sorted(trends, key=lambda t: t.keyword)
        else:
            return trends

    def group_by_platform(self, trends: List[TrendItem]) -> Dict[str, List[TrendItem]]:
        """
        按平台分组

        Args:
            trends: 趋势数据

        Returns:
            Dict[str, List[TrendItem]]: 按平台分组的趋势
        """
        grouped = {}
        for trend in trends:
            if trend.platform not in grouped:
                grouped[trend.platform] = []
            grouped[trend.platform].append(trend)

        return grouped

    def export_trends(self, trends: List[TrendItem], format: str = "markdown") -> str:
        """
        导出趋势数据

        Args:
            trends: 趋势数据
            format: 导出格式 (markdown/table)

        Returns:
            str: 格式化后的趋势
        """
        if format == "markdown":
            return self._export_markdown(trends)
        elif format == "table":
            return self._export_table(trends)
        else:
            return str(trends)

    def _export_markdown(self, trends: List[TrendItem]) -> str:
        """导出为Markdown格式"""
        grouped = self.group_by_platform(trends)

        lines = ["# 热门趋势数据\n"]

        for platform, items in grouped.items():
            lines.append(f"\n## {platform}\n")
            for item in items:
                trend_icon = "↑" if item.trend == "up" else "↓" if item.trend == "down" else "→"
                lines.append(f"- **{item.keyword}** {trend_icon} (热度: {item.heat:.0f})")

        return "\n".join(lines)

    def _export_table(self, trends: List[TrendItem]) -> str:
        """导出为表格格式"""
        lines = ["平台 | 关键词 | 热度 | 视频数 | 趋势"]
        lines.append("|------|--------|------|------|------")

        for item in trends:
            trend_icon = "↑" if item.trend == "up" else "↓" if item.trend == "down" else "→"
            lines.append(f"| {item.platform} | {item.keyword} | {item.heat:.0f} | {item.videos} | {trend_icon} |")

        return "\n".join(lines)


def create_trend_fetcher() -> TrendFetcher:
    """创建趋势抓取服务"""
    return TrendFetcher()