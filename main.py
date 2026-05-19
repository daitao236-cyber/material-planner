# main.py
# 游戏素材规划工具 - 程序入口

import streamlit as st
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """主函数 - Streamlit应用入口"""

    # 页面配置
    st.set_page_config(
        page_title="游戏素材规划工具",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 侧边栏配置
    st.sidebar.title("🎯 游戏素材规划工具")
    st.sidebar.divider()

    # 导航
    pages = {
        "📦 版本内容": "version_content",
        "🏠 首页": "home",
        "📊 数据上传": "data_upload",
        "🔥 趋势监控": "trend_monitor",
        "📝 规划生成": "plan_generate"
    }

    selection = st.sidebar.radio("导航", list(pages.keys()), 0)
    current_page = pages[selection]

    # API配置
    st.sidebar.divider()
    st.sidebar.header("⚙️ 设置")

    # Kimi API密钥 - 优先从 Streamlit Secrets 读取，否则从用户输入读取
    default_key = ""
    try:
        default_key = st.secrets.get("KIMI_API_KEY", "")
    except Exception:
        pass

    api_key = st.sidebar.text_input(
        "Kimi API密钥",
        type="password",
        value=st.session_state.get("KIMI_API_KEY", default_key),
        help="输入Kimi API密钥以启用AI功能（已部署版本无需手动输入）"
    )

    if api_key:
        st.session_state.KIMI_API_KEY = api_key

    # AI素材占比
    ai_ratio = st.sidebar.slider(
        "AI素材占比",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.05,
        help="AI生成素材占总素材的比例"
    )

    # 保存设置
    st.session_state.settings = {
        "AI_MATERIAL_RATIO": ai_ratio,
        "CORE_AUDIENCE": "成年男性",  # 三角洲核心用户
        "ACQUISITION_TARGETS": ["女性", "未成年人"],  # 拉新专项目标
        "GAME_KEYWORDS": [
            "三角洲行动",
            "FPS游戏",
            "战术射击",
            "干员",
            "特种部队",
            "烽火地带",
            "全面战场"
        ]
    }

    # 渲染页面
    if current_page == "version_content":
        from ui.pages.version_content import render_version_content_page
        render_version_content_page()

    elif current_page == "home":
        from ui.pages.home import render_home_page
        render_home_page()

    elif current_page == "data_upload":
        from ui.pages.data_upload import render_data_upload_page
        render_data_upload_page()

    elif current_page == "trend_monitor":
        from ui.pages.trend_monitor import render_trend_monitor_page
        render_trend_monitor_page()

    elif current_page == "plan_generate":
        from ui.pages.plan_generate import render_plan_generate_page
        render_plan_generate_page()


# 辅助函数
def ensure_directories():
    """确保必要目录存在"""
    dirs = ["data", "output", ".cache"]
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)


def check_dependencies():
    """检查依赖包"""
    try:
        import streamlit
        import pandas
        import openai
        import docx
        import httpx
        return True
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        return False


if __name__ == "__main__":
    # 确保目录存在
    ensure_directories()

    # 检查依赖
    if not check_dependencies():
        print("错误: 缺少必要的依赖包")
        print("请运行: pip install -r requirements.txt")
        exit(1)

    # 启动应用
    logger.info("启动游戏素材规划工具...")
    main()