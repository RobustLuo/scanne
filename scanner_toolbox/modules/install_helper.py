"""
模块8: 安装助手（VC++运行库、.NET、常用软件批量安装）
支持两种模式：
  - 交互式（CLI 菜单）：run_install_helper()
  - 程序化（Web UI / GUI）：check_vc_redist() / check_dotnet() / install_vc_redist_silent() / install_common_tools()
"""

import os
import subprocess

from scanner_toolbox.config.constants import Colors


def check_vc_redist():
    """检查已安装的VC++运行库"""
    installed = []
    paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for reg_path in paths:
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            i = 0
            while True:
                try:
                    sub_name = winreg.EnumKey(key, i)
                    sub_key = winreg.OpenKey(key, sub_name)
                    try:
                        name, _ = winreg.QueryValueEx(sub_key, "DisplayName")
                        if "Visual C++" in name or "VC++" in name:
                            installed.append(name)
                    except Exception:
                        pass
                    winreg.CloseKey(sub_key)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
    return sorted(set(installed))


def check_dotnet():
    """检查已安装的.NET版本"""
    versions = []
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\NET Framework Setup\NDP")
        for ver in ["v2.0", "v3.0", "v3.5", "v4"]:
            try:
                sub = winreg.OpenKey(key, ver)
                try:
                    inst, _ = winreg.QueryValueEx(sub, "Install")
                    if inst == 1:
                        versions.append(ver)
                except Exception:
                    pass
                winreg.CloseKey(sub)
            except Exception:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass

    try:
        r = subprocess.run(
            ["dotnet", "--list-runtimes"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        if r.returncode == 0:
            for line in r.stdout.split("\n"):
                if line.strip():
                    versions.append(f".NET Core/5+: {line.strip()}")
    except Exception:
        pass

    return versions


def install_vc_redist_silent():
    """静默安装VC++运行库合集"""
    print(f"\n  {Colors.YELLOW}提示: 需要下载 VC++ 运行库合集{Colors.RESET}")
    print(f"  推荐下载地址:")
    print(f"    https://github.com/abbodi1406/vcredist/releases")
    print(f"\n  下载后运行:")
    print(f"    install_all.bat /silent")
    print(f"\n  {Colors.CYAN}或使用 winget 安装:{Colors.RESET}")
    print(f"    winget install Microsoft.VCRedist.2015+.x64")
    print(f"    winget install Microsoft.VCRedist.2015+.x86")


def install_common_tools():
    """常用工具安装建议"""
    tools = {
        "7-Zip": "winget install 7zip.7zip",
        "Notepad++": "winget install Notepad++.Notepad++",
        "VS Code": "winget install Microsoft.VisualStudioCode",
        "Git": "winget install Git.Git",
        "Python": "winget install Python.Python.3.12",
        "Node.js": "winget install OpenJS.NodeJS.LTS",
        "Chrome": "winget install Google.Chrome",
        "Firefox": "winget install Mozilla.Firefox",
        "PowerToys": "winget install Microsoft.PowerToys",
    }
    print(f"\n  {Colors.BOLD}常用工具安装命令 (winget):{Colors.RESET}\n")
    for name, cmd in tools.items():
        print(f"    {Colors.GREEN}{name}:{Colors.RESET}")
        print(f"      {cmd}\n")


# ============================================================
# 程序化接口（Web UI / GUI 调用）
# ============================================================

def check_vc_redist_info():
    """程序化检查VC++运行库（带格式化输出）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  检查 VC++ 运行库")
    print(f"{'='*50}{Colors.RESET}\n")
    items = check_vc_redist()
    if not items:
        print(f"  {Colors.RED}✗ 未安装任何 VC++ 运行库{Colors.RESET}")
    else:
        print(f"  {Colors.BOLD}已安装 {len(items)} 个 VC++ 运行库:{Colors.RESET}\n")
        for it in items:
            print(f"    {Colors.GREEN}✓ {it}{Colors.RESET}")


def check_dotnet_info():
    """程序化检查.NET版本（带格式化输出）"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  检查 .NET 版本")
    print(f"{'='*50}{Colors.RESET}\n")
    items = check_dotnet()
    if not items:
        print(f"  {Colors.RED}✗ 未安装 .NET{Colors.RESET}")
    else:
        print(f"  {Colors.BOLD}已安装 .NET 版本:{Colors.RESET}\n")
        for it in items:
            print(f"    {Colors.GREEN}✓ {it}{Colors.RESET}")


# ============================================================
# 交互式入口（CLI 菜单）
# ============================================================

def run_install_helper():
    """安装助手主入口（交互式菜单）"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           安装助手                         │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 检查 VC++ 运行库                   │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 检查 .NET 版本                     │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 安装 VC++ 运行库建议               │")
        print(f"│  {Colors.GREEN}[4]{Colors.CYAN} 常用工具安装建议                   │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            check_vc_redist_info()
        elif ch == "2":
            check_dotnet_info()
        elif ch == "3":
            install_vc_redist_silent()
        elif ch == "4":
            install_common_tools()
        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")
