"""
文件操作工具：目录大小计算、强力删除、权限获取等
"""

import os
import shutil
import subprocess
import ctypes

from scanner_toolbox.config.constants import (
    Colors, MOVEFILE_DELAY_UNTIL_REBOOT
)


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


def _schedule_delete_on_reboot(path):
    """登记到 PendingFileRenameOperations，下次开机由 smss.exe 删除"""
    try:
        nt_path = path if path.startswith("\\??\\") else "\\??\\" + path
        ok = ctypes.windll.kernel32.MoveFileExW(
            nt_path, None, MOVEFILE_DELAY_UNTIL_REBOOT
        )
        return bool(ok)
    except Exception:
        return False


def _force_delete_file(fp):
    """强力删除单个文件：直接删 → cmd强删 → 提权后删 → 登记重启删"""
    # 第1级：直接删
    try:
        os.remove(fp)
        return True, "direct"
    except (PermissionError, OSError):
        pass

    # 第2级：cmd /c del /f /q
    try:
        subprocess.run(["cmd", "/c", "del", "/f", "/q", fp],
                       capture_output=True, timeout=5)
        if not os.path.exists(fp):
            return True, "cmd_del"
    except Exception:
        pass

    # 第3级：提权后删
    try:
        _take_ownership(fp, recursive=False)
        os.remove(fp)
        return True, "takeown"
    except Exception:
        pass

    # 第4级：登记重启删除
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


def force_delete(path):
    """
    多级强力删除：直接删 -> 杀占用进程后删 -> takeown+icacls后删 -> MoveFileEx重启删
    返回: ("deleted" | "pending_reboot" | "failed", detail)
    """
    if not os.path.exists(path):
        return ("deleted", "已不存在")

    is_dir = os.path.isdir(path)

    # 去掉只读/隐藏/系统属性
    try:
        ctypes.windll.kernel32.SetFileAttributesW(path, 0x80)
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


def format_size(size_bytes):
    """格式化字节数为人类可读格式"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def _clean_paths(paths):
    """
    清理一组路径列表
    paths: [(path, description), ...]
    返回: (total_cleaned_bytes, total_files, total_errors)
    """
    total_cleaned = 0
    total_files = 0
    total_errors = 0

    for path, desc in paths:
        if not os.path.exists(path):
            continue
        print(f"    {Colors.CYAN}清理: {desc} ({path}){Colors.RESET}")
        if os.path.isfile(path):
            try:
                sz = os.path.getsize(path)
                status, detail = force_delete(path)
                if status == "deleted":
                    total_cleaned += sz
                    total_files += 1
                    print(f"      {Colors.GREEN}✓ {detail}{Colors.RESET}")
                else:
                    total_errors += 1
                    print(f"      {Colors.YELLOW}⚠ {detail}{Colors.RESET}")
            except Exception as e:
                total_errors += 1
                print(f"      {Colors.RED}✗ {e}{Colors.RESET}")
        elif os.path.isdir(path):
            sz_before = get_dir_size(path)
            try:
                for root, dirs, files in os.walk(path, topdown=False):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            fsz = os.path.getsize(fp)
                            status, _ = force_delete(fp)
                            if status == "deleted":
                                total_cleaned += fsz
                                total_files += 1
                        except Exception:
                            total_errors += 1
                    for d in dirs:
                        dp = os.path.join(root, d)
                        try:
                            _force_delete_dir(dp)
                        except Exception:
                            total_errors += 1
                if os.path.exists(path):
                    _force_delete_dir(path)
            except Exception as e:
                total_errors += 1
                print(f"      {Colors.RED}✗ {e}{Colors.RESET}")

    return total_cleaned, total_files, total_errors


def _clean_files_by_ext(folder, extensions, desc):
    """
    按扩展名批量清理文件
    返回: (total_cleaned_bytes, total_files, total_errors)
    """
    total_cleaned = 0
    total_files = 0
    total_errors = 0

    if not os.path.isdir(folder):
        return 0, 0, 0

    print(f"    {Colors.CYAN}清理: {desc}{Colors.RESET}")
    for root, dirs, files in os.walk(folder):
        for f in files:
            if any(f.lower().endswith(ext) for ext in extensions):
                fp = os.path.join(root, f)
                try:
                    sz = os.path.getsize(fp)
                    status, _ = force_delete(fp)
                    if status == "deleted":
                        total_cleaned += sz
                        total_files += 1
                    else:
                        total_errors += 1
                except Exception:
                    total_errors += 1

    return total_cleaned, total_files, total_errors
