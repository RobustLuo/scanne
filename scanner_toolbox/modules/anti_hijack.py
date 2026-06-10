"""
模块3: 反劫持检测（Hosts、浏览器快捷方式、右键菜单、启动项）
"""

import os
import ctypes
import winreg
import subprocess
import shutil
from datetime import datetime

from scanner_toolbox.config.constants import Colors, HOSTS_PATH, DEFAULT_HOSTS_CONTENT
from scanner_toolbox.config.malware_db import HOSTS_SUSPICIOUS_KEYWORDS, CONTEXT_MENU_KEYWORDS
from scanner_toolbox.config.constants import STARTUP_REGISTRY_KEYS, STARTUP_FOLDERS


def scan_hosts():
    """检查hosts文件中的可疑/非默认条目"""
    suspicious = []
    custom = []
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for ln, line in enumerate(f, 1):
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                low = s.lower()
                if "localhost" in low and ("127.0.0.1" in s or "::1" in s):
                    continue
                custom.append((ln, s))
                for kw in HOSTS_SUSPICIOUS_KEYWORDS:
                    if kw in low:
                        suspicious.append((ln, s))
                        break
    except FileNotFoundError:
        pass
    except PermissionError:
        return None, None
    except Exception:
        pass
    return custom, suspicious


def restore_hosts():
    """备份并还原hosts为默认内容"""
    try:
        if os.path.exists(HOSTS_PATH):
            backup = f"{HOSTS_PATH}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(HOSTS_PATH, backup)
            ctypes.windll.kernel32.SetFileAttributesW(HOSTS_PATH, 0x80)
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_HOSTS_CONTENT)
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
        return True, backup if os.path.exists(HOSTS_PATH) else None
    except Exception as e:
        return False, str(e)


def scan_browser_shortcuts():
    """扫描浏览器快捷方式是否被追加广告URL"""
    locations = [
        os.path.expandvars(r"%USERPROFILE%\Desktop"),
        os.path.expandvars(r"%PUBLIC%\Desktop"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Internet Explorer\Quick Launch"),
    ]
    browsers = ["chrome.exe", "msedge.exe", "firefox.exe", "iexplore.exe",
                "360se.exe", "360chrome.exe", "qqbrowser.exe", "sogouexplorer.exe"]
    suspicious = []

    lnks = []
    for loc in locations:
        if os.path.isdir(loc):
            for root, _, files in os.walk(loc):
                for f in files:
                    if f.lower().endswith(".lnk"):
                        lnks.append(os.path.join(root, f))

    if not lnks:
        return suspicious

    ps_paths = ";".join(f'"{p}"' for p in lnks)
    ps_cmd = (
        "$sh = New-Object -ComObject WScript.Shell; "
        f"@({ps_paths}) | ForEach-Object {{ "
        "$s = $sh.CreateShortcut($_); "
        "Write-Output ($_+ '|' + $s.TargetPath + '|' + $s.Arguments) }"
    )
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30
        )
        for line in r.stdout.split("\n"):
            parts = line.strip().split("|")
            if len(parts) < 3:
                continue
            lnk_path, target, args = parts[0], parts[1], parts[2]
            tname = os.path.basename(target).lower()
            if tname not in browsers:
                continue
            args_low = args.lower().strip()
            if args_low and ("http://" in args_low or "https://" in args_low or ".com" in args_low or ".cn" in args_low):
                suspicious.append(f"{lnk_path}  =>  {target} {args}")
    except Exception:
        pass

    return suspicious


def fix_browser_shortcuts(items):
    """去除快捷方式中的劫持参数"""
    fixed = 0
    failed = 0
    for item in items:
        lnk = item.split("  =>  ")[0]
        ps_cmd = (
            "$sh = New-Object -ComObject WScript.Shell; "
            f"$s = $sh.CreateShortcut('{lnk}'); "
            "$s.Arguments = ''; $s.Save()"
        )
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd],
                               capture_output=True, text=True, timeout=15)
            if r.returncode == 0:
                fixed += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    return fixed, failed


def scan_context_menu():
    """扫描右键菜单中的可疑项"""
    found = []
    targets = [
        r"HKCR\*\shell",
        r"HKCR\*\shellex\ContextMenuHandlers",
        r"HKCR\Directory\shell",
        r"HKCR\Directory\shellex\ContextMenuHandlers",
        r"HKCR\Directory\Background\shell",
        r"HKCR\Directory\Background\shellex\ContextMenuHandlers",
        r"HKCR\Folder\shell",
        r"HKCR\Folder\shellex\ContextMenuHandlers",
        r"HKCR\AllFilesystemObjects\shell",
        r"HKCR\AllFilesystemObjects\shellex\ContextMenuHandlers",
    ]
    for base in targets:
        try:
            r = subprocess.run(["reg", "query", base], capture_output=True,
                               text=True, encoding="gbk", errors="ignore", timeout=10)
            for line in r.stdout.split("\n"):
                line = line.strip()
                if not line.startswith("HKEY"):
                    continue
                low = line.lower()
                for kw in CONTEXT_MENU_KEYWORDS:
                    if kw.lower() in low:
                        found.append(line)
                        break
        except Exception:
            pass
    return list(set(found))


def delete_context_menu(items):
    """删除右键菜单注册表项"""
    ok, fail = 0, 0
    for path in items:
        try:
            r = subprocess.run(["reg", "delete", path, "/f"],
                               capture_output=True, timeout=10)
            if r.returncode == 0:
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    return ok, fail


def list_all_startup():
    """列出全部启动项"""
    items = []
    hive_map = {
        0x80000002: winreg.HKEY_LOCAL_MACHINE,
        0x80000001: winreg.HKEY_CURRENT_USER,
    }
    for hive_val, path, label in STARTUP_REGISTRY_KEYS:
        hive = hive_map.get(hive_val, hive_val)
        try:
            key = winreg.OpenKey(hive, path)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append((label, name, value))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    for folder, label in STARTUP_FOLDERS:
        if os.path.isdir(folder):
            try:
                for f in os.listdir(folder):
                    items.append((label, f, os.path.join(folder, f)))
            except Exception:
                pass

    return items


def run_anti_hijack():
    """反劫持主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           反劫持检测                       │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} Hosts 文件检查与还原              │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 浏览器快捷方式劫持检测            │")
        print(f"│  {Colors.GREEN}[3]{Colors.CYAN} 右键菜单清理                       │")
        print(f"│  {Colors.GREEN}[4]{Colors.CYAN} 全部启动项总览                     │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            custom, sus = scan_hosts()
            if custom is None:
                print(f"  {Colors.RED}✗ 无法读取hosts文件{Colors.RESET}")
            else:
                print(f"\n  {Colors.BOLD}Hosts自定义条目共 {len(custom)} 条:{Colors.RESET}")
                for ln, s in custom:
                    color = Colors.RED if (ln, s) in sus else Colors.YELLOW
                    print(f"    {color}L{ln}: {s}{Colors.RESET}")
                if sus:
                    print(f"\n  {Colors.RED}⚠ 其中 {len(sus)} 条疑似流氓软件添加{Colors.RESET}")
                    if input(f"\n  是否备份并还原为默认hosts？(y/n): ").strip().lower() == "y":
                        ok, info = restore_hosts()
                        if ok:
                            print(f"  {Colors.GREEN}✓ 已还原，备份: {info}{Colors.RESET}")
                        else:
                            print(f"  {Colors.RED}✗ 还原失败: {info}{Colors.RESET}")
                elif custom:
                    print(f"  {Colors.GREEN}未检测到典型流氓特征{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}✓ hosts干净{Colors.RESET}")

        elif ch == "2":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_browser_shortcuts()
            if not items:
                print(f"  {Colors.GREEN}✓ 未发现被劫持的浏览器快捷方式{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个被劫持的快捷方式:{Colors.RESET}")
                for it in items:
                    print(f"    {Colors.RED}✗ {it}{Colors.RESET}")
                if input(f"\n  是否清除劫持参数？(y/n): ").strip().lower() == "y":
                    f1, f2 = fix_browser_shortcuts(items)
                    print(f"  {Colors.GREEN}修复 {f1} 个{Colors.RESET}"
                          + (f"，{Colors.RED}失败 {f2} 个{Colors.RESET}" if f2 else ""))

        elif ch == "3":
            print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
            items = scan_context_menu()
            if not items:
                print(f"  {Colors.GREEN}✓ 右键菜单干净{Colors.RESET}")
            else:
                print(f"\n  {Colors.RED}发现 {len(items)} 个可疑右键菜单项:{Colors.RESET}")
                for it in items:
                    print(f"    {Colors.RED}✗ {it}{Colors.RESET}")
                if input(f"\n  是否删除以上注册表项？(y/n): ").strip().lower() == "y":
                    ok, fail = delete_context_menu(items)
                    print(f"  {Colors.GREEN}删除 {ok} 个{Colors.RESET}"
                          + (f"，{Colors.RED}失败 {fail} 个{Colors.RESET}" if fail else ""))

        elif ch == "4":
            items = list_all_startup()
            print(f"\n  {Colors.BOLD}共 {len(items)} 个启动项:{Colors.RESET}\n")
            for label, name, value in items:
                low = (name + value).lower()
                is_sus = any(kw in low for kw in ["360", "2345", "baidu", "百度",
                            "sogou", "搜狗", "ludashi", "鲁大师", "qihoo", "duba",
                            "liebao", "haozip", "kuaizip", "ucbrowser", "qqpcmgr"])
                color = Colors.RED if is_sus else Colors.GREEN
                tag = " [可疑]" if is_sus else ""
                print(f"  {color}[{label}] {name}{tag}{Colors.RESET}")
                print(f"      → {value}")

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")
