"""
超级骆狗工具箱 - 主入口（命令行版）
"""

import sys
import os

# 确保项目根目录在 sys.path 中
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后运行
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scanner_toolbox.config.constants import Colors
from scanner_toolbox.core.scanner import run_full_scan
from scanner_toolbox.core.cleaner import clean_malware
from scanner_toolbox.core.report import generate_report
from scanner_toolbox.modules.cache_clean import clean_cache
from scanner_toolbox.modules.anti_hijack import run_anti_hijack
from scanner_toolbox.modules.space_manager import run_space_tools
from scanner_toolbox.modules.security_audit import run_security_audit
from scanner_toolbox.modules.network_tools import run_network_tools
from scanner_toolbox.modules.sysinfo import run_sysinfo
from scanner_toolbox.modules.install_helper import run_install_helper
from scanner_toolbox.modules.perf_optimizer import run_perf_optimizer


def main_menu():
    """主菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔════════════════════════════════════════════╗")
        print(f"║        超级骆狗工具箱 v2.0                  ║")
        print(f"║        流氓软件终结者                       ║")
        print(f"╠════════════════════════════════════════════╣")
        print(f"║  {Colors.GREEN}[1]{Colors.CYAN} 流氓软件全盘扫描 + 强力清理        ║")
        print(f"║  {Colors.GREEN}[2]{Colors.CYAN} 系统垃圾深度清理                   ║")
        print(f"║  {Colors.GREEN}[3]{Colors.CYAN} 反劫持检测（Hosts/快捷方式/右键）  ║")
        print(f"║  {Colors.GREEN}[4]{Colors.CYAN} 空间清理增强（大文件/重复文件）    ║")
        print(f"║  {Colors.GREEN}[5]{Colors.CYAN} 安全审计套件                       ║")
        print(f"║  {Colors.GREEN}[6]{Colors.CYAN} 网络工具集                         ║")
        print(f"║  {Colors.GREEN}[7]{Colors.CYAN} 系统信息总览                       ║")
        print(f"║  {Colors.GREEN}[8]{Colors.CYAN} 安装助手                           ║")
        print(f"║  {Colors.GREEN}[9]{Colors.CYAN} 性能优化器                         ║")
        print(f"║  {Colors.GREEN}[0]{Colors.CYAN} 退出工具箱                          ║")
        print(f"╚════════════════════════════════════════════╝{Colors.RESET}")

        choice = input(f"\n  {Colors.YELLOW}请选择功能: {Colors.RESET}").strip()

        if choice == "1":
            print(f"\n  {Colors.BOLD}开始全盘扫描...{Colors.RESET}")
            results = run_full_scan()
            if results["found"]:
                total = sum(len(v) for v in results.values() if isinstance(v, list))
                print(f"\n  {Colors.RED}共发现 {total} 个可疑项！{Colors.RESET}")
                generate_report(results)
                if input(f"\n  是否立即清理？(y/n): ").strip().lower() == "y":
                    clean_malware(results)
            else:
                print(f"\n  {Colors.GREEN}✓ 系统干净，未发现流氓软件！{Colors.RESET}")

        elif choice == "2":
            clean_cache()

        elif choice == "3":
            run_anti_hijack()

        elif choice == "4":
            run_space_tools()

        elif choice == "5":
            run_security_audit()

        elif choice == "6":
            run_network_tools()

        elif choice == "7":
            run_sysinfo()

        elif choice == "8":
            run_install_helper()

        elif choice == "9":
            run_perf_optimizer()

        elif choice == "0":
            print(f"\n  {Colors.GREEN}感谢使用，再见！{Colors.RESET}")
            break

        else:
            print(f"  {Colors.RED}无效选项，请重新输入{Colors.RESET}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {Colors.YELLOW}用户中断，退出...{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n  {Colors.RED}发生错误: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
