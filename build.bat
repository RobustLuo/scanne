@echo off
chcp 65001 >nul
echo ============================================
echo   超级骆狗工具箱 - 打包脚本
echo ============================================
echo.
echo   [1] 打包 GUI 版（推荐）
echo   [2] 打包命令行版
echo.
set /p choice="请选择 (1/2): "

echo.
echo [1/3] 安装依赖...
pip install pyinstaller customtkinter -q

if "%choice%"=="2" goto console

:gui
echo [2/3] 打包 GUI 版...
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
