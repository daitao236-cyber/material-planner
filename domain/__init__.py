# domain/__init__.py
# 领域模型模块初始化

from .models import (
    MaterialData,
    TrendItem,
    MaterialPlan,
    PlanSection,
    PlanItem,
    FemaleStyle,
    TimelineItem,
)
from .schemas import (
    TrendResponse,
    PlanRequest,
    PlanResponse,
    DataInsights,
)

__all__ = [
    "MaterialData",
    "TrendItem",
    "MaterialPlan",
    "PlanSection",
    "PlanItem",
    "FemaleStyle",
    "TimelineItem",
    "TrendResponse",
    "PlanRequest",
    "PlanResponse",
    "DataInsights",
]