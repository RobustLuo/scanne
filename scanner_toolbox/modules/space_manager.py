"""
模块4: 空间清理增强（大文件查找 + 重复文件查找）
"""

import os
import hashlib
import heapq
from collections import defaultdict

from scanner_toolbox.config.constants import Colors
from scanner_toolbox.utils.terminal import format_size
from scanner_toolbox.core.scanner import get_all_drives


def find_big_files(min_mb=100, top=30, scan_drives=None):
    """查找大文件 Top N"""
    heap = []  # (size, path)
    if scan_drives is None:
        scan_drives = [d for d in get_all_drives()]
    skip_dirs = {"windows", "$recycle.bin", "system volume information",
                 "windowsapps", "winsxs"}
    min_bytes = min_mb * 1024 * 1024

    for drive in scan_drives:
        try:
            for root, dirs, files in os.walk(drive):
                parts = root.lower().split(os.sep)
                if any(p in skip_dirs for p in parts):
                    dirs.clear()
                    continue
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        if sz < min_bytes:
                            continue
                        if len(heap) < top:
                            heapq.heappush(heap, (sz, fp))
                        elif sz > heap[0][0]:
                            heapq.heapreplace(heap, (sz, fp))
                    except Exception:
                        pass
        except Exception:
            pass

    return sorted(heap, key=lambda x: -x[0])


def find_duplicate_files(folder, min_kb=100):
    """查找重复文件（按大小+SHA1）"""
    size_groups = defaultdict(list)
    min_bytes = min_kb * 1024
    for root, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                if sz >= min_bytes:
                    size_groups[sz].append(fp)
            except Exception:
                pass

    duplicates = []
    for sz, paths in size_groups.items():
        if len(paths) < 2:
            continue
        hash_groups = defaultdict(list)
        for p in paths:
            try:
                h = hashlib.sha1()
                with open(p, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        h.update(chunk)
                hash_groups[h.hexdigest()].append(p)
            except Exception:
                pass
        for hsh, ps in hash_groups.items():
            if len(ps) > 1:
                duplicates.append((sz, ps))
    return sorted(duplicates, key=lambda x: -x[0])


def run_space_tools():
    """空间清理增强主入口"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌────────────────────────────────────────────┐")
        print(f"│           空间清理增强                     │")
        print(f"├────────────────────────────────────────────┤")
        print(f"│  {Colors.GREEN}[1]{Colors.CYAN} 大文件查找 (默认 ≥100MB Top30)    │")
        print(f"│  {Colors.GREEN}[2]{Colors.CYAN} 重复文件查找 (按SHA1)             │")
        print(f"│  {Colors.GREEN}[0]{Colors.CYAN} 返回上级                           │")
        print(f"└────────────────────────────────────────────┘{Colors.RESET}")
        ch = input(f"\n  {Colors.YELLOW}请选择: {Colors.RESET}").strip()

        if ch == "1":
            mb = input("  最小大小(MB,回车=100): ").strip()
            mb = int(mb) if mb.isdigit() else 100
            top = input("  返回前N个(回车=30): ").strip()
            top = int(top) if top.isdigit() else 30
            print(f"\n  {Colors.YELLOW}扫描中（可能需几分钟）...{Colors.RESET}")
            results = find_big_files(mb, top)
            print(f"\n  {Colors.BOLD}Top {len(results)} 大文件:{Colors.RESET}\n")
            for sz, fp in results:
                print(f"  {Colors.YELLOW}{format_size(sz):>10}{Colors.RESET}  {fp}")

        elif ch == "2":
            folder = input("  扫描目录(例 D:\\): ").strip().strip('"')
            if not os.path.isdir(folder):
                print(f"  {Colors.RED}目录不存在{Colors.RESET}")
            else:
                kb = input("  最小大小(KB,回车=100): ").strip()
                kb = int(kb) if kb.isdigit() else 100
                print(f"\n  {Colors.YELLOW}扫描中...{Colors.RESET}")
                dups = find_duplicate_files(folder, kb)
                if not dups:
                    print(f"  {Colors.GREEN}✓ 未发现重复文件{Colors.RESET}")
                else:
                    saveable = 0
                    print(f"\n  {Colors.BOLD}发现 {len(dups)} 组重复:{Colors.RESET}\n")
                    for sz, ps in dups:
                        saveable += sz * (len(ps) - 1)
                        print(f"  {Colors.YELLOW}[{format_size(sz)} × {len(ps)}]{Colors.RESET}")
                        for p in ps:
                            print(f"    {p}")
                    print(f"\n  {Colors.GREEN}保留每组1份可释放: {format_size(saveable)}{Colors.RESET}")

        elif ch == "0":
            break
        else:
            print(f"  {Colors.RED}无效选项{Colors.RESET}")
        input(f"\n  {Colors.CYAN}按回车继续...{Colors.RESET}")
