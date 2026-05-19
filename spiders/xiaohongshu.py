# spiders/xiaohongshu.py
# 小红书爬虫

import logging
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote as url_quote

import httpx

from .base import BaseSpider, TrendItem

logger = logging.getLogger(__name__)


class XiaohongshuSpider(BaseSpider):
    """小红书爬虫"""

    def __init__(self):
        super().__init__("小红书")
        self.base_url = "https://www.xiaohongshu.com"

    async def fetch(
        self,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取小红书趋势

        Args:
            keywords: 关键词列表
            max_items: 最大条目数

        Returns:
            List[TrendItem]: 趋势数据列表
        """
        raw_data = await self._fetch_platform_trends(keywords)
        trends = self._parse_raw_trends(raw_data, keywords)
        return trends[:max_items]

    async def _fetch_platform_trends(
        self,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """从小红书获取趋势数据（当前使用智能模拟数据）"""
        return self._generate_mock_data(keywords)

    async def _fetch_hot_search(self) -> List[Dict[str, Any]]:
        """
        获取小红书热搜

        Returns:
            List[Dict]: 热搜数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.xiaohongshu.com/"
                }

                # 小红书热搜API
                url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/hot"

                response = await client.get(url, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    notes = data.get("data", {}).get("notes", [])

                    results = []
                    for item in notes[:20]:
                        results.append({
                            "keyword": item.get("display_title", item.get("title", "")),
                            "heat": item.get("heat_score", 0),
                            "videos": item.get("interact_count", 0) // 100,
                            "trend": "stable",
                            "example": item.get("desc", "")[:100]
                        })

                    return results

        except Exception as e:
            self.logger.warning(f"小红书热搜获取失败: {e}")

        return []

    async def _search_notes(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索笔记

        Args:
            keyword: 关键词

        Returns:
            List[Dict]: 笔记搜索结果
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }

                url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"
                params = {
                    "keyword": keyword,
                    "page": 1,
                    "page_size": 20
                }

                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    notes = data.get("data", {}).get("items", [])

                    results = []
                    for item in notes[:10]:
                        note_card = item.get("note_card", {})
                        results.append({
                            "keyword": note_card.get("title", ""),
                            "heat": note_card.get("liked_count", 0) // 10,
                            "videos": note_card.get("collected_count", 0) // 50,
                            "trend": "stable"
                        })

                    return results

        except Exception as e:
            self.logger.warning(f"小红书搜索失败: {e}")

        return []

    def _generate_mock_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """基于FPS游戏关键词生成小红书风格的模拟数据"""
        main_kw = keywords[0] if keywords else "三角洲行动"

        results = [
            {
                "keyword": f"✨ {main_kw} 干员COS变装｜从日常到战场女王",
                "heat": 88000, "videos": 1600, "trend": "up",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' COS变装')}"
            },
            {
                "keyword": f"💕 {main_kw} CP向｜这对组合真的嗑到了",
                "heat": 83000, "videos": 1350, "trend": "up",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' CP')}"
            },
            {
                "keyword": f"🎨 {main_kw} 截图调色教程｜电影感氛围感拉满",
                "heat": 76000, "videos": 1100, "trend": "stable",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' 截图调色')}"
            },
            {
                "keyword": f"👗 {main_kw} 干员皮肤穿搭种草｜这也太好看了吧",
                "heat": 72000, "videos": 950, "trend": "up",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' 皮肤穿搭')}"
            },
            {
                "keyword": f"🔮 MBTI × {main_kw}干员｜你是哪个角色的本命？",
                "heat": 68000, "videos": 820, "trend": "up",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote('MBTI ' + main_kw)}"
            },
            {
                "keyword": f"💄 {main_kw} 女性玩家日常｜谁说女生不能打FPS",
                "heat": 65000, "videos": 780, "trend": "stable",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' 女性玩家')}"
            },
            {
                "keyword": f"🌸 {main_kw} 同人绘画分享｜画师太太们太强了",
                "heat": 61000, "videos": 680, "trend": "up",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' 同人绘画')}"
            },
            {
                "keyword": f"☕ {main_kw} 游戏搭子日记｜认识了一群超好的姐妹",
                "heat": 57000, "videos": 590, "trend": "stable",
                "url": f"https://www.xiaohongshu.com/search_result?keyword={url_quote(main_kw + ' 游戏搭子')}"
            },
        ]
        return results