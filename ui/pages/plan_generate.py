# ui/pages/plan_generate.py
# 规划生成页面

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any

from services.plan_generator import PlanGenerator
from services.document_builder import DocumentBuilder
from ui.components import StreamlitComponents as ui


def render_plan_generate_page():
    """渲染规划生成页面"""
    ui.page_header(
        "📝 素材规划生成",
        "基于数据洞察和趋势分析，AI智能生成素材规划文档"
    )

    # 检查API密钥 - 只从session_state获取
    if "KIMI_API_KEY" not in st.session_state:
        api_key_input = st.text_input("请输入 Kimi API Key", type="password")
        if api_key_input:
            st.session_state.KIMI_API_KEY = api_key_input
            st.rerun()
        else:
            st.warning("⚠️ 请在左侧设置中配置 Kimi API Key")
            return
        api_key = st.session_state.KIMI_API_KEY
    else:
        api_key = st.session_state.KIMI_API_KEY

    if not api_key:
        st.warning("⚠️ 请先配置 Kimi API 密钥")
        return

    # 规划配置
    ui.section_header("规划配置")

    col1, col2 = ui.columns(2)

    with col1:
        season = st.text_input(
            "赛季名称",
            value=f"2024年第{((datetime.now().month - 1) // 3) + 1}季度",
            help="规划所属的赛季名称"
        )

    with col2:
        ai_ratio = st.slider(
            "AI素材占比",
            min_value=0.0,
            max_value=1.0,
            value=0.9,
            step=0.05,
            help="AI生成素材占总素材的比例"
        )

    # 开始日期
    start_date = st.date_input(
        "计划开始日期",
        value=datetime.now().date(),
        help="素材制作计划的开始日期"
    )

    ui.divider()

    # 数据洞察
    ui.section_header("数据来源")

    # 获取已有数据
    data_insights = {}
    if "data_analyzer" in st.session_state:
        analyzer = st.session_state.data_analyzer
        if analyzer.data is not None:
            insights = analyzer.get_data_insights()
            data_insights = {
                "total_spend": insights.total_spend,
                "avg_cpa": insights.avg_cpa,
                "avg_roi": insights.avg_roi,
                "new_users": insights.new_users,
                "new_ratio": insights.new_ratio,
                "retention_d1": insights.retention_d1,
                "cpa_trend": insights.cpa_trend,
                "roi_trend": insights.roi_trend,
                "platform_comparison": {
                    "iOS": insights.ios_data,
                    "Android": insights.android_data
                }
            }

    if data_insights:
        st.success("✅ 已加载历史数据分析结果")
        with st.expander("查看数据洞察"):
            for key, value in data_insights.items():
                st.write(f"- **{key}**: {value}")
    else:
        st.info("📊 可在「数据上传」页面加载历史数据")

    # 趋势数据
    trends_data = []
    if "trends" in st.session_state and st.session_state.trends:
        trends_data = [t.to_dict() for t in st.session_state.trends]

    if trends_data:
        st.success(f"✅ 已加载趋势数据 ({len(trends_data)} 条)")
    else:
        st.info("🔥 可在「趋势监控」页面抓取趋势数据")

    ui.divider()

    # 生成按钮
    if st.button("🎯 一键生成素材规划", type="primary", use_container_width=True):
        with st.spinner("正在生成素材规划，请稍候..."):
            try:
                # 创建规划生成器
                generator = PlanGenerator(api_key)

                # 游戏关键词
                game_keywords = [
                    "三角洲行动", "FPS游戏", "战术射击", "干员",
                    "烽火地带", "全面战场", "特种部队"
                ]

                # 女性向关键词
                female_keywords = [
                    "女性向", "乙女", "CP", "二次元",
                    "帅哥", "男神", "角色"
                ]

                # 生成规划
                plan_content = generator.generate_plan(
                    data_insights=data_insights,
                    trends=trends_data,
                    season=season,
                    game_keywords=game_keywords,
                    female_keywords=female_keywords,
                    ai_ratio=ai_ratio
                )

                # 保存规划内容
                st.session_state.plan_content = plan_content

                st.success("✅ 素材规划生成成功！")

            except Exception as e:
                st.error(f"❌ 规划生成失败: {e}")

    ui.divider()

    # 规划展示
    ui.section_header("素材规划内容")

    if "plan_content" in st.session_state and st.session_state.plan_content:
        plan_content = st.session_state.plan_content

        # 标签页
        tabs = st.tabs(["预览", "导出"])

        with tabs[0]:
            st.markdown(plan_content)

            # 保存到会话状态
            if st.button("💾 保存规划"):
                st.session_state.last_plan = f"素材规划_{datetime.now().strftime('%Y%m%d_%H%M')}"
                st.success("✅ 规划已保存")

        with tabs[1]:
            col1, col2 = ui.columns(2)

            with col1:
                # 导出Markdown
                st.download_button(
                    "📄 下载 Markdown",
                    plan_content.encode("utf-8"),
                    f"素材规划_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    "text/markdown"
                )

            with col2:
                # 导出Word
                if st.button("📊 导出 Word"):
                    try:
                        from domain.models import MaterialPlan

                        # 简单解析
                        plan = MaterialPlan(
                            title="素材规划",
                            season=season,
                            ai_ratio=ai_ratio,
                            normal_ratio=1 - ai_ratio
                        )

                        # 生成时间线
                        from services.plan_generator import PlanGenerator
                        generator = PlanGenerator(api_key)
                        timeline = generator.generate_timeline(
                            ["商业化", "新干员", "烽火地带", "猛攻节", "拉新专项"],
                            start_date,
                            90
                        )
                        plan.timeline = timeline

                        # 构建文档
                        builder = DocumentBuilder()
                        docx_data = builder.build_word(plan)

                        st.download_button(
                            "下载 Word",
                            docx_data,
                            f"素材规划_{datetime.now().strftime('%Y%m%d_%H%M')}.docx",
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )

                    except Exception as e:
                        st.error(f"Word导出失败: {e}")

    else:
        st.info("👆 点击「一键生成素材规划」按钮开始生成")

        # 规划说明
        with st.expander("📋 规划内容说明"):
            st.markdown("""
            **生成的素材规划包含以下内容**：

            ### 1. 核心主旨
            - 3条赛季方向
            - 每条包含：方向名称、核心策略、目标效果

            ### 2. 板块分类
            - 商业化素材
            - 新干员宣传
            - 烽火地带/全面战场
            - 猛攻节活动
            - 拉新专项

            ### 3. 比例分配
            - AI素材占比（默认90%）
            - 常规素材占比（默认10%）

            ### 4. AI漫剧专项
            - 男频题材方向（5-8个）
            - 女频题材方向（5-8个）

            ### 5. 女性向素材
            - CP向：角色互动/配对
            - 女主向：玩家视角
            - 收集向：角色收集
            - 乙女向：浪漫内容
            - 命理向：星座/MBTI

            ### 6. 制作周期
            - 准备阶段（2周）
            - 制作阶段（6周）
            - 投放阶段（4周）
            """)

    ui.footer()


def init_plan_generate_state():
    """初始化规划生成状态"""
    pass