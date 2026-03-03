@echo off
chcp 65001 >nul
echo ========================================
echo 网络故障排查工具 - Windows打包脚本
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo.
echo [2/5] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
)

echo.
echo [3/5] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [4/5] 开始打包...
pyinstaller --clean ^
    --name="网络故障排查工具" ^
    --windowed ^
    --onefile ^
    --add-data="data;data" ^
    --add-data="网络故障排查指导文档.md;." ^
    --hidden-import="PyQt5.QtCore" ^
    --hidden-import="PyQt5.QtGui" ^
    --hidden-import="PyQt5.QtWidgets" ^
    --hidden-import="psutil" ^
    --hidden-import="dns.resolver" ^
    --hidden-import="requests" ^
    --hidden-import="speedtest" ^
    run.py

echo.
echo [5/5] 清理临时文件...
if exist "build" rmdir /s /q build
if exist "__pycache__" rmdir /s /q __pycache__

echo.
echo ========================================
echo 打包完成！
echo 可执行文件位置: dist\网络故障排查工具.exe
echo ========================================
echo.

pause
