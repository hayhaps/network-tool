#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络故障排查工具 v1.1
功能：
- 网络连通性测试（ping、traceroute）
- 端口扫描和服务检测（多线程优化）
- 网络速度测试（带宽、延迟）
- 网络设备配置管理
- 流量分析和监控
- DNS查询和分析
- Wi-Fi信号强度检测
- SNMP管理和VLAN配置
- 主题切换（浅色/深色）
- 窗口状态记忆
- 快速工具访问
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
