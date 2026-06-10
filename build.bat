@echo off
chcp 65001 >nul
echo ============================================
echo   超级骆狗工具箱 v2.0 - 本地打包脚本
echo ============================================
echo.
echo   [1] 打包网页版（pywebview · 漂亮 Material 界面，推荐）
echo   [2] 打包 GUI 版（CustomTkinter）
echo   [3] 打包命令行版
echo.
set /p choice="请选择 (1/2/3): "

echo.
echo [1/3] 安装依赖...
if "%choice%"=="2" (
    pip install -e ".[dev]" customtkinter -q
) else if "%choice%"=="3" (
    pip install -e ".[dev]" -q
) else (
    pip install -e ".[dev]" pywebview -q
)

if "%choice%"=="2" goto gui
if "%choice%"=="3" goto console

:webview
echo [2/3] 打包网页版（pywebview）...
pyinstaller --onefile --windowed ^
    --name "超级骆狗工具箱" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --add-data "preview.html;." ^
    --hidden-import webview.platforms.edgechromium ^
    --hidden-import webview.platforms.mshtml ^
    --hidden-import webview.platforms.winforms ^
    --hidden-import scanner_toolbox ^
    --hidden-import scanner_toolbox.config ^
    --hidden-import scanner_toolbox.config.constants ^
    --hidden-import scanner_toolbox.config.malware_db ^
    --hidden-import scanner_toolbox.core ^
    --hidden-import scanner_toolbox.core.scanner ^
    --hidden-import scanner_toolbox.core.cleaner ^
    --hidden-import scanner_toolbox.core.report ^
    --hidden-import scanner_toolbox.modules ^
    --hidden-import scanner_toolbox.modules.cache_clean ^
    --hidden-import scanner_toolbox.modules.anti_hijack ^
    --hidden-import scanner_toolbox.modules.space_manager ^
    --hidden-import scanner_toolbox.modules.security_audit ^
    --hidden-import scanner_toolbox.modules.network_tools ^
    --hidden-import scanner_toolbox.modules.sysinfo ^
    --hidden-import scanner_toolbox.modules.install_helper ^
    --hidden-import scanner_toolbox.modules.perf_optimizer ^
    --hidden-import scanner_toolbox.utils ^
    --hidden-import scanner_toolbox.utils.terminal ^
    --hidden-import scanner_toolbox.utils.file_ops ^
    --clean ^
    scanner_webview.py
goto done

:gui
echo [2/3] 打包 GUI 版（CustomTkinter）...
pyinstaller --onefile --windowed ^
    --name "超级骆狗工具箱-GUI" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --collect-data customtkinter ^
    --hidden-import scanner_toolbox ^
    --hidden-import scanner_toolbox.config ^
    --hidden-import scanner_toolbox.config.constants ^
    --hidden-import scanner_toolbox.config.malware_db ^
    --hidden-import scanner_toolbox.core ^
    --hidden-import scanner_toolbox.core.scanner ^
    --hidden-import scanner_toolbox.core.cleaner ^
    --hidden-import scanner_toolbox.core.report ^
    --hidden-import scanner_toolbox.modules ^
    --hidden-import scanner_toolbox.modules.cache_clean ^
    --hidden-import scanner_toolbox.modules.anti_hijack ^
    --hidden-import scanner_toolbox.modules.space_manager ^
    --hidden-import scanner_toolbox.modules.security_audit ^
    --hidden-import scanner_toolbox.modules.network_tools ^
    --hidden-import scanner_toolbox.modules.sysinfo ^
    --hidden-import scanner_toolbox.modules.install_helper ^
    --hidden-import scanner_toolbox.modules.perf_optimizer ^
    --hidden-import scanner_toolbox.utils ^
    --hidden-import scanner_toolbox.utils.terminal ^
    --hidden-import scanner_toolbox.utils.file_ops ^
    --clean ^
    scanner_gui.py
goto done

:console
echo [2/3] 打包命令行版...
pyinstaller --onefile ^
    --name "超级骆狗工具箱-命令行" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --hidden-import scanner_toolbox ^
    --hidden-import scanner_toolbox.config ^
    --hidden-import scanner_toolbox.config.constants ^
    --hidden-import scanner_toolbox.config.malware_db ^
    --hidden-import scanner_toolbox.core ^
    --hidden-import scanner_toolbox.core.scanner ^
    --hidden-import scanner_toolbox.core.cleaner ^
    --hidden-import scanner_toolbox.core.report ^
    --hidden-import scanner_toolbox.modules ^
    --hidden-import scanner_toolbox.modules.cache_clean ^
    --hidden-import scanner_toolbox.modules.anti_hijack ^
    --hidden-import scanner_toolbox.modules.space_manager ^
    --hidden-import scanner_toolbox.modules.security_audit ^
    --hidden-import scanner_toolbox.modules.network_tools ^
    --hidden-import scanner_toolbox.modules.sysinfo ^
    --hidden-import scanner_toolbox.modules.install_helper ^
    --hidden-import scanner_toolbox.modules.perf_optimizer ^
    --hidden-import scanner_toolbox.utils ^
    --hidden-import scanner_toolbox.utils.terminal ^
    --hidden-import scanner_toolbox.utils.file_ops ^
    --clean ^
    scanner_toolbox/main.py
goto done

:done
echo [3/3] 完成!
echo.
echo ============================================
echo   输出文件在 dist\ 目录下
echo ============================================
echo.
echo 提示: 如果要彻底消除SmartScreen警告，需要购买代码签名证书
echo       对exe进行数字签名 (signtool sign)
echo.
pause
