"""
模块5: 安全审计套件（可疑进程、Defender排除项、未签名驱动）
"""

import os
import winreg
import subprocess

from scanner_toolbox.config.constants import Colors


def scan_suspicious_processes():
    """列出路径异常或无签名的进程"""
    suspicious_dirs = ["\\temp\\", "\\appdata\\local\\temp\\",
                       "\\users\\public\\", "\\programdata\\temp\\",
                       "\\downloads\\", "\\$recycle.bin\\"]
    results = []
    try:
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
            pass

    return [(pid, name, exe, why, "N/A") for pid, name, exe, why in results]


def scan_defender_exclusions():
    """列出Defender排除项"""
    exclusions = {"路径": [], "扩展名": [], "进程": []}
    sub_map = {"路径": "Path", "扩展名": "Extension", "进程": "Process"}
    for sub, reg_name in sub_map.items():
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"SOFTWARE\Microsoft\Windows Defender\Exclusions\\" + reg_name)
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
