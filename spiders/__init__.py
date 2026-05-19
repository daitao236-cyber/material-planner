# spiders/__init__.py
# 爬虫模块初始化

from .base import BaseSpider, TrendItem
from .douyin import DouyinSpider
from .bilibili import BilibiliSpider
from .kuaishou import KuaishouSpider
from .xiaohongshu import XiaohongshuSpider
from .weibo import WeiboSpider

__all__ = [
    "BaseSpider",
    "TrendItem",
    "DouyinSpider",
    "BilibiliSpider",
    "KuaishouSpider",
    "XiaohongshuSpider",
    "WeiboSpider"
]