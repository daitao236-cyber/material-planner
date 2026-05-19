# spiders/bilibili.py
# B站爬虫

import logging
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote as url_quote

import httpx

from .base import BaseSpider, TrendItem

logger = logging.getLogger(__name__)


class BilibiliSpider(BaseSpider):
    """B站爬虫"""

    def __init__(self):
        super().__init__("B站")
        self.base_url = "https://www.bilibili.com"
        self.hot_api = "https://api.bilibili.com/x/web-interface/popular/history"

    async def fetch(
        self,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取B站趋势

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
        """从B站获取趋势数据（当前使用智能模拟数据）"""
        return self._generate_mock_data(keywords)

    async def _fetch_hot_videos(self) -> List[Dict[str, Any]]:
        """
        获取热门视频

        Returns:
            List[Dict]: 热门视频数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.bilibili.com/"
                }

                # B站热门排行API
                url = "https://api.bilibili.com/x/web-interface/ranking/v2"
                params = {"rid": 0, "type": "all"}

                response = await client.get(url, params=params, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    list_data = data.get("data", {}).get("list", [])

                    results = []
                    for item in list_data:
                        results.append({
                            "keyword": item.get("title", ""),
                            "heat": item.get("stat", {}).get("view", 0) // 100,
                            "videos": 1,
                            "trend": "stable",
                            "example": item.get("desc", "")[:100]
                        })

                    return results

        except Exception as e:
            self.logger.warning(f"B站API请求失败: {e}")

        return []

    async def _fetch_search_hot(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        获取搜索热词

        Args:
            keywords: 关键词列表

        Returns:
            List[Dict]: 搜索热词数据
        """
        results = []

        for keyword in keywords:
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }

                    # B站搜索API
                    url = f"https://api.bilibili.com/x/web-interface/search/all/v2"
                    params = {"keyword": keyword}

                    response = await client.get(url, params=params, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        results_data = data.get("data", {}).get("result", [])

                        for item in results_data[:5]:
                            results.append({
                                "keyword": item.get("title", item.get("keyword", "")),
                                "heat": item.get("goto", "") == "video" and 50000 or 30000,
                                "videos": item.get("video_count", 1),
                                "trend": "stable"
                            })

                await self._delay()

            except Exception as e:
                self.logger.warning(f"搜索热词获取失败: {e}")

        return results

    def _generate_mock_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """基于FPS游戏关键词生成B站风格的模拟数据"""
        main_kw = keywords[0] if keywords else "三角洲行动"

        results = [
            {
                "keyword": f"【{main_kw}】全干员强度排行T0-T3（2024最新版）",
                "heat": 95000, "videos": 3200, "trend": "up",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 干员排行')}"
            },
            {
                "keyword": f"【{main_kw}】武器伤害测试｜谁才是版本答案？",
                "heat": 89000, "videos": 2500, "trend": "up",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 武器测试')}"
            },
            {
                "keyword": f"【{main_kw}】烽火地带完整攻略｜萌新入门到精通",
                "heat": 85000, "videos": 2100, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 烽火地带攻略')}"
            },
            {
                "keyword": f"【{main_kw}】职业选手视角｜决赛圈1v4极限反杀",
                "heat": 82000, "videos": 1800, "trend": "up",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 职业选手')}"
            },
            {
                "keyword": f"【{main_kw}】新版本剧情模式全流程实况解说",
                "heat": 78000, "videos": 1500, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 剧情模式')}"
            },
            {
                "keyword": f"【{main_kw}】地图点位详解｜这些架枪位你都知道吗",
                "heat": 74000, "videos": 1300, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 地图点位')}"
            },
            {
                "keyword": f"【{main_kw}】创意工坊MOD推荐｜玩法太丰富了",
                "heat": 70000, "videos": 1100, "trend": "up",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 创意工坊')}"
            },
            {
                "keyword": f"【{main_kw}】干员技能全方位测评｜实战效果展示",
                "heat": 67000, "videos": 950, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 干员技能')}"
            },
            {
                "keyword": f"【{main_kw}】配件搭配教学｜这样配输出最大化",
                "heat": 64000, "videos": 800, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 配件搭配')}"
            },
            {
                "keyword": f"【{main_kw}】经典赛事回顾｜当年那场比赛封神了",
                "heat": 60000, "videos": 700, "trend": "stable",
                "url": f"https://search.bilibili.com/all?keyword={url_quote(main_kw + ' 赛事回顾')}"
            },
        ]
        return results