# config/settings.py
# 全局配置管理

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """全局配置类"""

    # ============ API配置 ============
    KIMI_API_KEY: str = Field(default="", description="Kimi API密钥")
    KIMI_BASE_URL: str = Field(default="https://api.moonshot.cn/v1", description="Kimi API地址")
    KIMI_MODEL: str = Field(default="moonshot-v1-8k", description="Kimi模型")

    # ============ 日志配置 ============
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # ============ 目录配置 ============
    CACHE_DIR: Path = Field(default=Path(".cache"), description="缓存目录")
    OUTPUT_DIR: Path = Field(default=Path("output"), description="输出目录")
    DATA_DIR: Path = Field(default=Path("data"), description="数据目录")

    # ============ 游戏关键词配置 ============
    GAME_KEYWORDS: List[str] = Field(
        default=[
            "三角洲行动",
            "三角洲",
            "三角洲手游",
            "FPS游戏",
            "战术射击",
            "干员",
            "特种部队",
            "Delta Force",
        ],
        description="游戏相关关键词"
    )

    # ============ 核心用户与拉新关键词 ============
    # 核心用户：成年男性（FPS硬核玩家），拉新专项目标：女性+未成年人
    CORE_AUDIENCE: str = Field(
        default="成年男性",
        description="核心用户群体"
    )

    ACQUISITION_TARGETS: List[str] = Field(
        default=["女性", "未成年人"],
        description="拉新专项目标人群"
    )

    FEMALE_KEYWORDS: List[str] = Field(
        default=[
            "女性向",
            "乙女",
            "CP",
            "二游",
            "二次元",
            "手游女角色",
            "帅哥",
            "男神",
        ],
        description="女性向关键词"
    )

    YOUNG_KEYWORDS: List[str] = Field(
        default=[
            "未成年",
            "学生",
            "暑假",
            "寒假",
            "高中",
            "大学",
            "校园",
        ],
        description="未成年人关键词"
    )

    # ============ 爬虫配置 ============
    CRAWLER_REQUEST_DELAY: float = Field(default=1.0, description="爬虫请求间隔(秒)")
    CRAWLER_TIMEOUT: int = Field(default=30, description="爬虫超时时间(秒)")
    CRAWLER_MAX_RETRIES: int = Field(default=3, description="爬虫最大重试次数")

    # ============ AI素材配置 ============
    AI_MATERIAL_RATIO: float = Field(default=0.9, description="AI素材占比")
    NORMAL_MATERIAL_RATIO: float = Field(default=0.1, description="常规素材占比")

    # ============ 缓存配置 ============
    TREND_CACHE_TTL: int = Field(default=3600, description="趋势缓存TTL(秒)")
    USER_PREF_CACHE_TTL: int = Field(default=86400, description="用户偏好缓存TTL(秒)")
    ANALYSIS_CACHE_TTL: int = Field(default=14400, description="分析结果缓存TTL(秒)")

    # ============ 文件上传配置 ============
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, description="最大上传文件大小(字节)")
    ALLOWED_EXTENSIONS: List[str] = Field(default=["xlsx", "xls"], description="允许的文件扩展名")

    class Config:
        # 环境变量配置文件
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True  # 区分大小写

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保目录存在
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)


# 全局设置实例
_settings: Settings | None = None


def get_settings() -> Settings:
    """获取全局设置实例（单例模式）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings