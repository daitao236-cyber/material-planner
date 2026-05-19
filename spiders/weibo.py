# spiders/weibo.py
# 微博爬虫

import logging
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote as url_quote

import httpx

from .base import BaseSpider, TrendItem

logger = logging.getLogger(__name__)


class WeiboSpider(BaseSpider):
    """微博爬虫"""

    def __init__(self):
        super().__init__("微博")
        self.base_url = "https://weibo.com"
        self.hot_api = "https://weibo.com/ajax/side/hotSearch"

    async def fetch(
        self,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取微博趋势

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
        """从微博获取趋势数据（当前使用智能模拟数据）"""
        return self._generate_mock_data(keywords)

    async def _fetch_hot_search(self) -> List[Dict[str, Any]]:
        """
        获取微博热搜

        Returns:
            List[Dict]: 热搜数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://weibo.com/",
                    "Cookie": ""  # 可能需要登录cookie
                }

                response = await client.get(self.hot_api, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    band_list = data.get("data", {}).get("band_list", [])

                    results = []
                    for item in band_list[:30]:
                        results.append({
                            "keyword": item.get("word", item.get("note", "")),
                            "heat": item.get("raw_hot", item.get("hot", 0)),
                            "videos": item.get("num", 0) // 100,
                            "trend": "up" if item.get("word_scheme") else "stable",
                            "example": item.get("word", "")
                        })

                    return results

        except Exception as e:
            self.logger.warning(f"微博热搜获取失败: {e}")

        return []

    async def _fetch_super_topics(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        获取超话热搜

        Args:
            keywords: 关键词列表

        Returns:
            List[Dict]: 超话数据
        """
        results = []

        for keyword in keywords:
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }

                    url = "https://weibo.com/ajax/side/hotSearch"
                    params = {"type": "topic", "keyword": keyword}

                    response = await client.get(url, params=params, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        data_list = data.get("data", {}).get("data", [])

                        for item in data_list[:5]:
                            results.append({
                                "keyword": f"#{item.get('word', keyword)}#",
                                "heat": item.get("raw_hot", 30000),
                                "videos": item.get("num", 0) // 100,
                                "trend": "stable"
                            })

                await self._delay()

            except Exception as e:
                self.logger.warning(f"微博超话获取失败: {e}")

        return results

    def _generate_mock_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """基于FPS游戏关键词生成微博话题风格的模拟数据"""
        main_kw = keywords[0] if keywords else "三角洲行动"

        results = [
            {
                "keyword": f"#{main_kw}新版本# 全新干员「烬」技能太帅了吧",
                "heat": 92000, "videos": 2800, "trend": "up",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 新版本')}"
            },
            {
                "keyword": f"#FPS手游哪个最好玩#{main_kw} vs CODM vs CF",
                "heat": 85000, "videos": 2100, "trend": "up",
                "url": f"https://s.weibo.com/we?q={url_quote('FPS手游 对比')}"
            },
            {
                "keyword": f"#游戏里的神仙队友# {main_kw}排位遇到的离谱操作",
                "heat": 78000, "videos": 1650, "trend": "stable",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 搞笑队友')}"
            },
            {
                "keyword": f"#{main_kw}干员皮肤# 这波新皮肤设计我给满分💯",
                "heat": 73000, "videos": 1350, "trend": "up",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 干员皮肤')}"
            },
            {
                "keyword": f"#{main_kw}攻略# 烽火地带新手避坑指南（含隐藏彩蛋）",
                "heat": 68000, "videos": 1100, "trend": "stable",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 烽火地带攻略')}"
            },
            {
                "keyword": f"#电竞女孩# 谁说女生不能玩好{main_kw}？晒战绩",
                "heat": 64000, "videos": 920, "trend": "up",
                "url": f"https://s.weibo.com/we?q={url_quote('电竞女孩 ' + main_kw)}"
            },
            {
                "keyword": f"#{main_kw}二创# 大佬画的同人图太绝了，求出周边",
                "heat": 60000, "videos": 780, "trend": "stable",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 二创')}"
            },
            {
                "keyword": f"#{main_kw}赛事# 年度总决赛回顾，那场翻盘看哭了",
                "heat": 56000, "videos": 650, "trend": "stable",
                "url": f"https://s.weibo.com/we?q={url_quote(main_kw + ' 赛事')}"
            },
        ]
        return results