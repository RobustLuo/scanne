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
    """Windows控制台颜色"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


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
    print(f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════╗
║                                                      ║
║        欢迎进入超级骆狗的工具箱                       ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║          流氓软件扫描器 v2.0                         ║
║  360/2345/百度/金山/猎豹/驱动精灵/搜狗/暴风...       ║
║  全面扫描隐藏的国产流氓捆绑软件残留                  ║
╠══════════════════════════════════════════════════════╣
║  作者: RobustLuo                                     ║
╚══════════════════════════════════════════════════════╝
{Colors.RESET}""")


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


def clean_cache():
    """清理系统缓存"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统缓存清理")
    print(f"{'='*50}{Colors.RESET}\n")

    cache_paths = [
        (os.path.expandvars(r"%TEMP%"), "用户临时文件"),
        (os.path.expandvars(r"%SystemRoot%\Temp"), "系统临时文件"),
        (os.path.expandvars(r"%SystemRoot%\Prefetch"), "预读取缓存"),
        (os.path.expandvars(r"%LocalAppData%\Temp"), "本地临时文件"),
        (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\INetCache"), "IE/Edge缓存"),
        (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer"), "缩略图缓存"),
        (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"), "Chrome缓存"),
        (os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"), "Edge缓存"),
        (os.path.expandvars(r"%SystemRoot%\SoftwareDistribution\Download"), "Windows更新缓存"),
        (os.path.expandvars(r"%LocalAppData%\CrashDumps"), "崩溃转储文件"),
        (os.path.expandvars(r"%ProgramData%\Microsoft\Windows\WER"), "错误报告"),
    ]

    total_cleaned = 0
    total_files = 0
    total_errors = 0

    for path, desc in cache_paths:
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
        for root, dirs, files in os.walk(path, topdown=False):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    size = os.path.getsize(fp)
                    os.remove(fp)
                    cleaned += size
                    total_files += 1
                except Exception:
                    errors += 1
            for d in dirs:
                dp = os.path.join(root, d)
                try:
                    os.rmdir(dp)
                except Exception:
                    pass

        total_cleaned += cleaned
        total_errors += errors
        if cleaned > 0:
            print(f"    {Colors.GREEN}已清理: {format_size(cleaned)}{Colors.RESET}")
        if errors > 0:
            print(f"    {Colors.RED}跳过 {errors} 个被占用文件{Colors.RESET}")
        print()

    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}共清理 {total_files} 个文件，释放空间: {format_size(total_cleaned)}{Colors.RESET}")
    if total_errors > 0:
        print(f"  {Colors.YELLOW}(有 {total_errors} 个文件被占用，跳过){Colors.RESET}")


def clean_malware(results):
    """清理扫描到的流氓软件残留"""
    import shutil

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  开始清理流氓软件残留")
    print(f"{'='*50}{Colors.RESET}\n")

    cleaned_count = 0
    failed_count = 0

    # 1. 删除可疑目录
    if results.get("可疑目录"):
        print(f"  {Colors.YELLOW}[清理目录]{Colors.RESET}")
        for item in results["可疑目录"]:
            path = item.replace(" [隐藏]", "")
            try:
                # 先去掉隐藏属性
                ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)  # NORMAL
                shutil.rmtree(path, ignore_errors=False)
                print(f"    {Colors.GREEN}✓ 已删除: {path}{Colors.RESET}")
                cleaned_count += 1
            except Exception as e:
                print(f"    {Colors.RED}✗ 删除失败: {path} ({e}){Colors.RESET}")
                failed_count += 1

    # 2. 删除可疑文件
    if results.get("可疑文件"):
        print(f"\n  {Colors.YELLOW}[清理文件]{Colors.RESET}")
        for fp in results["可疑文件"]:
            try:
                os.remove(fp)
                print(f"    {Colors.GREEN}✓ 已删除: {fp}{Colors.RESET}")
                cleaned_count += 1
            except Exception as e:
                print(f"    {Colors.RED}✗ 删除失败: {fp} ({e}){Colors.RESET}")
                failed_count += 1

    # 3. 删除注册表项
    if results.get("注册表残留"):
        print(f"\n  {Colors.YELLOW}[清理注册表]{Colors.RESET}")
        for reg_item in results["注册表残留"]:
            if reg_item.startswith("[权限不足]"):
                continue
            try:
                if reg_item.startswith("HKLM\\"):
                    hive = winreg.HKEY_LOCAL_MACHINE
                    key_path = reg_item[5:]
                elif reg_item.startswith("HKCU\\"):
                    hive = winreg.HKEY_CURRENT_USER
                    key_path = reg_item[5:]
                else:
                    continue
                # 递归删除注册表项
                subprocess.run(
                    ["reg", "delete", f"{'HKLM' if hive == winreg.HKEY_LOCAL_MACHINE else 'HKCU'}\\{key_path}", "/f"],
                    capture_output=True, text=True
                )
                print(f"    {Colors.GREEN}✓ 已删除: {reg_item}{Colors.RESET}")
                cleaned_count += 1
            except Exception as e:
                print(f"    {Colors.RED}✗ 删除失败: {reg_item} ({e}){Colors.RESET}")
                failed_count += 1

    # 4. 停止并删除可疑服务
    if results.get("可疑服务"):
        print(f"\n  {Colors.YELLOW}[停止并删除服务]{Colors.RESET}")
        for svc_line in results["可疑服务"]:
            # 提取服务名
            svc_name = svc_line.split(":")[-1].strip() if ":" in svc_line else svc_line.strip()
            try:
                subprocess.run(["sc", "stop", svc_name], capture_output=True)
                subprocess.run(["sc", "delete", svc_name], capture_output=True)
                print(f"    {Colors.GREEN}✓ 已停止并删除服务: {svc_name}{Colors.RESET}")
                cleaned_count += 1
            except Exception as e:
                print(f"    {Colors.RED}✗ 处理失败: {svc_name} ({e}){Colors.RESET}")
                failed_count += 1

    # 5. 删除可疑计划任务
    if results.get("计划任务"):
        print(f"\n  {Colors.YELLOW}[删除计划任务]{Colors.RESET}")
        for task_line in results["计划任务"]:
            task_name = task_line.split(",")[0].strip().strip('"')
            if task_name and task_name != "TaskName":
                try:
                    subprocess.run(
                        ["schtasks", "/delete", "/tn", task_name, "/f"],
                        capture_output=True
                    )
                    print(f"    {Colors.GREEN}✓ 已删除任务: {task_name}{Colors.RESET}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"    {Colors.RED}✗ 删除失败: {task_name} ({e}){Colors.RESET}")
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
            for hive, key_path in startup_keys:
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                    print(f"    {Colors.GREEN}✓ 已移除启动项: {name}{Colors.RESET}")
                    cleaned_count += 1
                    break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"    {Colors.RED}✗ 移除失败: {name} ({e}){Colors.RESET}")
                    failed_count += 1
                    break

    # 总结
    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}成功清理: {cleaned_count} 项{Colors.RESET}")
    if failed_count > 0:
        print(f"  {Colors.RED}清理失败: {failed_count} 项 (可能被占用或权限不足){Colors.RESET}")
        print(f"  {Colors.YELLOW}提示: 部分文件可能需要进入安全模式后再清理{Colors.RESET}")


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


def print_menu():
    """打印主菜单"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
    print(f"│              功能菜单                      │")
    print(f"├────────────────────────────────────────────┤")
    print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 流氓软件扫描                        │")
    print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 清理系统缓存                        │")
    print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 查看系统信息                        │")
    print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 退出                                │")
    print(f"└────────────────────────────────────────────┘{Colors.RESET}")


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
        choice = input(f"\n  {Colors.YELLOW}请输入选项编号: {Colors.RESET}").strip()

        if choice == "1":
            run_scan()
        elif choice == "2":
            confirm = input(f"\n  {Colors.RED}确认清理系统缓存？(y/n): {Colors.RESET}").strip().lower()
            if confirm == "y":
                clean_cache()
            else:
                print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        elif choice == "3":
            show_system_info()
        elif choice == "0":
            print(f"\n  {Colors.CYAN}感谢使用超级骆狗的工具箱，再见！{Colors.RESET}\n")
            break
        else:
            print(f"\n  {Colors.RED}无效选项，请重新输入{Colors.RESET}")

        input(f"\n  {Colors.CYAN}按回车键返回菜单...{Colors.RESET}")


if __name__ == "__main__":
    main()
