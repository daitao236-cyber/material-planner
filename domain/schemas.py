# domain/schemas.py
# Pydantic数据模式定义

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator


class TrendResponse(BaseModel):
    """趋势数据响应"""
    platform: str = Field(description="平台名称")
    keyword: str = Field(description="关键词")
    heat: float = Field(description="热度指数")
    videos: int = Field(default=0, description="相关视频数")
    trend: str = Field(default="stable", description="趋势方向")
    related_elements: List[str] = Field(default_factory=list, description="关联元素")
    example_content: str = Field(default="", description="示例内容")
    fetched_at: datetime = Field(default_factory=datetime.now, description="抓取时间")


class PlanRequest(BaseModel):
    """规划生成请求"""
    season: str = Field(description="赛季名称")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    target_audience: List[str] = Field(
        default=["女性", "未成年人"],
        description="目标人群"
    )
    ai_material_ratio: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="AI素材占比"
    )
    include_platforms: List[str] = Field(
        default=["抖音", "B站", "快手", "小红书", "微博"],
        description="包含的平台"
    )
    custom_keywords: List[str] = Field(
        default_factory=list,
        description="自定义关键词"
    )

    @field_validator("ai_material_ratio")
    @classmethod
    def validate_ratio(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("AI素材占比必须在0-1之间")
        return v


class PlanResponse(BaseModel):
    """规划生成响应"""
    success: bool
    plan: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str = ""
    generated_at: datetime = Field(default_factory=datetime.now)


class DataInsights(BaseModel):
    """数据分析洞察"""
    total_spend: float = Field(default=0.0, description="总消耗")
    total_users: int = Field(default=0, description="总曝光用户")
    avg_cpa: float = Field(default=0.0, description="平均CPA")
    avg_roi: float = Field(default=0.0, description="平均ROI")
    new_users: int = Field(default=0, description="新进用户")
    new_ratio: float = Field(default=0.0, description="新进占比")
    retention_d1: float = Field(default=0.0, description="次留率")
    
    # 趋势分析
    cpa_trend: str = Field(default="stable", description="CPA趋势")
    roi_trend: str = Field(default="stable", description="ROI趋势")
    
    # 平台拆分
    ios_data: Dict[str, float] = Field(default_factory=dict, description="iOS数据")
    android_data: Dict[str, float] = Field(default_factory=dict, description="Android数据")
    
    # 高表现素材
    top_performers: List[Dict[str, Any]] = Field(default_factory=list, description="高表现素材")

    class Config:
        json_schema_extra = {
            "example": {
                "total_spend": 1000000.0,
                "total_users": 5000000,
                "avg_cpa": 25.0,
                "avg_roi": 1.5,
                "new_users": 40000,
                "new_ratio": 0.8,
                "retention_d1": 0.45,
                "cpa_trend": "down",
                "roi_trend": "up",
                "ios_data": {"cpa": 30.0, "roi": 1.4},
                "android_data": {"cpa": 22.0, "roi": 1.6},
                "top_performers": []
            }
        }


class UploadResponse(BaseModel):
    """文件上传响应"""
    success: bool
    file_name: str
    file_size: int
    rows_count: int
    columns: List[str]
    message: str = ""


class TrendFetchRequest(BaseModel):
    """趋势抓取请求"""
    keywords: List[str] = Field(
        default=["三角洲行动", "FPS游戏", "战术射击"],
        description="搜索关键词"
    )
    platforms: List[str] = Field(
        default=["douyin", "bilibili", "kuaishou", "xiaohongshu", "weibo"],
        description="抓取平台"
    )
    max_items_per_platform: int = Field(
        default=20,
        ge=1,
        le=100,
        description="每个平台最大条目数"
    )