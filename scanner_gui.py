"""
超级骆狗工具箱 v3.0 - GUI版
基于 CustomTkinter 深色主题
"""

import os
import sys
import threading
import queue
import io
from contextlib import redirect_stdout, redirect_stderr

import customtkinter as ctk

# 设置主题
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ============================================================
# 重定向 print 输出到 GUI 日志
# ============================================================

class QueueWriter:
    """将 print 输出重定向到 queue，供 GUI 消费"""
    def __init__(self, log_queue):
        self.queue = log_queue

    def write(self, text):
        if text.strip():
            # 去掉 ANSI 颜色码
            import re
            clean = re.sub(r'\x1b\[[0-9;]*m', '', text)
            self.queue.put(clean)

    def flush(self):
        pass


# ============================================================
# 导入 scanner.py 中的功能函数
# ============================================================

# 添加当前目录到 path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 延迟导入（仅在 Windows 上有效）
scanner_module = None

def import_scanner():
    global scanner_module
    try:
        import scanner as scanner_module
        return True
    except Exception as e:
        return False


# ============================================================
# 侧边栏按钮配置
# ============================================================

MODULES = [
    ("流氓扫描", "scan"),
    ("垃圾清理", "clean"),
    ("反劫持", "hijack"),
    ("空间管理", "space"),
    ("安全审计", "security"),
    ("网络工具", "network"),
    ("系统信息", "sysinfo"),
    ("装机助手", "install"),
    ("性能优化", "perf"),
]


# ============================================================
# 主应用窗口
# ============================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("超级骆狗工具箱 v3.0")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # 日志队列
        self.log_queue = queue.Queue()
        self.running_task = False

        # ---- 主容器 用 pack 布局 ----
        # 左侧导航栏
        self.nav_frame = ctk.CTkFrame(self, width=170, corner_radius=0)
        self.nav_frame.pack(side="left", fill="y")
        self.nav_frame.pack_propagate(False)

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.nav_frame, text="骆狗工具箱",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.logo_label.pack(padx=15, pady=(20, 25))

        # 导航按钮
        self.nav_buttons = {}
        for label, key in MODULES:
            btn = ctk.CTkButton(
                self.nav_frame, text=label, height=34,
                font=ctk.CTkFont(size=13),
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w", corner_radius=8,
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(padx=8, pady=2, fill="x")
            self.nav_buttons[key] = btn

        # 版本信息（底部）
        spacer = ctk.CTkLabel(self.nav_frame, text="")
        spacer.pack(expand=True)
        self.ver_label = ctk.CTkLabel(
            self.nav_frame, text="v3.0", font=ctk.CTkFont(size=11),
            text_color="gray50"
        )
        self.ver_label.pack(pady=(0, 10))

        # ---- 右侧内容区 ----
        self.content_frame = ctk.CTkFrame(self, corner_radius=10)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # 页面标题
        self.page_title = ctk.CTkLabel(
            self.content_frame, text="欢迎使用骆狗工具箱",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.page_title.pack(padx=20, pady=(15, 0), anchor="w")

        # 页面描述
        self.page_desc = ctk.CTkLabel(
            self.content_frame, text="请从左侧选择功能模块",
            font=ctk.CTkFont(size=13), text_color="gray60"
        )
        self.page_desc.pack(padx=20, pady=(2, 10), anchor="w")

        # 按钮行
        self.btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.btn_frame.pack(padx=15, pady=(0, 5), fill="x")

        # 日志输出区
        self.log_box = ctk.CTkTextbox(
            self.content_frame, font=ctk.CTkFont(size=12),
            state="disabled", wrap="word"
        )
        self.log_box.pack(padx=15, pady=(0, 5), fill="both", expand=True)

        # 进度条
        self.progress = ctk.CTkProgressBar(self.content_frame, mode="indeterminate")
        self.progress.pack(padx=20, pady=(0, 10), fill="x")
        self.progress.set(0)

        # 当前页面
        self.current_page = None

        # 定时检查日志队列
        self.after(100, self._poll_log_queue)

        # 默认显示首页
        self.show_page("scan")

    def _poll_log_queue(self):
        """定期从队列取出日志写入文本框"""
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                self.log_box.insert("end", msg + "\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
            except queue.Empty:
                break
        self.after(100, self._poll_log_queue)

    def _highlight_nav(self, key):
        """高亮当前选中的导航按钮"""
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")

    def _clear_action_buttons(self):
        """清空操作按钮区"""
        for widget in self.btn_frame.winfo_children():
            widget.destroy()

    def _clear_log(self):
        """清空日志"""
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _run_task(self, func, *args):
        """在后台线程运行任务"""
        if func is None:
            self.log_queue.put("⚠️ 此功能需要在 Windows 环境下运行")
            return
        if self.running_task:
            self.log_queue.put("⚠️ 有任务正在执行中，请等待完成...")
            return

        self._clear_log()
        self.running_task = True
        self.progress.start()

        def worker():
            # 重定向 stdout 到日志
            writer = QueueWriter(self.log_queue)
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = writer
            sys.stderr = writer
            try:
                func(*args)
            except Exception as e:
                self.log_queue.put(f"\n❌ 错误: {e}")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                self.running_task = False
                self.after(0, self.progress.stop)
                self.after(0, lambda: self.progress.set(0))
                self.log_queue.put("\n✅ 任务完成")

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    # ============================================================
    # 各功能页面
    # ============================================================

    def show_page(self, key):
        self.current_page = key
        self._highlight_nav(key)
        self._clear_action_buttons()

        pages = {
            "scan": self._page_scan,
            "clean": self._page_clean,
            "hijack": self._page_hijack,
            "space": self._page_space,
            "security": self._page_security,
            "network": self._page_network,
            "sysinfo": self._page_sysinfo,
            "install": self._page_install,
            "perf": self._page_perf,
        }
        pages[key]()

    def _get_func(self, name):
        """安全获取 scanner 模块的函数"""
        if scanner_module is None:
            return None
        return getattr(scanner_module, name, None)

    def _page_scan(self):
        self.page_title.configure(text="流氓软件扫描与清理")
        self.page_desc.configure(text="扫描全盘查找 360/2345/百度/金山等流氓软件残留，支持四级强力删除")

        btn = ctk.CTkButton(self.btn_frame, text="开始扫描", width=140,
                            command=lambda: self._run_task(self._get_func('run_scan')))
        btn.pack(side="left", padx=5)

    def _page_clean(self):
        self.page_title.configure(text="系统垃圾深度清理")
        self.page_desc.configure(text="8大类垃圾文件清理，支持分类选择，强力删除被占用文件")

        # 复选框区域
        self.clean_vars = {}
        categories = [
            ("1", "系统临时文件与缓存"),
            ("2", "浏览器缓存（全部浏览器）"),
            ("3", "Windows更新与日志"),
            ("4", "常用软件缓存"),
            ("5", "国产软件缓存（微信/QQ/迅雷等）"),
            ("6", "Windows.old与系统残留"),
            ("7", "回收站"),
            ("8", "DNS缓存刷新"),
        ]

        check_frame = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        check_frame.pack(side="left", padx=10)

        for i, (key, name) in enumerate(categories):
            var = ctk.BooleanVar(value=True)
            self.clean_vars[key] = var
            cb = ctk.CTkCheckBox(check_frame, text=name, variable=var,
                                 font=ctk.CTkFont(size=12))
            cb.grid(row=i // 2, column=i % 2, padx=10, pady=2, sticky="w")

        btn_frame2 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        btn_frame2.pack(side="left", padx=20)

        btn_all = ctk.CTkButton(btn_frame2, text="全选", width=60,
                                command=lambda: [v.set(True) for v in self.clean_vars.values()])
        btn_all.pack(pady=2)

        btn_none = ctk.CTkButton(btn_frame2, text="全不选", width=60,
                                 fg_color="gray40",
                                 command=lambda: [v.set(False) for v in self.clean_vars.values()])
        btn_none.pack(pady=2)

        btn_run = ctk.CTkButton(btn_frame2, text="开始清理", width=100,
                                fg_color="#d45050", hover_color="#b03030",
                                command=self._run_clean)
        btn_run.pack(pady=(10, 2))

    def _run_clean(self):
        """执行垃圾清理（带分类选择）"""
        selected = [k for k, v in self.clean_vars.items() if v.get()]
        if not selected:
            self.log_queue.put("⚠️ 请至少选择一个清理类别")
            return

        def do_clean():
            # 模拟用户输入选择（因为原函数用 input()）
            # 这里直接调用内部逻辑
            import scanner as sc
            categories = self._get_clean_categories(sc)
            total_cleaned = 0
            total_files = 0
            total_errors = 0

            for sel in selected:
                cat = categories.get(sel)
                if not cat:
                    continue
                print(f"\n── {cat['name']} ──\n")
                if "special" in cat:
                    if cat["special"] == "recycle_bin":
                        sc._empty_recycle_bin()
                    elif cat["special"] == "flush_dns":
                        sc._flush_dns()
                    elif cat["special"] == "windows_old":
                        sc._clean_windows_old()
                else:
                    cleaned, files, errors = sc._clean_paths(cat["paths"])
                    total_cleaned += cleaned
                    total_files += files
                    total_errors += errors

            print(f"\n{'='*50}")
            print(f"  共清理 {total_files} 个文件，释放空间: {sc.format_size(total_cleaned)}")
            if total_errors > 0:
                print(f"  (有 {total_errors} 个文件被占用，跳过)")

        self._run_task(do_clean)

    def _get_clean_categories(self, sc):
        """获取清理类别定义"""
        return {
            "1": {"name": "系统临时文件与缓存", "paths": [
                (os.path.expandvars(r"%TEMP%"), "用户临时文件"),
                (os.path.expandvars(r"%SystemRoot%\Temp"), "系统临时文件"),
                (os.path.expandvars(r"%LocalAppData%\Temp"), "本地临时文件"),
                (os.path.expandvars(r"%SystemRoot%\Prefetch"), "预读取缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer"), "缩略图缓存"),
            ]},
            "2": {"name": "浏览器缓存", "paths": [
                (os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"), "Chrome缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"), "Edge缓存"),
                (os.path.expandvars(r"%LocalAppData%\Mozilla\Firefox\Profiles"), "Firefox缓存"),
                (os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\INetCache"), "IE缓存"),
            ]},
            "3": {"name": "Windows更新与日志", "paths": [
                (os.path.expandvars(r"%SystemRoot%\SoftwareDistribution\Download"), "更新缓存"),
                (os.path.expandvars(r"%ProgramData%\Microsoft\Windows\WER"), "错误报告"),
                (os.path.expandvars(r"%LocalAppData%\CrashDumps"), "崩溃转储"),
            ]},
            "4": {"name": "常用软件缓存", "paths": [
                (os.path.expandvars(r"%LocalAppData%\pip\cache"), "pip缓存"),
                (os.path.expandvars(r"%LocalAppData%\npm-cache"), "npm缓存"),
                (os.path.expandvars(r"%AppData%\Microsoft\Teams\Cache"), "Teams缓存"),
            ]},
            "5": {"name": "国产软件缓存", "paths": [
                (os.path.expandvars(r"%AppData%\Tencent\WeChat\log"), "微信日志"),
                (os.path.expandvars(r"%AppData%\Tencent\QQ\Temp"), "QQ临时"),
                (os.path.expandvars(r"%AppData%\Baidu\BaiduNetdisk\temp"), "百度网盘临时"),
                (os.path.expandvars(r"%LocalAppData%\Netease\CloudMusic\Cache"), "网易云缓存"),
            ]},
            "6": {"name": "Windows.old", "special": "windows_old"},
            "7": {"name": "回收站", "special": "recycle_bin"},
            "8": {"name": "DNS缓存", "special": "flush_dns"},
        }

    def _page_hijack(self):
        self.page_title.configure(text="反劫持检测")
        self.page_desc.configure(text="检测 Hosts劫持 / 浏览器快捷方式劫持 / 右键菜单 / 可疑启动项")

        btns = [
            ("Hosts检测", lambda: self._run_task(self._get_func('check_hosts_hijack'))),
            ("快捷方式检测", lambda: self._run_task(self._get_func('check_shortcut_hijack'))),
            ("右键菜单检测", lambda: self._run_task(self._get_func('scan_context_menu'))),
            ("启动项总览", lambda: self._run_task(self._get_func('list_all_startups'))),
        ]
        for text, cmd in btns:
            ctk.CTkButton(self.btn_frame, text=text, width=120,
                          command=cmd).pack(side="left", padx=5)

    def _page_space(self):
        self.page_title.configure(text="空间清理增强")
        self.page_desc.configure(text="查找大文件 / 重复文件，快速释放磁盘空间")

        ctk.CTkButton(self.btn_frame, text="大文件查找 (Top30)", width=160,
                      command=lambda: self._run_task(self._get_func('find_large_files'))
                      ).pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="重复文件查找", width=140,
                      command=lambda: self._run_task(self._get_func('find_duplicate_files'))
                      ).pack(side="left", padx=5)

    def _page_security(self):
        self.page_title.configure(text="安全审计")
        self.page_desc.configure(text="可疑进程 / Defender排除项 / 未签名驱动检查")

        btns = [
            ("可疑进程扫描", lambda: self._run_task(self._get_func('scan_suspicious_processes'))),
            ("Defender排除项", lambda: self._run_task(self._get_func('audit_defender_exclusions'))),
            ("未签名驱动", lambda: self._run_task(self._get_func('check_unsigned_drivers'))),
        ]
        for text, cmd in btns:
            ctk.CTkButton(self.btn_frame, text=text, width=130,
                          command=cmd).pack(side="left", padx=5)

    def _page_network(self):
        self.page_title.configure(text="网络工具")
        self.page_desc.configure(text="DNS/代理检查 / 端口占用查询 / 一键网络诊断修复")

        btns = [
            ("DNS/代理检查", lambda: self._run_task(self._get_func('check_dns_proxy'))),
            ("端口占用查询", self._port_query),
            ("网络诊断修复", lambda: self._run_task(self._get_func('network_reset'))),
        ]
        for text, cmd in btns:
            ctk.CTkButton(self.btn_frame, text=text, width=130,
                          command=cmd).pack(side="left", padx=5)

    def _port_query(self):
        """端口查询弹窗"""
        dialog = ctk.CTkInputDialog(text="输入要查询的端口号:", title="端口查询")
        port = dialog.get_input()
        if port and port.isdigit():
            self._run_task(self._get_func('query_port'), int(port))

    def _page_sysinfo(self):
        self.page_title.configure(text="系统信息")
        self.page_desc.configure(text="CPU / 内存 / 磁盘使用情况")

        ctk.CTkButton(self.btn_frame, text="查看系统信息", width=140,
                      command=lambda: self._run_task(self._get_func('show_system_info'))
                      ).pack(side="left", padx=5)

    def _page_install(self):
        self.page_title.configure(text="装机助手")
        self.page_desc.configure(text="重置电脑 / 制作U盘 / 高级启动 / 装机教程")

        btns = [
            ("系统重置", lambda: self._run_task(self._get_func('system_reset_guide'))),
            ("U盘制作指南", lambda: self._run_task(self._get_func('usb_boot_guide'))),
            ("高级启动", lambda: self._run_task(self._get_func('advanced_boot'))),
            ("装机教程", lambda: self._run_task(self._get_func('newbie_guide'))),
        ]
        for text, cmd in btns:
            ctk.CTkButton(self.btn_frame, text=text, width=110,
                          command=cmd).pack(side="left", padx=5)

    def _page_perf(self):
        self.page_title.configure(text="性能优化")
        self.page_desc.configure(text="智能识别设备类型，一键差异化优化，可一键还原")

        ctk.CTkButton(self.btn_frame, text="一键优化", width=120,
                      fg_color="#2d8a4e", hover_color="#1f6b3a",
                      command=lambda: self._run_task(self._get_func('performance_menu'))
                      ).pack(side="left", padx=5)
        ctk.CTkButton(self.btn_frame, text="还原优化", width=120,
                      fg_color="gray40",
                      command=lambda: self._run_task(self._get_func('restore_performance'))
                      ).pack(side="left", padx=5)


# ============================================================
# 入口
# ============================================================

def main():
    # 尝试导入 scanner 模块
    if not import_scanner():
        print("警告: 无法导入 scanner 模块（可能不在 Windows 环境）")

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
