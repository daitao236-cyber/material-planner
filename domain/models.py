# domain/models.py
# 核心数据模型定义

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum


class Platform(Enum):
    """平台枚举"""
    IOS = "iOS"
    ANDROID = "Android"
    ALL = "all"


class TrendDirection(Enum):
    """趋势方向枚举"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    NEW = "new"


class Priority(Enum):
    """优先级枚举"""
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"


class FemaleStyleType(Enum):
    """女性向风格类型"""
    CP = "CP向"
    PROTAGONIST = "女主向"
    COLLECTION = "收集向"
    OTOME = "乙女向"
    FATE = "命理向"


@dataclass
class TimelineItem:
    """时间线条目"""
    phase: str
    start_date: date
    end_date: date
    actions: List[str]
    outputs: List[str]
    notes: Optional[str] = None


@dataclass
class MaterialData:
    """素材投放数据"""
    # 整体数据
    cash: float = 0.0
    users: int = 0
    cpa: float = 0.0
    roi1: float = 0.0
    new_users: int = 0
    new_cpa: float = 0.0
    new_ratio: float = 0.0
    retention_d1: float = 0.0
    ltv1: float = 0.0
    ltv7: float = 0.0

    # 分组维度
    month: str = ""
    week: str = ""
    version: str = ""
    platform: str = ""

    # 扩展字段
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "cash": self.cash,
            "users": self.users,
            "cpa": self.cpa,
            "roi1": self.roi1,
            "new_users": self.new_users,
            "new_cpa": self.new_cpa,
            "new_ratio": self.new_ratio,
            "retention_d1": self.retention_d1,
            "ltv1": self.ltv1,
            "ltv7": self.ltv7,
            "month": self.month,
            "week": self.week,
            "version": self.version,
            "platform": self.platform,
            **self.extra
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MaterialData":
        """从字典创建"""
        known_fields = {
            "cash", "users", "cpa", "roi1", "new_users", "new_cpa",
            "new_ratio", "retention_d1", "ltv1", "ltv7",
            "month", "week", "version", "platform"
        }
        main_data = {k: v for k, v in data.items() if k in known_fields}
        extra_data = {k: v for k, v in data.items() if k not in known_fields}
        main_data["extra"] = extra_data
        return cls(**main_data)


@dataclass
class TrendItem:
    """热门趋势条目"""
    platform: str
    keyword: str
    heat: float
    videos: int = 0
    trend: str = "stable"
    related_elements: List[str] = field(default_factory=list)
    example_content: str = ""
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "platform": self.platform,
            "keyword": self.keyword,
            "heat": self.heat,
            "videos": self.videos,
            "trend": self.trend,
            "related_elements": self.related_elements,
            "example_content": self.example_content,
            "fetched_at": self.fetched_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrendItem":
        """从字典创建"""
        if isinstance(data.get("fetched_at"), str):
            data["fetched_at"] = datetime.fromisoformat(data["fetched_at"])
        return cls(**data)


@dataclass
class PlanItem:
    """规划条目"""
    沟通口径: str
    创意延展: str
    优先级: str = "T1"
    预估效果: str = ""
    目标人群: str = ""
    内容形式: str = ""
    投放平台: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "沟通口径": self.沟通口径,
            "创意延展": self.创意延展,
            "优先级": self.优先级,
            "预估效果": self.预估效果,
            "目标人群": self.目标人群,
            "内容形式": self.内容形式,
            "投放平台": self.投放平台
        }


@dataclass
class PlanSection:
    """规划板块"""
    name: str
    priority: str
    items: List[PlanItem] = field(default_factory=list)
    description: str = ""
    goals: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "priority": self.priority,
            "description": self.description,
            "goals": self.goals,
            "items": [item.to_dict() for item in self.items]
        }


@dataclass
class FemaleStyle:
    """女性向素材风格"""
    type: str
    target_audience: str
    content_directions: List[str] = field(default_factory=list)
    recommended_elements: List[str] = field(default_factory=list)
    platform_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "target_audience": self.target_audience,
            "content_directions": self.content_directions,
            "recommended_elements": self.recommended_elements,
            "platform_suggestions": self.platform_suggestions
        }


@dataclass
class DataInsights:
    """数据洞察结果"""
    total_spend: float = 0.0
    total_users: int = 0
    avg_cpa: float = 0.0
    avg_roi: float = 0.0
    new_users: int = 0
    new_ratio: float = 0.0
    retention_d1: float = 0.0
    ltv7: float = 0.0

    # 平台数据
    ios_data: Dict[str, float] = field(default_factory=dict)
    android_data: Dict[str, float] = field(default_factory=dict)

    # 趋势数据
    cpa_trend: str = "stable"
    roi_trend: str = "stable"

    # 高表现素材
    top_performers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_spend": self.total_spend,
            "total_users": self.total_users,
            "avg_cpa": self.avg_cpa,
            "avg_roi": self.avg_roi,
            "new_users": self.new_users,
            "new_ratio": self.new_ratio,
            "retention_d1": self.retention_d1,
            "ltv7": self.ltv7,
            "ios_data": self.ios_data,
            "android_data": self.android_data,
            "cpa_trend": self.cpa_trend,
            "roi_trend": self.roi_trend,
            "top_performers": self.top_performers
        }


@dataclass
class MaterialPlan:
    """素材规划文档"""
    title: str
    season: str
    created_at: datetime = field(default_factory=datetime.now)

    # 内容板块
    sections: List[PlanSection] = field(default_factory=list)

    # 比例分配
    ai_ratio: float = 0.9
    normal_ratio: float = 0.1

    # 制作周期
    timeline: List[TimelineItem] = field(default_factory=list)

    # AI漫剧专项
    male_content: List[str] = field(default_factory=list)
    female_content: List[str] = field(default_factory=list)

    # 女性向素材
    female_styles: List[FemaleStyle] = field(default_factory=list)

    # 核心主旨
    core_themes: List[str] = field(default_factory=list)

    # 元信息
    data_insights: Dict[str, Any] = field(default_factory=dict)
    trends: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "season": self.season,
            "created_at": self.created_at.isoformat(),
            "sections": [s.to_dict() for s in self.sections],
            "ai_ratio": self.ai_ratio,
            "normal_ratio": self.normal_ratio,
            "timeline": [
                {
                    "phase": t.phase,
                    "start_date": t.start_date.isoformat(),
                    "end_date": t.end_date.isoformat(),
                    "actions": t.actions,
                    "outputs": t.outputs,
                    "notes": t.notes
                }
                for t in self.timeline
            ],
            "male_content": self.male_content,
            "female_content": self.female_content,
            "female_styles": [f.to_dict() for f in self.female_styles],
            "core_themes": self.core_themes,
            "data_insights": self.data_insights,
            "trends": self.trends
        }


@dataclass
class APIResponse:
    """统一API响应格式"""
    success: bool
    data: Any = None
    error: str = ""
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "message": self.message
        }