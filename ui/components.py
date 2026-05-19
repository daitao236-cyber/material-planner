# ui/components.py
# Streamlit通用组件

import streamlit as st
from typing import Optional, Dict, Any, List
from datetime import datetime


class StreamlitComponents:
    """Streamlit通用组件库"""

    @staticmethod
    def page_header(title: str, description: Optional[str] = None):
        """
        页面标题

        Args:
            title: 标题
            description: 描述
        """
        st.title(title)
        if description:
            st.markdown(f"*{description}*")

    @staticmethod
    def section_header(title: str):
        """章节标题"""
        st.markdown(f"### {title}")

    @staticmethod
    def info_box(message: str, style: str = "info"):
        """
        信息提示框

        Args:
            message: 消息内容
            style: 样式 (info/success/warning/error)
        """
        if style == "info":
            st.info(message)
        elif style == "success":
            st.success(message)
        elif style == "warning":
            st.warning(message)
        elif style == "error":
            st.error(message)

    @staticmethod
    def metrics_row(metrics: Dict[str, float]):
        """
        指标行展示

        Args:
            metrics: 指标字典 {名称: 值}
        """
        cols = st.columns(len(metrics))
        for col, (name, value) in zip(cols, metrics.items()):
            with col:
                st.metric(name, f"{value:,.2f}" if isinstance(value, float) else value)

    @staticmethod
    def file_uploader(
        label: str,
        accepted_types: List[str] = ["xlsx", "xls"],
        help_text: Optional[str] = None
    ):
        """
        文件上传组件

        Args:
            label: 标签
            accepted_types: 接受的文件类型
            help_text: 帮助文本

        Returns:
            上传的文件对象
        """
        return st.file_uploader(
            label,
            type=accepted_types,
            help=help_text
        )

    @staticmethod
    def selectbox_with_options(
        label: str,
        options: List[str],
        index: int = 0,
        help_text: Optional[str] = None
    ):
        """带选项的选择框"""
        return st.selectbox(label, options, index, help_text)

    @staticmethod
    def multiselect(
        label: str,
        options: List[str],
        default: Optional[List[str]] = None,
        help_text: Optional[str] = None
    ):
        """
        多选组件

        Args:
            label: 标签
            options: 选项列表
            default: 默认选择
            help_text: 帮助文本

        Returns:
            List[str]: 选中的选项
        """
        if default is None:
            default = []
        return st.multiselect(
            label,
            options,
            default,
            help=help_text
        )

    @staticmethod
    def slider_with_range(
        label: str,
        min_value: float,
        max_value: float,
        value: float,
        step: float = 1.0
    ):
        """带范围的滑块"""
        return st.slider(label, min_value, max_value, value, step)

    @staticmethod
    def text_input(
        label: str,
        value: str = "",
        placeholder: Optional[str] = None,
        help_text: Optional[str] = None
    ):
        """文本输入框"""
        return st.text_input(label, value, placeholder, help_text)

    @staticmethod
    def text_area(
        label: str,
        value: str = "",
        height: int = 200,
        help_text: Optional[str] = None
    ):
        """文本区域"""
        return st.text_area(label, value, height, help_text)

    @staticmethod
    def button(
        label: str,
        variant: str = "primary",
        disabled: bool = False
    ):
        """
        按钮

        Args:
            label: 标签
            variant: 样式 (primary/secondary)
            disabled: 是否禁用

        Returns:
            bool: 是否点击
        """
        if variant == "primary":
            return st.button(label, type="primary", disabled=disabled)
        else:
            return st.button(label, disabled=disabled)

    @staticmethod
    def download_button(
        label: str,
        data: bytes,
        file_name: str,
        mime: str = "application/octet-stream"
    ):
        """下载按钮"""
        return st.download_button(label, data, file_name, mime)

    @staticmethod
    def data_table(
        data: List[Dict[str, Any]],
        height: Optional[int] = None
    ):
        """
        数据表格

        Args:
            data: 数据列表
            height: 表格高度
        """
        if data:
            import pandas as pd
            df = pd.DataFrame(data)
            st.dataframe(df, height=height)
        else:
            st.info("暂无数据")

    @staticmethod
    def json_viewer(data: Dict[str, Any]):
        """JSON查看器"""
        st.json(data)

    @staticmethod
    def progress_bar(value: float):
        """进度条"""
        return st.progress(value)

    @staticmethod
    def spinner(message: str = "处理中..."):
        """加载 spinner"""
        return st.spinner(message)

    @staticmethod
    def tabs(tab_names: List[str]):
        """
        标签页

        Args:
            tab_names: 标签名称列表

        Returns:
            List[str]: 标签页对象列表
        """
        return st.tabs(tab_names)

    @staticmethod
    def expander(title: str, content: str = ""):
        """可展开区域"""
        return st.expander(title, expanded=False)

    @staticmethod
    def divider():
        """分隔线"""
        st.markdown("---")

    @staticmethod
    def empty_line():
        """空行"""
        st.write("")

    @staticmethod
    def columns(n: int, ratios: Optional[List[int]] = None):
        """
        创建列布局

        Args:
            n: 列数
            ratios: 列宽比例

        Returns:
            List: 列对象列表
        """
        if ratios:
            return st.columns(ratios)
        return st.columns(n)

    @staticmethod
    def render_trend_item(item: Dict[str, Any]):
        """
        渲染趋势条目

        Args:
            item: 趋势数据字典
        """
        platform = item.get("platform", "")
        keyword = item.get("keyword", "")
        heat = item.get("heat", 0)
        trend = item.get("trend", "stable")

        trend_icon = "🔺" if trend == "up" else "🔻" if trend == "down" else "➡️"

        st.markdown(f"**{platform}** {trend_icon} **{keyword}** - 热度: {heat:,.0f}")

    @staticmethod
    def render_plan_section(section: Dict[str, Any]):
        """
        渲染规划板块

        Args:
            section: 板块数据字典
        """
        name = section.get("name", "")
        priority = section.get("priority", "T1")

        priority_color = "🟢" if priority == "T0" else "🟡" if priority == "T1" else "🔴"

        st.markdown(f"### {name} {priority_color}")

        items = section.get("items", [])
        if items:
            for item in items:
                st.markdown(f"- **沟通口径**: {item.get('沟通口径', '')}")
                st.markdown(f"  - **创意延展**: {item.get('创意延展', '')}")
                st.markdown(f"  - **优先级**: {item.get('优先级', 'T1')}")

    @staticmethod
    def render_female_style(style: Dict[str, Any]):
        """
        渲染女性向风格

        Args:
            style: 风格数据字典
        """
        style_type = style.get("type", "")
        target = style.get("target_audience", "")
        directions = style.get("content_directions", [])

        st.markdown(f"#### {style_type}")
        st.markdown(f"*目标人群: {target}*")

        if directions:
            st.markdown("**内容方向**:")
            for d in directions:
                st.markdown(f"- {d}")

    @staticmethod
    def render_timeline(timeline: List[Dict[str, Any]]):
        """
        渲染时间线

        Args:
            timeline: 时间线数据列表
        """
        for item in timeline:
            phase = item.get("phase", "")
            start = item.get("start_date", "")
            end = item.get("end_date", "")
            actions = item.get("actions", [])
            outputs = item.get("outputs", [])

            st.markdown(f"#### {phase} ({start} ~ {end})")

            if actions:
                st.markdown("**执行动作**:")
                for a in actions:
                    st.markdown(f"- {a}")

            if outputs:
                st.markdown("**输出结果**:")
                for o in outputs:
                    st.markdown(f"- {o}")

    @staticmethod
    def render_markdown(content: str):
        """渲染Markdown"""
        st.markdown(content)

    @staticmethod
    def render_code(content: str, language: str = "python"):
        """渲染代码块"""
        st.code(content, language)

    @staticmethod
    def sidebar_header():
        """侧边栏标题"""
        st.sidebar.title("🎯 游戏素材规划工具")
        st.sidebar.divider()

    @staticmethod
    def sidebar_nav(pages: List[str], current_page: str) -> str:
        """
        侧边栏导航

        Args:
            pages: 页面列表
            current_page: 当前页面

        Returns:
            str: 选中的页面
        """
        return st.sidebar.radio("导航", pages, pages.index(current_page) if current_page in pages else 0)

    @staticmethod
    def sidebar_selectbox(label: str, options: List[str], index: int = 0):
        """侧边栏选择框"""
        return st.sidebar.selectbox(label, options, index)

    @staticmethod
    def sidebar_multiselect(
        label: str,
        options: List[str],
        default: Optional[List[str]] = None
    ):
        """侧边栏多选"""
        if default is None:
            default = []
        return st.sidebar.multiselect(label, options, default)

    @staticmethod
    def sidebar_slider(
        label: str,
        min_value: float,
        max_value: float,
        value: float,
        step: float = 1.0
    ):
        """侧边栏滑块"""
        return st.sidebar.slider(label, min_value, max_value, value, step)

    @staticmethod
    def sidebar_button(
        label: str,
        key: Optional[str] = None
    ):
        """侧边栏按钮"""
        return st.sidebar.button(label, key=key)

    @staticmethod
    def footer():
        """页脚信息"""
        st.divider()
        st.caption("© 2024 三角洲行动素材规划工具 | Made with ❤️")