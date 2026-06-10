"""
模块9: 性能优化器（电源计划、视觉特效、服务优化）
支持两种模式：
  - 交互式（CLI 菜单）：run_perf_optimizer()
  - 程序化（Web UI / GUI）：set_power_plan() / disable_visual_effects() / enable_visual_effects() / disable_nonessential_services() / enable_essential_services()
"""

import os
import subprocess
import winreg

from scanner_toolbox.config.constants import Colors, POWER_PLAN_HIGH


def set_power_plan():
    """设置高性能电源计划"""
    print(f"\n  {Colors.CYAN}设置电源计划为「高性能」...{Colors.RESET}")
    try:
        r = subprocess.run(
            ["powercfg", "/setactive", POWER_PLAN_HIGH],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            print(f"    {Colors.GREEN}✓ 已设置为高性能模式{Colors.RESET}")
        else:
            print(f"    {Colors.RED}✗ 设置失败{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}✗ 异常: {e}{Colors.RESET}")


def disable_visual_effects():
    """关闭视觉特效以提升性能"""
    print(f"\n  {Colors.CYAN}关闭视觉特效...{Colors.RESET}")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        print(f"    {Colors.GREEN}✓ 已设置为「调整为最佳性能」{Colors.RESET}")
        print(f"    {Colors.YELLOW}需要注销或重启生效{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}✗ 异常: {e}{Colors.RESET}")


def enable_visual_effects():
    """恢复Windows默认视觉特效"""
    print(f"\n  {Colors.CYAN}恢复默认视觉特效...{Colors.RESET}")
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print(f"    {Colors.GREEN}✓ 已恢复为「让Windows选择」{Colors.RESET}")
        print(f"    {Colors.YELLOW}需要注销或重启生效{Colors.RESET}")
    except Exception as e:
        print(f"    {Colors.RED}✗ 异常: {e}{Colors.RESET}")


def disable_nonessential_services(confirm=True):
    """禁用非必要服务
    
    Args:
        confirm: 是否需要用户确认（程序化调用时可设为False）
    """
    services = [
        ("DiagTrack", "诊断跟踪服务"),
        ("dmwappushservice", "WAP推送消息路由服务"),
        ("WSearch", "Windows搜索索引"),
        ("SysMain", "SuperFetch/预读取"),
        ("MapsBroker", "下载地图管理器"),
        ("XblAuthManager", "Xbox身份验证"),
        ("XblGameSave", "Xbox游戏保存"),
        ("XboxNetApiSvc", "Xbox网络服务"),
    ]
    print(f"\n  {Colors.CYAN}将禁用以下服务:{Colors.RESET}")
    for svc, desc in services:
        print(f"    {svc} - {desc}")
    if confirm and input(f"\n  确认禁用？(y/n): ").strip().lower() != "y":
        print(f"  {Colors.YELLOW}已取消{Colors.RESET}")
        return
    for svc, desc in services:
        try:
            subprocess.run(["sc", "config", svc, "start=", "disabled"],
                           capture_output=True, timeout=10)
            subprocess.run(["sc", "stop", svc],
                           capture_output=True, timeout=10)
            print(f"    {Colors.GREEN}✓ {svc} 已禁用{Colors.RESET}")
        except Exception as e:
            print(f"    {Colors.RED}✗ {svc} 失败: {e}{Colors.RESET}")


def enable_essential_services():
    """恢复被禁用的服务"""
    services = [
        ("DiagTrack", "手动"),
        ("dmwappushservice", "手动"),
        ("WSearch", "自动"),
        ("SysMain", "自动"),
        ("MapsBroker", "手动"),
        ("XblAuthManager", "手动"),
        ("XblGameSave", "手动"),
        ("XboxNetApiSvc", "手动"),
    ]
    print(f"\n  {Colors.CYAN}恢复服务启动类型...{Colors.RESET}")
    for svc, start_type in services:
        try:
            subprocess.run(["sc", "config", svc, "start=", start_type],
                           capture_output=True, timeout=10)
            print(f"    {Colors.GREEN}✓ {svc} → {start_type}{Colors.RESET}")
        except Exception as e:
            print(f"    {Colors.RED}✗ {svc} 失败: {e}{Colors.RESET}")


# ============================================================
# 交互式入口（CLI 菜单）
# ============================================================

def run_perf_optimizer():
    """性能优化器主入口（交互式菜单）"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           性能优化器                       │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 设置高性能电源计划                 │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 关闭视觉特效                       │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 恢复默认视觉特效                   │")
        print(f"│  {Colors.GREEN}[4]{Colors.CYAN} 禁用非必要服务                     │")
        print(f"│  {Colors.GREEN}[5]{Colors.CYAN} 恢复被禁用服务                     │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            set_power_plan()
        elif ch == "2":
            disable_visual_effects()
        elif ch == "3":
            enable_visual_effects()
        elif ch == "4":
            disable_nonessential_services(confirm=True)
        elif ch == "5":
            enable_essential_services()
        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")
