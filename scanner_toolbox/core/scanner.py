"""
扫描引擎：目录、文件、注册表、服务、计划任务、启动项扫描
"""

import os
import string
import ctypes
import winreg
import subprocess

from scanner_toolbox.config.malware_db import (
    KNOWN_DIRS, KNOWN_FILES, KNOWN_SERVICES,
    REGISTRY_KEYS, SCHEDULED_TASK_KEYWORDS
)
from scanner_toolbox.config.constants import Colors


def get_all_drives():
    """获取所有可用磁盘驱动器"""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
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

        try:
            for root, dirs, files in os.walk(drive):
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
                                if attrs & 2:
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
    """扫描注册表中的残留项"""
    found = []
    hive_map = {
        0x80000002: winreg.HKEY_LOCAL_MACHINE,
        0x80000001: winreg.HKEY_CURRENT_USER,
    }
    for hive_val, key_path in REGISTRY_KEYS:
        hive = hive_map.get(hive_val, hive_val)
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
        "ucbrowser", "小鸟壁纸","uc浏览器","WinRAR",
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


def run_full_scan():
    """运行完整扫描，返回 results dict"""
    drives = get_all_drives()
    results = {}

    results["可疑目录"] = scan_directories(drives)
    results["可疑文件"] = scan_files(drives)
    results["注册表残留"] = scan_registry()
    results["可疑服务"] = scan_services()
    results["计划任务"] = scan_scheduled_tasks()
    results["启动项"] = scan_startup()

    return results, drives
