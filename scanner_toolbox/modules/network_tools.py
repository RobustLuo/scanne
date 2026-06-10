"""
模块6: 网络工具集（DNS/代理检查、端口查询、网络诊断）
"""

import winreg
import subprocess

from scanner_toolbox.config.constants import Colors


def check_dns_proxy():
    """检查 DNS 与代理设置"""
    info = {"DNS": [], "代理": []}
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
                ip = line.strip()
                if ip and "." in ip:
                    info["DNS"][-1] += f", {ip}"
    except Exception:
        pass

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
