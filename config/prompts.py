# config/prompts.py
# AI提示词模板管理

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PromptTemplate:
    """提示词模板"""
    role: str
    template: str
    description: str


class PromptManager:
    """AI提示词管理器"""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._init_templates()

    def _init_templates(self):
        """初始化所有提示词模板"""

        # ============ 规划生成提示词 ============
        self._templates["plan_generation"] = PromptTemplate(
            role="游戏素材规划专家",
            template=self._get_plan_generation_template(),
            description="素材规划生成主提示词"
        )

        # ============ 数据分析提示词 ============
        self._templates["data_analysis"] = PromptTemplate(
            role="数据分析师",
            template=self._get_data_analysis_template(),
            description="数据分析洞察提示词"
        )

        # ============ 趋势解读提示词 ============
        self._templates["trend_interpretation"] = PromptTemplate(
            role="趋势分析师",
            template=self._get_trend_interpretation_template(),
            description="热门趋势解读提示词"
        )

        # ============ 板块生成提示词 ============
        self._templates["section_generation"] = PromptTemplate(
            role="内容策划专家",
            template=self._get_section_generation_template(),
            description="单个板块内容生成提示词"
        )

        # ============ 女性向素材提示词 ============
        self._templates["female_material"] = PromptTemplate(
            role="女性向内容策划专家",
            template=self._get_female_material_template(),
            description="女性向素材方向生成提示词"
        )

    def _get_plan_generation_template(self) -> str:
        """获取规划生成主模板"""
        return """你是游戏素材规划专家，专门为《三角洲行动》这样的FPS战术射击游戏制定素材规划。

## 背景信息
- 游戏类型：FPS战术射击游戏（手游+端游）
- 核心用户：**成年男性**（FPS硬核玩家），大部分素材面向核心用户
- 当前拉新专项：针对**女性用户**和**未成年人**的拉新专项目标
- AI素材占比要求：90%
- 素材类型：AI漫剧（男频/女频）、女性向素材（CP向/女主向/收集向/乙女向/命理向）

## 用户习惯的规划格式
请按照以下格式生成素材规划：

### 一、核心主旨
列出3条赛季方向，每条包含：
- 方向名称
- 核心策略
- 目标效果

### 二、板块分类
按照以下板块进行规划：
1. 商业化素材（面向核心用户）
2. 新干员宣传（面向核心用户）
3. 烽火地带/全面战场（面向核心用户）
4. 猛攻节活动（面向核心用户）
5. 拉新专项（面向女性+未成年用户）

每个板块需要包含：
- 沟通口径：核心传达信息
- 创意延展：具体创意方向
- 优先级：T0/T1/T2
- 预估效果：ROI/CPA预估

### 三、比例分配
- AI素材：90%
- 常规素材：10%
- 核心用户素材：约70%（常规买量+玩法展示）
- 拉新专项素材：约30%（女性向+未成年向）

### 四、AI漫剧专项
#### 男频题材方向
- 列出5-8个适合成年男性核心用户的题材方向

#### 女频题材方向
- 列出5-8个适合女性的题材方向

### 五、拉新专项素材（女性+未成年）
按照以下分类生成内容方向：
1. **CP向**：角色之间的互动/配对
2. **女主向**：以玩家为主角视角
3. **收集向**：角色收集/养成相关
4. **乙女向**：浪漫/情感向内容
5. **命理向**：星座/塔罗/MBTI相关

### 六、制作周期
时间表，包含：
- 阶段划分
- 关键时间节点
- 执行动作
- 输出结果

## 输入数据
{data_input}

## 热门趋势
{trends_input}

## 输出要求
1. 生成完整、详细的素材规划文档
2. 所有内容必须使用中文
3. 符合《三角洲行动》的游戏特色和调性
4. 大部分素材面向成年男性核心用户，拉新专项重点覆盖女性和未成年用户
5. AI漫剧内容要适合在抖音/B站等平台传播
"""
        return template

    def _get_data_analysis_template(self) -> str:
        """获取数据分析提示词模板"""
        return """你是数据分析师，负责从游戏素材投放数据中提取关键洞察。

## 分析维度
1. ROI分析：计算各渠道/类型的投资回报率
2. CPA分析：单次获客成本分析
3. 转化漏斗：曝光→点击→下载→注册→付费
4. 趋势变化：周/月度趋势对比
5. 平台差异：iOS/Android表现对比
6. 人群分析：用户画像与行为特征

## 数据输入
{raw_data}

## 输出要求
1. 识别表现最好的素材类型和渠道
2. 发现用户偏好和内容趋势
3. 找出成本效益最高的目标人群
4. 提出优化建议

## 输出格式
以结构化的JSON格式返回分析结果。
"""

    def _get_trend_interpretation_template(self) -> str:
        """获取趋势解读提示词模板"""
        return """你是趋势分析师，负责解读社交媒体热门趋势。

## 任务
1. 分析以下趋势数据的特征
2. 识别与游戏素材相关的热点
3. 提出内容创意方向

## 趋势数据
{trends}

## 输出要求
1. 总结当前热门趋势特征
2. 提出可结合的游戏元素
3. 建议具体的内容形式
"""

    def _get_section_generation_template(self) -> str:
        """获取板块生成提示词模板"""
        return """你是内容策划专家，负责为游戏素材规划具体的板块内容。

## 板块信息
- 板块名称：{section_name}
- 优先级：{priority}
- 目标人群：{target_audience}

## 背景数据
- 历史表现：{performance_data}
- 热门趋势：{trends}

## 输出要求
生成该板块的具体内容规划，包括：
1. 沟通口径（核心信息）
2. 创意延展（具体方向）
3. 内容示例
4. 预估效果
"""

    def _get_female_material_template(self) -> str:
        """获取女性向素材提示词模板"""
        return """你是女性向内容策划专家，专门为游戏拉新制定针对女性用户和未成年人的内容策略。

## 背景
- 核心用户：成年男性（FPS硬核玩家）
- 拉新专项目标：女性用户和未成年人
- AI素材占比：90%
- 平台：抖音/B站/快手/小红书

## 女性向素材分类
1. **CP向**：角色配对、互动内容
2. **女主向**：玩家视角、沉浸体验
3. **收集向**：角色收集、图鉴展示
4. **乙女向**：浪漫情节、情感共鸣
5. **命理向**：星座、塔罗、MBTI话题

## 游戏元素
- 干员角色：各具特色的特种兵
- 武器装备：现代军事风格
- 游戏模式：烽火地带（战术）、全面战场（大规模）
- 剧情背景：全球危机、精英部队

## 输出要求
为每种类型生成：
1. 内容方向（5-8个）
2. 创意要点
3. 平台适配建议
4. 预估效果

## 格式
以清晰的分类结构输出，使用中文。
"""

    def get_prompt(self, template_name: str, **kwargs) -> tuple[str, str]:
        """
        获取填充后的提示词

        Args:
            template_name: 模板名称
            **kwargs: 填充参数

        Returns:
            tuple[str, str]: (角色设定, 用户输入)
        """
        template = self._templates.get(template_name)
        if not template:
            raise ValueError(f"未找到模板: {template_name}")

        # 替换模板中的占位符
        filled_template = template.template.format(**kwargs)

        return template.role, filled_template

    def get_system_prompt(self) -> str:
        """获取通用系统提示词"""
        return """你是一位专业的游戏素材规划专家，专注于为FPS战术射击游戏《三角洲行动》制定内容策略。

你的专长：
1. 分析游戏素材投放数据，提取有效洞察
2. 解读社交媒体热门趋势，发现内容机会
3. 制定符合用户习惯的素材规划文档
4. 核心用户为成年男性FPS玩家，同时擅长女性和未成年用户的拉新策略

输出风格：
- 专业、简洁、有条理
- 使用中文
- 结构清晰，便于阅读

请始终以专业的态度提供高质量的建议。
"""

    def build_plan_prompt(
        self,
        data_insights: Dict,
        trends: List[Dict],
        season: Optional[str] = None
    ) -> tuple[str, str]:
        """构建规划生成提示词"""
        data_input = self._format_data_insights(data_insights)
        trends_input = self._format_trends(trends)

        role, template = self.get_prompt(
            "plan_generation",
            data_input=data_input,
            trends_input=trends_input
        )

        # 添加赛季信息
        if season:
            template = f"## 当前赛季\n{season}\n\n{template}"

        return role, template

    def _format_data_insights(self, insights: Dict) -> str:
        """格式化数据洞察"""
        lines = ["## 历史数据分析结果\n"]
        for key, value in insights.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_trends(self, trends: List[Dict]) -> str:
        """格式化趋势数据"""
        lines = ["## 热门趋势数据\n"]
        for trend in trends:
            platform = trend.get("platform", "未知")
            keyword = trend.get("keyword", "")
            heat = trend.get("heat", 0)
            lines.append(f"- [{platform}] {keyword} (热度: {heat})")
        return "\n".join(lines)


# 全局提示词管理器实例
prompt_manager = PromptManager()