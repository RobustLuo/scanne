"""
常量定义：颜色、路径、电源计划 GUID 等
"""

import os


# ============================================================
# ANSI 终端颜色
# ============================================================

class Colors:
    """Windows控制台颜色 (ANSI)"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    DARK_GREEN = "\033[32m"
    DARK_CYAN = "\033[36m"
    DARK_YELLOW = "\033[33m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


# ============================================================
# 系统路径常量
# ============================================================

HOSTS_PATH = os.path.expandvars(r"%SystemRoot%\System32\drivers\etc\hosts")

DEFAULT_HOSTS_CONTENT = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# 127.0.0.1       localhost
# ::1             localhost
"""

PERF_BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "..", "perf_backup.json")

# ============================================================
# 电源计划 GUID
# ============================================================

POWER_PLAN_HIGH = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
POWER_PLAN_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
POWER_PLAN_SAVER = "a1841308-3541-4fab-bc81-f71556f20b4a"
POWER_PLAN_ULTIMATE = "e9a42b02-d5df-448d-aa00-03f14749eb61"

# ============================================================
# Windows API 常量
# ============================================================

MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
MOVEFILE_REPLACE_EXISTING = 0x1
SPI_SETDROPSHADOW = 0x1025
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02

# ============================================================
# 启动项注册表路径
# ============================================================

STARTUP_REGISTRY_KEYS = [
    (0x80000002, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run"),
    (0x80000002, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run(32)"),
    (0x80000001, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU\\Run"),
    (0x80000002, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM\\RunOnce"),
    (0x80000001, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU\\RunOnce"),
]

STARTUP_FOLDERS = [
    (os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"), "用户启动夹"),
    (os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"), "公共启动夹"),
]
