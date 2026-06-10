"""
模块2: 系统缓存清理
支持两种模式：
  - 交互式（CLI 菜单）：clean_cache()
  - 程序化（Web UI / GUI）：clean_cache_all() / clean_category(key)
"""

import os
import subprocess
import ctypes

from scanner_toolbox.config.constants import Colors
from scanner_toolbox.utils.file_ops import get_dir_size, format_size, _clean_paths, _clean_files_by_ext


# ============================================================
# 清理类别定义（共享给 CLI 和 Web UI）
# ============================================================

CLEAN_CATEGORIES = {
    "1": {
        "name": "系统临时文件与缓存",
        "paths": [
            (os.path.expandvars(r"%TEMP%"), "用户临时文件"),
            (os.path.expandvars(r"%SystemRoot%\Temp"), "系统临时文件"),
            (os.path.expandvars(r"%LocalAppData%\Temp"), "本地临时文件"),
            (os.path.expandvars(r"%SystemRoot%\Prefetch"), "预读取缓存"),
            (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer"), "缩略图缓存"),
            (os.path.expandvars(r"%SystemRoot%\ServiceProfiles\LocalService\AppData\Local\FontCache"), "字体缓存"),
        ]
    },
    "2": {
        "name": "浏览器缓存",
        "paths": [
            (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\INetCache"), "IE/Edge缓存"),
            (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"), "Chrome缓存"),
            (os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"), "Edge缓存"),
            (os.path.expandvars(r"%LocalAppData%\Mozilla\Firefox\Profiles"), "Firefox缓存"),
        ]
    },
    "3": {
        "name": "Windows更新与日志",
        "paths": [
            (os.path.expandvars(r"%SystemRoot%\SoftwareDistribution\Download"), "更新下载"),
            (os.path.expandvars(r"%LocalAppData%\CrashDumps"), "崩溃转储"),
            (os.path.expandvars(r"%SystemRoot%\Minidump"), "系统转储"),
            (os.path.expandvars(r"%SystemRoot%\Logs\CBS"), "CBS日志"),
        ]
    },
    "4": {
        "name": "常用软件缓存",
        "paths": [
            (os.path.expandvars(r"%LocalAppData%\Microsoft\Office\16.0\OfficeFileCache"), "Office缓存"),
            (os.path.expandvars(r"%LocalAppData%\pip\cache"), "pip缓存"),
            (os.path.expandvars(r"%LocalAppData%\npm-cache"), "npm缓存"),
        ]
    },
    "5": {
        "name": "国产软件缓存",
        "paths": [
            (os.path.expandvars(r"%AppData%\Tencent\WeChat\XPlugin\Temp"), "微信插件"),
            (os.path.expandvars(r"%AppData%\Tencent\QQ\Temp"), "QQ临时"),
            (os.path.expandvars(r"%LocalAppData%\Kingsoft\WPS Cloud Files\cache"), "WPS缓存"),
        ]
    },
    "6": {"name": "Windows.old 与系统残留", "special": "windows_old"},
    "7": {"name": "回收站", "special": "recycle_bin"},
    "8": {"name": "DNS缓存刷新", "special": "flush_dns"},
}


# ============================================================
# 内部清理函数
# ============================================================

def _empty_recycle_bin():
    """清空回收站"""
    print(f"  {Colors.YELLOW}清理: 回收站{Colors.RESET}")
    try:
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
    """清理 Windows.old 与系统升级残留"""
    print(f"  {Colors.YELLOW}清理: Windows.old 与系统残留{Colors.RESET}")

    from scanner_toolbox.core.scanner import get_all_drives
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
                subprocess.run(["takeown", "/f", wo, "/r", "/d", "y"],
                               capture_output=True, timeout=120)
                subprocess.run(["icacls", wo, "/grant", "administrators:F", "/t"],
                               capture_output=True, timeout=120)
                subprocess.run(["cmd", "/c", "rd", "/s", "/q", wo],
                               capture_output=True, timeout=300)
                if not os.path.exists(wo):
                    print(f"    {Colors.GREEN}已删除: {wo}{Colors.RESET}")
                else:
                    print(f"    {Colors.YELLOW}部分残留: {wo}{Colors.RESET}")
            except Exception as e:
                print(f"    {Colors.RED}清理失败 {wo}: {e}{Colors.RESET}")

    print(f"\n    {Colors.CYAN}启动 DISM 清理组件存储...{Colors.RESET}")
    try:
        subprocess.run(
            ["dism", "/online", "/cleanup-image", "/startcomponentcleanup", "/resetbase"],
            capture_output=True, timeout=600
        )
        print(f"    {Colors.GREEN}组件存储清理完成{Colors.RESET}")
    except subprocess.TimeoutExpired:
        print(f"    {Colors.YELLOW}DISM 超时{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}DISM 清理失败: {e}{Colors.RESET}")

    print()


def _run_category(key):
    """执行单个清理类别，返回 (cleaned_bytes, files, errors)"""
    cat = CLEAN_CATEGORIES.get(key)
    if not cat:
        return 0, 0, 0

    if "special" in cat:
        if cat["special"] == "windows_old":
            _clean_windows_old()
        elif cat["special"] == "recycle_bin":
            _empty_recycle_bin()
        elif cat["special"] == "flush_dns":
            _flush_dns()
        return 0, 0, 0

    print(f"\n  {Colors.BOLD}清理: {cat['name']}{Colors.RESET}\n")
    return _clean_paths(cat["paths"])


# ============================================================
# 程序化接口（Web UI / GUI 调用）
# ============================================================

def clean_cache_all():
    """清理全部类别（无交互，直接执行）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统垃圾深度清理 - 全部清理")
    print(f"{'='*50}{Colors.RESET}\n")

    total_cleaned = 0
    total_files = 0
    total_errors = 0

    for key in sorted(CLEAN_CATEGORIES.keys()):
        cleaned, files, errors = _run_category(key)
        total_cleaned += cleaned
        total_files += files
        total_errors += errors

    # 额外清理系统日志
    sys_root = os.path.expandvars(r"%SystemRoot%")
    c1, f1, e1 = _clean_files_by_ext(
        os.path.join(sys_root, "Logs"), [".log", ".etl", ".tmp"],
        "系统日志文件"
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


def clean_category(key):
    """清理指定类别（无交互，直接执行）"""
    cat = CLEAN_CATEGORIES.get(key)
    if not cat:
        print(f"  {Colors.RED}无效的清理类别: {key}{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统垃圾深度清理 - {cat['name']}")
    print(f"{'='*50}{Colors.RESET}\n")

    cleaned, files, errors = _run_category(key)

    # 如果是类别3，额外清理系统日志
    if key == "3":
        sys_root = os.path.expandvars(r"%SystemRoot%")
        c1, f1, e1 = _clean_files_by_ext(
            os.path.join(sys_root, "Logs"), [".log", ".etl", ".tmp"],
            "系统日志文件"
        )
        cleaned += c1
        files += f1
        errors += e1

    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}共清理 {files} 个文件，释放空间: {format_size(cleaned)}{Colors.RESET}")
    if errors > 0:
        print(f"  {Colors.YELLOW}(有 {errors} 个文件被占用，跳过){Colors.RESET}")


# ============================================================
# 交互式入口（CLI 菜单）
# ============================================================

def clean_cache():
    """系统垃圾深度清理主入口（交互式菜单）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统垃圾深度清理")
    print(f"{'='*50}{Colors.RESET}\n")

    print(f"  请选择要清理的类别（可多选，用逗号分隔）：\n")
    for key, cat in CLEAN_CATEGORIES.items():
        print(f"    {Colors.GREEN}[{key}]{Colors.RESET} {cat['name']}")
    print(f"    {Colors.GREEN}[A]{Colors.RESET} 全部清理")
    print()

    choice = input(f"  {Colors.CYAN}请输入选项 (例: 1,2,3 或 A): {Colors.RESET}").strip().upper()

    if not choice:
        print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        return

    selected = set()
    if choice == "A":
        selected = set(CLEAN_CATEGORIES.keys())
    else:
        for c in choice.replace("，", ",").split(","):
            c = c.strip()
            if c in CLEAN_CATEGORIES:
                selected.add(c)

    if not selected:
        print(f"  {Colors.RED}无效选项{Colors.RESET}")
        return

    total_cleaned = 0
    total_files = 0
    total_errors = 0

    for key in sorted(selected):
        cleaned, files, errors = _run_category(key)
        total_cleaned += cleaned
        total_files += files
        total_errors += errors

    if "3" in selected:
        sys_root = os.path.expandvars(r"%SystemRoot%")
        c1, f1, e1 = _clean_files_by_ext(
            os.path.join(sys_root, "Logs"), [".log", ".etl", ".tmp"],
            "系统日志文件"
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
