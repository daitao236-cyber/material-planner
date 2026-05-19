# ui/pages/data_upload.py
# 数据上传页面

import streamlit as st
from pathlib import Path
import pandas as pd

from services.data_analyzer import DataAnalyzer
from ui.components import StreamlitComponents as ui


def render_data_upload_page():
    """渲染数据上传页面"""
    ui.page_header(
        "📊 数据上传与分析",
        "上传历史投放数据，系统自动分析关键指标"
    )

    # 状态初始化
    if "data_analyzer" not in st.session_state:
        st.session_state.data_analyzer = DataAnalyzer()

    analyzer = st.session_state.data_analyzer

    # 上传区域
    ui.section_header("上传数据文件")

    uploaded_file = st.file_uploader(
        "选择Excel文件",
        type=["xlsx", "xls"],
        help="支持 .xlsx 和 .xls 格式，文件大小不超过 50MB"
    )

    col1, col2 = ui.columns(2)

    if uploaded_file:
        with col1:
            if st.button("📥 加载数据", type="primary"):
                with st.spinner("正在加载数据..."):
                    try:
                        # 保存上传文件
                        save_path = Path("data") / uploaded_file.name
                        save_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # 加载数据
                        analyzer.load_data(save_path)
                        st.session_state.last_upload = uploaded_file.name

                        st.success(f"✅ 数据加载成功！共 {len(analyzer.data)} 行")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ 数据加载失败: {e}")

        with col2:
            if st.button("🔄 重置数据"):
                if "data" in st.session_state:
                    del st.session_state.data
                st.rerun()

    ui.divider()

    # 数据预览
    ui.section_header("数据预览")

    if analyzer.data is not None and len(analyzer.data) > 0:
        st.dataframe(analyzer.data.head(20), height=300)

        # 数据统计
        col1, col2, col3, col4 = ui.columns(4)

        with col1:
            st.metric("总行数", len(analyzer.data))

        with col2:
            st.metric("总列数", len(analyzer.data.columns))

        with col3:
            st.metric("平台数", analyzer.data["平台"].nunique() if "平台" in analyzer.data.columns else "-")

        with col4:
            months = analyzer.data["月份"].nunique() if "月份" in analyzer.data.columns else 0
            st.metric("月份数", months)

        ui.divider()

        # 关键指标
        ui.section_header("关键指标分析")

        metrics = analyzer.calculate_metrics()

        if metrics:
            col1, col2, col3 = ui.columns(3)

            with col1:
                total_cash = metrics.get("消耗", 0)
                st.metric("总消耗", f"¥{total_cash:,.2f}" if total_cash else "-")

            with col2:
                total_users = metrics.get("用户量", 0)
                st.metric("总曝光用户", f"{total_users:,}" if total_users else "-")

            with col3:
                new_users = metrics.get("新进用户", 0)
                st.metric("新进用户", f"{new_users:,}" if new_users else "-")

            col1, col2, col3 = ui.columns(3)

            with col1:
                avg_cpa = metrics.get("平均CPA", 0)
                st.metric("平均CPA", f"¥{avg_cpa:.2f}" if avg_cpa else "-")

            with col2:
                avg_roi = metrics.get("平均ROI", 0)
                st.metric("平均ROI", f"{avg_roi:.2f}x" if avg_roi else "-")

            with col3:
                retention = metrics.get("平均次留", 0)
                st.metric("平均次留率", f"{retention:.2%}" if retention else "-")

        ui.divider()

        # 平台对比
        ui.section_header("平台对比分析")

        platform_summary = analyzer.get_platform_summary()

        if not platform_summary.empty:
            st.dataframe(platform_summary, height=200)
        else:
            st.info("暂无平台数据")

        ui.divider()

        # 月度趋势
        ui.section_header("月度趋势")

        monthly_summary = analyzer.get_monthly_summary()

        if not monthly_summary.empty:
            st.dataframe(monthly_summary, height=300)
        else:
            st.info("暂无月度数据")

        ui.divider()

        # 数据洞察
        ui.section_header("数据洞察报告")

        if st.button("📊 生成数据洞察报告"):
            with st.spinner("正在生成报告..."):
                try:
                    report = analyzer.export_summary()
                    st.markdown(report)

                    # 下载报告
                    st.download_button(
                        "📥 下载报告",
                        report.encode("utf-8"),
                        "数据洞察报告.md",
                        "text/markdown"
                    )

                except Exception as e:
                    st.error(f"报告生成失败: {e}")

        ui.divider()

        # 高表现素材
        ui.section_header("高表现素材 Top 10")

        insights = analyzer.get_data_insights()

        if insights.top_performers:
            top_df = pd.DataFrame(insights.top_performers)
            st.dataframe(top_df, height=300)
        else:
            st.info("暂无高表现素材数据")

    else:
        st.info("👆 请先上传Excel数据文件")

        # 示例数据提示
        with st.expander("📋 数据格式要求"):
            st.markdown("""
            **必需列**：
            - `消耗` - 消耗金额
            - `用户量` - 曝光用户数
            - `cpa` - 单次获客成本
            - `roi1` - ROI (Day1)
            - `新进用户` - 新进用户数

            **可选列**：
            - `月份` - 数据所属月份
            - `平台` - iOS/Android
            - `版本` - 游戏版本
            - `次留` - 次留率

            **示例格式**：
            | 月份 | 平台 | 消耗 | 用户量 | cpa | roi1 | 新进用户 |
            |------|------|------|--------|-----|------|----------|
            | 2024-01 | iOS | 500000 | 1000000 | 25 | 1.5 | 20000 |
            """)

    ui.footer()


def init_data_upload_state():
    """初始化数据上传状态"""
    pass