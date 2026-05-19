# services/data_analyzer.py
# 数据分析服务

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

from domain.models import MaterialData, DataInsights
from infrastructure.excel_reader import ExcelReader

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """数据分析服务"""

    def __init__(self):
        self.reader = ExcelReader()
        self._df: Optional[pd.DataFrame] = None

    def load_data(self, file_path: str | Path) -> pd.DataFrame:
        """
        加载数据文件

        Args:
            file_path: 文件路径

        Returns:
            pd.DataFrame: 加载的数据
        """
        self._df = self.reader.read(file_path)
        logger.info(f"加载数据: {len(self._df)} 行")
        return self._df

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """获取当前数据"""
        return self._df

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        计算关键指标

        Returns:
            Dict: 指标字典
        """
        if self._df is None or len(self._df) == 0:
            return {}

        metrics = {}

        # 计算总和/平均值
        numeric_cols = ["消耗", "用户量", "新进用户"]
        for col in numeric_cols:
            if col in self._df.columns:
                metrics[col] = self._df[col].sum()

        # 计算平均CPA和ROI
        if "cpa" in self._df.columns:
            metrics["平均CPA"] = self._df["cpa"].mean()

        if "roi1" in self._df.columns:
            metrics["平均ROI"] = self._df["roi1"].mean()

        if "次留" in self._df.columns:
            metrics["平均次留"] = self._df["次留"].mean()

        # 新进占比
        if "新进占比" in self._df.columns:
            metrics["平均新进占比"] = self._df["新进占比"].mean()

        # LTV
        if "ltv7" in self._df.columns:
            metrics["平均LTV7"] = self._df["ltv7"].mean()

        return metrics

    def get_data_insights(self) -> DataInsights:
        """
        获取数据洞察

        Returns:
            DataInsights: 数据洞察对象
        """
        if self._df is None or len(self._df) == 0:
            return DataInsights()

        metrics = self.calculate_metrics()

        # 基础指标
        insights = DataInsights(
            total_spend=metrics.get("消耗", 0),
            total_users=metrics.get("用户量", 0),
            avg_cpa=metrics.get("平均CPA", 0),
            avg_roi=metrics.get("平均ROI", 0),
            new_users=int(metrics.get("新进用户", 0)),
            retention_d1=metrics.get("平均次留", 0)
        )

        # 新进占比
        if "新进占比" in self._df.columns:
            insights.new_ratio = metrics.get("平均新进占比", 0)

        # 平台拆分
        insights.ios_data = self._segment_by_platform("iOS")
        insights.android_data = self._segment_by_platform("Android")

        # 高表现素材
        insights.top_performers = self._identify_top_performers()

        # 趋势分析
        insights.cpa_trend = self._analyze_trend("cpa")
        insights.roi_trend = self._analyze_trend("roi1")

        return insights

    def _segment_by_platform(self, platform: str) -> Dict[str, float]:
        """
        按平台拆分数据

        Args:
            platform: 平台名称

        Returns:
            Dict[str, float]: 平台数据
        """
        if self._df is None or "平台" not in self._df.columns:
            return {}

        platform_data = self._df[self._df["平台"] == platform]
        if len(platform_data) == 0:
            return {}

        return {
            "cpa": platform_data["cpa"].mean() if "cpa" in platform_data.columns else 0,
            "roi": platform_data["roi1"].mean() if "roi1" in platform_data.columns else 0,
            "次留": platform_data["次留"].mean() if "次留" in platform_data.columns else 0
        }

    def _identify_top_performers(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        识别高表现素材

        Args:
            n: 返回数量

        Returns:
            List[Dict[str, Any]]: 高表现素材列表
        """
        if self._df is None:
            return []

        # 按ROI降序排序
        if "roi1" not in self._df.columns:
            return []

        sorted_df = self._df.sort_values("roi1", ascending=False).head(n)

        results = []
        for _, row in sorted_df.iterrows():
            item = {
                "roi": row.get("roi1", 0),
                "cpa": row.get("cpa", 0),
                "平台": row.get("平台", ""),
                "月份": row.get("月份", "")
            }
            results.append(item)

        return results

    def _analyze_trend(self, column: str) -> str:
        """
        分析趋势

        Args:
            column: 列名

        Returns:
            str: 趋势方向 (up/down/stable)
        """
        if self._df is None or column not in self._df.columns:
            return "stable"

        if "月份" not in self._df.columns:
            return "stable"

        # 按月份分组
        monthly_avg = self._df.groupby("月份")[column].mean()

        if len(monthly_avg) < 2:
            return "stable"

        # 计算趋势
        first_half = monthly_avg.iloc[:len(monthly_avg)//2].mean()
        second_half = monthly_avg.iloc[len(monthly_avg)//2:].mean()

        if second_half > first_half * 1.05:
            return "up"
        elif second_half < first_half * 0.95:
            return "down"
        else:
            return "stable"

    def segment_by_time(self, time_column: str = "月份") -> Dict[str, pd.DataFrame]:
        """
        按时段拆分数据

        Args:
            time_column: 时间列名

        Returns:
            Dict[str, pd.DataFrame]: 时间段数据字典
        """
        if self._df is None or time_column not in self._df.columns:
            return {}

        segments = {}
        for month in self._df[time_column].unique():
            segments[str(month)] = self._df[self._df[time_column] == month]

        return segments

    def get_platform_summary(self) -> pd.DataFrame:
        """
        获取平台汇总

        Returns:
            pd.DataFrame: 平台汇总数据
        """
        if self._df is None or "平台" not in self._df.columns:
            return pd.DataFrame()

        return self._df.groupby("平台").agg({
            col: "mean" for col in self._df.select_dtypes(include=["number"]).columns
        })

    def get_monthly_summary(self) -> pd.DataFrame:
        """
        获取月度汇总

        Returns:
            pd.DataFrame: 月度汇总数据
        """
        if self._df is None or "月份" not in self._df.columns:
            return pd.DataFrame()

        return self._df.groupby("月份").agg({
            col: "sum" for col in ["消耗", "用户量", "新进用户"]
        }).join(
            self._df.groupby("月份").agg({
                col: "mean" for col in ["cpa", "roi1", "次留"]
            })
        )

    def export_summary(self) -> str:
        """
        导出汇总报告

        Returns:
            str: Markdown格式的汇总报告
        """
        insights = self.get_data_insights()

        report = f"""# 数据分析汇总报告

## 基础指标
- 总消耗: {insights.total_spend:,.2f}
- 总曝光用户: {insights.total_users:,}
- 平均CPA: {insights.avg_cpa:.2f}
- 平均ROI: {insights.avg_roi:.2f}
- 新进用户: {insights.new_users:,}
- 新进占比: {insights.new_ratio:.2%}
- 次留率: {insights.retention_d1:.2%}

## 趋势分析
- CPA趋势: {'上升' if insights.cpa_trend == 'up' else '下降' if insights.cpa_trend == 'down' else '稳定'}
- ROI趋势: {'上升' if insights.roi_trend == 'up' else '下降' if insights.roi_trend == 'down' else '稳定'}

## 平台对比
"""

        if insights.ios_data:
            report += f"- iOS: CPA={insights.ios_data.get('cpa', 0):.2f}, ROI={insights.ios_data.get('roi', 0):.2f}\n"

        if insights.android_data:
            report += f"- Android: CPA={insights.android_data.get('cpa', 0):.2f}, ROI={insights.android_data.get('roi', 0):.2f}\n"

        report += f"""
## 高表现素材 (Top 10)
| 排名 | ROI | CPA | 平台 | 月份 |
|------|-----|-----|------|------|
"""

        for i, item in enumerate(insights.top_performers, 1):
            report += f"| {i} | {item.get('roi', 0):.2f} | {item.get('cpa', 0):.2f} | {item.get('平台', '-')} | {item.get('月份', '-')} |\n"

        return report