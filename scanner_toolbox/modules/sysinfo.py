"""
模块7: 系统信息总览（硬件、软件、网络、性能）
"""

import os
import platform
import subprocess
import winreg
from datetime import datetime

from scanner_toolbox.config.constants import Colors
from scanner_toolbox.utils.terminal import format_size


def get_cpu_info():
    """获取CPU信息"""
    try:
        r = subprocess.run(
            ["wmic", "cpu", "get", "Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed", "/format:list"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        info = {}
        for line in r.stdout.split("\n"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                info[k] = v
        return info
    except Exception:
        return {}


def get_gpu_info():
    """获取GPU信息"""
    try:
        r = subprocess.run(
            ["wmic", "path", "win32_videocontroller", "get", "Name,DriverVersion,AdapterRAM", "/format:list"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        gpus = []
        cur = {}
        for line in r.stdout.split("\n"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cur[k] = v
            elif not line.strip() and cur:
                gpus.append(cur)
                cur = {}
        if cur:
            gpus.append(cur)
        return gpus
    except Exception:
        return []


def get_disk_info():
    """获取磁盘信息"""
    try:
        r = subprocess.run(
            ["wmic", "diskdrive", "get", "Model,Size,MediaType,InterfaceType", "/format:list"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        disks = []
        cur = {}
        for line in r.stdout.split("\n"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cur[k] = v
            elif not line.strip() and cur:
                disks.append(cur)
                cur = {}
        if cur:
            disks.append(cur)
        return disks
    except Exception:
        return []


def get_partitions():
    """获取分区使用情况"""
    try:
        r = subprocess.run(
            ["wmic", "logicaldisk", "get", "DeviceID,Size,FreeSpace,FileSystem,VolumeName", "/format:list"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        parts = []
        cur = {}
        for line in r.stdout.split("\n"):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                cur[k] = v
            elif not line.strip() and cur:
                parts.append(cur)
                cur = {}
        if cur:
            parts.append(cur)
        return parts
    except Exception:
        return []


def get_installed_software():
    """获取已安装软件列表"""
    software = []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for reg_path in paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            i = 0
            while True:
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    sub_key = winreg.OpenKey(key, sub_key_name)
                    try:
                        name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        ver, _ = winreg.QueryValueEx(sub_key, "DisplayVersion")
                        pub, _ = winreg.QueryValueEx(sub_key, "Publisher")
                        inst_date, _ = winreg.QueryValueEx(sub_key, "InstallDate")
                        software.append({
                            "name": name,
                            "version": ver,
                            "publisher": pub,
                            "install_date": inst_date,
                        })
                    except Exception:
                        pass
                    winreg.CloseKey(sub_key)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    return sorted(software, key=lambda x: x["name"].lower())


def get_system_info():
    """获取系统基本信息"""
    info = {
        "系统": f"{platform.system()} {platform.release()}",
        "版本": platform.version(),
        "架构": platform.machine(),
        "计算机名": platform.node(),
        "用户名": os.getlogin() if hasattr(os, "getlogin") else "N/A",
        "启动时间": "N/A",
    }
    try:
        r = subprocess.run(
            ["wmic", "os", "get", "LastBootUpTime,InstallDate", "/format:list"],
            capture_output=True, text=True, encoding="gbk", errors="ignore"
        )
        for line in r.stdout.split("\n"):
            if "LastBootUpTime=" in line:
                ts = line.split("=", 1)[1].strip()
                if len(ts) >= 14:
                    info["启动时间"] = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}:{ts[12:14]}"
    except Exception:
        pass
    return info


def get_network_info():
    """获取网络信息"""
    info = {"IP地址": [], "MAC地址": [], "网关": []}
    try:
        r = subprocess.run(["ipconfig"], capture_output=True,
                           text=True, encoding="gbk", errors="ignore")
        cur_adapter = ""
        for line in r.stdout.split("\n"):
            if line and not line.startswith(" "):
                cur_adapter = line.strip().rstrip(":")
            low = line.lower()
            if "ipv4" in low or "ipv4 地址" in line:
                ip = line.split(":")[-1].strip()
                info["IP地址"].append(f"{cur_adapter}: {ip}")
            elif "物理地址" in line or "physical address" in low:
                mac = line.split(":")[-1].strip()
                info["MAC地址"].append(f"{cur_adapter}: {mac}")
            elif "默认网关" in line or "default gateway" in low:
                gw = line.split(":")[-1].strip()
                if gw:
                    info["网关"].append(f"{cur_adapter}: {gw}")
    except Exception:
        pass
    return info


def run_sysinfo():
    """系统信息总览主入口"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  系统信息总览")
    print(f"{'='*50}{Colors.RESET}\n")

    sys_info = get_system_info()
    print(f"  {Colors.BOLD}[系统]{Colors.RESET}")
    for k, v in sys_info.items():
        print(f"    {k}: {v}")

    cpu = get_cpu_info()
    if cpu:
        print(f"\n  {Colors.BOLD}[CPU]{Colors.RESET}")
        print(f"    型号: {cpu.get('Name', 'N/A')}")
        print(f"    核心数: {cpu.get('NumberOfCores', 'N/A')}")
        print(f"    逻辑处理器: {cpu.get('NumberOfLogicalProcessors', 'N/A')}")
        print(f"    最大频率: {cpu.get('MaxClockSpeed', 'N/A')} MHz")

    gpus = get_gpu_info()
    if gpus:
        print(f"\n  {Colors.BOLD}[GPU]{Colors.RESET}")
        for i, gpu in enumerate(gpus, 1):
            print(f"    GPU {i}: {gpu.get('Name', 'N/A')}")
            ram = gpu.get('AdapterRAM')
            if ram and ram.isdigit():
                print(f"    显存: {format_size(int(ram))}")

    disks = get_disk_info()
    if disks:
        print(f"\n  {Colors.BOLD}[磁盘]{Colors.RESET}")
        for i, d in enumerate(disks, 1):
            print(f"    磁盘 {i}: {d.get('Model', 'N/A')}")
            size = d.get('Size')
            if size and size.isdigit():
                print(f"    容量: {format_size(int(size))}")

    parts = get_partitions()
    if parts:
        print(f"\n  {Colors.BOLD}[分区]{Colors.RESET}")
        for p in parts:
            did = p.get('DeviceID', '')
            size = p.get('Size')
            free = p.get('FreeSpace')
            if size and size.isdigit() and free and free.isdigit():
                total = int(size)
                used = total - int(free)
                pct = used / total * 100 if total > 0 else 0
                color = Colors.RED if pct > 90 else Colors.YELLOW if pct > 70 else Colors.GREEN
                print(f"    {did}  已用 {format_size(used)}/{format_size(total)} ({pct:.1f}%) {color}{'█' * int(pct/5)}{Colors.RESET}")
            else:
                print(f"    {did}")

    net = get_network_info()
    if net["IP地址"]:
        print(f"\n  {Colors.BOLD}[网络]{Colors.RESET}")
        for ip in net["IP地址"]:
            print(f"    {ip}")

    print(f"\n  {Colors.BOLD}[已安装软件]{Colors.RESET}")
    software = get_installed_software()
    if software:
        print(f"    共 {len(software)} 个软件\n")
        for sw in software:
            pub = sw.get('publisher', '')
            ver = sw.get('version', '')
            print(f"    {Colors.GREEN}•{Colors.RESET} {sw['name']}")
            if ver:
                print(f"      版本: {ver}")
            if pub:
                print(f"      厂商: {pub}")
    else:
        print(f"    (未获取到)")

    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    input(f"\n  {Colors.CYAN}按回车返回...{Colors.RESET}")
