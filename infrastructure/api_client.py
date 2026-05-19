# infrastructure/api_client.py
# API客户端封装

import json
import logging
from typing import Dict, Optional, Any, List
from pathlib import Path

import requests
from openai import OpenAI

logger = logging.getLogger(__name__)


class APIClient:
    """通用API客户端基类"""

    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """GET请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"GET请求失败: {url}, 错误: {e}")
            raise

    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
        """POST请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            if json_data:
                response = self.session.post(url, json=json_data, timeout=self.timeout)
            else:
                response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"POST请求失败: {url}, 错误: {e}")
            raise


class KimiClient:
    """Kimi API客户端（Moonshot AI）"""

    def __init__(self, api_key: str, base_url: str = "https://api.moonshot.cn/v1"):
        """
        初始化Kimi客户端

        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = "moonshot-v1-8k"
        self.max_tokens = 8192
        self.temperature = 0.7

        # 初始化OpenAI兼容客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        **kwargs
    ) -> str:
        """
        生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数

        Returns:
            str: 生成的文本
        """
        messages = []

        # 添加系统提示词
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加用户提示词
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Kimi API调用失败: {e}")
            raise

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ):
        """
        流式生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数

        Yields:
            str: 生成的文本片段
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Kimi API流式调用失败: {e}")
            raise

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_format: Optional[Dict] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        生成JSON格式响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            response_format: 响应格式定义
            model: 模型名称

        Returns:
            Dict: 解析后的JSON
        """
        # 构建提示词
        json_prompt = f"""{prompt}

请以JSON格式返回结果，不要包含其他内容。
JSON格式：{json.dumps(response_format or {}, ensure_ascii=False, indent=2)}
"""

        result = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            model=model,
            **kwargs
        )

        # 尝试解析JSON
        try:
            # 移除可能的markdown代码块
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            return json.loads(cleaned.strip())

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始内容: {result[:500]}")
            raise

    def batch_generate(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        批量生成

        Args:
            prompts: 提示词列表
            system_prompt: 系统提示词
            model: 模型名称

        Returns:
            List[str]: 生成结果列表
        """
        results = []
        for prompt in prompts:
            try:
                result = self.generate(prompt, system_prompt, model, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"批量生成失败: {prompt[:50]}..., 错误: {e}")
                results.append("")

        return results


class KimiClientWrapper:
    """Kimi客户端封装器，提供更高级的接口"""

    def __init__(self, api_key: str):
        self.client = KimiClient(api_key)

    def generate_plan(
        self,
        data_insights: Dict,
        trends: List[Dict],
        season: str,
        female_keywords: List[str],
        game_keywords: List[str],
        version_context: Optional[str] = None
    ) -> str:
        """
        生成素材规划

        Args:
            data_insights: 数据洞察
            trends: 趋势数据
            season: 赛季名称
            female_keywords: 女性向关键词
            game_keywords: 游戏关键词
            version_context: 版本上下文信息（可选）

        Returns:
            str: 生成的规划内容
        """
        # 构建提示词
        prompt = self._build_plan_prompt(
            data_insights, trends, season, female_keywords, game_keywords, version_context
        )

        system_prompt = self._get_plan_system_prompt()

        return self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=8192
        )

    def _build_plan_prompt(
        self,
        data_insights: Dict,
        trends: List[Dict],
        season: str,
        female_keywords: List[str],
        game_keywords: List[str],
        version_context: Optional[str] = None
    ) -> str:
        """构建规划提示词"""
        # 格式化数据洞察
        insights_str = self._format_data_insights(data_insights)
        
        # 格式化趋势
        trends_str = self._format_trends(trends)

        # 构建版本上下文部分
        version_section = ""
        if version_context:
            version_section = f"""

## 版本内容上下文
{version_context}

请重点关注版本内容中的商业化、新干员、新地图/玩法、活动和拉新专项，确保规划与版本内容高度契合。
"""

        prompt = f"""## 当前赛季
{season}

## 历史数据分析结果
{insights_str}

## 热门趋势数据
{trends_str}

## 游戏关键词
{', '.join(game_keywords)}

## 女性向关键词
{', '.join(female_keywords)}
{version_section}

请基于以上信息，生成完整的素材规划文档。
规划需要包含：
1. 核心主旨（3条赛季方向）
2. 板块分类（商业化、新干员、烽火地带、猛攻节、拉新专项）
3. AI素材占比（90%）
4. AI漫剧专项（男频/女频题材方向）
5. 女性向素材（CP向、女主向、收集向、乙女向、命理向）
6. 制作周期与时间表

请用中文输出，规划要详细、专业、可执行。
"""
        return prompt

    def _format_data_insights(self, insights: Dict) -> str:
        """格式化数据洞察"""
        lines = []
        for key, value in insights.items():
            if isinstance(value, dict):
                lines.append(f"- {key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"- {key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines) if lines else "暂无数据"

    def _format_trends(self, trends: List[Dict]) -> str:
        """格式化趋势数据"""
        if not trends:
            return "暂无趋势数据"

        lines = []
        for trend in trends[:30]:  # 限制最多30条
            platform = trend.get("platform", "未知")
            keyword = trend.get("keyword", "")
            heat = trend.get("heat", 0)
            lines.append(f"- [{platform}] {keyword} (热度: {heat})")

        return "\n".join(lines)

    def _get_plan_system_prompt(self) -> str:
        """获取规划生成系统提示词"""
        return """你是游戏素材规划专家，专门为《三角洲行动》制定素材规划。

你的专长：
1. 分析历史投放数据，提取有效洞察
2. 解读热门趋势，发现内容机会
3. 制定符合行业习惯的素材规划
4. 特别关注女性用户和未成年人群体

输出要求：
- 专业、详细、可执行
- 使用中文
- 结构清晰，使用Markdown格式

规划格式：
1. 核心主旨（3条）
2. 板块分类（5大板块）
3. AI素材占比
4. AI漫剧专项
5. 女性向素材
6. 制作周期
"""


def create_kimi_client(api_key: str) -> KimiClientWrapper:
    """
    创建Kimi客户端

    Args:
        api_key: API密钥

    Returns:
        KimiClientWrapper: Kimi客户端封装器
    """
    return KimiClientWrapper(api_key)