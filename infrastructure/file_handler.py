# infrastructure/file_handler.py
# 文件读写处理

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


class FileHandler:
    """文件处理工具"""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        初始化文件处理器

        Args:
            base_dir: 基础目录，默认为当前工作目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    def ensure_dir(self, *paths: str) -> Path:
        """
        确保目录存在

        Args:
            *paths: 相对路径部分

        Returns:
            Path: 目录路径
        """
        full_path = self.base_dir.joinpath(*paths)
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path

    def read_json(self, file_path: str | Path) -> Dict[str, Any]:
        """
        读取JSON文件

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: JSON数据
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(
        self,
        data: Dict[str, Any],
        file_path: str | Path,
        indent: int = 2
    ) -> None:
        """
        写入JSON文件

        Args:
            data: 数据
            file_path: 文件路径
            indent: 缩进
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)

    def read_text(self, file_path: str | Path) -> str:
        """
        读取文本文件

        Args:
            file_path: 文件路径

        Returns:
            str: 文本内容
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def write_text(self, content: str, file_path: str | Path) -> None:
        """
        写入文本文件

        Args:
            content: 文本内容
            file_path: 文件路径
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def copy_file(self, src: str | Path, dst: str | Path) -> None:
        """
        复制文件

        Args:
            src: 源文件路径
            dst: 目标文件路径
        """
        src = Path(src)
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    def move_file(self, src: str | Path, dst: str | Path) -> None:
        """
        移动文件

        Args:
            src: 源文件路径
            dst: 目标文件路径
        """
        src = Path(src)
        dst = Path(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    def delete_file(self, file_path: str | Path) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否成功删除
        """
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_files(
        self,
        directory: str | Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """
        列出文件

        Args:
            directory: 目录路径
            pattern: 文件模式
            recursive: 是否递归

        Returns:
            List[Path]: 文件列表
        """
        directory = Path(directory)
        
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))

    def get_file_info(self, file_path: str | Path) -> Dict[str, Any]:
        """
        获取文件信息

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, Any]: 文件信息
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        stat = file_path.stat()
        return {
            "name": file_path.name,
            "path": str(file_path),
            "size": stat.st_size,
            "size_mb": round(stat.st_size / 1024 / 1024, 2),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "suffix": file_path.suffix
        }

    def read_lines(
        self,
        file_path: str | Path,
        max_lines: Optional[int] = None
    ) -> List[str]:
        """
        按行读取文件

        Args:
            file_path: 文件路径
            max_lines: 最大行数

        Returns:
            List[str]: 行列表
        """
        file_path = Path(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            if max_lines:
                return [f.readline() for _ in range(max_lines)]
            return f.readlines()

    def append_line(self, content: str, file_path: str | Path) -> None:
        """
        追加行到文件

        Args:
            content: 内容
            file_path: 文件路径
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content + "\n")

    def save_cache(
        self,
        key: str,
        data: Any,
        cache_dir: Optional[Path] = None
    ) -> None:
        """
        保存缓存

        Args:
            key: 缓存键
            data: 缓存数据
            cache_dir: 缓存目录
        """
        cache_dir = cache_dir or Path(".cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 清理键名（移除非法字符）
        safe_key = self._sanitize_key(key)
        cache_file = cache_dir / f"{safe_key}.json"
        
        self.write_json({
            "key": key,
            "data": data,
            "cached_at": datetime.now().isoformat()
        }, cache_file)

    def load_cache(
        self,
        key: str,
        cache_dir: Optional[Path] = None,
        ttl: Optional[int] = None
    ) -> Optional[Any]:
        """
        加载缓存

        Args:
            key: 缓存键
            cache_dir: 缓存目录
            ttl: 缓存有效期（秒）

        Returns:
            Optional[Any]: 缓存数据，如果过期或不存在返回None
        """
        cache_dir = cache_dir or Path(".cache")
        safe_key = self._sanitize_key(key)
        cache_file = cache_dir / f"{safe_key}.json"
        
        if not cache_file.exists():
            return None

        try:
            cached = self.read_json(cache_file)
            cached_at = datetime.fromisoformat(cached["cached_at"])
            
            # 检查是否过期
            if ttl:
                age = (datetime.now() - cached_at).total_seconds()
                if age > ttl:
                    return None
            
            return cached["data"]
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
            return None

    def _sanitize_key(self, key: str) -> str:
        """清理键名"""
        # 替换非法字符
        import re
        return re.sub(r'[^\w\-_.]', '_', key)


# 便捷函数
_handler = FileHandler()

read_json = _handler.read_json
write_json = _handler.write_json
read_text = _handler.read_text
write_text = _handler.write_text