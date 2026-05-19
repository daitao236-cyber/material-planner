# spiders/douyin.py
# 抖音爬虫

import logging
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import quote as url_quote

import httpx

from .base import BaseSpider, TrendItem

logger = logging.getLogger(__name__)


class DouyinSpider(BaseSpider):
    """抖音爬虫"""

    def __init__(self):
        super().__init__("抖音")
        self.base_url = "https://www.douyin.com"
        self.api_url = "https://www.douyin.com/aweme/v1/web/general/search/single"

    async def fetch(
        self,
        keywords: List[str],
        max_items: int = 20
    ) -> List[TrendItem]:
        """
        抓取抖音趋势

        Args:
            keywords: 关键词列表
            max_items: 最大条目数

        Returns:
            List[TrendItem]: 趋势数据列表
        """
        raw_data = await self._fetch_platform_trends(keywords)
        trends = self._parse_raw_trends(raw_data, keywords)

        # 限制数量
        return trends[:max_items]

    async def _fetch_platform_trends(
        self,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        从抖音获取趋势数据（当前使用智能模拟数据）

        Args:
            keywords: 关键词列表

        Returns:
            List[Dict]: 趋势数据
        """
        # 直接使用基于关键词生成的智能模拟数据
        # 确保内容与FPS游戏高度相关
        return self._generate_mock_data(keywords)

    async def _fetch_hot_search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        获取热搜数据

        Args:
            keyword: 关键词

        Returns:
            List[Dict]: 热搜数据
        """
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                # 抖音热搜API（可能需要登录）
                url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.douyin.com/"
                }

                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    word_list = data.get("data", {}).get("word_list", [])
                    
                    results = []
                    for item in word_list:
                        results.append({
                            "keyword": item.get("word", ""),
                            "heat": item.get("hot_value", 0),
                            "videos": item.get("video_count", 0),
                            "trend": "stable"
                        })
                    
                    return results

        except Exception as e:
            self.logger.warning(f"抖音API请求失败，使用模拟数据: {e}")

        # 返回模拟数据
        return self._generate_mock_data_for_keyword(keyword)

    def _generate_mock_data(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """基于FPS游戏关键词生成高质量模拟数据"""
        # 从关键词中提取主关键词用于组合标题
        main_kw = keywords[0] if keywords else "三角洲行动"

        results = [
            {
                "keyword": f"{main_kw} 精彩击杀集锦｜一穿四高光时刻",
                "heat": 92000, "videos": 2300, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 精彩击杀')}"
            },
            {
                "keyword": f"AI一键换脸成{main_kw}干员｜效果太真实了",
                "heat": 88000, "videos": 1850, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' AI换脸')}"
            },
            {
                "keyword": f"{main_kw} 烽火地带｜暗区撤离路线教学",
                "heat": 85000, "videos": 1520, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 烽火地带攻略')}"
            },
            {
                "keyword": f"当热门舞蹈遇上{main_kw}｜二次元燃起来了",
                "heat": 82000, "videos": 1400, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 舞蹈')}"
            },
            {
                "keyword": f"{main_kw} 变装挑战｜从素人到特种兵",
                "heat": 79000, "videos": 1280, "trend": "stable",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 变装')}"
            },
            {
                "keyword": f"新手上分必看｜{main_kw}枪械搭配指南",
                "heat": 75000, "videos": 1100, "trend": "stable",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 枪械攻略')}"
            },
            {
                "keyword": f"{main_kw} 搞笑翻车｜队友的神操作笑死我了",
                "heat": 71000, "videos": 950, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 搞笑')}"
            },
            {
                "keyword": f"{main_kw} 干员COS｜还原度100%惊艳全场",
                "heat": 68000, "videos": 870, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' COS')}"
            },
            {
                "keyword": f"{main_kw} 全面战场｜载具作战太爽了",
                "heat": 65000, "videos": 780, "trend": "stable",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 全面战场')}"
            },
            {
                "keyword": f"手机玩{main_kw}设置｜60帧丝滑流畅",
                "heat": 60000, "videos": 650, "trend": "stable",
                "url": f"https://www.douyin.com/search/{url_quote(main_kw + ' 手机设置')}"
            },
        ]
        return results

    def _generate_mock_data_for_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """为特定关键词生成模拟数据"""
        return [
            {
                "keyword": f"{keyword} 最新版本更新解读｜新干员/新地图一览",
                "heat": 90000, "videos": 2000, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(keyword + ' 版本更新')}"
            },
            {
                "keyword": f"{keyword} 排位上分技巧｜从青铜到战神",
                "heat": 72000, "videos": 1200, "trend": "up",
                "url": f"https://www.douyin.com/search/{url_quote(keyword + ' 上分技巧')}"
            },
            {
                "keyword": f"{keyword} 神级反应操作｜这手速绝了",
                "heat": 55000, "videos": 800, "trend": "stable",
                "url": f"https://www.douyin.com/search/{url_quote(keyword)}"
            }
        ]