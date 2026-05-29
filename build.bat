@echo off
chcp 65001 >nul
echo ============================================
echo   超级骆狗工具箱 - 打包脚本
echo ============================================
echo.
echo   [1] 打包 GUI 版（CustomTkinter）
echo   [2] 打包命令行版
echo   [3] 打包网页版（pywebview · 1:1 漂亮界面，推荐）
echo.
set /p choice="请选择 (1/2/3): "

echo.
echo [1/3] 安装依赖...
if "%choice%"=="3" (
    pip install pyinstaller pywebview -q
) else if "%choice%"=="2" (
    pip install pyinstaller -q
) else (
    pip install pyinstaller customtkinter -q
)

if "%choice%"=="2" goto console
if "%choice%"=="3" goto webview

:gui
echo [2/3] 打包 GUI 版（CustomTkinter）...
pyinstaller --onefile --windowed ^
    --name "超级骆狗工具箱" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --collect-data customtkinter ^
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
    --clean ^
    scanner.py
goto done

:webview
echo [2/3] 打包网页版（pywebview）...
pyinstaller --onefile --windowed ^
    --name "超级骆狗工具箱-Web" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --add-data "preview.html;." ^
    --hidden-import webview.platforms.edgechromium ^
    --hidden-import webview.platforms.mshtml ^
    --hidden-import webview.platforms.winforms ^
    --clean ^
    scanner_webview.py
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
