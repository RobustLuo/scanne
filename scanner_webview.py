"""
超级骆狗工具箱 v3.0 - Web UI 版
================================
用 pywebview 把 preview.html 包装成一个原生桌面 exe 窗口，
并把网页上的按钮接到 scanner.py 的真实功能上。

界面长相 == preview.html（1:1 一致）
真实功能 == scanner.py（不改动）
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
# 1. 准备：导入 scanner 模块（跨平台容错）
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

scanner = None
SCANNER_OK = False
_IMPORT_ERR = ""
try:
    import scanner as _scanner  # noqa: E402
    scanner = _scanner
    SCANNER_OK = True
except Exception as e:
    _IMPORT_ERR = repr(e)


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
        # 用 json.dumps 安全转义为 JS 字符串字面量
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


def _t_scan():
    if _need_scanner():
        scanner.run_scan()


def _t_clean():
    if _need_scanner():
        scanner.clean_cache()


def _t_hijack_hosts():
    if not _need_scanner():
        return
    custom, suspicious = scanner.scan_hosts()
    print(f"自定义 hosts 条目: {len(custom)} 条")
    for c in custom:
        print("  " + c)
    print(f"可疑/劫持条目: {len(suspicious)} 条")
    for s in suspicious:
        print("  " + s)
    if not custom and not suspicious:
        print("hosts 文件干净，无异常")


def _t_hijack_shortcut():
    if not _need_scanner():
        return
    items = scanner.scan_browser_shortcuts()
    if not items:
        print("浏览器快捷方式均正常，未发现劫持")
    else:
        print(f"发现 {len(items)} 个可疑快捷方式：")
        for it in items:
            print(f"  {it}")


def _t_hijack_context():
    if not _need_scanner():
        return
    items = scanner.scan_context_menu()
    if not items:
        print("右键菜单干净，未发现可疑项")
    else:
        print(f"发现 {len(items)} 个可疑右键菜单项：")
        for it in items:
            print(f"  {it}")


def _t_hijack_startups():
    if _need_scanner():
        scanner.list_all_startup()


def _t_space_large():
    if not _need_scanner():
        return
    files = scanner.find_big_files(min_mb=100, top=30)
    print(f"Top {len(files)} 大文件：")
    for size, path in files:
        print(f"  {scanner.format_size(size):>10}  {path}")


def _t_space_dup(folder=None):
    if not _need_scanner():
        return
    folder = folder or os.environ.get("USERPROFILE", "C:\\")
    print(f"扫描重复文件: {folder}")
    scanner.find_duplicate_files(folder)


def _t_sec_proc():
    if _need_scanner():
        scanner.scan_suspicious_processes()


def _t_sec_defender():
    if _need_scanner():
        scanner.scan_defender_exclusions()


def _t_sec_driver():
    if _need_scanner():
        scanner.scan_unsigned_drivers()


def _t_net_dns():
    if not _need_scanner():
        return
    info = scanner.check_dns_proxy()
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
    scanner.query_port(port)


def _t_net_diag():
    if _need_scanner():
        scanner.network_diagnostic()


def _t_sysinfo():
    if _need_scanner():
        scanner.show_system_info()


def _t_inst_reset():
    if _need_scanner():
        scanner.reset_this_pc()


def _t_inst_usb():
    if _need_scanner():
        scanner.make_usb_guide()


def _t_inst_boot():
    if _need_scanner():
        scanner.advanced_startup()


def _t_inst_tut():
    if _need_scanner():
        scanner.show_install_tutorial()


def _t_perf_optimize():
    if not _need_scanner():
        return
    dt, detail = scanner.detect_device_type()
    disk = scanner.get_system_disk_type()
    print(f"设备类型: {dt}（{detail}）")
    print(f"系统盘类型: {disk}")
    scanner.one_click_optimize(dt, disk)


def _t_perf_restore():
    if _need_scanner():
        scanner.restore_all_perf()


def _t_perf_power():
    if _need_scanner():
        scanner.manage_power_plans()


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

    ("install",  "reset"):    ("install",  _t_inst_reset),
    ("install",  "usb"):      ("install",  _t_inst_usb),
    ("install",  "boot"):     ("install",  _t_inst_boot),
    ("install",  "tutorial"): ("install",  _t_inst_tut),
    ("install",  None):       ("install",  _t_inst_tut),

    ("perf",     "optimize"): ("perf",     _t_perf_optimize),
    ("perf",     "restore"):  ("perf",     _t_perf_restore),
    ("perf",     "power"):    ("perf",     _t_perf_power),
    ("perf",     None):       ("perf",     _t_perf_optimize),
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
        if not SCANNER_OK:
            return False
        try:
            return bool(scanner.is_admin())
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
                self._push(module, "[WARN] 已有任务在执行中，请等待完成")
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

def main():
    api = Api()
    html_path = os.path.join(BASE_DIR, "preview.html")
    if not os.path.exists(html_path):
        print(f"[FATAL] 找不到 preview.html: {html_path}")
        sys.exit(1)

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
