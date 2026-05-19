# services/plan_generator.py
# 规划生成服务

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date

from domain.models import MaterialPlan, PlanSection, PlanItem, FemaleStyle, TimelineItem, TrendItem
from config.prompts import PromptManager
from infrastructure.api_client import KimiClientWrapper, create_kimi_client

logger = logging.getLogger(__name__)


class PlanGenerator:
    """规划生成服务"""

    def __init__(self, api_key: str):
        """
        初始化规划生成服务

        Args:
            api_key: Kimi API密钥
        """
        self.kimi_client = create_kimi_client(api_key)
        self.prompt_manager = PromptManager()

    def generate_plan(
        self,
        data_insights: Dict,
        trends: List[Dict],
        season: str,
        game_keywords: List[str],
        female_keywords: List[str],
        ai_ratio: float = 0.9,
        version_content: Optional[Dict] = None
    ) -> str:
        """
        生成素材规划

        Args:
            data_insights: 数据洞察
            trends: 趋势数据
            season: 赛季名称
            game_keywords: 游戏关键词
            female_keywords: 女性向关键词
            ai_ratio: AI素材占比
            version_content: 版本内容字典（可选），包含商业化、新干员、新地图等活动内容

        Returns:
            str: 生成的规划内容（Markdown格式）
        """
        try:
            # 如果有版本内容，构建版本上下文信息
            version_context = ""
            if version_content:
                version_context = self._build_version_context(version_content)
            
            plan_content = self.kimi_client.generate_plan(
                data_insights=data_insights,
                trends=trends,
                season=season,
                female_keywords=female_keywords,
                game_keywords=game_keywords,
                version_context=version_context
            )

            return plan_content

        except Exception as e:
            logger.error(f"生成规划失败: {e}")
            raise

    def _build_version_context(self, version_content: Dict) -> str:
        """构建版本上下文信息

        Args:
            version_content: 版本内容字典

        Returns:
            str: 格式化的版本上下文字符串
        """
        context_parts = []
        
        # 版本基本信息
        if version_content.get('version_name'):
            context_parts.append(f"版本名称: {version_content['version_name']}")
        if version_content.get('game_type'):
            context_parts.append(f"版本类型: {version_content['game_type']}")
        if version_content.get('update_date'):
            context_parts.append(f"预计更新日期: {version_content['update_date']}")
        if version_content.get('target_users'):
            users = version_content['target_users']
            if isinstance(users, list):
                users = ', '.join(users)
            context_parts.append(f"目标人群: {users}")
        
        # 内容详情
        if version_content.get('commercial'):
            context_parts.append(f"\n商业化内容:\n{version_content['commercial']}")
        if version_content.get('new_operators'):
            context_parts.append(f"\n新干员/角色:\n{version_content['new_operators']}")
        if version_content.get('new_content'):
            context_parts.append(f"\n新地图/玩法:\n{version_content['new_content']}")
        if version_content.get('activities'):
            context_parts.append(f"\n版本活动:\n{version_content['activities']}")
        if version_content.get('user_acquisition'):
            context_parts.append(f"\n拉新专项:\n{version_content['user_acquisition']}")
        
        return '\n'.join(context_parts)

    def parse_plan(self, plan_content: str) -> MaterialPlan:
        """
        解析规划内容为结构化对象

        Args:
            plan_content: 规划内容（Markdown格式）

        Returns:
            MaterialPlan: 解析后的规划对象
        """
        plan = MaterialPlan(
            title="素材规划",
            season="当前赛季"
        )

        # 简单解析Markdown
        lines = plan_content.split("\n")
        current_section = None
        current_subsection = None

        for line in lines:
            line = line.strip()

            # 标题
            if line.startswith("# "):
                plan.title = line[2:].strip()
            elif line.startswith("## "):
                current_section = line[3:].strip()
            elif line.startswith("### "):
                current_subsection = line[4:].strip()

            # 核心主旨
            if "核心主旨" in current_section or "核心方向" in current_section:
                if line.startswith("-") or line.startswith("1."):
                    plan.core_themes.append(line.lstrip("-0123456789. ").strip())

            # AI漫剧
            if "男频" in current_subsection:
                if line.startswith("-") or line.startswith("•"):
                    plan.male_content.append(line.lstrip("-• ").strip())
            if "女频" in current_subsection:
                if line.startswith("-") or line.startswith("•"):
                    plan.female_content.append(line.lstrip("-• ").strip())

        return plan

    def generate_timeline(
        self,
        sections: List[str],
        start_date: date,
        duration_days: int = 90
    ) -> List[TimelineItem]:
        """
        生成制作周期时间表

        Args:
            sections: 板块列表
            start_date: 开始日期
            duration_days: 持续天数

        Returns:
            List[TimelineItem]: 时间线条目
        """
        timeline = []

        # 阶段划分
        phases = [
            ("准备阶段", 0, 14),
            ("制作阶段", 14, 60),
            ("投放阶段", 60, 90)
        ]

        for phase_name, start_offset, end_offset in phases:
            start = start_date + datetime.timedelta(days=start_offset)
            end = start_date + datetime.timedelta(days=end_offset)

            timeline.append(TimelineItem(
                phase=phase_name,
                start_date=start.date(),
                end_date=end.date(),
                actions=self._generate_phase_actions(phase_name, sections),
                outputs=self._generate_phase_outputs(phase_name)
            ))

        return timeline

    def _generate_phase_actions(self, phase: str, sections: List[str]) -> List[str]:
        """生成阶段动作"""
        actions_map = {
            "准备阶段": [
                "确定素材方向和创意",
                "收集参考素材和热点",
                "制定详细制作计划"
            ],
            "制作阶段": [
                "AI漫剧素材制作",
                "女性向素材制作",
                "常规素材制作",
                "素材审核与修改"
            ],
            "投放阶段": [
                "分批次投放测试",
                "数据监控与优化",
                "大规模投放"
            ]
        }
        return actions_map.get(phase, [])

    def _generate_phase_outputs(self, phase: str) -> List[str]:
        """生成阶段输出"""
        outputs_map = {
            "准备阶段": [
                "素材规划文档",
                "创意方向清单",
                "制作排期表"
            ],
            "制作阶段": [
                "AI漫剧素材 (10+条)",
                "女性向素材 (20+条)",
                "常规素材 (5+条)"
            ],
            "投放阶段": [
                "投放数据报告",
                "效果分析报告",
                "优化建议"
            ]
        }
        return outputs_map.get(phase, [])

    def generate_female_styles(
        self,
        female_content: List[str],
        game_keywords: List[str]
    ) -> List[FemaleStyle]:
        """
        生成女性向素材风格

        Args:
            female_content: 女频内容方向
            game_keywords: 游戏关键词

        Returns:
            List[FemaleStyle]: 女性向风格列表
        """
        styles = []

        # CP向
        styles.append(FemaleStyle(
            type="CP向",
            target_audience="喜欢嗑CP的女性用户",
            content_directions=[
                "干员之间的互动",
                "角色配对故事",
                "双人合作场景"
            ],
            recommended_elements=game_keywords[:5],
            platform_suggestions=["小红书", "微博", "B站"]
        ))

        # 女主向
        styles.append(FemaleStyle(
            type="女主向",
            target_audience="喜欢代入的女性用户",
            content_directions=[
                "玩家视角体验",
                "女性干员故事",
                "沉浸式玩法展示"
            ],
            recommended_elements=game_keywords[:5],
            platform_suggestions=["抖音", "B站"]
        ))

        # 收集向
        styles.append(FemaleStyle(
            type="收集向",
            target_audience="喜欢收集的女性用户",
            content_directions=[
                "角色图鉴展示",
                "皮肤收集",
                "干员立绘欣赏"
            ],
            recommended_elements=["干员", "皮肤", "立绘"],
            platform_suggestions=["小红书", "微博"]
        ))

        # 乙女向
        styles.append(FemaleStyle(
            type="乙女向",
            target_audience="喜欢浪漫内容的女性用户",
            content_directions=[
                "浪漫剧情片段",
                "角色告白场景",
                "情感向内容"
            ],
            recommended_elements=["干员", "剧情", "情感"],
            platform_suggestions=["抖音", "小红书"]
        ))

        # 命理向
        styles.append(FemaleStyle(
            type="命理向",
            target_audience="对星座/MBTI感兴趣的女性用户",
            content_directions=[
                "干员MBTI测试",
                "角色星座分析",
                "塔罗占卜风格"
            ],
            recommended_elements=["MBTI", "星座", "测试"],
            platform_suggestions=["小红书", "微博"]
        ))

        return styles

    def generate_sections(
        self,
        section_names: List[str],
        context: Dict
    ) -> List[PlanSection]:
        """
        生成板块内容

        Args:
            section_names: 板块名称列表
            context: 上下文数据

        Returns:
            List[PlanSection]: 板块列表
        """
        sections = []

        for name in section_names:
            section = self._generate_single_section(name, context)
            sections.append(section)

        return sections

    def _generate_single_section(
        self,
        name: str,
        context: Dict
    ) -> PlanSection:
        """生成单个板块"""
        # 优先级判断
        priority = "T1"
        if "拉新" in name or "新干员" in name:
            priority = "T0"
        elif "商业化" in name:
            priority = "T1"

        section = PlanSection(
            name=name,
            priority=priority,
            description=f"{name}相关素材规划"
        )

        # 生成条目
        items = self._generate_section_items(name, context)
        section.items = items

        return section

    def _generate_section_items(
        self,
        section_name: str,
        context: Dict
    ) -> List[PlanItem]:
        """生成板块条目"""
        items = []

        # 根据板块类型生成不同条目
        if "拉新" in section_name:
            items.append(PlanItem(
                沟通口径="针对女性用户和未成年人的拉新素材",
                创意延展="展示游戏魅力，吸引目标用户",
                优先级="T0",
                预估效果="CPA下降15%，ROI提升20%"
            ))
        elif "新干员" in section_name:
            items.append(PlanItem(
                沟通口径="新干员角色展示",
                创意延展="干员背景故事和技能展示",
                优先级="T0",
                预估效果="新版本用户增长30%"
            ))

        # 默认添加通用条目
        items.append(PlanItem(
            沟通口径=f"{section_name}核心卖点",
            创意延展="创意方向和表现形式",
            优先级="T1",
            预估效果="待评估"
        ))

        return items


def create_plan_generator(api_key: str) -> PlanGenerator:
    """
    创建规划生成服务

    Args:
        api_key: Kimi API密钥

    Returns:
        PlanGenerator: 规划生成服务实例
    """
    return PlanGenerator(api_key)