@echo off
chcp 65001 >nul
echo ========================================
echo    网络故障排查工具 - 单文件打包
echo ========================================
echo.
echo 此脚本将生成一个单独的exe文件
echo 适合直接分发使用
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

echo.
echo [2/4] 安装PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo 错误: PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 安装项目依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [4/4] 开始打包单文件版本...
echo 这可能需要5-10分钟，请耐心等待...
echo.

pyinstaller --clean network_tool_onefile.spec

if errorlevel 1 (
    echo.
    echo 错误: 打包失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\网络故障排查工具.exe
echo.
echo 提示: 
echo   - 这是一个单独的exe文件，可以直接运行
echo   - 首次运行可能需要防火墙允许
echo   - 文件较大（约50-100MB），包含所有依赖
echo.
pause
