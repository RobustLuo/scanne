"""
资源路径解析：兼容开发环境与 PyInstaller 打包后的 _MEIPASS 目录。
"""

import os
import sys


def get_bundle_dir() -> str:
    """返回打包资源根目录（preview.html、assets/ 等）。"""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def resource_path(*parts: str) -> str:
    """拼接 bundle 内的资源路径。"""
    return os.path.join(get_bundle_dir(), *parts)
