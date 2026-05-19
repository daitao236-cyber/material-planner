# ui/pages/__init__.py
# 页面模块初始化

from .home import render_home_page
from .data_upload import render_data_upload_page
from .trend_monitor import render_trend_monitor_page
from .plan_generate import render_plan_generate_page

__all__ = [
    "render_home_page",
    "render_data_upload_page",
    "render_trend_monitor_page",
    "render_plan_generate_page"
]