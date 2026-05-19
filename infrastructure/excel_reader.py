# infrastructure/excel_reader.py
# Excel数据读取

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class ExcelReader:
    """Excel文件读取器"""

    # 预期的列名映射（支持多种命名）
    COLUMN_MAPPING = {
        # 消耗相关
        "消耗": ["消耗", "cash", "spend", "cost", "金额"],
        "消费": ["消费", "消耗"],
        
        # 用户相关
        "用户量": ["用户量", "users", "曝光用户", "曝光人数"],
        "新进用户": ["新进用户", "new_users", "新增用户", "注册用户"],
        
        # CPA/ROI
        "cpa": ["cpa", "CPA", "单次获客成本", "获客成本"],
        "roi": ["roi", "ROI", "投资回报率"],
        "roi1": ["roi1", "ROI1", "ROI_D1"],
        
        # 留存/LTV
        "次留": ["次留", "retention_d1", "D1留存", "留存率"],
        "ltv1": ["ltv1", "LTV1", "LTV_D1"],
        "ltv7": ["ltv7", "LTV7", "LTV_D7"],
        
        # 维度字段
        "月份": ["月份", "month", "月", "日期", "时间"],
        "周次": ["周次", "week", "周"],
        "版本": ["版本", "version", "version_name"],
        "平台": ["平台", "platform", "渠道", "OS"],
        "新进占比": ["新进占比", "new_ratio", "新占比"],
    }

    def __init__(self):
        self._column_cache: Dict[str, Dict[str, str]] = {}

    def read(self, file_path: str | Path) -> pd.DataFrame:
        """
        读取Excel文件

        Args:
            file_path: 文件路径

        Returns:
            pd.DataFrame: 读取的数据
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            # 尝试读取Excel
            df = pd.read_excel(file_path, engine="openpyxl")
            logger.info(f"成功读取文件: {file_path}, 共 {len(df)} 行")
            
            # 标准化列名
            df = self._normalize_columns(df)
            
            return df

        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise

    def read_with_mapping(self, file_path: str | Path) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """
        读取Excel文件并返回列名映射

        Args:
            file_path: 文件路径

        Returns:
            Tuple[pd.DataFrame, Dict[str, str]]: 数据和列名映射
        """
        df = self.read(file_path)
        return df, self._column_cache.get(str(file_path), {})

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化列名

        Args:
            df: 原始数据框

        Returns:
            pd.DataFrame: 标准化后的数据框
        """
        normalized_df = df.copy()
        column_mapping = {}

        for col in df.columns:
            # 查找对应的标准列名
            standard_name = self._find_standard_column(col)
            if standard_name:
                column_mapping[col] = standard_name
                normalized_df.rename(columns={col: standard_name}, inplace=True)

        # 保存映射关系
        # 注意：在实际使用时需要根据文件路径保存
        return normalized_df

    def _find_standard_column(self, col_name: str) -> Optional[str]:
        """
        查找标准列名

        Args:
            col_name: 原始列名

        Returns:
            Optional[str]: 标准列名，如果没有匹配返回None
        """
        col_lower = str(col_name).lower().strip()
        
        for standard_name, aliases in self.COLUMN_MAPPING.items():
            if col_lower in [a.lower() for a in aliases]:
                return standard_name
        
        return None

    def parse_date_columns(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """
        解析日期列

        Args:
            df: 数据框
            date_columns: 日期列名列表

        Returns:
            pd.DataFrame: 解析后的数据框
        """
        result = df.copy()
        
        for col in date_columns:
            if col in result.columns:
                try:
                    result[col] = pd.to_datetime(result[col])
                except Exception as e:
                    logger.warning(f"解析日期列 {col} 失败: {e}")

        return result

    def filter_by_date_range(
        self,
        df: pd.DataFrame,
        date_column: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        按日期范围筛选数据

        Args:
            df: 数据框
            date_column: 日期列名
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 筛选后的数据
        """
        if date_column not in df.columns:
            return df

        result = df.copy()
        
        if start_date:
            result = result[result[date_column] >= start_date]
        
        if end_date:
            result = result[result[date_column] <= end_date]

        return result

    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        验证数据模式

        Args:
            df: 数据框

        Returns:
            Tuple[bool, List[str]]: (是否有效, 缺失列列表)
        """
        required_columns = ["消耗", "用户量", "cpa", "roi1"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        return len(missing_columns) == 0, missing_columns

    def get_summary(self, df: pd.DataFrame) -> Dict:
        """
        获取数据摘要

        Args:
            df: 数据框

        Returns:
            Dict: 数据摘要
        """
        summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }

        # 数值列统计
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()

        return summary


def load_material_data(file_path: str | Path) -> pd.DataFrame:
    """
    便捷函数：加载素材数据

    Args:
        file_path: 文件路径

    Returns:
        pd.DataFrame: 素材数据
    """
    reader = ExcelReader()
    return reader.read(file_path)