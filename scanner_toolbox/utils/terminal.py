"""
终端 UI 工具：ANSI 颜色、方框绘制、文本对齐、尺寸格式化
"""

import re
import sys
import ctypes

from scanner_toolbox.config.constants import Colors

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _visual_len(s):
    """计算字符串可视宽度（中文/emoji 算 2，ANSI 不算）"""
    s = _ANSI_RE.sub("", s)
    w = 0
    for ch in s:
        cp = ord(ch)
        if (0x1100 <= cp <= 0x115F or 0x2E80 <= cp <= 0x303E or
            0x3041 <= cp <= 0x33FF or 0x3400 <= cp <= 0x4DBF or
            0x4E00 <= cp <= 0x9FFF or 0xA000 <= cp <= 0xA4CF or
            0xAC00 <= cp <= 0xD7A3 or 0xF900 <= cp <= 0xFAFF or
            0xFE30 <= cp <= 0xFE4F or 0xFF00 <= cp <= 0xFF60 or
            0xFFE0 <= cp <= 0xFFE6 or 0x1F300 <= cp <= 0x1FAFF or
            0x2600 <= cp <= 0x27BF):
            w += 2
        else:
            w += 1
    return w


def _pad_to(s, width, fill=" "):
    """把字符串按可视宽度右侧填充到 width"""
    cur = _visual_len(s)
    if cur >= width:
        return s
    return s + fill * (width - cur)


def draw_box(title, lines, width=58, color=None):
    """绘制对齐的 Unicode 方框
    lines: 每行可以是 str 或 ('label', 'desc') 元组
    """
    color = color or Colors.CYAN
    bold = Colors.BOLD
    reset = Colors.RESET
    inner = width - 2
    top = f"{color}{bold}┌{'─' * inner}┐{reset}"
    sep = f"{color}{bold}├{'─' * inner}┤{reset}"
    bot = f"{color}{bold}└{'─' * inner}┘{reset}"
    print(top)
    pad = (inner - _visual_len(title)) // 2
    title_line = " " * pad + title
    title_line = _pad_to(title_line, inner)
    print(f"{color}{bold}│{reset}{Colors.WHITE}{Colors.BOLD}{title_line}{reset}{color}{bold}│{reset}")
    print(sep)
    for line in lines:
        if line is None:
            print(sep)
            continue
        if isinstance(line, tuple) and len(line) == 2:
            text = f" {line[0]} {line[1]}"
        else:
            text = f" {line}"
        padded = _pad_to(text, inner)
        print(f"{color}{bold}│{reset}{padded}{color}{bold}│{reset}")
    print(bot)


def section(title, color=None, char="═"):
    """打印一个二级标题分割线"""
    color = color or Colors.CYAN
    bar = char * 58
    print(f"\n{color}{Colors.BOLD}{bar}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}  ▎ {title}{Colors.RESET}")
    print(f"{color}{Colors.BOLD}{bar}{Colors.RESET}\n")


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def enable_virtual_terminal():
    """启用Windows虚拟终端，支持ANSI颜色"""
    if sys.platform == "win32":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """请求以管理员权限重新运行"""
    import sys
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]),
            None, 1
        )
        sys.exit(0)
