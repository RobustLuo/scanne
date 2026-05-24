@echo off
chcp 65001 >nul
echo ============================================
echo   超级骆狗工具箱 - 打包脚本
echo ============================================
echo.

echo [1/3] 安装依赖...
pip install pyinstaller -q

echo [2/3] 打包为exe...
pyinstaller --onefile ^
    --name "超级骆狗工具箱" ^
    --version-file version_info.py ^
    --manifest app.manifest ^
    --uac-admin ^
    --clean ^
    scanner.py

echo [3/3] 完成!
echo.
echo ============================================
echo   输出文件: dist\超级骆狗工具箱.exe
echo ============================================
echo.
echo 提示: 如果要彻底消除SmartScreen警告，需要购买代码签名证书
echo       对exe进行数字签名 (signtool sign)
echo.
pause
