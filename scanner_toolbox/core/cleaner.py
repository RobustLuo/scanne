"""
清理引擎：预处理、强力清理、注册表清理等
"""

import os
import winreg
import subprocess

from scanner_toolbox.config.malware_db import KNOWN_FILES
from scanner_toolbox.config.constants import Colors
from scanner_toolbox.utils.file_ops import force_delete


def _pre_neutralize(results):
    """清理前置：禁用并停止可疑服务/任务/进程，斩断守护链"""
    print(f"  {Colors.YELLOW}[预处理] 停止守护进程/服务/任务...{Colors.RESET}")

    # 1. 禁用服务
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
    for fp in results.get("可疑文件", []):
        exe_set.add(os.path.basename(fp).lower())
    for exe in KNOWN_FILES:
        exe_set.add(exe.lower())
    for exe in exe_set:
        subprocess.run(["taskkill", "/F", "/IM", exe, "/T"], capture_output=True, timeout=10)


def clean_malware(results):
    """清理扫描到的流氓软件残留"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  开始清理流氓软件残留")
    print(f"{'='*50}{Colors.RESET}\n")

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

    # 3. 删除注册表项
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

    # 4. 删除可疑服务
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

    print(f"\n{Colors.BOLD}{'='*50}")
    print(f"  清理完成")
    print(f"{'='*50}{Colors.RESET}")
    print(f"\n  {Colors.GREEN}成功清理: {cleaned_count} 项{Colors.RESET}")
    if pending_reboot > 0:
        print(f"  {Colors.YELLOW}⏰ 待重启清理: {pending_reboot} 项{Colors.RESET}")
        print(f"  {Colors.BOLD}{Colors.YELLOW}请尽快重启电脑{Colors.RESET}")
    if failed_count > 0:
        print(f"  {Colors.RED}清理失败: {failed_count} 项{Colors.RESET}")
