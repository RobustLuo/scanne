"""
超级骆狗工具箱 v3.0 - Web UI 版
================================
用 pywebview 把 preview.html 包装成一个原生桌面 exe 窗口，
并把网页上的按钮接到 scanner_toolbox 的真实功能上。

界面长相 == preview.html（1:1 一致）
真实功能 == scanner_toolbox 各模块（不改动）
"""

import os
import sys
import re
import io
import json
import threading
from contextlib import redirect_stdout, redirect_stderr

import webview

# ============================================================
# 1. 准备：项目路径（须在 import scanner_toolbox 之前）
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scanner_toolbox.utils.paths import resource_path

SCANNER_OK = False
_IMPORT_ERR = ""
try:
    from scanner_toolbox.core.scanner import run_full_scan as _run_full_scan
    from scanner_toolbox.core.cleaner import clean_malware
    from scanner_toolbox.core.report import generate_report
    from scanner_toolbox.modules.cache_clean import clean_cache_all, clean_category
    from scanner_toolbox.modules.anti_hijack import (
        scan_hosts, scan_browser_shortcuts, scan_context_menu, list_all_startup
    )
    from scanner_toolbox.modules.space_manager import find_big_files, find_duplicate_files
    from scanner_toolbox.modules.security_audit import (
        scan_suspicious_processes, scan_defender_exclusions, scan_unsigned_drivers
    )
    from scanner_toolbox.modules.network_tools import check_dns_proxy, query_port, network_diagnostic
    from scanner_toolbox.modules.sysinfo import run_sysinfo
    from scanner_toolbox.modules.install_helper import (
        check_vc_redist_info, check_dotnet_info, install_vc_redist_silent, install_common_tools
    )
    from scanner_toolbox.modules.perf_optimizer import (
        set_power_plan, disable_visual_effects, enable_visual_effects,
        disable_nonessential_services, enable_essential_services
    )
    from scanner_toolbox.utils.terminal import format_size
    SCANNER_OK = True
except Exception as e:
    _IMPORT_ERR = repr(e)


# ============================================================
# 1.5 Web UI 模式下替换 input()，防止阻塞线程
#     所有确认提示默认返回 "n"（安全：不自动执行破坏性操作）
# ============================================================

def _safe_input(prompt=""):
    """Web UI 下非交互式 input：打印提示 + 返回安全默认值"""
    print(f"[需要确认] {prompt.rstrip()} (Web UI 模式默认跳过)")
    return "n"

if SCANNER_OK:
    try:
        import builtins
        builtins.input = _safe_input
    except Exception:
        pass


# ============================================================
# 2. stdout/stderr → 网页日志面板 的流式重定向
# ============================================================

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


class StreamWriter(io.TextIOBase):
    """把 print 出来的每一行实时推送到指定的日志框"""

    def __init__(self, window, log_id: str):
        super().__init__()
        self._window = window
        self._log_id = log_id
        self._buf = ""

    def write(self, text):
        if not text:
            return 0
        clean = _strip_ansi(text).replace("\r", "")
        self._buf += clean
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._push(line)
        return len(text)

    def flush(self):
        if self._buf:
            self._push(self._buf)
            self._buf = ""

    def writable(self):
        return True

    def _push(self, line: str):
        if not self._window:
            return
        js = "window.appendLog && window.appendLog({lid},{txt})".format(
            lid=json.dumps(self._log_id),
            txt=json.dumps(line),
        )
        try:
            self._window.evaluate_js(js)
        except Exception:
            pass


# ============================================================
# 3. 任务分发：(module, action) → 真实函数
# ============================================================

def _need_scanner():
    if not SCANNER_OK:
        print(f"[ERROR] scanner 模块加载失败: {_IMPORT_ERR}")
        print("提示: 本功能需要在 Windows 环境下运行")
        return False
    return True


# --- 扫描 & 清理 ---

def _t_scan():
    if _need_scanner():
        _run_full_scan()


def _t_clean():
    if _need_scanner():
        clean_cache_all()


# --- 防劫持 ---

def _t_hijack_hosts():
    if not _need_scanner():
        return
    custom, suspicious = scan_hosts()
    print(f"自定义 hosts 条目: {len(custom)} 条")
    for c in custom:
        print("  " + str(c))
    print(f"可疑/劫持条目: {len(suspicious)} 条")
    for s in suspicious:
        print("  " + str(s))
    if not custom and not suspicious:
        print("hosts 文件干净，无异常")


def _t_hijack_shortcut():
    if not _need_scanner():
        return
    items = scan_browser_shortcuts()
    if not items:
        print("浏览器快捷方式均正常，未发现劫持")
    else:
        print(f"发现 {len(items)} 个可疑快捷方式：")
        for it in items:
            print(f"  {it}")


def _t_hijack_context():
    if not _need_scanner():
        return
    items = scan_context_menu()
    if not items:
        print("右键菜单干净，未发现可疑项")
    else:
        print(f"发现 {len(items)} 个可疑右键菜单项：")
        for it in items:
            print(f"  {it}")


def _t_hijack_startups():
    if _need_scanner():
        list_all_startup()


# --- 空间管理 ---

def _t_space_large():
    if not _need_scanner():
        return
    files = find_big_files(min_mb=100, top=30)
    print(f"Top {len(files)} 大文件：")
    for size, path in files:
        print(f"  {format_size(size):>10}  {path}")


def _t_space_dup(folder=None):
    if not _need_scanner():
        return
    folder = folder or os.environ.get("USERPROFILE", "C:\\")
    print(f"扫描重复文件: {folder}")
    find_duplicate_files(folder)


# --- 安全审计 ---

def _t_sec_proc():
    if _need_scanner():
        scan_suspicious_processes()


def _t_sec_defender():
    if _need_scanner():
        scan_defender_exclusions()


def _t_sec_driver():
    if _need_scanner():
        scan_unsigned_drivers()


# --- 网络工具 ---

def _t_net_dns():
    if not _need_scanner():
        return
    info = check_dns_proxy()
    print("DNS 配置：")
    for d in info.get("DNS", []):
        print(f"  {d}")
    print("代理设置：")
    for p in info.get("代理", []):
        print(f"  {p}")


def _t_net_port(port=None):
    if not _need_scanner():
        return
    try:
        port = int(port) if port else 80
    except (TypeError, ValueError):
        port = 80
    print(f"查询端口 {port} 的占用情况...")
    query_port(port)


def _t_net_diag():
    if _need_scanner():
        network_diagnostic()


# --- 系统信息 ---

def _t_sysinfo():
    if _need_scanner():
        run_sysinfo()


# --- 安装助手 ---

def _t_inst_vc():
    if _need_scanner():
        check_vc_redist_info()


def _t_inst_dotnet():
    if _need_scanner():
        check_dotnet_info()


def _t_inst_vcdl():
    if _need_scanner():
        install_vc_redist_silent()


def _t_inst_tools():
    if _need_scanner():
        install_common_tools()


# --- 性能优化 ---

def _t_perf_power():
    if _need_scanner():
        set_power_plan()


def _t_perf_disable_fx():
    if _need_scanner():
        disable_visual_effects()


def _t_perf_enable_fx():
    if _need_scanner():
        enable_visual_effects()


def _t_perf_disable_svc():
    if _need_scanner():
        disable_nonessential_services(confirm=False)


def _t_perf_enable_svc():
    if _need_scanner():
        enable_essential_services()


# --- 缓存清理子类别 ---

def _t_clean_cat(key):
    if _need_scanner():
        clean_category(key)


# (module, action) → (网页日志面板id, 真实函数)
TASK_MAP = {
    ("scan",     None):       ("scan",     _t_scan),
    ("clean",    None):       ("clean",    _t_clean),

    ("hijack",   "hosts"):    ("hijack",   _t_hijack_hosts),
    ("hijack",   "shortcut"): ("hijack",   _t_hijack_shortcut),
    ("hijack",   "context"):  ("hijack",   _t_hijack_context),
    ("hijack",   "startups"): ("hijack",   _t_hijack_startups),
    ("hijack",   None):       ("hijack",   _t_hijack_hosts),

    ("space",    "large"):    ("space",    _t_space_large),
    ("space",    "dup"):      ("space",    _t_space_dup),
    ("space",    None):       ("space",    _t_space_large),

    ("security", "process"):  ("security", _t_sec_proc),
    ("security", "defender"): ("security", _t_sec_defender),
    ("security", "driver"):   ("security", _t_sec_driver),
    ("security", None):       ("security", _t_sec_proc),

    ("network",  "dns"):      ("network",  _t_net_dns),
    ("network",  "port"):     ("network",  _t_net_port),
    ("network",  "diag"):     ("network",  _t_net_diag),
    ("network",  None):       ("network",  _t_net_dns),

    ("sysinfo",  None):       ("sysinfo",  _t_sysinfo),

    ("install",  "vc"):       ("install",  _t_inst_vc),
    ("install",  "dotnet"):   ("install",  _t_inst_dotnet),
    ("install",  "vcdl"):     ("install",  _t_inst_vcdl),
    ("install",  "tools"):    ("install",  _t_inst_tools),
    ("install",  None):       ("install",  _t_inst_vc),

    ("perf",     "power"):    ("perf",     _t_perf_power),
    ("perf",     "disable_fx"): ("perf",   _t_perf_disable_fx),
    ("perf",     "enable_fx"):  ("perf",   _t_perf_enable_fx),
    ("perf",     "disable_svc"): ("perf",  _t_perf_disable_svc),
    ("perf",     "enable_svc"):  ("perf",  _t_perf_enable_svc),
    ("perf",     None):       ("perf",     _t_perf_power),

    ("clean_cat", "1"):       ("clean",    lambda: _t_clean_cat("1")),
    ("clean_cat", "2"):       ("clean",    lambda: _t_clean_cat("2")),
    ("clean_cat", "3"):       ("clean",    lambda: _t_clean_cat("3")),
    ("clean_cat", "4"):       ("clean",    lambda: _t_clean_cat("4")),
    ("clean_cat", "5"):       ("clean",    lambda: _t_clean_cat("5")),
    ("clean_cat", "6"):       ("clean",    lambda: _t_clean_cat("6")),
    ("clean_cat", "7"):       ("clean",    lambda: _t_clean_cat("7")),
    ("clean_cat", "8"):       ("clean",    lambda: _t_clean_cat("8")),
}


# ============================================================
# 4. JS ↔ Python 桥（暴露给网页调用）
# ============================================================

class Api:
    def __init__(self):
        self._window = None
        self._lock = threading.Lock()
        self._running = False

    def attach(self, window):
        self._window = window

    # --- 给网页查询用 ---

    def is_admin(self):
        try:
            from scanner_toolbox.utils.terminal import is_admin
            return bool(is_admin())
        except Exception:
            return False

    def backend_ready(self):
        return {
            "ok": SCANNER_OK,
            "err": "" if SCANNER_OK else _IMPORT_ERR,
            "platform": sys.platform,
        }

    # --- 主入口：网页点按钮就调这个 ---

    def run_task(self, module, action=None, params=None):
        with self._lock:
            if self._running:
                self._push("scan", "[WARN] 已有任务在执行中，请等待完成")
                return {"ok": False, "err": "busy"}
            self._running = True

        key = (module, action) if (module, action) in TASK_MAP else (module, None)
        if key not in TASK_MAP:
            self._push(module, f"[ERROR] 未知任务: {module}/{action}")
            self._finish(module, success=False)
            with self._lock:
                self._running = False
            return {"ok": False, "err": "unknown_task"}

        log_id, fn = TASK_MAP[key]
        kwargs = params or {}

        def worker():
            writer = StreamWriter(self._window, log_id)
            ok = True
            try:
                with redirect_stdout(writer), redirect_stderr(writer):
                    fn(**kwargs) if kwargs else fn()
                writer.flush()
            except Exception as e:
                writer.flush()
                self._push(log_id, f"[ERROR] {e}")
                ok = False
            finally:
                self._finish(log_id, success=ok)
                with self._lock:
                    self._running = False

        threading.Thread(target=worker, daemon=True).start()
        return {"ok": True}

    # --- 内部工具 ---

    def _push(self, log_id, text):
        if not self._window:
            return
        js = "window.appendLog && window.appendLog({lid},{txt})".format(
            lid=json.dumps(log_id), txt=json.dumps(text),
        )
        try:
            self._window.evaluate_js(js)
        except Exception:
            pass

    def _finish(self, log_id, success=True):
        if not self._window:
            return
        js = "window.taskDone && window.taskDone({lid},{ok})".format(
            lid=json.dumps(log_id), ok="true" if success else "false",
        )
        try:
            self._window.evaluate_js(js)
        except Exception:
            pass


# ============================================================
# 5. 入口
# ============================================================

def _show_fatal(message: str):
    """窗口模式下弹出错误，避免静默白屏。"""
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, "超级骆狗工具箱", 0x10)
        else:
            print(message, file=sys.stderr)
    except Exception:
        print(message, file=sys.stderr)


def _validate_bundle() -> str:
    """检查 UI 资源是否齐全，返回 preview.html 绝对路径。"""
    html_path = resource_path("preview.html")
    missing = []
    for rel in ("preview.html", "assets/app.css", "assets/fonts.css"):
        if not os.path.isfile(resource_path(*rel.split("/"))):
            missing.append(rel)
    if missing:
        _show_fatal(
            "界面资源缺失，无法启动：\n\n"
            + "\n".join(f"  • {name}" for name in missing)
            + "\n\n请重新下载完整安装包，或使用 build.bat 重新打包。"
        )
        sys.exit(1)
    return html_path


def main():
    api = Api()
    html_path = _validate_bundle()

    window = webview.create_window(
        title="超级骆狗工具箱 v3.0",
        url=html_path,
        js_api=api,
        width=1180,
        height=760,
        min_size=(960, 640),
    )
    api.attach(window)
    webview.start()


if __name__ == "__main__":
    main()
