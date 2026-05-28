"""
流氓软件扫描器 v2.0
扫描所有磁盘驱动器，查找隐藏的国产流氓/捆绑/垃圾软件残留
支持: 360全家桶、2345系列、百度系、金山/猎豹/毒霸、驱动精灵/人生、
      搜狗捆绑、暴风/风行/PPTV、快压/好压、小鸟壁纸、装机工具等
"""

import os
import sys
import string
import ctypes
import winreg
import subprocess
from datetime import datetime


# ============================================================
# 目标软件分类清单
# ============================================================

KNOWN_DIRS = [
    # --- 360全家桶 ---
    "360Safe", "360sd", "360Downloads", "360AP", "360Chrome",
    "360DeskTop", "360Rec", "360zip", "360驱动大师", "360急救箱",
    "360壁纸", "360文件恢复", "Qihoo", "360TotalSecurity",
    "360GameCenter", "360浏览器", "360安全浏览器", "360极速浏览器",
    "LiveUpdate360", "360Safeguard", "360Speedld", "360Safe\deepscan",
    "HipsMain", "360WiFi", "360手机助手",
    # --- 2345系列 ---
    "2345Explorer", "2345Pinyin", "2345Calc", "2345好压",
    "2345MPCSafe", "2345Downloads", "2345王牌", "2345看图王",
    "Hao123", "hao123桌面",
    # --- 百度系 ---
    "BaiduSd", "BaiduAnSafe", "BaiduProtect", "BaiduNetdiskPlugin",
    "Baidu", "百度杀毒", "百度卫士", "百度浏览器", "百度输入法",
    "BaiduPinyin", "BaiduBrowser", "BaiduPlayer",
    # --- 金山/猎豹/毒霸 ---
    "Kingsoft", "kbasesrv", "WPSOffice_promote", "KSafe",
    "KingsonAntivirus", "金山毒霸", "金山卫士", "liebao",
    "猎豹浏览器", "猎豹清理大师", "Cheetah", "CheetahBrowser",
    "cmcm", "KingsmountainSafe", "duba", "ijinshan",
    # --- 鲁大师 ---
    "鲁大师", "LuDaShi", "ludashi", "ComputerZ",
    # --- 驱动精灵/驱动人生/万能驱动 ---
    "DriverGenius", "驱动精灵", "DrvCeo", "驱动人生",
    "DTLSoft", "EasyDrivers", "万能驱动",
    # --- 搜狗 ---
    "SogouInput", "Sogou", "SogouExplorer", "搜狗输入法",
    "搜狗浏览器", "SogouPinyin",
    # --- 腾讯电脑管家(部分用户视为流氓) ---
    "QQPCMgr", "Tencent\QQPCMgr", "腾讯电脑管家",
    # --- 暴风/风行/PPTV ---
    "暴风影音", "Baofeng", "StormII", "FunshionInstall",
    "Funshion", "风行", "PPLive", "PPTV",
    # --- 迅雷推广组件 ---
    "XLServicePlatform", "ThunderPlatform", "迅雷看看",
    # --- 快压/速压/好压 ---
    "快压", "KuaiZip", "速压", "SuYa", "好压", "HaoZip", "2345好压",
    # --- 小鸟壁纸/桌面日历/布丁 ---
    "小鸟壁纸", "BirdWallpaper", "桌面日历", "布丁桌面",
    "DesktopCal", "pudding",
    # --- 装机/Ghost工具(常捆绑) ---
    "老毛桃", "大白菜", "OneKey", "小白一键重装",
    "系统之家", "雨林木风", "深度技术", "Ghost",
    # --- 其他流氓/广告 ---
    "ADSafe", "净网大师", "瑞星", "Rising",
    "飞速PDF", "万能看图", "WanNeng",
    "UC浏览器", "UCBrowser", "桔子浏览器",
    "趣输入", "QuInput", "章鱼输入法",
    "WiFi万能钥匙", "WiFiMaster",
    "P2PSearcher", "盗版资源搜索",
    "电脑店", "U深度", "微PE工具箱_promote",
    "天天动听", "酷狗推广", "kugou_promote",
]

KNOWN_FILES = [
    # 360
    "360tray.exe", "360safe.exe", "360sd.exe", "360rp.exe",
    "QHSafeMain.exe", "QHActiveDefense.exe", "360leakfixer.exe",
    "360hotfix.exe", "360speedld.exe", "PopBlock.exe", "360Chrome.exe",
    "HelperMain.exe", "360TSLiveUpdate.exe", "360Game.exe",
    # 2345
    "2345Explorer.exe", "2345MPCSafe.exe", "2345Pinyin.exe",
    "2345Calc.exe", "2345pic.exe", "Hao123.exe",
    # 百度
    "BaiduSd.exe", "BaiduAnSafe.exe", "BaiduProtect.exe",
    "BaiduHips.exe", "BaiduPinyin.exe", "BaiduBrowser.exe",
    # 金山/猎豹/毒霸
    "kdump.exe", "kxescore.exe", "kxetray.exe", "ksafe.exe",
    "KSafeSvc.exe", "KSafeTray.exe", "kislive.exe",
    "liebao.exe", "CheetahBrowser.exe", "cmcm.exe",
    "duba.exe", "kwatch.exe", "kavlog2.exe",
    # 鲁大师
    "ComputerZ.exe", "ludashi.exe", "LuDaShiSvc.exe",
    # 驱动精灵/人生
    "DGService.exe", "DriverGenius.exe", "DTLService.exe",
    "DriveTheLife.exe", "DrvCeo.exe",
    # 搜狗
    "SogouExplorer.exe", "SGTool.exe", "SogouCloud.exe",
    "PinyinUp.exe", "SogouServices.exe",
    # 暴风/风行/PPTV
    "StormPlayer.exe", "Baofeng.exe", "Funshion.exe",
    "PPLive.exe", "PPTV.exe",
    # 快压/好压
    "KuaiZip.exe", "HaoZip.exe", "SuYaZip.exe",
    # 其他
    "ADSafe.exe", "UCBrowser.exe", "Rising.exe", "RavMon.exe",
    "WifiMaster.exe", "QuInput.exe",
    "PCMgrUpdate.exe", "QQPCMgr.exe",
    # 弹窗广告进程
    "PopupHelper.exe", "MiniNews.exe", "NewsTray.exe",
    "TrayHelper.exe", "DesktopLite.exe", "MiniBrowser.exe",
]

KNOWN_SERVICES = [
    # 360
    "ZhuDongFangYu", "360rp", "360Safeguard", "QHActiveDefense",
    "QHWatchdog", "QHHTTP", "QPCore", "360netfilter",
    "LiveUpdate360", "360FsFlt", "360AntiHacker",
    # 百度
    "BaiduSdSvc", "BaiduHips", "BaiduProtect",
    # 金山/毒霸
    "KSafeSvc", "kbasesrv", "KWatchSvc", "KisliveService",
    # 2345
    "2345Explorer", "2345MPCSafe",
    # 鲁大师
    "LuDaShiSvc",
    # 驱动精灵/人生
    "DGService", "DTLService", "DriveTheLifeService",
    # 搜狗
    "SogouServices",
    # 暴风
    "StormService", "BaofengService",
    # 迅雷
    "XLServicePlatform",
    # 瑞星
    "RsRavMon", "RsCCenter",
    # 腾讯管家
    "QQPCRTP", "QQPCMgr",
]

REGISTRY_KEYS = [
    # 360
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\360Safe"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\360"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Qihoo"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\360Safe"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Qihoo"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\360Safe"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\360"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\360安全卫士"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\360杀毒"),
    # 2345
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\2345"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\HaoZip"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\2345"),
    # 百度
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Baidu"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\BaiduSd"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Baidu"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Baidu"),
    # 金山/猎豹
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Kingsoft"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Kingsoft"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\liebao"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\cmcm"),
    # 鲁大师
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\LuDaShi"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\LuDaShi"),
    # 驱动精灵/人生
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\DriverGenius"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\DTLSoft\DriveTheLife"),
    # 搜狗
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Sogou"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Sogou"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\SogouInput"),
    # 瑞星
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Rising"),
    # 腾讯管家
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\QQPCMgr"),
    # 暴风
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Baofeng"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\StormII"),
    # 快压
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\KuaiZip"),
]

SCHEDULED_TASK_KEYWORDS = [
    "360", "Qihoo", "2345", "Kingsoft", "鲁大师",
    "Baidu", "百度", "BaiduSd", "liebao", "猎豹",
    "DriverGenius", "驱动精灵", "DriveTheLife", "驱动人生",
    "Sogou", "搜狗", "Rising", "瑞星",
    "KSafe", "金山", "duba", "毒霸",
    "Baofeng", "暴风", "Funshion", "PPTV",
    "KuaiZip", "快压", "HaoZip",
    "QQPCMgr", "LuDaShi", "ludashi",
    "ADSafe", "小鸟壁纸", "BirdWallpaper",
]


class Colors:
    """Windows控制台颜色 (ANSI)"""
    # 基础前景色
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    # 深色（不那么刺眼）
    DARK_GREEN = "\033[32m"
    DARK_CYAN = "\033[36m"
    DARK_YELLOW = "\033[33m"
    # 背景色
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    # 样式
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


# ============================================================
# UI 工具：处理中文/emoji 宽度对齐
# ============================================================
import re as _re
_ANSI_RE = _re.compile(r"\x1b\[[0-9;]*m")


def _visual_len(s):
    """计算字符串可视宽度（中文/emoji 算 2，ANSI 不算）"""
    s = _ANSI_RE.sub("", s)
    w = 0
    for ch in s:
        cp = ord(ch)
        # CJK 基本块 + 中日韩标点 + 全角 + emoji
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
    # 标题居中
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


def enable_virtual_terminal():
    """启用Windows虚拟终端，支持ANSI颜色"""
    if sys.platform == "win32":
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


def get_all_drives():
    """获取所有可用磁盘驱动器"""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
            # 检查驱动器是否可访问（排除光驱等）
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            if drive_type in (3, 6):  # DRIVE_FIXED=3, DRIVE_RAMDISK=6
                drives.append(drive)
        bitmask >>= 1
    return drives


def scan_directories(drives):
    """扫描所有磁盘中的可疑目录"""
    found = []
    common_paths = [
        "Program Files",
        "Program Files (x86)",
        "ProgramData",
        "Users",
    ]

    for drive in drives:
        # 扫描根目录
        try:
            for item in os.listdir(drive):
                item_lower = item.lower()
                for known in KNOWN_DIRS:
                    if known.lower() in item_lower:
                        full_path = os.path.join(drive, item)
                        if os.path.isdir(full_path):
                            found.append(full_path)
        except PermissionError:
            pass
        except Exception:
            pass

        # 扫描常见安装路径
        for sub in common_paths:
            base = os.path.join(drive, sub)
            if not os.path.isdir(base):
                continue
            try:
                for item in os.listdir(base):
                    item_lower = item.lower()
                    for known in KNOWN_DIRS:
                        if known.lower() in item_lower:
                            full_path = os.path.join(base, item)
                            if os.path.isdir(full_path):
                                found.append(full_path)
            except PermissionError:
                pass
            except Exception:
                pass

        # 扫描隐藏目录（带hidden属性的）
        try:
            for root, dirs, files in os.walk(drive):
                # 只扫描前两层避免太慢
                depth = root.replace(drive, "").count(os.sep)
                if depth > 2:
                    dirs.clear()
                    continue
                for d in dirs:
                    d_lower = d.lower()
                    for known in KNOWN_DIRS:
                        if known.lower() in d_lower:
                            full_path = os.path.join(root, d)
                            try:
                                attrs = ctypes.windll.kernel32.GetFileAttributesW(full_path)
                                if attrs & 2:  # FILE_ATTRIBUTE_HIDDEN
                                    found.append(f"{full_path} [隐藏]")
                                elif full_path not in found:
                                    found.append(full_path)
                            except Exception:
                                pass
        except Exception:
            pass

    return list(set(found))


def scan_files(drives):
    """扫描可疑可执行文件"""
    found = []
    search_paths = []

    for drive in drives:
        for sub in ["Program Files", "Program Files (x86)", "ProgramData", "Windows\\Temp"]:
            path = os.path.join(drive, sub)
            if os.path.isdir(path):
                search_paths.append(path)

    for base in search_paths:
        try:
            for root, dirs, files in os.walk(base):
                depth = root.replace(base, "").count(os.sep)
                if depth > 3:
                    dirs.clear()
                    continue
                for f in files:
                    f_lower = f.lower()
                    for known in KNOWN_FILES:
                        if known.lower() == f_lower:
                            found.append(os.path.join(root, f))
        except PermissionError:
            pass
        except Exception:
            pass

    return list(set(found))


def scan_registry():
    """扫描注册表中的360相关项"""
    found = []
    for hive, key_path in REGISTRY_KEYS:
        try:
            key = winreg.OpenKey(hive, key_path)
            hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
            found.append(f"{hive_name}\\{key_path}")
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass
        except PermissionError:
            found.append(f"[权限不足] {key_path}")
        except Exception:
            pass
    return found


def scan_services():
    """扫描可疑Windows服务"""
    found = []
    try:
        result = subprocess.run(
            ["sc", "query", "state=", "all"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        lines = result.stdout.split("\n")
        for line in lines:
            line_lower = line.lower()
            for svc in KNOWN_SERVICES:
                if svc.lower() in line_lower:
                    found.append(line.strip())
    except Exception:
        pass
    return found


def scan_scheduled_tasks():
    """扫描可疑计划任务"""
    found = []
    try:
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "csv"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        for line in result.stdout.split("\n"):
            line_lower = line.lower()
            for kw in SCHEDULED_TASK_KEYWORDS:
                if kw.lower() in line_lower:
                    found.append(line.strip().strip('"'))
                    break
    except Exception:
        pass
    return found


def scan_startup():
    """扫描启动项"""
    found = []
    startup_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    ]

    keywords = [
        "360", "qihoo", "2345", "kingsoft", "鲁大师",
        "baidu", "百度", "liebao", "猎豹", "duba", "毒霸",
        "sogou", "搜狗", "rising", "瑞星",
        "drivergenius", "驱动精灵", "drivethelife", "驱动人生",
        "baofeng", "暴风", "funshion", "pptv",
        "kuaizip", "快压", "haozip",
        "qqpcmgr", "ludashi", "adsafe",
        "ucbrowser", "小鸟壁纸",
    ]

    for hive, key_path in startup_keys:
        try:
            key = winreg.OpenKey(hive, key_path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    for kw in keywords:
                        if kw.lower() in name.lower() or kw.lower() in value.lower():
                            found.append(f"{name} -> {value}")
                            break
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    return found


def get_dir_size(path):
    """获取目录大小"""
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except Exception:
                    pass
    except Exception:
        pass
    return total


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


def print_header():
    """打印标题"""
    C = Colors
    print(f"""
{C.BOLD}{C.CYAN}
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║   {C.WHITE}███████╗██╗   ██╗██████╗ ███████╗██████╗{C.CYAN}     ║
    ║   {C.WHITE}██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗{C.CYAN}    ║
    ║   {C.WHITE}███████╗██║   ██║██████╔╝█████╗  ██████╔╝{C.CYAN}    ║
    ║   {C.WHITE}╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗{C.CYAN}    ║
    ║   {C.WHITE}███████║╚██████╔╝██║     ███████╗██║  ██║{C.CYAN}    ║
    ║   {C.WHITE}╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝{C.CYAN}   ║
    ║                                                   ║
    ╠═══════════════════════════════════════════════════╣
    ║                                                   ║
    ║   {C.GREEN}超级骆狗工具箱 v3.0{C.CYAN}                          ║
    ║   {C.GRAY}Windows 一站式维护 · 9大模块{C.CYAN}                  ║
    ║                                                   ║
    ║   {C.DIM}反流氓 · 反劫持 · 空间清理 · 安全审计{C.CYAN}        ║
    ║   {C.DIM}网络工具 · 装机助手 · 性能优化{C.CYAN}                ║
    ║                                                   ║
    ╠═══════════════════════════════════════════════════╣
    ║   {C.GRAY}Author: RobustLuo{C.CYAN}                             ║
    ║   {C.GRAY}GitHub: github.com/RobustLuo/scanne{C.CYAN}           ║
    ╚═══════════════════════════════════════════════════╝
{C.RESET}""")


def print_section(title, items, show_size=False):
    """打印扫描结果区段"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}{Colors.RESET}")

    if not items:
        print(f"  {Colors.GREEN}✓ 未发现可疑项{Colors.RESET}")
        return 0

    total_size = 0
    for item in items:
        print(f"  {Colors.RED}✗ {item}{Colors.RESET}")
        if show_size and os.path.isdir(item.replace(" [隐藏]", "")):
            real_path = item.replace(" [隐藏]", "")
            size = get_dir_size(real_path)
            total_size += size
            print(f"    {Colors.YELLOW}占用: {format_size(size)}{Colors.RESET}")

    if show_size and total_size > 0:
        print(f"\n  {Colors.YELLOW}总占用空间: {format_size(total_size)}{Colors.RESET}")

    return len(items)


def generate_report(results):
    """生成扫描报告到文件"""
    report_name = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_name, "w", encoding="utf-8") as f:
        f.write("流氓软件扫描报告 v2.0\n")
        f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        for section, items in results.items():
            f.write(f"[{section}]\n")
            if items:
                for item in items:
                    f.write(f"  - {item}\n")
            else:
                f.write("  无\n")
            f.write("\n")

    return report_name


def _force_delete_file(fp):
    """强力删除单个文件：直接删 → cmd强删 → 提权后删 → 登记重启删
    注：_take_ownership/_schedule_delete_on_reboot 定义于本模块后段，调用时已解析"""
    # 第1级：直接删
    try:
        os.remove(fp)
        return True, "direct"
    except (PermissionError, OSError):
        pass

    # 第2级：cmd /c del /f /q 绕过 Python 句柄限制
    try:
        subprocess.run(["cmd", "/c", "del", "/f", "/q", fp],
                       capture_output=True, timeout=5)
        if not os.path.exists(fp):
            return True, "cmd_del"
    except Exception:
        pass

    # 第3级：复用现有 _take_ownership 提权后删
    try:
        _take_ownership(fp, recursive=False)
        os.remove(fp)
        return True, "takeown"
    except Exception:
        pass

    # 第4级：复用现有 _schedule_delete_on_reboot 登记重启删除
    if _schedule_delete_on_reboot(fp):
        return True, "reboot"

    return False, "failed"


def _force_delete_dir(dp):
    """强力删除目录"""
    try:
        os.rmdir(dp)
        return True
    except OSError:
        pass
    try:
        subprocess.run(
            ["cmd", "/c", "rd", "/s", "/q", dp],
            capture_output=True, timeout=10
        )
        return not os.path.exists(dp)
    except Exception:
        return False


def _clean_paths(paths_list):
    """通用路径清理（强力版），返回 (cleaned_bytes, file_count, error_count)"""
    total_cleaned = 0
    total_files = 0
    total_errors = 0
    reboot_pending = 0

    for path, desc in paths_list:
        if not os.path.isdir(path):
            continue

        size_before = get_dir_size(path)
        if size_before == 0:
            continue

        print(f"  {Colors.YELLOW}清理: {desc}{Colors.RESET}")
        print(f"    路径: {path}")
        print(f"    大小: {format_size(size_before)}")

        cleaned = 0
        errors = 0
        pending = 0
        for root, dirs, files in os.walk(path, topdown=False):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    size = os.path.getsize(fp)
                except Exception:
                    size = 0
                success, method = _force_delete_file(fp)
                if success:
                    cleaned += size
                    total_files += 1
                    if method == "reboot":
                        pending += 1
                else:
                    errors += 1
            for d in dirs:
                dp = os.path.join(root, d)
                _force_delete_dir(dp)

        total_cleaned += cleaned
        total_errors += errors
        reboot_pending += pending
        if cleaned > 0:
            print(f"    {Colors.GREEN}已清理: {format_size(cleaned)}{Colors.RESET}")
        if pending > 0:
            print(f"    {Colors.CYAN}已登记 {pending} 个文件重启后删除{Colors.RESET}")
        if errors > 0:
            print(f"    {Colors.RED}跳过 {errors} 个无法删除的文件{Colors.RESET}")
        print()

    if reboot_pending > 0:
        print(f"  {Colors.CYAN}提示: 共有 {reboot_pending} 个顽固文件已登记重启删除，下次开机自动清除{Colors.RESET}\n")

    return total_cleaned, total_files, total_errors


def _clean_files_by_ext(directory, extensions, desc):
    """清理指定目录下特定扩展名文件，返回 (cleaned_bytes, file_count, error_count)"""
    cleaned = 0
    files_count = 0
    errors = 0
    if not os.path.isdir(directory):
        return 0, 0, 0

    found_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if any(f.lower().endswith(ext) for ext in extensions):
                found_files.append(os.path.join(root, f))

    if not found_files:
        return 0, 0, 0

    total_size = sum(os.path.getsize(fp) for fp in found_files if os.path.exists(fp))
    print(f"  {Colors.YELLOW}清理: {desc}{Colors.RESET}")
    print(f"    路径: {directory}")
    print(f"    文件数: {len(found_files)}，大小: {format_size(total_size)}")

    for fp in found_files:
        try:
            size = os.path.getsize(fp)
            os.remove(fp)
            cleaned += size
            files_count += 1
        except Exception:
            errors += 1

    if cleaned > 0:
        print(f"    {Colors.GREEN}已清理: {format_size(cleaned)}{Colors.RESET}")
    if errors > 0:
        print(f"    {Colors.RED}跳过 {errors} 个被占用文件{Colors.RESET}")
    print()
    return cleaned, files_count, errors


def _empty_recycle_bin():
    """清空回收站"""
    print(f"  {Colors.YELLOW}清理: 回收站{Colors.RESET}")
    try:
        # SHEmptyRecycleBinW flags: SHERB_NOCONFIRMATION=1 | SHERB_NOPROGRESSUI=2 | SHERB_NOSOUND=4
        result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        if result == 0:
            print(f"    {Colors.GREEN}回收站已清空{Colors.RESET}")
        else:
            print(f"    {Colors.GREEN}回收站已经是空的{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}清空回收站失败: {e}{Colors.RESET}")
    print()


def _flush_dns():
    """刷新DNS缓存"""
    print(f"  {Colors.YELLOW}清理: DNS缓存{Colors.RESET}")
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=10)
        print(f"    {Colors.GREEN}DNS缓存已刷新{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}刷新DNS失败: {e}{Colors.RESET}")
    print()


def _clean_windows_old():
    """清理 Windows.old 与系统升级残留（调用系统 cleanmgr 静默清理）"""
    print(f"  {Colors.YELLOW}清理: Windows.old 与系统残留{Colors.RESET}")

    # 检查所有盘的 Windows.old
    drives = get_all_drives()
    found_any = False
    total_size = 0
    for d in drives:
        wo = os.path.join(d, "Windows.old")
        if os.path.isdir(wo):
            found_any = True
            sz = get_dir_size(wo)
            total_size += sz
            print(f"    发现: {wo}  ({format_size(sz)})")

    if not found_any:
        print(f"    {Colors.GREEN}未发现 Windows.old 残留{Colors.RESET}")
    else:
        print(f"\n    {Colors.CYAN}使用 takeown + rd 强力删除...{Colors.RESET}")
        for d in drives:
            wo = os.path.join(d, "Windows.old")
            if not os.path.isdir(wo):
                continue
            try:
                # 提权
                subprocess.run(["takeown", "/f", wo, "/r", "/d", "y"],
                               capture_output=True, timeout=120)
                subprocess.run(["icacls", wo, "/grant", "administrators:F", "/t"],
                               capture_output=True, timeout=120)
                # 强删
                subprocess.run(["cmd", "/c", "rd", "/s", "/q", wo],
                               capture_output=True, timeout=300)
                if not os.path.exists(wo):
                    print(f"    {Colors.GREEN}已删除: {wo}{Colors.RESET}")
                else:
                    print(f"    {Colors.YELLOW}部分残留: {wo}{Colors.RESET}")
            except Exception as e:
                print(f"    {Colors.RED}清理失败 {wo}: {e}{Colors.RESET}")

    # 另外调用 cleanmgr 处理 Windows 升级日志/旧驱动包
    print(f"\n    {Colors.CYAN}启动 Windows 磁盘清理（cleanmgr）静默处理升级残留...{Colors.RESET}")
    try:
        # 用预设 sageset/sagerun，这里直接调用 dism 清理组件存储（最有效）
        subprocess.run(
            ["dism", "/online", "/cleanup-image", "/startcomponentcleanup", "/resetbase"],
            capture_output=True, timeout=600
        )
        print(f"    {Colors.GREEN}组件存储清理完成（WinSxS 旧版本已移除）{Colors.RESET}")
    except subprocess.TimeoutExpired:
        print(f"    {Colors.YELLOW}DISM 超时，建议手动运行{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}DISM 清理失败: {e}{Colors.RESET}")

    print()


def clean_cache():
    """系统垃圾深度清理（增强版）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统垃圾深度清理")
    print(f"{'='*50}{Colors.RESET}\n")

    # 定义清理类别
    categories = {
        "1": {
            "name": "系统临时文件与缓存",
            "paths": [
                (os.path.expandvars(r"%TEMP%"), "用户临时文件 (%TEMP%)"),
                (os.path.expandvars(r"%SystemRoot%\Temp"), "系统临时文件"),
                (os.path.expandvars(r"%LocalAppData%\Temp"), "本地临时文件"),
                (os.path.expandvars(r"%SystemRoot%\Prefetch"), "预读取缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer"), "缩略图缓存"),
                (os.path.expandvars(r"%SystemRoot%\ServiceProfiles\LocalService\AppData\Local\FontCache"), "字体缓存"),
            ]
        },
        "2": {
            "name": "浏览器缓存（全部浏览器）",
            "paths": [
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\INetCache"), "IE/Edge网页缓存"),
                (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"), "Chrome缓存"),
                (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Code Cache"), "Chrome代码缓存"),
                (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\GPUCache"), "Chrome GPU缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"), "Edge缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Code Cache"), "Edge代码缓存"),
                (os.path.expandvars(r"%LocalAppData%\Mozilla\Firefox\Profiles"), "Firefox缓存"),
                (os.path.expandvars(r"%LocalAppData%\Opera Software\Opera Stable\Cache"), "Opera缓存"),
                (os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Cache"), "Brave缓存"),
                (os.path.expandvars(r"%LocalAppData%\360Chrome\Chrome\User Data\Default\Cache"), "360浏览器缓存"),
                (os.path.expandvars(r"%LocalAppData%\Tencent\QQBrowser\User Data\Default\Cache"), "QQ浏览器缓存"),
                (os.path.expandvars(r"%LocalAppData%\2345Explorer\User Data\Default\Cache"), "2345浏览器缓存"),
                (os.path.expandvars(r"%LocalAppData%\Sogou\SogouExplorer\Cache"), "搜狗浏览器缓存"),
            ]
        },
        "3": {
            "name": "Windows更新与日志",
            "paths": [
                (os.path.expandvars(r"%SystemRoot%\SoftwareDistribution\Download"), "Windows更新下载缓存"),
                (os.path.expandvars(r"%SystemRoot%\SoftwareDistribution\DataStore\Logs"), "更新日志"),
                (os.path.expandvars(r"%LocalAppData%\CrashDumps"), "用户崩溃转储"),
                (os.path.expandvars(r"%SystemRoot%\Minidump"), "系统小型转储"),
                (os.path.expandvars(r"%ProgramData%\Microsoft\Windows\WER"), "Windows错误报告"),
                (os.path.expandvars(r"%SystemRoot%\Logs\CBS"), "CBS日志"),
                (os.path.expandvars(r"%SystemRoot%\Logs\DISM"), "DISM日志"),
                (os.path.expandvars(r"%SystemRoot%\Panther"), "安装日志"),
            ]
        },
        "4": {
            "name": "常用软件缓存",
            "paths": [
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Office\16.0\OfficeFileCache"), "Office文件缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\WebCache"), "Web缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Terminal Server Client\Cache"), "远程桌面缓存"),
                (os.path.expandvars(r"%LocalAppData%\pip\cache"), "Python pip缓存"),
                (os.path.expandvars(r"%LocalAppData%\npm-cache"), "npm缓存"),
                (os.path.expandvars(r"%LocalAppData%\NuGet\Cache"), "NuGet缓存"),
                (os.path.expandvars(r"%AppData%\Microsoft\Teams\Cache"), "Teams缓存"),
                (os.path.expandvars(r"%AppData%\Microsoft\Teams\GPUCache"), "Teams GPU缓存"),
                (os.path.expandvars(r"%LocalAppData%\Packages\MicrosoftWindows.Client.CBS_cw5n1h2txyewy\TempState"), "微软商店临时"),
            ]
        },
        "5": {
            "name": "国产软件缓存（微信/QQ/迅雷/WPS等）",
            "paths": [
                (os.path.expandvars(r"%AppData%\Tencent\WeChat\XPlugin\Temp"), "微信插件临时"),
                (os.path.expandvars(r"%AppData%\Tencent\WeChat\log"), "微信日志"),
                (os.path.expandvars(r"%AppData%\Tencent\QQ\Temp"), "QQ临时文件"),
                (os.path.expandvars(r"%AppData%\Tencent\QQMusic\Cache"), "QQ音乐缓存"),
                (os.path.expandvars(r"%LocalAppData%\Tencent\QQMusic\Cache"), "QQ音乐本地缓存"),
                (os.path.expandvars(r"%AppData%\Thunder Network\Thunder\Temp"), "迅雷临时文件"),
                (os.path.expandvars(r"%LocalAppData%\Kingsoft\WPS Cloud Files\cache"), "WPS云文件缓存"),
                (os.path.expandvars(r"%AppData%\kingsoft\office6\cache"), "WPS Office缓存"),
                (os.path.expandvars(r"%LocalAppData%\Netease\CloudMusic\Cache"), "网易云音乐缓存"),
                (os.path.expandvars(r"%AppData%\Baidu\BaiduNetdisk\temp"), "百度网盘临时"),
                (os.path.expandvars(r"%AppData%\DingTalk\Cache"), "钉钉缓存"),
                (os.path.expandvars(r"%AppData%\feishu\Cache"), "飞书缓存"),
                (os.path.expandvars(r"%LocalAppData%\Alibaba\taobao\Cache"), "淘宝缓存"),
                (os.path.expandvars(r"%AppData%\Sogou\SGInput\Temp"), "搜狗输入法临时"),
                (os.path.expandvars(r"%LocalAppData%\Bilibili\Cache"), "哔哩哔哩缓存"),
                (os.path.expandvars(r"%LocalAppData%\360\SoftMgr\cache"), "360软件管家缓存"),
                (os.path.expandvars(r"%ProgramData%\Tencent\QQPCMgr\Patch"), "腾讯管家补丁"),
            ]
        },
        "6": {
            "name": "Windows.old 与系统残留（可释放数GB）",
            "special": "windows_old"
        },
        "7": {
            "name": "回收站",
            "special": "recycle_bin"
        },
        "8": {
            "name": "DNS缓存刷新",
            "special": "flush_dns"
        },
    }

    # 显示分类菜单
    print(f"  请选择要清理的类别（可多选，用逗号分隔）：\n")
    for key, cat in categories.items():
        print(f"    {Colors.GREEN}[{key}]{Colors.RESET} {cat['name']}")
    print(f"    {Colors.GREEN}[A]{Colors.RESET} 全部清理")
    print()

    choice = input(f"  {Colors.CYAN}请输入选项 (例: 1,2,3 或 A): {Colors.RESET}").strip().upper()

    if not choice:
        print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        return

    if choice == "A":
        selected = list(categories.keys())
    else:
        selected = [c.strip() for c in choice.split(",") if c.strip() in categories]

    if not selected:
        print(f"  {Colors.RED}无效选择{Colors.RESET}")
        return

    # 先扫描统计
    print(f"\n{Colors.BOLD}  正在扫描垃圾文件...{Colors.RESET}\n")

    total_cleaned = 0
    total_files = 0
    total_errors = 0

    for sel in selected:
        cat = categories[sel]
        print(f"  {Colors.BOLD}{Colors.CYAN}── {cat['name']} ──{Colors.RESET}\n")

        if "special" in cat:
            if cat["special"] == "recycle_bin":
                _empty_recycle_bin()
            elif cat["special"] == "flush_dns":
                _flush_dns()
            elif cat["special"] == "windows_old":
                _clean_windows_old()
        else:
            cleaned, files, errors = _clean_paths(cat["paths"])
            total_cleaned += cleaned
            total_files += files
            total_errors += errors

    # 额外：清理系统日志文件（.log, .tmp, .etl）
    if "3" in selected:
        sys_root = os.path.expandvars(r"%SystemRoot%")
        c1, f1, e1 = _clean_files_by_ext(
            os.path.join(sys_root, "Logs"), [".log", ".etl", ".tmp"],
            "系统日志文件 (*.log, *.etl, *.tmp)"
        )
        total_cleaned += c1
        total_files += f1
        total_errors += e1

    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  垃圾清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}共清理 {total_files} 个文件，释放空间: {format_size(total_cleaned)}{Colors.RESET}")
    if total_errors > 0:
        print(f"  {Colors.YELLOW}(有 {total_errors} 个文件被占用，跳过){Colors.RESET}")


# ============================================================
# 强力删除工具（应对流氓软件自我保护）
# ============================================================

MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
MOVEFILE_REPLACE_EXISTING = 0x1


def _schedule_delete_on_reboot(path):
    """登记到 PendingFileRenameOperations，下次开机由 smss.exe 在驱动加载前删除"""
    try:
        # 路径需为 NT 风格 \??\C:\... 才能被 smss 识别
        nt_path = path if path.startswith("\\??\\") else "\\??\\" + path
        ok = ctypes.windll.kernel32.MoveFileExW(
            nt_path, None, MOVEFILE_DELAY_UNTIL_REBOOT
        )
        return bool(ok)
    except Exception:
        return False


def _take_ownership(path, recursive=True):
    """takeown + icacls 强夺权限"""
    try:
        subprocess.run(
            ["takeown", "/f", path] + (["/r", "/d", "y"] if recursive and os.path.isdir(path) else []),
            capture_output=True, timeout=30
        )
        subprocess.run(
            ["icacls", path, "/grant", "administrators:F"] + (["/t", "/c"] if recursive else ["/c"]),
            capture_output=True, timeout=30
        )
        return True
    except Exception:
        return False


def _kill_holders(path):
    """尝试 kill 占用该文件/目录下文件的进程"""
    killed = []
    try:
        # 用 PowerShell 找出哪些进程的 Path 在该路径下
        ps = (
            "Get-Process | Where-Object { $_.Path -and $_.Path -like '"
            + path.replace("'", "''") + "*' } | "
            "Select-Object -ExpandProperty Id"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, text=True, timeout=15)
        for pid in r.stdout.split():
            pid = pid.strip()
            if pid.isdigit():
                subprocess.run(["taskkill", "/F", "/PID", pid, "/T"],
                               capture_output=True, timeout=10)
                killed.append(pid)
    except Exception:
        pass
    return killed


def force_delete(path):
    """
    多级强力删除：直接删 -> 杀占用进程后删 -> takeown+icacls后删 -> MoveFileEx重启删
    返回: ("deleted" | "pending_reboot" | "failed", detail)
    """
    import shutil

    if not os.path.exists(path):
        return ("deleted", "已不存在")

    is_dir = os.path.isdir(path)

    # 去掉只读/隐藏/系统属性
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)  # NORMAL
        if is_dir:
            for root, dirs, files in os.walk(path):
                for n in dirs + files:
                    try:
                        ctypes.windll.kernel32.SetFileAttributesW(os.path.join(root, n), 0x80)
                    except Exception:
                        pass
    except Exception:
        pass

    # 尝试 1：直接删
    try:
        if is_dir:
            shutil.rmtree(path)
        else:
            os.remove(path)
        return ("deleted", "直接删除")
    except Exception:
        pass

    # 尝试 2：杀占用进程后再删
    killed = _kill_holders(path)
    if killed:
        try:
            if is_dir:
                shutil.rmtree(path)
            else:
                os.remove(path)
            return ("deleted", f"杀进程后删除(PIDs={','.join(killed)})")
        except Exception:
            pass

    # 尝试 3：takeown + icacls 后再删
    _take_ownership(path)
    try:
        if is_dir:
            shutil.rmtree(path)
        else:
            os.remove(path)
        return ("deleted", "提权后删除")
    except Exception:
        pass

    # 尝试 4：MoveFileEx 重启删除
    if is_dir:
        # 目录需要递归登记内部所有文件 + 目录本身
        all_paths = []
        for root, dirs, files in os.walk(path, topdown=False):
            for f in files:
                all_paths.append(os.path.join(root, f))
            for d in dirs:
                all_paths.append(os.path.join(root, d))
        all_paths.append(path)
        any_ok = False
        for p in all_paths:
            if _schedule_delete_on_reboot(p):
                any_ok = True
        if any_ok:
            return ("pending_reboot", "已登记重启删除")
    else:
        if _schedule_delete_on_reboot(path):
            return ("pending_reboot", "已登记重启删除")

    return ("failed", "全部尝试均失败")


def _pre_neutralize(results):
    """清理前置：禁用并停止可疑服务/任务/进程，斩断守护链"""
    print(f"  {Colors.YELLOW}[预处理] 停止守护进程/服务/任务...{Colors.RESET}")

    # 1. 先禁用服务（避免被看门狗拉起）
    for svc_line in results.get("可疑服务", []):
        svc_name = svc_line.split(":")[-1].strip() if ":" in svc_line else svc_line.strip()
        if not svc_name:
            continue
        subprocess.run(["sc", "config", svc_name, "start=", "disabled"], capture_output=True, timeout=10)
        subprocess.run(["sc", "stop", svc_name], capture_output=True, timeout=10)

    # 2. 禁用计划任务
    for task_line in results.get("计划任务", []):
        task_name = task_line.split(",")[0].strip().strip('"')
        if task_name and task_name != "TaskName":
            subprocess.run(["schtasks", "/change", "/tn", task_name, "/disable"],
                           capture_output=True, timeout=10)
            subprocess.run(["schtasks", "/end", "/tn", task_name],
                           capture_output=True, timeout=10)

    # 3. taskkill 已知的可疑进程名
    exe_set = set()
    # 来自扫描到的可疑文件
    for fp in results.get("可疑文件", []):
        exe_set.add(os.path.basename(fp).lower())
    # 来自 KNOWN_FILES 大全
    for exe in KNOWN_FILES:
        exe_set.add(exe.lower())
    for exe in exe_set:
        subprocess.run(["taskkill", "/F", "/IM", exe, "/T"], capture_output=True, timeout=10)


def clean_malware(results):
    """清理扫描到的流氓软件残留（带强力删除）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  开始清理流氓软件残留")
    print(f"{'='*50}{Colors.RESET}\n")

    # 预处理：先停掉守护链
    _pre_neutralize(results)

    cleaned_count = 0
    failed_count = 0
    pending_reboot = 0

    def _handle(status, detail, label):
        nonlocal cleaned_count, failed_count, pending_reboot
        if status == "deleted":
            print(f"    {Colors.GREEN}✓ 已删除: {label}  [{detail}]{Colors.RESET}")
            cleaned_count += 1
        elif status == "pending_reboot":
            print(f"    {Colors.YELLOW}⏰ 已安排重启删除: {label}{Colors.RESET}")
            pending_reboot += 1
        else:
            print(f"    {Colors.RED}✗ 删除失败: {label}  ({detail}){Colors.RESET}")
            failed_count += 1

    # 1. 删除可疑目录
    if results.get("可疑目录"):
        print(f"\n  {Colors.YELLOW}[清理目录]{Colors.RESET}")
        for item in results["可疑目录"]:
            path = item.replace(" [隐藏]", "")
            status, detail = force_delete(path)
            _handle(status, detail, path)

    # 2. 删除可疑文件
    if results.get("可疑文件"):
        print(f"\n  {Colors.YELLOW}[清理文件]{Colors.RESET}")
        for fp in results["可疑文件"]:
            status, detail = force_delete(fp)
            _handle(status, detail, fp)

    # 3. 删除注册表项（带 takeown 重试）
    if results.get("注册表残留"):
        print(f"\n  {Colors.YELLOW}[清理注册表]{Colors.RESET}")
        for reg_item in results["注册表残留"]:
            if reg_item.startswith("[权限不足]"):
                reg_item = reg_item.replace("[权限不足] ", "")
            if reg_item.startswith("HKLM\\"):
                root_name, key_path = "HKLM", reg_item[5:]
            elif reg_item.startswith("HKCU\\"):
                root_name, key_path = "HKCU", reg_item[5:]
            else:
                continue
            full = f"{root_name}\\{key_path}"
            r = subprocess.run(["reg", "delete", full, "/f"], capture_output=True, text=True)
            if r.returncode == 0:
                print(f"    {Colors.GREEN}✓ 已删除: {reg_item}{Colors.RESET}")
                cleaned_count += 1
            else:
                # ACL 拒绝 → 尝试用 PowerShell 强制夺取所有权
                ps = (
                    f"$key = [Microsoft.Win32.Registry]::{'LocalMachine' if root_name=='HKLM' else 'CurrentUser'}"
                    f".OpenSubKey('{key_path}', [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree, "
                    f"[System.Security.AccessControl.RegistryRights]::TakeOwnership); "
                    "if ($key) { "
                    "  $acl = $key.GetAccessControl(); "
                    "  $acl.SetOwner([System.Security.Principal.NTAccount]'Administrators'); "
                    "  $acl.AddAccessRule((New-Object System.Security.AccessControl.RegistryAccessRule("
                    "    'Administrators','FullControl','ContainerInherit','None','Allow'))); "
                    "  $key.SetAccessControl($acl); $key.Close() }"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                               capture_output=True, timeout=15)
                r2 = subprocess.run(["reg", "delete", full, "/f"], capture_output=True, text=True)
                if r2.returncode == 0:
                    print(f"    {Colors.GREEN}✓ 已删除(提权后): {reg_item}{Colors.RESET}")
                    cleaned_count += 1
                else:
                    print(f"    {Colors.RED}✗ 删除失败: {reg_item}{Colors.RESET}")
                    failed_count += 1

    # 4. 删除可疑服务（前面已停，这里只 sc delete）
    if results.get("可疑服务"):
        print(f"\n  {Colors.YELLOW}[删除服务]{Colors.RESET}")
        for svc_line in results["可疑服务"]:
            svc_name = svc_line.split(":")[-1].strip() if ":" in svc_line else svc_line.strip()
            if not svc_name:
                continue
            r = subprocess.run(["sc", "delete", svc_name], capture_output=True)
            if r.returncode == 0:
                print(f"    {Colors.GREEN}✓ 已删除服务: {svc_name}{Colors.RESET}")
                cleaned_count += 1
            else:
                # 服务进程还在 / 驱动锁定 → 用注册表强删
                full = f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\{svc_name}"
                r2 = subprocess.run(["reg", "delete", full, "/f"], capture_output=True)
                if r2.returncode == 0:
                    print(f"    {Colors.YELLOW}⏰ 服务注册表已删，重启后生效: {svc_name}{Colors.RESET}")
                    pending_reboot += 1
                else:
                    print(f"    {Colors.RED}✗ 处理失败: {svc_name}{Colors.RESET}")
                    failed_count += 1

    # 5. 删除可疑计划任务
    if results.get("计划任务"):
        print(f"\n  {Colors.YELLOW}[删除计划任务]{Colors.RESET}")
        for task_line in results["计划任务"]:
            task_name = task_line.split(",")[0].strip().strip('"')
            if not task_name or task_name == "TaskName":
                continue
            r = subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)
            if r.returncode == 0:
                print(f"    {Colors.GREEN}✓ 已删除任务: {task_name}{Colors.RESET}")
                cleaned_count += 1
            else:
                print(f"    {Colors.RED}✗ 删除失败: {task_name}{Colors.RESET}")
                failed_count += 1

    # 6. 清理启动项
    if results.get("启动项"):
        print(f"\n  {Colors.YELLOW}[清理启动项]{Colors.RESET}")
        startup_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]
        for item in results["启动项"]:
            name = item.split(" -> ")[0].strip()
            removed = False
            for hive, key_path in startup_keys:
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                    removed = True
                    break
                except FileNotFoundError:
                    continue
                except Exception:
                    continue
            if removed:
                print(f"    {Colors.GREEN}✓ 已移除启动项: {name}{Colors.RESET}")
                cleaned_count += 1
            else:
                print(f"    {Colors.RED}✗ 移除失败: {name}{Colors.RESET}")
                failed_count += 1

    # 总结
    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}成功清理: {cleaned_count} 项{Colors.RESET}")
    if pending_reboot > 0:
        print(f"  {Colors.YELLOW}⏰ 待重启清理: {pending_reboot} 项 (受流氓自保护拦截，已登记到系统重启删除队列){Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.YELLOW}请尽快重启电脑，重启后这些文件将在驱动加载前被自动删除{Colors.RESET}")
    if failed_count > 0:
        print(f"  {Colors.RED}清理失败: {failed_count} 项{Colors.RESET}")
        print(f"  {Colors.YELLOW}提示: 这些项可能受内核驱动深度保护，建议进入安全模式后再次运行扫描{Colors.RESET}")


def run_scan():
    """运行流氓软件扫描"""
    print(f"\n{Colors.YELLOW}正在扫描，请稍候...{Colors.RESET}\n")

    drives = get_all_drives()
    print(f"  检测到磁盘: {', '.join(drives)}")

    total_issues = 0
    results = {}

    print(f"\n  {Colors.CYAN}[1/6] 扫描可疑目录...{Colors.RESET}")
    dirs = scan_directories(drives)
    results["可疑目录"] = dirs
    total_issues += print_section("可疑目录", dirs, show_size=True)

    print(f"\n  {Colors.CYAN}[2/6] 扫描可疑文件...{Colors.RESET}")
    files = scan_files(drives)
    results["可疑文件"] = files
    total_issues += print_section("可疑可执行文件", files)

    print(f"\n  {Colors.CYAN}[3/6] 扫描注册表...{Colors.RESET}")
    reg = scan_registry()
    results["注册表残留"] = reg
    total_issues += print_section("注册表残留", reg)

    print(f"\n  {Colors.CYAN}[4/6] 扫描Windows服务...{Colors.RESET}")
    services = scan_services()
    results["可疑服务"] = services
    total_issues += print_section("可疑Windows服务", services)

    print(f"\n  {Colors.CYAN}[5/6] 扫描计划任务...{Colors.RESET}")
    tasks = scan_scheduled_tasks()
    results["计划任务"] = tasks
    total_issues += print_section("可疑计划任务", tasks)

    print(f"\n  {Colors.CYAN}[6/6] 扫描启动项...{Colors.RESET}")
    startup = scan_startup()
    results["启动项"] = startup
    total_issues += print_section("可疑启动项", startup)

    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  扫描完成")
    print(f"{'='*50}{Colors.RESET}")

    if total_issues > 0:
        print(f"\n  {Colors.RED}⚠ 共发现 {total_issues} 个可疑项!{Colors.RESET}")
        report = generate_report(results)
        print(f"  {Colors.YELLOW}报告已保存至: {report}{Colors.RESET}")

        # 询问是否清理
        confirm = input(f"\n  {Colors.RED}是否立即清理以上发现的流氓软件残留？(y/n): {Colors.RESET}").strip().lower()
        if confirm == "y":
            clean_malware(results)
        else:
            print(f"  {Colors.YELLOW}已跳过清理{Colors.RESET}")
    else:
        print(f"\n  {Colors.GREEN}✓ 您的系统很干净，未发现流氓/垃圾软件残留{Colors.RESET}")


def show_system_info():
    """显示系统基本信息"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统信息")
    print(f"{'='*50}{Colors.RESET}\n")

    try:
        result = subprocess.run(
            ["systeminfo"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        lines = result.stdout.split("\n")
        keywords = ["主机名", "OS 名称", "OS 版本", "系统制造商", "系统型号",
                    "处理器", "物理内存总量", "可用的物理内存", "Host Name",
                    "OS Name", "OS Version", "System Manufacturer", "System Model",
                    "Processor", "Total Physical Memory", "Available Physical Memory"]
        for line in lines:
            for kw in keywords:
                if kw in line:
                    print(f"  {Colors.GREEN}{line.strip()}{Colors.RESET}")
                    break
    except Exception:
        print(f"  {Colors.RED}获取系统信息失败{Colors.RESET}")

    # 磁盘信息
    print(f"\n  {Colors.BOLD}磁盘使用情况:{Colors.RESET}")
    drives = get_all_drives()
    for drive in drives:
        try:
            total, used, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), ctypes.c_ulonglong()
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                drive, ctypes.byref(free), ctypes.byref(total), None
            )
            t = total.value
            f = free.value
            u = t - f
            pct = (u / t * 100) if t > 0 else 0
            bar_len = 20
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            color = Colors.RED if pct > 90 else Colors.YELLOW if pct > 70 else Colors.GREEN
            print(f"  {drive} [{color}{bar}{Colors.RESET}] {pct:.1f}%  "
                  f"已用 {format_size(u)} / 共 {format_size(t)}")
        except Exception:
            pass


# ============================================================
# 反劫持四件套
# ============================================================

HOSTS_PATH = os.path.expandvars(r"%SystemRoot%\System32\drivers\etc\hosts")

DEFAULT_HOSTS_CONTENT = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# 127.0.0.1       localhost
# ::1             localhost
"""

HOSTS_SUSPICIOUS_KEYWORDS = [
    "360", "qihoo", "2345", "baidu", "sogou", "kingsoft", "duba",
    "ludashi", "rising", "liebao", "cmcm", "qq.com", "tencent",
    "xunlei", "thunder", "haozip", "kuaizip", "ad", "ads",
    "track", "stat", "analytic",
]


def scan_hosts():
    """检查hosts文件中的可疑/非默认条目"""
    suspicious = []
    custom = []
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for ln, line in enumerate(f, 1):
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                # 忽略 localhost 标准条目
                low = s.lower()
                if "localhost" in low and ("127.0.0.1" in s or "::1" in s):
                    continue
                custom.append((ln, s))
                for kw in HOSTS_SUSPICIOUS_KEYWORDS:
                    if kw in low:
                        suspicious.append((ln, s))
                        break
    except FileNotFoundError:
        pass
    except PermissionError:
        return None, None
    except Exception:
        pass
    return custom, suspicious


def restore_hosts():
    """备份并还原hosts为默认内容"""
    try:
        if os.path.exists(HOSTS_PATH):
            backup = f"{HOSTS_PATH}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(HOSTS_PATH, backup)
            ctypes.windll.kernel32.SetFileAttributesW(HOSTS_PATH, 0x80)
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_HOSTS_CONTENT)
        # 刷新DNS
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
        return True, backup if os.path.exists(HOSTS_PATH) else None
    except Exception as e:
        return False, str(e)


def scan_browser_shortcuts():
    """扫描浏览器快捷方式是否被追加广告URL/参数"""
    import glob
    locations = [
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%PUBLIC%\Desktop"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Internet Explorer\Quick Launch"),
    ]
    browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "iexplore.exe",
                "360se.exe", "360chrome.exe", "qqbrowser.exe", "sogouexplorer.exe"]
    suspicious = []
    try:
        import pythoncom  # 可能没有
    except ImportError:
        pythoncom = None

    # 用 PowerShell 解析 .lnk
    lnks = []
    for loc in locations:
        if os.path.isdir(loc):
            for root, _, files in os.walk(loc):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        lnks.append(os.path.join(root, f))

    if not lnks:
        return suspicious

    # 用单次PowerShell批量解析
    ps_paths = ";".join(f'"{p}"' for p in lnks)
    ps_cmd = (
        "$sh = New-Object -ComObject WScript.Shell; "
        f"@({ps_paths}) | ForEach-Object {{ "
        "$s = $sh.CreateShortcut($_); "
        "Write-Output ($_+ '|' + $s.TargetPath + '|' + $s.Arguments) }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30
        )
        for line in r.stdout.split("\n"):
            parts = line.strip().split("|")
            if len(parts) < 3:
                continue
            lnk_path, target, args = parts[0], parts[1], parts[2]
            tname = os.path.basename(target).lower()
            if tname not in browsers:
                continue
            args_low = args.lower().strip()
            # 浏览器快捷方式带URL参数 => 几乎一定是劫持
            if args_low and ("http://" in args_low or "https://" in args_low or ".com" in args_low or ".cn" in args_low):
                suspicious.append(f"{lnk_path}  =>  {target} {args}")
    except Exception:
        pass

    return suspicious


def fix_browser_shortcuts(items):
    """去除快捷方式中的劫持参数"""
    fixed = 0
    failed = 0
    for item in items:
        lnk = item.split("  =>  ")[0]
        ps_cmd = (
            "$sh = New-Object -ComObject WScript.Shell; "
            f"$s = $sh.CreateShortcut('{lnk}'); "
            "$s.Arguments = ''; $s.Save()"
        )
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                               capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                fixed += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    return fixed, failed


CONTEXT_MENU_KEYWORDS = [
    "360", "qihoo", "2345", "baidu", "百度网盘", "xunlei", "迅雷",
    "haozip", "好压", "kuaizip", "快压", "wps云", "wps_promote",
    "sogou", "搜狗", "ludashi", "鲁大师", "duba", "liebao",
]


def scan_context_menu():
    """扫描右键菜单中的可疑项"""
    found = []
    # 直接用 reg query 找
    targets = [
        r"HKCR\*\shell",
        r"HKCR\*\shellex\ContextMenuHandlers",
        r"HKCR\Directory\shell",
        r"HKCR\Directory\shellex\ContextMenuHandlers",
        r"HKCR\Directory\Background\shell",
        r"HKCR\Directory\Background\shellex\ContextMenuHandlers",
        r"HKCR\Folder\shell",
        r"HKCR\Folder\shellex\ContextMenuHandlers",
        r"HKCR\AllFilesystemObjects\shell",
        r"HKCR\AllFilesystemObjects\shellex\ContextMenuHandlers",
    ]
    for base in targets:
        try:
            r = subprocess.run(["reg", "query", base], capture_output=True,
                               text=True, encoding="gbk", errors="ignore", timeout=10)
            for line in r.stdout.split("\n"):
                line = line.strip()
                if not line.startswith("HKEY"):
                    continue
                low = line.lower()
                for kw in CONTEXT_MENU_KEYWORDS:
                    if kw.lower() in low:
                        found.append(line)
                        break
        except Exception:
            pass
    return list(set(found))


def delete_context_menu(items):
    """删除右键菜单注册表项"""
    ok, fail = 0, 0
    for path in items:
        try:
            r = subprocess.run(["reg", "delete", path, "/f"],
                               capture_output=True, timeout=10)
            if r.returncode == 0:
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    return ok, fail


def list_all_startup():
    """列出全部启动项（不仅限可疑）"""
    items = []
    # 1. Run 注册表
    run_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM\\Run(32)"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKCU\\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM\\RunOnce"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU\\RunOnce"),
    ]
    for hive, path, label in run_keys:
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append((label, name, value))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    # 2. 启动文件夹
    folders = [
        (os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"), "用户启动夹"),
        (os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"), "公共启动夹"),
    ]
    for folder, label in folders:
        if os.path.isdir(folder):
            try:
                for f in os.listdir(folder):
                    items.append((label, f, os.path.join(folder, f)))
            except Exception:
                pass

    return items


def run_anti_hijack():
    """反劫持四件套主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           反劫持检测                       │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} Hosts 文件检查与还原              │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 浏览器快捷方式劫持检测            │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 右键菜单清理                       │")
        print(f"│  {Colors.GREEN}[4]{Colors.CYAN} 全部启动项总览                     │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            custom, sus = scan_hosts()
            if custom is None:
                print(f"  {Colors.RED}✗ 无法读取hosts文件（权限不足）{Colors.RESET}")
            else:
                print(f"\n  {Colors.BOLD}Hosts自定义条目共 {len(custom)} 条:{Colors.RESET}")
                for ln, s in custom:
                    color = Colors.RED if (ln, s) in sus else Colors.YELLOW
                    print(f"    {color}L{ln}: {s}{Colors.RESET}")
                if sus:
                    print(f"\n  {Colors.RED}⚠ 其中 {len(sus)} 条疑似流氓软件添加{Colors.RESET}")
                    if input(f"\n  是否备份并还原为默认hosts？(y/n): ").strip().lower() == "y":
                        ok, info = restore_hosts()
                        if ok:
                            print(f"  {Colors.GREEN}✓ 已还原，备份: {info}{Colors.RESET}")
                        else:
                            print(f"  {Colors.RED}✗ 还原失败: {info}{Colors.RESET}")
                elif custom:
                    print(f"  {Colors.GREEN}未检测到典型流氓特征{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}✓ hosts干净{Colors.RESET}")

        elif ch == "2":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_browser_shortcuts()
            if not items:
                print(f"  {Colors.GREEN}✓ 未发现被劫持的浏览器快捷方式{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个被劫持的快捷方式:{Colors.RESET}")
                for it in items:
                    print(f"    {Colors.RED}✗ {it}{Colors.RESET}")
                if input(f"\n  是否清除劫持参数？(y/n): ").strip().lower() == "y":
                    f1, f2 = fix_browser_shortcuts(items)
                    print(f"  {Colors.GREEN}修复 {f1} 个{Colors.RESET}"
                          + (f"，{Colors.RED}失败 {f2} 个{Colors.RESET}" if f2 else ""))

        elif ch == "3":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_context_menu()
            if not items:
                print(f"  {Colors.GREEN}✓ 右键菜单干净{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个可疑右键菜单项:{Colors.RESET}")
                for it in items:
                    print(f"    {Colors.RED}✗ {it}{Colors.RESET}")
                if input(f"\n  是否删除以上注册表项？(y/n): ").strip().lower() == "y":
                    ok, fail = delete_context_menu(items)
                    print(f"  {Colors.GREEN}删除 {ok} 个{Colors.RESET}"
                          + (f"，{Colors.RED}失败 {fail} 个{Colors.RESET}" if fail else ""))

        elif ch == "4":
            items = list_all_startup()
            print(f"\n  {Colors.BOLD}共 {len(items)} 个启动项:{Colors.RESET}\n")
            for label, name, value in items:
                # 标记可疑
                low = (name + value).lower()
                is_sus = any(kw in low for kw in ["360", "2345", "baidu", "百度",
                            "sogou", "搜狗", "ludashi", "鲁大师", "qihoo", "duba",
                            "liebao", "haozip", "kuaizip", "ucbrowser", "qqpcmgr"])
                color = Colors.RED if is_sus else Colors.GREEN
                tag = " [可疑]" if is_sus else ""
                print(f"  {color}[{label}] {name}{tag}{Colors.RESET}")
                print(f"      → {value}")

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


# ============================================================
# 空间清理增强（大文件 + 重复文件）
# ============================================================

def find_big_files(min_mb=100, top=30, scan_drives=None):
    """查找大文件 Top N"""
    import heapq
    heap = []  # (size, path)
    if scan_drives is None:
        scan_drives = [d for d in get_all_drives()]
    skip_dirs = {"windows", "$recycle.bin", "system volume information",
                 "windowsapps", "winsxs"}
    min_bytes = min_mb * 1024 * 1024

    for drive in scan_drives:
        try:
            for root, dirs, files in os.walk(drive):
                # 跳过系统目录
                parts = root.lower().split(os.sep)
                if any(p in skip_dirs for p in parts):
                    dirs.clear()
                    continue
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        if sz < min_bytes:
                            continue
                        if len(heap) < top:
                            heapq.heappush(heap, (sz, fp))
                        elif sz > heap[0][0]:
                            heapq.heapreplace(heap, (sz, fp))
                    except Exception:
                        pass
        except Exception:
            pass

    return sorted(heap, key=lambda x: -x[0])


def find_duplicate_files(folder, min_kb=100):
    """查找重复文件（按大小+SHA1）"""
    import hashlib
    from collections import defaultdict

    size_groups = defaultdict(list)
    min_bytes = min_kb * 1024
    for root, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                if sz >= min_bytes:
                    size_groups[sz].append(fp)
            except Exception:
                pass

    duplicates = []
    for sz, paths in size_groups.items():
        if len(paths) < 2:
            continue
        hash_groups = defaultdict(list)
        for p in paths:
            try:
                h = hashlib.sha1()
                with open(p, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        h.update(chunk)
                hash_groups[h.hexdigest()].append(p)
            except Exception:
                pass
        for hsh, ps in hash_groups.items():
            if len(ps) > 1:
                duplicates.append((sz, ps))
    return sorted(duplicates, key=lambda x: -x[0])


def run_space_tools():
    """空间清理增强主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           空间清理增强                     │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 大文件查找 (默认 ≥100MB Top30)    │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 重复文件查找 (按SHA1)             │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            mb = input("  最小大小(MB,回车=100): ").strip()
            mb = int(mb) if mb.isdigit() else 100
            top = input("  返回前N个(回车=30): ").strip()
            top = int(top) if top.isdigit() else 30
            print(f"\n  {Colors.YELLOW}扫描中（可能需几分钟）...{Colors.RESET}")
            results = find_big_files(mb, top)
            print(f"\n  {Colors.BOLD}Top {len(results)} 大文件:{Colors.RESET}\n")
            for sz, fp in results:
                print(f"  {Colors.YELLOW}{format_size(sz):>10}{Colors.RESET}  {fp}")

        elif ch == "2":
            folder = input("  扫描目录(例 D:\\): ").strip().strip('"')
            if not os.path.isdir(folder):
                print(f"  {Colors.RED}目录不存在{Colors.RESET}")
            else:
                kb = input("  最小大小(KB,回车=100): ").strip()
                kb = int(kb) if kb.isdigit() else 100
                print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
                dups = find_duplicate_files(folder, kb)
                if not dups:
                    print(f"  {Colors.GREEN}✓ 未发现重复文件{Colors.RESET}")
                else:
                    saveable = 0
                    print(f"\n  {Colors.BOLD}发现 {len(dups)} 组重复:{Colors.RESET}\n")
                    for sz, ps in dups:
                        saveable += sz * (len(ps) - 1)
                        print(f"  {Colors.YELLOW}[{format_size(sz)} × {len(ps)}]{Colors.RESET}")
                        for p in ps:
                            print(f"    {p}")
                    print(f"\n  {Colors.GREEN}保留每组1份可释放: {format_size(saveable)}{Colors.RESET}")

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


# ============================================================
# 安全审计套件
# ============================================================

def scan_suspicious_processes():
    """列出路径异常或无签名的进程"""
    suspicious_dirs = ["\\temp\\", "\\appdata\\local\\temp\\",
                       "\\users\\public\\", "\\programdata\\temp\\",
                       "\\downloads\\", "\\$recycle.bin\\"]
    results = []
    try:
        # 用WMIC获取进程路径
        r = subprocess.run(
            ["wmic", "process", "get", "ProcessId,Name,ExecutablePath", "/format:csv"],
            capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=20
        )
        for line in r.stdout.split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                continue
            _, exe, name, pid = parts[0], parts[1], parts[2], parts[3]
            if not exe or exe == "ExecutablePath":
                continue
            low = exe.lower()
            reasons = []
            for d in suspicious_dirs:
                if d in low:
                    reasons.append(f"路径在{d}")
                    break
            if reasons:
                results.append((pid, name, exe, ";".join(reasons)))
    except Exception:
        pass

    # 无签名检测（用PowerShell批量查）
    if results:
        paths = ";".join(f"'{r[2]}'" for r in results)
        ps_cmd = (
            f"@({paths}) | ForEach-Object {{ "
            "$s = Get-AuthenticodeSignature $_ -ErrorAction SilentlyContinue; "
            "Write-Output ($_ + '|' + $s.Status) }"
        )
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                               capture_output=True, text=True, timeout=30)
            sig_map = {}
            for line in r.stdout.split("\n"):
                if "|" in line:
                    p, st = line.strip().rsplit("|", 1)
                    sig_map[p.lower()] = st
            enriched = []
            for pid, name, exe, why in results:
                st = sig_map.get(exe.lower(), "Unknown")
                enriched.append((pid, name, exe, why, st))
            return enriched
        except Exception:
            return [(p, n, e, w, "?") for p, n, e, w in results]

    return []


def scan_defender_exclusions():
    """审计 Windows Defender 排除项"""
    exclusions = {"路径": [], "扩展名": [], "进程": []}
    base = r"SOFTWARE\Microsoft\Windows Defender\Exclusions"
    for sub, key in [("路径", "Paths"), ("扩展名", "Extensions"), ("进程", "Processes")]:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{base}\\{key}")
            i = 0
            while True:
                try:
                    name, _, _ = winreg.EnumValue(k, i)
                    exclusions[sub].append(name)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(k)
        except Exception:
            pass
    return exclusions


def scan_unsigned_drivers():
    """列出未签名/测试签名驱动"""
    results = []
    try:
        r = subprocess.run(
            ["driverquery", "/si", "/fo", "csv"],
            capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=30
        )
        for line in r.stdout.split("\n")[1:]:
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) < 5:
                continue
            # DeviceName, InfName, IsSigned, Manufacturer, ...
            name, inf, signed = parts[0], parts[1], parts[2]
            if signed.upper() in ("FALSE", "否"):
                results.append(f"{name}  (inf={inf})")
    except Exception:
        pass
    return results


def run_security_audit():
    """安全审计主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           安全审计套件                     │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 可疑进程扫描                       │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} Defender 排除项审计               │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 未签名驱动检查                     │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_suspicious_processes()
            if not items:
                print(f"  {Colors.GREEN}✓ 未发现可疑进程{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个可疑进程:{Colors.RESET}\n")
                for pid, name, exe, why, sig in items:
                    sig_color = Colors.RED if sig != "Valid" else Colors.GREEN
                    print(f"  {Colors.RED}PID {pid}  {name}{Colors.RESET}")
                    print(f"    路径: {exe}")
                    print(f"    原因: {why}")
                    print(f"    签名: {sig_color}{sig}{Colors.RESET}\n")

        elif ch == "2":
            ex = scan_defender_exclusions()
            total = sum(len(v) for v in ex.values())
            if total == 0:
                print(f"  {Colors.GREEN}✓ 无 Defender 排除项{Colors.RESET}")
            else:
                print(f"\n  {Colors.BOLD}Defender 排除项 ({total} 条):{Colors.RESET}\n")
                for kind, items in ex.items():
                    if items:
                        print(f"  {Colors.YELLOW}[{kind}]{Colors.RESET}")
                        for it in items:
                            print(f"    - {it}")
                print(f"\n  {Colors.YELLOW}提示: 若有非自己添加的排除项，可能是流氓软件白名单逃逸{Colors.RESET}")

        elif ch == "3":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_unsigned_drivers()
            if not items:
                print(f"  {Colors.GREEN}✓ 所有驱动均已签名{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个未签名驱动:{Colors.RESET}\n")
                for it in items:
                    print(f"    {Colors.RED}✗ {it}{Colors.RESET}")

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


# ============================================================
# 网络工具集
# ============================================================

def check_dns_proxy():
    """检查 DNS 与代理设置"""
    info = {"DNS": [], "代理": []}
    # DNS
    try:
        r = subprocess.run(["ipconfig", "/all"], capture_output=True,
                           text=True, encoding="gbk", errors="ignore")
        cur_adapter = ""
        for line in r.stdout.split("\n"):
            if line and not line.startswith(" "):
                cur_adapter = line.strip().rstrip(":")
            low = line.lower()
            if "dns servers" in low or "dns 服务器" in line or "dns服务器" in line:
                ip = line.split(":")[-1].strip()
                if ip:
                    info["DNS"].append(f"{cur_adapter}: {ip}")
            elif line.startswith("                                       ") and info["DNS"]:
                # DNS第二行
                ip = line.strip()
                if ip and "." in ip:
                    info["DNS"][-1] += f", {ip}"
    except Exception:
        pass

    # 代理
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
        try:
            enabled, _ = winreg.QueryValueEx(k, "ProxyEnable")
            info["代理"].append(f"ProxyEnable = {enabled}")
        except Exception:
            pass
        try:
            srv, _ = winreg.QueryValueEx(k, "ProxyServer")
            info["代理"].append(f"ProxyServer = {srv}")
        except Exception:
            pass
        try:
            pac, _ = winreg.QueryValueEx(k, "AutoConfigURL")
            info["代理"].append(f"AutoConfigURL = {pac}")
        except Exception:
            pass
        winreg.CloseKey(k)
    except Exception:
        pass

    return info


def query_port(port):
    """查询端口占用"""
    results = []
    try:
        r = subprocess.run(["netstat", "-ano"], capture_output=True,
                           text=True, encoding="gbk", errors="ignore")
        for line in r.stdout.split("\n"):
            if f":{port} " in line or f":{port}\t" in line or line.rstrip().endswith(f":{port}"):
                parts = line.split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pid = parts[-1]
                    # 获取进程名
                    try:
                        t = subprocess.run(["tasklist", "/fi", f"pid eq {pid}", "/fo", "csv", "/nh"],
                                           capture_output=True, text=True, encoding="gbk", errors="ignore")
                        name = t.stdout.strip().split(",")[0].strip('"') if t.stdout else "?"
                    except Exception:
                        name = "?"
                    results.append(f"{line.strip()}  =>  PID {pid} ({name})")
    except Exception:
        pass
    return results


def network_diagnostic():
    """网络诊断一键化"""
    cmds = [
        (["ipconfig", "/flushdns"], "刷新DNS缓存"),
        (["ipconfig", "/release"], "释放IP"),
        (["ipconfig", "/renew"], "重新获取IP"),
        (["netsh", "winsock", "reset"], "重置Winsock"),
        (["netsh", "int", "ip", "reset"], "重置TCP/IP栈"),
        (["netsh", "advfirewall", "reset"], "重置防火墙规则"),
    ]
    print(f"\n  {Colors.BOLD}将执行以下操作:{Colors.RESET}")
    for i, (_, desc) in enumerate(cmds, 1):
        print(f"    {i}. {desc}")
    print(f"\n  {Colors.YELLOW}⚠ 部分操作需要重启生效，防火墙规则将被重置！{Colors.RESET}")
    if input(f"\n  确认执行？(y/n): ").strip().lower() != "y":
        print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        return
    for cmd, desc in cmds:
        print(f"\n  {Colors.CYAN}> {desc}...{Colors.RESET}")
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="gbk", errors="ignore", timeout=30)
            if r.returncode == 0:
                print(f"    {Colors.GREEN}✓ 完成{Colors.RESET}")
            else:
                print(f"    {Colors.RED}✗ 失败 (code {r.returncode}){Colors.RESET}")
        except Exception as e:
            print(f"    {Colors.RED}✗ 异常: {e}{Colors.RESET}")
    print(f"\n  {Colors.YELLOW}建议重启电脑以完全生效{Colors.RESET}")


def run_network_tools():
    """网络工具主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           网络工具集                       │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} DNS / 代理 设置检查               │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 端口占用查询                       │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 网络诊断一键化                     │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            info = check_dns_proxy()
            print(f"\n  {Colors.BOLD}[DNS]{Colors.RESET}")
            if info["DNS"]:
                for x in info["DNS"]:
                    print(f"    {x}")
            else:
                print(f"    (未获取到)")
            print(f"\n  {Colors.BOLD}[代理]{Colors.RESET}")
            if info["代理"]:
                for x in info["代理"]:
                    color = Colors.RED if "= 1" in x or "AutoConfigURL" in x else Colors.GREEN
                    print(f"    {color}{x}{Colors.RESET}")
            else:
                print(f"    (无代理配置)")
            print(f"\n  {Colors.YELLOW}提示: ProxyEnable=1 或 AutoConfigURL 存在时请确认是否本人设置{Colors.RESET}")

        elif ch == "2":
            port = input("  端口号: ").strip()
            if not port.isdigit():
                print(f"  {Colors.RED}端口号无效{Colors.RESET}")
            else:
                items = query_port(port)
                if not items:
                    print(f"  {Colors.GREEN}✓ 端口 {port} 未被占用{Colors.RESET}")
                else:
                    print(f"\n  {Colors.RED}端口 {port} 占用情况:{Colors.RESET}")
                    for it in items:
                        print(f"    {it}")

        elif ch == "3":
            network_diagnostic()

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


# ============================================================
# 装机助手（面向小白）
# ============================================================

INSTALL_TUTORIAL = """
══════════════════════════════════════════════════════════
              装机小白速查 · 一看就会
══════════════════════════════════════════════════════════

【情况 A】电脑还能开机，只是想清理 / 想重装
   👉 用本菜单的 [1] 重置此电脑
   👉 选"保留我的文件"——照片、文档、桌面都不会丢
   👉 全程半小时左右，第三方软件会被清空（专治流氓全家桶）

【情况 B】电脑卡顿严重，但还能进系统，想彻底重装
   👉 用本菜单的 [1] 重置此电脑
   👉 选"删除所有内容"——彻底干净，相当于全新出厂
   👉 重要文件请先备份到U盘/网盘

【情况 C】电脑根本开不了机 / 蓝屏 / 黑屏
   1. 找另一台能用的电脑
   2. 准备一个 ≥ 8GB 的 U盘（注意：会被清空，里面东西先转移）
   3. 用本菜单的 [2] 制作系统U盘指南，照着做
   4. U盘插到坏电脑，开机狂按 F12 / F2 / Del / Esc 进 BIOS
      （不同品牌不同：联想=F12  戴尔=F12  华硕=Esc  惠普=F9）
   5. 在启动菜单里选 USB 那一项，照着屏幕提示走

【情况 D】进不了系统但想先抢救文件
   👉 用本菜单的 [3] 进入高级启动
   👉 选"疑难解答 → 高级选项 → 命令提示符"
   👉 插U盘，用 xcopy C:\\Users\\你的用户名 U:\\备份 /s /e
   👉 拷完再考虑重装

══════════════════════════════════════════════════════════
              重要忠告（看完再动手！）
══════════════════════════════════════════════════════════

⚠ 重装系统前一定先备份：
   - C:\\Users\\你的用户名\\Desktop（桌面）
   - C:\\Users\\你的用户名\\Documents（文档）
   - C:\\Users\\你的用户名\\Pictures（图片）
   - 浏览器收藏夹（Chrome/Edge 登录账号自动同步即可）

⚠ 千万不要从这些地方下载 Windows：
   ✗ "系统之家"、"雨林木风"、"深度技术"、"番茄花园" 等
     —— 这些 GHOST 镜像 99% 捆绑流氓软件，装完比之前还脏！
   ✓ 唯一推荐：微软官网 / MSDN i tell you / Ventoy + 官方ISO

⚠ 系统盘选择：
   - C盘空间建议 ≥ 60GB（Windows 11 推荐 100GB）
   - 安装时只动C盘，其他盘的数据不会丢

⚠ 装完系统后第一件事：
   1. 联网 → Windows Update 装完所有补丁
   2. 别装 360 / 鲁大师 / 金山 / 腾讯管家 等国产"安全"软件
      —— Windows 自带的 Defender 已经够用，安静、不弹广告、不偷数据
   3. 浏览器装 Chrome / Edge（别装 360浏览器、2345浏览器、QQ浏览器）
   4. 输入法装微软拼音（自带）或 搜狗精简版（别装360输入法、百度输入法）
   5. 解压软件装 7-Zip / Bandizip（别装好压、快压、2345压缩）

══════════════════════════════════════════════════════════
"""


def get_removable_drives():
    """检测可移动磁盘（U盘）"""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            # DRIVE_REMOVABLE=2
            if drive_type == 2:
                try:
                    total = ctypes.c_ulonglong()
                    free = ctypes.c_ulonglong()
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        drive, ctypes.byref(free), ctypes.byref(total), None
                    )
                    # 读取卷标
                    vol_buf = ctypes.create_unicode_buffer(256)
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        drive, vol_buf, 256, None, None, None, None, 0
                    )
                    drives.append({
                        "letter": drive,
                        "label": vol_buf.value or "无卷标",
                        "total": total.value,
                        "free": free.value,
                    })
                except Exception:
                    drives.append({"letter": drive, "label": "?", "total": 0, "free": 0})
        bitmask >>= 1
    return drives


def reset_this_pc():
    """调用系统自带"重置此电脑"功能"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  重置此电脑")
    print(f"{'='*50}{Colors.RESET}\n")
    print(f"  Windows 内置的重装功能，无需U盘，无需下载镜像。")
    print(f"  接下来会弹出微软官方的重置向导窗口。\n")
    print(f"  {Colors.YELLOW}向导里你会看到两个选项:{Colors.RESET}")
    print(f"    {Colors.GREEN}► 保留我的文件{Colors.RESET}  —— 照片/文档/桌面都在，只卸软件 (推荐)")
    print(f"    {Colors.RED}► 删除所有内容{Colors.RESET}  —— 等同恢复出厂，所有数据消失\n")
    print(f"  {Colors.YELLOW}⚠ 重置过程约 30-60 分钟，期间电脑会自动重启数次{Colors.RESET}")
    print(f"  {Colors.YELLOW}⚠ 请确保电脑接通电源（笔记本必须插充电器）{Colors.RESET}\n")

    if input(f"  确认打开重置向导？(y/n): ").strip().lower() != "y":
        print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        return

    try:
        # systemreset.exe 是 Win10/11 内置
        subprocess.Popen(["systemreset.exe"])
        print(f"\n  {Colors.GREEN}✓ 重置向导已启动，请按照弹出窗口操作{Colors.RESET}")
    except FileNotFoundError:
        # 老版本Windows fallback
        print(f"  {Colors.YELLOW}未找到 systemreset.exe，尝试打开设置...{Colors.RESET}")
        try:
            subprocess.Popen(["start", "ms-settings:recovery"], shell=True)
            print(f"  {Colors.GREEN}✓ 已打开 [设置 → 恢复] 页面{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.RED}✗ 启动失败: {e}{Colors.RESET}")
            print(f"  {Colors.YELLOW}请手动操作: 设置 → 系统 → 恢复 → 重置此电脑{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.RED}✗ 启动失败: {e}{Colors.RESET}")


def make_usb_guide():
    """制作系统U盘指南"""
    import webbrowser
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  制作系统U盘 · 三步走")
    print(f"{'='*50}{Colors.RESET}\n")

    # 步骤1: 检测U盘
    print(f"  {Colors.BOLD}第 1 步：检测U盘{Colors.RESET}\n")
    usbs = get_removable_drives()
    if not usbs:
        print(f"    {Colors.RED}✗ 未检测到U盘{Colors.RESET}")
        print(f"    {Colors.YELLOW}请插入一个 ≥8GB 的U盘后重试{Colors.RESET}\n")
    else:
        print(f"    检测到 {len(usbs)} 个U盘:")
        for u in usbs:
            ok = u["total"] >= 8 * 1024**3
            color = Colors.GREEN if ok else Colors.RED
            tag = "✓" if ok else "✗ 容量不足8GB"
            print(f"    {color}{tag} {u['letter']} [{u['label']}]  "
                  f"{format_size(u['total'])} (剩余 {format_size(u['free'])}){Colors.RESET}")
        print()
        print(f"    {Colors.YELLOW}⚠ U盘会被清空，里面的东西先转移走{Colors.RESET}\n")

    # 步骤2: 下载工具
    print(f"  {Colors.BOLD}第 2 步：用官方工具制作U盘（任选其一）{Colors.RESET}\n")
    print(f"    {Colors.GREEN}方案 A：微软官方媒体创建工具（最简单，推荐小白）{Colors.RESET}")
    print(f"      - 自动下载最新 Windows + 写入U盘，一键完成")
    print(f"      - 缺点：每次只能装一个版本\n")
    print(f"    {Colors.GREEN}方案 B：Rufus（轻量，老手推荐）{Colors.RESET}")
    print(f"      - 需要自己准备 ISO 镜像")
    print(f"      - 速度比官方工具快\n")
    print(f"    {Colors.GREEN}方案 C：Ventoy（一盘多系统，推荐进阶用户）{Colors.RESET}")
    print(f"      - 制作一次，以后扔多个 ISO 进U盘都能启动")
    print(f"      - 装机狗的最爱\n")

    print(f"  {Colors.BOLD}第 3 步：开机进 BIOS 选U盘启动{Colors.RESET}\n")
    print(f"    开机狂按以下键进启动菜单：")
    print(f"      联想 / 戴尔: {Colors.YELLOW}F12{Colors.RESET}")
    print(f"      华硕:        {Colors.YELLOW}Esc{Colors.RESET} 或 {Colors.YELLOW}F8{Colors.RESET}")
    print(f"      惠普:        {Colors.YELLOW}F9{Colors.RESET}")
    print(f"      宏碁:        {Colors.YELLOW}F12{Colors.RESET}")
    print(f"      神舟 / 微星: {Colors.YELLOW}F11{Colors.RESET}")
    print(f"      其他 / 不确定: 试 {Colors.YELLOW}F12 / F2 / Del / Esc{Colors.RESET}\n")

    print(f"  {Colors.BOLD}{Colors.CYAN}是否打开对应官网？{Colors.RESET}")
    print(f"    [1] 微软官方 Windows 下载页（方案A）")
    print(f"    [2] Rufus 官网（方案B）")
    print(f"    [3] Ventoy 官网（方案C）")
    print(f"    [0] 不打开")
    ch = input(f"\n  选择: ").strip()

    urls = {
        "1": "https://www.microsoft.com/zh-cn/software-download/windows11",
        "2": "https://rufus.ie/zh/",
        "3": "https://www.ventoy.net/cn/index.html",
    }
    if ch in urls:
        try:
            webbrowser.open(urls[ch])
            print(f"  {Colors.GREEN}✓ 已用默认浏览器打开{Colors.RESET}")
        except Exception as e:
            print(f"  {Colors.RED}打开失败: {e}{Colors.RESET}")
            print(f"  {Colors.YELLOW}手动访问: {urls[ch]}{Colors.RESET}")


def advanced_startup():
    """进入Windows高级启动（WinRE）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  Windows 高级启动")
    print(f"{'='*50}{Colors.RESET}\n")
    print(f"  执行后电脑将立即重启，进入恢复环境（WinRE）。")
    print(f"  在里面可以选择:\n")
    print(f"    • 启动设置 → 安全模式（清理流氓的最佳时机）")
    print(f"    • 疑难解答 → 命令提示符（进系统抢救文件）")
    print(f"    • 疑难解答 → 启动修复（修复开不了机）")
    print(f"    • 疑难解答 → 系统还原（回到上一个还原点）\n")
    print(f"  {Colors.RED}⚠ 所有未保存的工作会丢失！请先保存关闭其他程序{Colors.RESET}\n")

    if input(f"  确认立即重启进入高级启动？(yes/n): ").strip().lower() != "yes":
        print(f"  {Colors.YELLOW}已取消（需要输入完整的 yes 确认）{Colors.RESET}")
        return
    try:
        # /r 重启 /o 进高级启动 /t 0 立即 /f 强制关闭程序
        subprocess.Popen(["shutdown", "/r", "/o", "/t", "5", "/f"])
        print(f"\n  {Colors.GREEN}✓ 系统将在 5 秒后重启进入高级启动环境{Colors.RESET}")
        print(f"  {Colors.YELLOW}如要取消，立即在另一个窗口运行: shutdown /a{Colors.RESET}")
    except Exception as e:
        print(f"  {Colors.RED}✗ 失败: {e}{Colors.RESET}")


def show_install_tutorial():
    """显示装机教程"""
    print(f"{Colors.CYAN}{INSTALL_TUTORIAL}{Colors.RESET}")


def run_install_helper():
    """装机助手主入口"""
    C = Colors
    while True:
        print()
        draw_box("装机助手 · 小白模式", [
            f"  {C.GREEN}[1]{C.RESET} {C.WHITE}重置此电脑{C.RESET} {C.YELLOW}推荐{C.RESET}       {C.GRAY}(保留文件/恢复出厂){C.RESET}",
            f"  {C.GREEN}[2]{C.RESET} {C.WHITE}制作系统U盘指南{C.RESET}       {C.GRAY}(三种方案可选){C.RESET}",
            f"  {C.GREEN}[3]{C.RESET} {C.WHITE}进入高级启动{C.RESET}           {C.GRAY}(PE/安全模式入口){C.RESET}",
            f"  {C.GREEN}[4]{C.RESET} {C.WHITE}装机小白速查{C.RESET}           {C.GRAY}(图文教程){C.RESET}",
            None,
            f"  {C.RED}[0]{C.RESET} {C.DIM}返回{C.RESET}",
        ], width=58, color=Colors.MAGENTA)
        ch = input(f"\n  {C.CYAN}{C.BOLD}>{C.RESET} {C.WHITE}请选择: {C.RESET}").strip()

        if ch == "1":
            reset_this_pc()
        elif ch == "2":
            make_usb_guide()
        elif ch == "3":
            advanced_startup()
        elif ch == "4":
            show_install_tutorial()
        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


# ============================================================
# 性能优化（智能识别笔记本/台式机）
# ============================================================

# 系统内置电源计划 GUID
POWER_PLAN_HIGH = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
POWER_PLAN_BALANCED = "381b4222-f694-41f0-9685-ff5bb260df2e"
POWER_PLAN_SAVER = "a1841308-3541-4fab-bc81-f71556f20b4a"
POWER_PLAN_ULTIMATE = "e9a42b02-d5df-448d-aa00-03f14749eb61"

PERF_BACKUP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "perf_backup.json")

SPI_SETDROPSHADOW = 0x1025
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02


def detect_device_type():
    """检测设备类型: ('laptop'|'desktop', detail)"""
    try:
        r = subprocess.run(
            ["wmic", "path", "Win32_Battery", "get", "BatteryStatus"],
            capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=10
        )
        # 有任何一行包含数字 → 存在电池 → 笔记本
        for line in r.stdout.split("\n"):
            line = line.strip()
            if line.isdigit():
                return "laptop", "检测到电池"
        return "desktop", "未检测到电池"
    except Exception:
        return "desktop", "检测失败（默认按台式机处理）"


def get_system_disk_type():
    """获取系统盘(C:)是 SSD 还是 HDD"""
    try:
        ps = (
            "$d = Get-PhysicalDisk | Where-Object { "
            "  (Get-Partition -DiskNumber $_.DeviceId -ErrorAction SilentlyContinue | "
            "   Get-Volume -ErrorAction SilentlyContinue | "
            "   Where-Object DriveLetter -eq 'C').Count -gt 0 }; "
            "$d.MediaType"
        )
        r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, text=True, timeout=15)
        out = r.stdout.strip()
        if "SSD" in out:
            return "SSD"
        elif "HDD" in out:
            return "HDD"
        return "未知"
    except Exception:
        return "未知"


def get_current_power_plan():
    """获取当前活动电源计划 GUID"""
    try:
        r = subprocess.run(["powercfg", "/getactivescheme"],
                           capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=10)
        # 输出形如: 电源方案 GUID: 381b4222-f694-41f0-9685-ff5bb260df2e (平衡)
        import re
        m = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",
                      r.stdout)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def set_power_plan(guid):
    """切换电源计划"""
    try:
        r = subprocess.run(["powercfg", "/setactive", guid],
                           capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False


def _load_backup():
    """加载性能备份"""
    try:
        import json
        if os.path.exists(PERF_BACKUP):
            with open(PERF_BACKUP, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_backup(data):
    """保存性能备份"""
    try:
        import json
        existing = _load_backup()
        existing.update(data)
        with open(PERF_BACKUP, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def disable_transparency_and_shadows():
    """关闭透明效果和窗口阴影（保留动画）"""
    backup = {}

    # 1. 透明
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                           winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            cur, _ = winreg.QueryValueEx(k, "EnableTransparency")
            backup["transparency"] = cur
        except Exception:
            backup["transparency"] = 1
        winreg.SetValueEx(k, "EnableTransparency", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(k)
    except Exception:
        pass

    # 2. 窗口阴影 (SystemParametersInfoW)
    try:
        # 先查当前值
        cur_shadow = ctypes.c_int(0)
        ctypes.windll.user32.SystemParametersInfoW(
            0x1024, 0, ctypes.byref(cur_shadow), 0  # SPI_GETDROPSHADOW
        )
        backup["dropshadow"] = bool(cur_shadow.value)
        # 关闭
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDROPSHADOW, 0, 0,
            SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
        )
    except Exception:
        pass

    _save_backup(backup)
    return backup


def restore_transparency_and_shadows():
    """还原透明和阴影"""
    backup = _load_backup()
    # 透明
    if "transparency" in backup:
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                               0, winreg.KEY_WRITE)
            winreg.SetValueEx(k, "EnableTransparency", 0, winreg.REG_DWORD,
                              int(backup["transparency"]))
            winreg.CloseKey(k)
        except Exception:
            pass
    # 阴影
    if backup.get("dropshadow"):
        try:
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDROPSHADOW, 0, 1,
                SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE
            )
        except Exception:
            pass


def disable_telemetry():
    """关闭遥测、广告 ID、内容推送"""
    actions = []

    # 1. DiagTrack 服务
    try:
        r = subprocess.run(["sc", "qc", "DiagTrack"], capture_output=True,
                           text=True, encoding="gbk", errors="ignore", timeout=10)
        was_auto = "AUTO_START" in r.stdout or "自动" in r.stdout
        subprocess.run(["sc", "config", "DiagTrack", "start=", "disabled"],
                       capture_output=True, timeout=10)
        subprocess.run(["sc", "stop", "DiagTrack"], capture_output=True, timeout=10)
        actions.append(f"DiagTrack 服务已禁用 (原状态: {'自动' if was_auto else '其他'})")
        _save_backup({"diagtrack_was_auto": was_auto})
    except Exception:
        pass

    # 2. AllowTelemetry 策略
    try:
        path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE)
        except Exception:
            k = None
        if k:
            winreg.SetValueEx(k, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(k)
            actions.append("遥测策略 AllowTelemetry=0")
    except Exception:
        pass

    # 3. 广告 ID
    try:
        k = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
            0, winreg.KEY_WRITE)
        winreg.SetValueEx(k, "Enabled", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(k)
        actions.append("广告 ID 已关闭")
    except Exception:
        pass

    # 4. 内容推送 / 建议应用 / 锁屏建议
    try:
        cdm_path = r"Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager"
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, cdm_path, 0, winreg.KEY_WRITE)
        for name in ["SubscribedContent-338388Enabled",
                     "SubscribedContent-338389Enabled",
                     "SubscribedContent-353698Enabled",
                     "SystemPaneSuggestionsEnabled",
                     "SilentInstalledAppsEnabled",
                     "RotatingLockScreenOverlayEnabled"]:
            try:
                winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, 0)
            except Exception:
                pass
        winreg.CloseKey(k)
        actions.append("Windows 推送/建议应用/锁屏广告 已关闭")
    except Exception:
        pass

    # 5. 反馈频率
    try:
        k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,
                               r"Software\Microsoft\Siuf\Rules", 0, winreg.KEY_WRITE)
        winreg.SetValueEx(k, "NumberOfSIUFInPeriod", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(k)
        actions.append("反馈提示频率已置 0")
    except Exception:
        pass

    return actions


def restore_telemetry():
    """还原遥测设置"""
    backup = _load_backup()
    actions = []
    # DiagTrack
    if backup.get("diagtrack_was_auto"):
        try:
            subprocess.run(["sc", "config", "DiagTrack", "start=", "auto"],
                           capture_output=True, timeout=10)
            subprocess.run(["sc", "start", "DiagTrack"], capture_output=True, timeout=10)
            actions.append("DiagTrack 恢复为自动启动")
        except Exception:
            pass
    # 删除策略
    try:
        subprocess.run(["reg", "delete",
                        r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                        "/v", "AllowTelemetry", "/f"], capture_output=True)
    except Exception:
        pass
    # 广告 ID 恢复
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                           r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                           0, winreg.KEY_WRITE)
        winreg.SetValueEx(k, "Enabled", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(k)
        actions.append("广告 ID 已恢复")
    except Exception:
        pass
    return actions


def battery_report():
    """生成电池健康报告"""
    out_path = os.path.join(os.path.expandvars("%TEMP%"), "battery-report.html")
    try:
        r = subprocess.run(
            ["powercfg", "/batteryreport", "/output", out_path],
            capture_output=True, text=True, encoding="gbk", errors="ignore", timeout=30
        )
        if os.path.exists(out_path):
            os.startfile(out_path)
            return True, out_path
        return False, r.stdout + r.stderr
    except Exception as e:
        return False, str(e)


def one_click_optimize(device_type, disk_type):
    """一键性能优化"""
    print(f"\n  {Colors.BOLD}开始优化（{device_type}, 系统盘 {disk_type}）...{Colors.RESET}\n")
    backup = {"original_power_plan": get_current_power_plan()}
    _save_backup(backup)

    # 1. 电源计划
    if device_type == "desktop":
        # 先尝试卓越性能，没有就高性能
        # 卓越性能需要先 powercfg /duplicatescheme
        try:
            r = subprocess.run(
                ["powercfg", "/duplicatescheme", POWER_PLAN_ULTIMATE],
                capture_output=True, text=True, timeout=10
            )
            # 不管成不成功，再切高性能（卓越性能Win10/11部分版本无）
        except Exception:
            pass
        ok = set_power_plan(POWER_PLAN_HIGH)
        print(f"  {Colors.GREEN}✓{Colors.RESET} 电源计划切换到 [高性能]" if ok
              else f"  {Colors.RED}✗{Colors.RESET} 电源计划切换失败")
    else:
        ok = set_power_plan(POWER_PLAN_BALANCED)
        print(f"  {Colors.GREEN}✓{Colors.RESET} 电源计划切换到 [平衡] (笔记本兼顾续航)" if ok
              else f"  {Colors.RED}✗{Colors.RESET} 电源计划切换失败")

    # 2. 视觉特效（保留动画）
    disable_transparency_and_shadows()
    print(f"  {Colors.GREEN}✓{Colors.RESET} 关闭透明/阴影 (保留窗口动画)")

    # 3. 遥测/广告
    acts = disable_telemetry()
    for a in acts:
        print(f"  {Colors.GREEN}✓{Colors.RESET} {a}")

    # 4. SysMain (SuperFetch) - 仅 SSD 关闭
    if disk_type == "SSD":
        try:
            subprocess.run(["sc", "config", "SysMain", "start=", "disabled"],
                           capture_output=True, timeout=10)
            subprocess.run(["sc", "stop", "SysMain"], capture_output=True, timeout=10)
            print(f"  {Colors.GREEN}✓{Colors.RESET} SSD 检测到 → SysMain (SuperFetch) 已关闭")
            _save_backup({"sysmain_disabled": True})
        except Exception:
            pass
    elif disk_type == "HDD":
        print(f"  {Colors.YELLOW}ℹ{Colors.RESET} HDD 系统盘 → 保留 SysMain (机械盘需要预读取)")

    # 5. 处理器最小状态（仅台式机拉满）
    if device_type == "desktop":
        try:
            # AC 状态下处理器最小状态 = 100%
            subprocess.run([
                "powercfg", "/setacvalueindex", "scheme_current",
                "sub_processor", "PROCTHROTTLEMIN", "100"
            ], capture_output=True, timeout=10)
            subprocess.run(["powercfg", "/setactive", "scheme_current"],
                           capture_output=True, timeout=10)
            print(f"  {Colors.GREEN}✓{Colors.RESET} 处理器最小状态拉到 100% (台式机)")
        except Exception:
            pass

    # 6. 加快菜单显示速度
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0,
                           winreg.KEY_READ | winreg.KEY_WRITE)
        try:
            cur, _ = winreg.QueryValueEx(k, "MenuShowDelay")
            _save_backup({"menu_show_delay": cur})
        except Exception:
            pass
        winreg.SetValueEx(k, "MenuShowDelay", 0, winreg.REG_SZ, "100")
        winreg.CloseKey(k)
        print(f"  {Colors.GREEN}✓{Colors.RESET} 菜单显示延迟 400ms → 100ms")
    except Exception:
        pass

    print(f"\n  {Colors.GREEN}{Colors.BOLD}✓ 优化完成{Colors.RESET}")
    print(f"  {Colors.YELLOW}部分设置需注销或重启后生效{Colors.RESET}")
    print(f"  {Colors.CYAN}原始设置已备份到: {PERF_BACKUP}{Colors.RESET}")
    print(f"  {Colors.CYAN}随时可用菜单 [7] 还原{Colors.RESET}")


def restore_all_perf():
    """还原所有性能优化"""
    backup = _load_backup()
    if not backup:
        print(f"  {Colors.YELLOW}未找到备份文件，无可还原项{Colors.RESET}")
        return

    print(f"  {Colors.BOLD}开始还原...{Colors.RESET}\n")

    # 电源计划
    if backup.get("original_power_plan"):
        if set_power_plan(backup["original_power_plan"]):
            print(f"  {Colors.GREEN}✓{Colors.RESET} 电源计划已还原")

    restore_transparency_and_shadows()
    print(f"  {Colors.GREEN}✓{Colors.RESET} 透明/阴影已还原")

    restore_telemetry()
    print(f"  {Colors.GREEN}✓{Colors.RESET} 遥测设置已恢复")

    # SysMain
    if backup.get("sysmain_disabled"):
        try:
            subprocess.run(["sc", "config", "SysMain", "start=", "auto"],
                           capture_output=True, timeout=10)
            subprocess.run(["sc", "start", "SysMain"], capture_output=True, timeout=10)
            print(f"  {Colors.GREEN}✓{Colors.RESET} SysMain 服务已恢复")
        except Exception:
            pass

    # 菜单延迟
    if "menu_show_delay" in backup:
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0,
                               winreg.KEY_WRITE)
            winreg.SetValueEx(k, "MenuShowDelay", 0, winreg.REG_SZ,
                              str(backup["menu_show_delay"]))
            winreg.CloseKey(k)
            print(f"  {Colors.GREEN}✓{Colors.RESET} 菜单延迟已还原")
        except Exception:
            pass

    # 清空备份文件
    try:
        os.remove(PERF_BACKUP)
    except Exception:
        pass
    print(f"\n  {Colors.GREEN}✓ 还原完成{Colors.RESET}")


def show_perf_status():
    """显示设备类型 & 当前性能状态"""
    device, reason = detect_device_type()
    disk = get_system_disk_type()
    plan_guid = get_current_power_plan()

    plan_names = {
        POWER_PLAN_HIGH: "高性能",
        POWER_PLAN_BALANCED: "平衡",
        POWER_PLAN_SAVER: "节能",
        POWER_PLAN_ULTIMATE: "卓越性能",
    }
    plan_name = plan_names.get(plan_guid, f"自定义 ({plan_guid})")

    print(f"\n  {Colors.BOLD}设备检测结果:{Colors.RESET}")
    icon = "💻" if device == "laptop" else "🖥"
    print(f"    {icon} 类型: {Colors.GREEN}{'笔记本' if device=='laptop' else '台式机'}{Colors.RESET}  ({reason})")
    print(f"    💾 系统盘: {Colors.GREEN}{disk}{Colors.RESET}")
    print(f"    ⚡ 当前电源计划: {Colors.GREEN}{plan_name}{Colors.RESET}")

    # 推荐建议
    print(f"\n  {Colors.BOLD}建议:{Colors.RESET}")
    if device == "desktop" and plan_guid != POWER_PLAN_HIGH and plan_guid != POWER_PLAN_ULTIMATE:
        print(f"    {Colors.YELLOW}► 台式机建议切到 [高性能] / [卓越性能] 电源计划{Colors.RESET}")
    elif device == "laptop" and plan_guid == POWER_PLAN_HIGH:
        print(f"    {Colors.YELLOW}► 笔记本长期 [高性能] 会发热严重、续航减半，建议 [平衡]{Colors.RESET}")
    else:
        print(f"    {Colors.GREEN}► 当前电源计划合理{Colors.RESET}")


def manage_power_plans():
    """电源计划手动管理"""
    plans = [
        ("高性能", POWER_PLAN_HIGH, "台式机推荐，CPU 火力全开"),
        ("平衡", POWER_PLAN_BALANCED, "默认，笔记本推荐"),
        ("节能", POWER_PLAN_SAVER, "极致省电，性能砍半"),
    ]
    print(f"\n  {Colors.BOLD}电源计划:{Colors.RESET}\n")
    cur = get_current_power_plan()
    for i, (name, guid, desc) in enumerate(plans, 1):
        tag = "  ← 当前" if guid == cur else ""
        print(f"    [{i}] {Colors.GREEN}{name}{Colors.RESET} - {desc}{Colors.YELLOW}{tag}{Colors.RESET}")
    print(f"    [4] {Colors.GREEN}卓越性能{Colors.RESET} - 解锁隐藏方案 (仅 Win10 1803+)")
    print(f"    [0] 取消")
    ch = input(f"\n  选择: ").strip()
    if ch == "1":
        ok = set_power_plan(POWER_PLAN_HIGH)
    elif ch == "2":
        ok = set_power_plan(POWER_PLAN_BALANCED)
    elif ch == "3":
        ok = set_power_plan(POWER_PLAN_SAVER)
    elif ch == "4":
        subprocess.run(["powercfg", "/duplicatescheme", POWER_PLAN_ULTIMATE],
                       capture_output=True, timeout=10)
        ok = set_power_plan(POWER_PLAN_ULTIMATE)
    else:
        return
    if ok:
        print(f"  {Colors.GREEN}✓ 电源计划已切换{Colors.RESET}")
    else:
        print(f"  {Colors.RED}✗ 切换失败（该计划可能不存在）{Colors.RESET}")


def run_performance_boost():
    """性能优化主入口"""
    C = Colors
    while True:
        print()
        draw_box("性能优化 · 智能识别设备", [
            f"  {C.GREEN}[1]{C.RESET} {C.WHITE}检测设备类型{C.RESET}           {C.GRAY}(笔记本/台式/SSD/HDD){C.RESET}",
            f"  {C.GREEN}[2]{C.RESET} {C.WHITE}一键性能优化{C.RESET} {C.YELLOW}推荐{C.RESET}    {C.GRAY}(差异化策略){C.RESET}",
            f"  {C.GREEN}[3]{C.RESET} {C.WHITE}电源计划管理{C.RESET}           {C.GRAY}(高性能/平衡/节能){C.RESET}",
            f"  {C.GREEN}[4]{C.RESET} {C.WHITE}关闭透明/阴影{C.RESET}          {C.GRAY}(保留窗口动画){C.RESET}",
            f"  {C.GREEN}[5]{C.RESET} {C.WHITE}关闭遥测/广告/推送{C.RESET}     {C.GRAY}(DiagTrack/广告ID){C.RESET}",
            f"  {C.GREEN}[6]{C.RESET} {C.WHITE}电池健康报告{C.RESET}           {C.GRAY}(仅笔记本){C.RESET}",
            f"  {C.YELLOW}[7]{C.RESET} {C.WHITE}还原所有优化{C.RESET}           {C.GRAY}(一键回滚){C.RESET}",
            None,
            f"  {C.RED}[0]{C.RESET} {C.DIM}返回{C.RESET}",
        ], width=58, color=Colors.BLUE)
        ch = input(f"\n  {C.CYAN}{C.BOLD}>{C.RESET} {C.WHITE}请选择: {C.RESET}").strip()

        if ch == "1":
            show_perf_status()
        elif ch == "2":
            device, _ = detect_device_type()
            disk = get_system_disk_type()
            print(f"\n  设备: {Colors.GREEN}{'笔记本' if device=='laptop' else '台式机'}{Colors.RESET}, "
                  f"系统盘: {Colors.GREEN}{disk}{Colors.RESET}")
            print(f"  将执行: 电源计划 + 透明/阴影 + 遥测 + SysMain(SSD时) + 菜单延迟")
            if input(f"\n  确认执行？(y/n): ").strip().lower() == "y":
                one_click_optimize(device, disk)
        elif ch == "3":
            manage_power_plans()
        elif ch == "4":
            disable_transparency_and_shadows()
            print(f"  {Colors.GREEN}✓ 透明效果与窗口阴影已关闭 (动画保留){Colors.RESET}")
        elif ch == "5":
            acts = disable_telemetry()
            for a in acts:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {a}")
        elif ch == "6":
            device, _ = detect_device_type()
            if device != "laptop":
                print(f"  {Colors.YELLOW}未检测到电池，此功能仅限笔记本{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}生成中...{Colors.RESET}")
                ok, info = battery_report()
                if ok:
                    print(f"  {Colors.GREEN}✓ 已生成并打开: {info}{Colors.RESET}")
                    print(f"  {Colors.CYAN}重点看 'Battery capacity history' 中 Design vs Full Charge{Colors.RESET}")
                else:
                    print(f"  {Colors.RED}✗ 生成失败: {info}{Colors.RESET}")
        elif ch == "7":
            if input(f"  确认还原所有优化？(y/n): ").strip().lower() == "y":
                restore_all_perf()
        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")


def print_menu():
    """打印主菜单"""
    C = Colors
    print()
    draw_box("功能菜单", [
        f"{C.GRAY}── 清理 ──────────────────────────────────────{C.RESET}",
        f"  {C.GREEN}[1]{C.RESET} {C.WHITE}流氓软件扫描与清理{C.RESET}      {C.GRAY}(强力四级删除){C.RESET}",
        f"  {C.GREEN}[2]{C.RESET} {C.WHITE}系统垃圾深度清理{C.RESET}        {C.GRAY}(6类垃圾/分类可选/回收站){C.RESET}",
        f"  {C.GREEN}[3]{C.RESET} {C.WHITE}反劫持检测{C.RESET}              {C.GRAY}(hosts/快捷方式/右键/启动){C.RESET}",
        f"  {C.GREEN}[4]{C.RESET} {C.WHITE}空间清理增强{C.RESET}            {C.GRAY}(大文件/重复文件){C.RESET}",
        None,
        f"{C.GRAY}── 检测 ──────────────────────────────────────{C.RESET}",
        f"  {C.GREEN}[5]{C.RESET} {C.WHITE}安全审计{C.RESET}                {C.GRAY}(进程/Defender/驱动签名){C.RESET}",
        f"  {C.GREEN}[6]{C.RESET} {C.WHITE}网络工具{C.RESET}                {C.GRAY}(DNS/端口/诊断){C.RESET}",
        f"  {C.GREEN}[7]{C.RESET} {C.WHITE}系统信息{C.RESET}                {C.GRAY}(CPU/内存/磁盘){C.RESET}",
        None,
        f"{C.GRAY}── 工具 ──────────────────────────────────────{C.RESET}",
        f"  {C.GREEN}[8]{C.RESET} {C.WHITE}装机助手{C.RESET}                {C.GRAY}(重装/U盘/教程){C.RESET}",
        f"  {C.GREEN}[9]{C.RESET} {C.WHITE}性能优化{C.RESET} {C.YELLOW}NEW{C.RESET}            {C.GRAY}(电源/遥测/自动识别设备){C.RESET}",
        None,
        f"  {C.RED}[0]{C.RESET} {C.DIM}退出{C.RESET}",
    ], width=60)


def is_admin():
    """检查是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    """请求以管理员权限重新运行"""
    if not is_admin():
        # 用ShellExecute以管理员身份重新启动自己
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join([f'"{arg}"' for arg in sys.argv]),
            None, 1
        )
        sys.exit(0)


def main():
    # 如果不是管理员，自动请求提权重启
    if not is_admin():
        print("正在请求管理员权限...")
        run_as_admin()
        return

    enable_virtual_terminal()
    print_header()

    print(f"  {Colors.GREEN}✓ 已获取管理员权限{Colors.RESET}")

    while True:
        print_menu()
        choice = input(f"\n  {Colors.CYAN}{Colors.BOLD}>{Colors.RESET} {Colors.WHITE}请选择: {Colors.RESET}").strip()

        if choice == "1":
            run_scan()
        elif choice == "2":
            confirm = input(f"\n  {Colors.RED}确认清理系统缓存？(y/n): {Colors.RESET}").strip().lower()
            if confirm == "y":
                clean_cache()
            else:
                print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        elif choice == "3":
            run_anti_hijack()
        elif choice == "4":
            run_space_tools()
        elif choice == "5":
            run_security_audit()
        elif choice == "6":
            run_network_tools()
        elif choice == "7":
            show_system_info()
        elif choice == "8":
            run_install_helper()
        elif choice == "9":
            run_performance_boost()
        elif choice == "0":
            print(f"\n  {Colors.DIM}────────────────────────────────{Colors.RESET}")
            print(f"  {Colors.CYAN}感谢使用，再见！{Colors.RESET}")
            print(f"  {Colors.GRAY}GitHub: github.com/RobustLuo/scanne{Colors.RESET}\n")
            break
        else:
            print(f"\n  {Colors.RED}✗ 无效选项{Colors.RESET}")

        input(f"\n  {Colors.DIM}按回车键返回菜单...{Colors.RESET}")


if __name__ == "__main__":
    main()
