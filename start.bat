@echo off
REM 网络故障排查工具启动脚本

echo 正在启动网络故障排查工具...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python3
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 启动程序
python main.py

pause
