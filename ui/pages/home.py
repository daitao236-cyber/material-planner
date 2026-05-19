# ui/pages/home.py
# 首页

import streamlit as st
from ui.components import StreamlitComponents as ui


def render_home_page():
    """渲染首页"""
    ui.page_header(
        "🎯 游戏素材规划工具",
        "游戏素材规划与趋势分析平台"
    )

    # 功能介绍
    ui.section_header("核心功能")

    col1, col2, col3 = ui.columns(3)

    with col1:
        st.markdown("""
        ### 📊 数据分析
        上传Excel数据，自动分析ROI、CPA、转化率等关键指标，识别高表现素材方向
        """)

    with col2:
        st.markdown("""
        ### 🔥 趋势抓取
        实时监控抖音、B站、快手、小红书、微博五大平台热门趋势，洞察内容热点
        """)

    with col3:
        st.markdown("""
        ### 📝 智能规划
        基于数据洞察和趋势分析，AI一键生成素材规划文档，支持Markdown/Word导出
        """)

    ui.divider()

    # 快速开始
    ui.section_header("快速开始")

    st.markdown("""
    1. **上传数据** → 在「数据上传」页面导入历史投放数据（Excel格式）
    2. **抓取趋势** → 在「趋势监控」页面获取各平台热门内容
    3. **生成规划** → 在「规划生成」页面一键生成素材规划文档

    ---

    ### 当前配置
    """)

    # 显示配置信息
    if "settings" in st.session_state:
        settings = st.session_state.settings
        st.write(f"- AI素材占比: {settings.get('AI_MATERIAL_RATIO', 0.9) * 100:.0f}%")
        st.write(f"- 拉新目标: 女性用户、未成年人")
        st.write(f"- 游戏关键词: {', '.join(settings.get('GAME_KEYWORDS', [])[:5])}...")
    else:
        st.info("请先在侧边栏配置API密钥")

    ui.divider()

    # 最近活动
    ui.section_header("最近活动")

    if "last_upload" in st.session_state:
        st.success(f"✅ 最近上传: {st.session_state.last_upload}")
    else:
        st.info("📂 暂无上传记录")

    if "last_plan" in st.session_state:
        st.success(f"📝 最近规划: {st.session_state.last_plan}")
    else:
        st.info("📝 暂无规划记录")

    ui.divider()

    # 提示信息
    with st.expander("ℹ️ 使用提示"):
        st.markdown("""
        **数据格式要求**：
        - 支持 .xlsx 和 .xls 格式
        - 需要包含以下列：消耗、用户量、CPA、ROI1、新进用户、月份、平台
        - 文件大小不超过 50MB

        **API配置**：
        - 需要配置 Kimi API 密钥才能使用AI生成功能
        - 可在侧边栏「设置」中进行配置
        """)

    ui.footer()


def init_home_state():
    """初始化首页状态"""
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "AI_MATERIAL_RATIO": 0.9,
            "GAME_KEYWORDS": ["三角洲行动", "FPS游戏", "战术射击", "干员"]
        }