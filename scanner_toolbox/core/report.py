"""
报告生成：扫描结果导出
"""

import os
from datetime import datetime

from scanner_toolbox.config.constants import Colors


def print_section(title, items, show_size=False):
    """打印扫描结果区段"""
    from scanner_toolbox.utils.file_ops import get_dir_size
    from scanner_toolbox.utils.terminal import format_size

    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}{Colors.RESET}")

    if not items:
        print(f"  {Colors.GREEN}✓ 未发现可疑项{Colors.RESET}")
        return 0

    total_size = 0
    for item in items:
        print(f"  {Colors.RED}✗ {item}{Colors.RESET}")
        if show_size and os.path.isdir(item.replace(" [隐藏]", "")):
            real_path = item.replace(" [隐藏]", "")
            size = get_dir_size(real_path)
            total_size += size
            print(f"    {Colors.YELLOW}占用: {format_size(size)}{Colors.RESET}")

    if show_size and total_size > 0:
        print(f"\n  {Colors.YELLOW}总占用空间: {format_size(total_size)}{Colors.RESET}")

    return len(items)


def generate_report(results):
    """生成扫描报告到文件"""
    report_name = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_name, "w", encoding="utf-8") as f:
        f.write("流氓软件扫描报告 v2.0\n")
        f.write(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")

        for section, items in results.items():
            f.write(f"[{section}]\n")
            if items:
                for item in items:
                    f.write(f"  - {item}\n")
            else:
                f.write("  无\n")
            f.write("\n")

    return report_name
