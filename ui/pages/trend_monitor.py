# ui/pages/trend_monitor.py
# 趋势监控页面

import streamlit as st
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from services.trend_fetcher import TrendFetcher
from config.settings import get_settings
from ui.components import StreamlitComponents as ui


def render_trend_monitor_page():
    """渲染趋势监控页面"""
    ui.page_header(
        "🔥 趋势监控",
        "实时抓取各大平台热门趋势，洞察内容热点"
    )

    # 状态初始化 — 用简单的字典列表存储，不用复杂对象
    if "trends_data" not in st.session_state:
        st.session_state.trends_data = []  # List[Dict]

    # 配置区域
    ui.section_header("趋势抓取配置")

    settings = get_settings()

    # 关键词输入
    default_keywords = settings.GAME_KEYWORDS[:3]
    keywords_input = st.text_area(
        "搜索关键词（每行一个）",
        value="\n".join(default_keywords),
        height=100,
        help="输入要搜索的关键词，每行一个"
    )

    keywords = [kw.strip() for kw in keywords_input.split("\n") if kw.strip()]

    # 平台选择（用原生 st.multiselect）
    platforms = st.multiselect(
        "选择平台",
        options=["抖音", "B站", "快手", "小红书", "微博"],
        default=["抖音", "B站", "小红书"]
    )
    st.caption("选择要抓取的社交媒体平台")

    # 映射到爬虫平台名
    platform_map = {
        "抖音": "douyin",
        "B站": "bilibili",
        "快手": "kuaishou",
        "小红书": "xiaohongshu",
        "微博": "weibo"
    }

    spider_platforms = [platform_map[p] for p in platforms] if platforms else []

    # 每平台最大条目数
    max_items = st.slider("每平台最大条目数", 5, 50, 20)

    # 抓取按钮
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 开始抓取", type="primary", disabled=len(keywords) == 0):
            if len(keywords) == 0 or not spider_platforms:
                st.warning("请至少输入一个关键词并选择一个平台")
            else:
                with st.spinner("正在抓取趋势数据..."):
                    try:
                        fetcher = TrendFetcher()
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        trend_objects = loop.run_until_complete(
                            fetcher.fetch_all(keywords, spider_platforms, max_items)
                        )
                        loop.close()

                        # 立即转为字典列表存入 session_state（不存对象！）
                        trends_dict_list = []
                        for t in trend_objects:
                            d = {
                                "platform": t.platform,
                                "keyword": t.keyword,
                                "heat": t.heat,
                                "videos": t.videos,
                                "trend": t.trend,
                            }
                            if hasattr(t, 'related_elements') and t.related_elements:
                                d["related_elements"] = t.related_elements
                            if hasattr(t, 'example_content') and t.example_content:
                                d["example_content"] = t.example_content
                            if hasattr(t, 'fetched_at'):
                                d["fetched_at"] = t.fetched_at.isoformat() if isinstance(t.fetched_at, datetime) else str(t.fetched_at)
                            if hasattr(t, 'url') and t.url:
                                d["url"] = t.url
                            trends_dict_list.append(d)

                        st.session_state.trends_data = trends_dict_list
                        st.success(f"✅ 抓取完成！共获取 {len(trends_dict_list)} 条趋势数据")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 抓取失败: {e}")

    with col2:
        if st.button("🔄 清除数据"):
            st.session_state.trends_data = []
            st.rerun()

    ui.divider()

    # ======== 趋势展示 ========
    ui.section_header("热门趋势数据")

    # 从 session_state 读取纯字典数据
    trends_data = st.session_state.get("trends_data", [])

    # 调试信息（帮助排查问题）
    # st.write(f"DEBUG: session_state.trends_data 长度 = {len(trends_data)}")
    # if trends_data:
    #     st.write(f"DEBUG: 第一条数据 = {trends_data[0]}")

    if not trends_data:
        st.info("👆 点击「开始抓取」按钮获取趋势数据")

        with st.expander("ℹ️ 趋势抓取说明"):
            st.markdown("""
            **支持的平台**：
            - 抖音 - 短视频热门内容
            - B站 - 视频与弹幕文化
            - 快手 - 下沉市场内容
            - 小红书 - 女性向生活方式
            - 微博 - 热搜话题与超话

            **抓取内容**：
            - 热门关键词
            - 热度指数
            - 相关视频数
            - 趋势方向（上升/下降/稳定）

            **使用建议**：
            1. 输入与游戏相关的关键词
            2. 选择目标用户活跃的平台
            3. 根据热度筛选高价值内容方向
            """)

        ui.footer()
        return

    # 有数据了，显示筛选选项
    col1, col2 = st.columns([3, 1])

    with col1:
        filter_platform = st.multiselect(
            "筛选平台",
            options=["抖音", "B站", "快手", "小红书", "微博"],
            default=[]
        )
        st.caption("筛选特定平台的趋势")

    with col2:
        sort_by = st.selectbox(
            "排序方式",
            options=["热度", "视频数", "关键词"],
            index=0
        )

    # 筛选 + 排序（直接操作字典列表）
    display_data = list(trends_data)  # 复制一份

    if filter_platform:
        spider_names = [platform_map[p] for p in filter_platform]
        display_data = [t for t in display_data if t.get("platform") in spider_names]

    if sort_by == "热度":
        display_data.sort(key=lambda x: x.get("heat", 0), reverse=True)
    elif sort_by == "视频数":
        display_data.sort(key=lambda x: x.get("videos", 0), reverse=True)
    else:
        display_data.sort(key=lambda x: x.get("keyword", ""))

    # 统计
    st.info(f"共 {len(display_data)} 条趋势数据")

    # 按平台分组展示
    platform_names_cn = {
        "douyin": "抖音",
        "bilibili": "B站",
        "kuaishou": "快手",
        "xiaohongshu": "小红书",
        "weibo": "微博"
    }

    # 创建标签页
    tab_labels = ["全部"]
    for sp in spider_platforms:
        tab_labels.append(platform_names_cn.get(sp, sp))
    tabs = st.tabs(tab_labels)

    # 全部标签页
    with tabs[0]:
        for item in display_data[:50]:
            _render_trend_item(item, platform_names_cn)

    # 各平台标签页
    for tab_idx, sp in enumerate(spider_platforms, 1):
        with tabs[tab_idx]:
            pt_data = [t for t in display_data if t.get("platform") == sp]
            if pt_data:
                for item in pt_data[:20]:
                    _render_trend_item(item, platform_names_cn)
            else:
                st.info("暂无数据")

    ui.divider()

    # 导出功能
    ui.section_header("导出趋势数据")

    col1, col2 = st.columns(2)

    with col1:
        export_format = st.selectbox(
            "导出格式",
            options=["Markdown", "表格"]
        )

    with col2:
        if st.button("📥 导出趋势数据"):
            if export_format == "Markdown":
                content = _export_markdown(display_data, platform_names_cn)
                filename = f"趋势数据_{len(display_data)}.md"
                mime_type = "text/markdown"
            else:
                content = _export_table(display_data, platform_names_cn)
                filename = f"趋势数据_{len(display_data)}.txt"
                mime_type = "text/plain"

            st.download_button(
                label="下载文件",
                data=content.encode("utf-8"),
                file_name=filename,
                mime=mime_type
            )

    ui.footer()


def _render_trend_item(item: Dict[str, Any], platform_names_cn: Dict[str, str]):
    """渲染单条趋势数据"""
    keyword = item.get("keyword", "")
    platform = item.get("platform", "")
    heat = item.get("heat", 0)
    videos = item.get("videos", 0)
    trend = item.get("trend", "stable")
    related = item.get("related_elements", [])
    example = item.get("example_content", "")
    fetched_at = item.get("fetched_at", "")
    url = item.get("url", "")

    trend_icon = "🔺" if trend == "up" else "🔻" if trend == "down" else "➡️"
    platform_cn = platform_names_cn.get(platform, platform)

    with st.expander(f"{trend_icon} {keyword} [{platform_cn}]"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**热度**: {heat:,.0f}")
            st.write(f"**视频数**: {videos}")
        with col2:
            st.write(f"**趋势**: {trend}")
            st.write(f"**平台**: {platform_cn}")

        if related:
            st.write(f"**关联元素**: {', '.join(str(r) for r in related[:5])}")
        if example:
            st.write(f"**示例内容**: {str(example)[:100]}...")
        if url:
            st.markdown(f"🔗 [观看原视频]({url}) →")
        if fetched_at:
            try:
                dt = datetime.fromisoformat(fetched_at) if isinstance(fetched_at, str) else fetched_at
                st.write(f"**抓取时间**: {dt.strftime('%Y-%m-%d %H:%M')}")
            except Exception:
                pass


def _export_markdown(data: List[Dict], platform_names_cn: Dict[str, str]) -> str:
    """导出为Markdown"""
    lines = ["# 热门趋势数据\n"]
    grouped = {}
    for item in data:
        p = item.get("platform", "")
        grouped.setdefault(p, []).append(item)

    for platform, items in grouped.items():
        lines.append(f"## {platform_names_cn.get(platform, platform)}\n")
        for item in items:
            icon = "↑" if item.get("trend") == "up" else "↓" if item.get("trend") == "down" else "→"
            lines.append(f"- **{item.get('keyword', '')}** {icon} (热度: {item.get('heat', 0):.0f})")

    return "\n".join(lines)


def _export_table(data: List[Dict], platform_names_cn: Dict[str, str]) -> str:
    """导出为表格"""
    lines = ["平台 | 关键词 | 热度 | 视频数 | 趋势"]
    lines.append("|------|--------|------|------|------")
    for item in data:
        icon = "↑" if item.get("trend") == "up" else "↓" if item.get("trend") == "down" else "→"
        lines.append(
            f"| {item.get('platform', '')} | {item.get('keyword', '')} "
            f"| {item.get('heat', 0):.0f} | {item.get('videos', 0)} | {icon}"
        )
    return "\n".join(lines)


def init_trend_monitor_state():
    """初始化趋势监控状态"""
    pass
