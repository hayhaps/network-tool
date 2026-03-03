# 网络故障排查工具 - Windows打包说明

## 📦 在Windows上生成可执行文件

### 方法一：使用自动打包脚本（推荐）

1. **安装Python**
   - 下载并安装 Python 3.8 或更高版本
   - 下载地址：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **下载项目代码**
   ```bash
   git clone https://github.com/hayhaps/network-tool.git
   cd network-tool
   ```

3. **运行打包脚本**
   - 双击运行 `build_windows.bat`
   - 等待打包完成
   - 可执行文件位于 `dist\网络故障排查工具.exe`

### 方法二：手动打包

1. **创建虚拟环境**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **执行打包命令**
   ```bash
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
   ```

4. **查找可执行文件**
   - 打包完成后，可执行文件位于 `dist\网络故障排查工具.exe`

## 🎯 功能特性

### 核心功能
- ✅ Ping测试 - 网络连通性测试
- ✅ 路由追踪 - 智能多方法路由追踪
- ✅ 端口扫描 - 网络端口状态检测
- ✅ 速度测试 - 网络带宽测试
- ✅ IP配置 - 网络配置查看和管理
- ✅ 流量监控 - 实时网络流量监控
- ✅ DNS查询 - 域名和IP双向解析
- ✅ Wi-Fi扫描 - 无线网络扫描
- ✅ 网络拓扑 - 网络结构可视化
- ✅ 子网计算 - IP子网计算器
- ✅ 网络诊断 - 批量网络诊断
- ✅ 智能助手 - AI网络故障排查助手
- ✅ SNMP管理 - SNMP设备管理
- ✅ VLAN配置 - VLAN信息查询

### 特色功能
- 🎨 工程师风格主题（黑底绿字）
- 🔄 三种主题切换（工程师/浅色/深色）
- 🖱️ 导航按钮选中状态高亮
- 🤖 AI智能故障排查
- 📊 实时网络监控

## 🖥️ 系统要求

### Windows系统
- Windows 7/8/10/11
- 无需安装Python环境（打包后）

### macOS系统
- macOS 10.13 或更高版本

### Linux系统
- 主流Linux发行版

## 📝 使用说明

### 路由追踪功能
- **Windows**: 自动使用 `tracert` 命令
- **macOS/Linux**: 智能尝试多种方法
  1. UDP traceroute
  2. ICMP traceroute
  3. Ping路由探测（无需权限）

### DNS查询功能
- 支持域名 → IP地址解析
- 支持IP地址 → 域名反向解析
- 自动识别输入类型
- 支持多种DNS记录类型

### 速度测试功能
- 自动识别运营商
- 智能选择最优服务器
- 显示详细测试信息

## 🔧 常见问题

### 1. 打包失败
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 确保Python版本 >= 3.8
- 尝试清理缓存：删除 `build` 和 `dist` 目录后重新打包

### 2. 运行时缺少模块
- 检查 `requirements.txt` 是否包含所有依赖
- 在打包命令中添加缺失的 `--hidden-import`

### 3. 路由追踪权限问题
- Windows: 以管理员身份运行
- macOS/Linux: 使用sudo或使用自动降级的ping探测

### 4. 防火墙拦截
- 首次运行时，允许程序通过防火墙
- 或在防火墙设置中添加例外

## 📦 项目结构

```
network-tool/
├── modules/              # 功能模块
│   ├── connectivity.py   # Ping和路由追踪
│   ├── dns_query.py      # DNS查询
│   ├── speed_test.py     # 速度测试
│   ├── traffic_monitor.py # 流量监控
│   └── ...
├── ui/                   # 界面模块
│   ├── main_window.py    # 主窗口
│   └── styles.py         # 样式主题
├── data/                 # 数据文件
│   └── network_troubleshooting_guide.md
├── utils/                # 工具函数
├── main.py               # 程序入口
├── run.py                # 打包入口
├── requirements.txt      # 依赖列表
├── build_windows.bat     # Windows打包脚本
└── README.md             # 说明文档
```

## 🚀 快速开始

1. 下载项目代码
2. 运行 `build_windows.bat`
3. 在 `dist` 目录找到可执行文件
4. 双击运行即可使用

## 📄 许可证

MIT License

## 👨‍💻 作者

@大笑无声

## 🙏 致谢

感谢所有开源项目的贡献者！
