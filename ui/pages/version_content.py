# ui/pages/version_content.py
# 版本内容上传页面

import streamlit as st
from datetime import datetime
from pathlib import Path

def render_version_content_page():
    """渲染版本内容上传页面"""
    st.title("📦 版本内容上传")
    st.markdown("上传本版本的最新内容，工具将基于此内容进行热点搜索和智能规划")
    
    # 版本信息输入
    st.subheader("版本基本信息")
    col1, col2 = st.columns(2)
    
    with col1:
        version_name = st.text_input("版本名称", placeholder="输入版本名称")
        update_date = st.date_input("预计更新日期")
    
    with col2:
        game_type = st.selectbox("版本类型", ["常规版本", "大版本", "赛季更新", "联动版本"], index=0)
        target_users = st.multiselect("目标人群", ["全部用户", "回流用户", "新进用户", "女性用户", "18-"], default=["全部用户"])
    
    # 内容分类上传
    st.subheader("📋 版本内容详情")
    
    # 使用折叠面板组织内容
    with st.expander("🎮 商业化内容", expanded=True):
        commercial = st.text_area(
            "商业化内容描述",
            placeholder="描述商业化内容",
            height=100
        )
        commercial_images = st.file_uploader(
            "上传相关图片（可选）",
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True
        )
    
    with st.expander("👤 新干员/角色", expanded=True):
        new_operators = st.text_area(
            "新干员信息",
            placeholder="填写新角色信息",
            height=120
        )
    
    with st.expander("🗺️ 新地图/玩法", expanded=True):
        new_content = st.text_area(
            "新地图/玩法内容",
            placeholder="描述新地图或玩法内容",
            height=100
        )
    
    with st.expander("🎉 活动内容", expanded=True):
        activities = st.text_area(
            "版本活动",
            placeholder="填写活动内容",
            height=100
        )
    
    with st.expander("💰 拉新专项", expanded=True):
        user_acquisition = st.text_area(
            "拉新相关活动",
            placeholder="描述拉新策略",
            height=80
        )
    
    with st.expander("📄 上传完整文档（可选）"):
        doc_file = st.file_uploader(
            "上传完整的版本规划文档",
            type=['docx', 'pdf', 'txt', 'md']
        )
        if doc_file:
            st.success(f"已上传: {doc_file.name}")
    
    # 保存按钮
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        save_clicked = st.button("💾 保存版本内容", use_container_width=True)
    
    with col2:
        clear_clicked = st.button("🗑️ 清空内容", use_container_width=True)
    
    # 保存逻辑
    if save_clicked:
        # 收集所有内容
        version_data = {
            "version_name": version_name,
            "update_date": str(update_date),
            "game_type": game_type,
            "target_users": target_users,
            "commercial": commercial,
            "new_operators": new_operators,
            "new_content": new_content,
            "activities": activities,
            "user_acquisition": user_acquisition,
            "saved_at": datetime.now().isoformat()
        }
        
        # 保存到 session_state
        st.session_state.version_content = version_data
        st.session_state.version_name = version_name
        
        # 保存到文件
        save_dir = Path("F:/GH/material-planner/data")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        save_file = save_dir / f"version_{version_name}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ 版本内容已保存！")
        st.info(f"文件路径: {save_file}")
    
    if clear_clicked:
        if 'version_content' in st.session_state:
            del st.session_state.version_content
        st.info("内容已清空")
    
    # 显示已保存的版本内容
    if 'version_content' in st.session_state and st.session_state.version_content:
        st.divider()
        st.subheader("📂 当前版本内容预览")
        
        vc = st.session_state.version_content
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("版本名称", vc.get('version_name', '-'))
            st.metric("版本类型", vc.get('game_type', '-'))
        
        with col2:
            st.metric("更新日期", vc.get('update_date', '-'))
            st.metric("目标人群", ', '.join(vc.get('target_users', [])))
        
        st.markdown("---")
        
        # 内容摘要
        if vc.get('commercial'):
            st.markdown(f"**商业化**: {vc['commercial'][:50]}...")
        if vc.get('new_operators'):
            st.markdown(f"**新干员**: {vc['new_operators'][:50]}...")
        if vc.get('new_content'):
            st.markdown(f"**新地图/玩法**: {vc['new_content'][:50]}...")
        
        st.info("💡 此版本内容将在「规划生成」页面被自动引用")
