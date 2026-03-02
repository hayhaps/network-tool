#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口UI模块
功能：主界面设计和交互逻辑
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QComboBox,
    QSpinBox, QGroupBox, QGridLayout, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QStatusBar,
    QSplitter, QFrame, QAction, QMenu, QMenuBar, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt, QThread, QSettings
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.connectivity import PingThread, TracerouteThread
from modules.port_scanner import PortScannerThread
from modules.speed_test import SpeedTestThread, LatencyTestThread
from modules.device_config import IPConfigThread, DNSFlushThread
from modules.traffic_monitor import TrafficMonitorThread, NetworkConnectionsThread
from modules.dns_query import DNSQueryThread, DNSResolveThread
from modules.wifi_tool import WifiScannerThread
from modules.snmp_manager import SNMPQueryThread, SNMPDeviceThread
from modules.vlan_config import VLANInfoThread
from modules.network_topology import NetworkTopology
from modules.network_diagnostic import BatchPingThread, NetworkDiagnosticThread
from modules.network_ai_assistant import NetworkAIAssistant
from ui.styles import LIGHT_THEME, DARK_THEME, ENGINEER_THEME, ButtonStyles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络故障排查工具 v1.2  By @大笑无声")
        
        # 加载设置
        self.settings = QSettings("NetworkTool", "NetworkDiagnosticTool")
        
        # 恢复窗口大小和位置
        self.restore_window_state()
        
        self.monitor_thread = None
        self.is_dark_theme = False
        self.current_theme = 'engineer'  # 默认使用工程师主题
        self.current_nav_button = None  # 当前选中的导航按钮
        
        self.init_ui()
        self.create_status_bar()
        self.create_menu_bar()
        
        # 应用保存的主题
        if self.settings.value("theme", "light") == "dark":
            self.toggle_theme()
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        export_action = QAction("导出结果", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        clear_action = QAction("清空历史", self)
        clear_action.triggered.connect(self.clear_history)
        file_menu.addAction(clear_action)
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menu_bar.addMenu("视图")
        
        theme_action = QAction("切换主题", self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # 工具菜单
        tools_menu = menu_bar.addMenu("工具")
        
        quick_scan_action = QAction("快速端口扫描", self)
        quick_scan_action.triggered.connect(self.quick_port_scan)
        tools_menu.addAction(quick_scan_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def restore_window_state(self):
        """恢复窗口状态"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.setGeometry(100, 100, 1200, 800)
    
    def save_window_state(self):
        """保存窗口状态"""
        self.settings.setValue("geometry", self.saveGeometry())
    
    def toggle_theme(self):
        """切换主题"""
        # 循环切换主题：工程师 -> 浅色 -> 深色 -> 工程师
        if self.current_theme == 'engineer':
            self.current_theme = 'light'
            self.setStyleSheet(LIGHT_THEME)
            self.settings.setValue("theme", "light")
        elif self.current_theme == 'light':
            self.current_theme = 'dark'
            self.setStyleSheet(DARK_THEME)
            self.settings.setValue("theme", "dark")
        else:  # dark
            self.current_theme = 'engineer'
            self.setStyleSheet(ENGINEER_THEME)
            self.settings.setValue("theme", "engineer")
        
        # 更新主题按钮文本
        for btn in self.nav_buttons:
            if btn.objectName() == "themeButton":
                if self.current_theme == 'engineer':
                    btn.setText("🎨 切换主题")
                elif self.current_theme == 'light':
                    btn.setText("🌙 切换主题")
                else:
                    btn.setText("🔧 切换主题")
    
    def export_results(self):
        """导出结果"""
        QMessageBox.information(self, "导出结果", "导出功能开发中...")
    
    def clear_history(self):
        """清空历史"""
        QMessageBox.information(self, "清空历史", "历史记录已清空")
    
    def quick_port_scan(self):
        """快速端口扫描"""
        # 切换到端口扫描标签并设置常用端口
        self.tabs.setCurrentIndex(2)  # 端口扫描标签
        self.start_port_spin.setValue(1)
        self.end_port_spin.setValue(1024)
    
    def show_about(self):
        """显示关于信息"""
        about_text = "网络故障排查工具 v1.1\n\n"
        about_text += "功能：\n"
        about_text += "- 网络连通性测试（ping、traceroute）\n"
        about_text += "- 端口扫描和服务检测\n"
        about_text += "- 网络速度测试（带宽、延迟）\n"
        about_text += "- 网络设备配置管理\n"
        about_text += "- 流量分析和监控\n"
        about_text += "- DNS查询和分析\n"
        about_text += "- Wi-Fi信号强度检测\n"
        about_text += "- SNMP管理和VLAN配置\n\n"
        about_text += "© 2026 网络故障排查工具"
        
        QMessageBox.about(self, "关于", about_text)
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 应用现代样式
        self.apply_modern_style()
        
        # 先创建状态栏
        self.create_status_bar()
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # 左侧功能模块导航栏
        self.nav_widget = QFrame()
        self.nav_widget.setObjectName("navFrame")
        self.nav_layout = QVBoxLayout()
        self.nav_layout.setSpacing(8)
        self.nav_layout.setContentsMargins(16, 16, 16, 16)
        self.nav_widget.setLayout(self.nav_layout)
        self.nav_widget.setMinimumWidth(200)
        self.nav_widget.setMaximumWidth(240)
        
        # 添加Logo和标题
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("🌐")
        logo_icon.setFont(QFont("Arial", 24))
        logo_icon.setAlignment(Qt.AlignCenter)
        
        logo_text = QLabel("网络工具箱")
        logo_text.setFont(QFont("Arial", 14, QFont.Bold))
        logo_text.setObjectName("titleLabel")
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.setAlignment(Qt.AlignCenter)
        self.nav_layout.addLayout(logo_layout)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e6ed; max-height: 1px;")
        self.nav_layout.addWidget(line)
        
        # 添加导航标题
        nav_title = QLabel("📋 功能模块")
        nav_title.setFont(QFont("Arial", 11, QFont.Bold))
        nav_title.setStyleSheet("color: #7f8c8d; padding: 8px 0;")
        self.nav_layout.addWidget(nav_title)
        
        # 创建导航按钮
        self.nav_buttons = []
        self.create_nav_buttons()
        
        # 添加垂直 spacer，使按钮靠上
        self.nav_layout.addStretch()
        
        # 添加主题切换按钮
        theme_btn = QPushButton("🌙 切换主题")
        theme_btn.setObjectName("themeButton")
        theme_btn.clicked.connect(self.toggle_theme)
        self.nav_layout.addWidget(theme_btn)
        
        # 右侧内容区域
        self.content_widget = QFrame()
        self.content_widget.setObjectName("contentFrame")
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(16)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_widget.setLayout(self.content_layout)
        
        # 创建内容显示区域
        self.content_stack = QWidget()
        self.content_stack_layout = QVBoxLayout()
        self.content_stack.setLayout(self.content_stack_layout)
        
        # 创建所有功能模块的内容页
        self.create_content_pages()
        
        # 将导航栏和内容区域添加到主布局
        main_layout.addWidget(self.nav_widget)
        main_layout.addWidget(self.content_widget, 1)  # 内容区域占据剩余空间
    
    def apply_modern_style(self):
        """应用现代化样式"""
        # 默认使用工程师主题
        self.current_theme = 'engineer'
        self.setStyleSheet(ENGINEER_THEME)
        self.is_dark_theme = False
    
    def create_nav_buttons(self):
        """创建导航按钮"""
        modules = [
            ("Ping测试", self.show_ping_page),
            ("路由追踪", self.show_traceroute_page),
            ("端口扫描", self.show_port_scanner_page),
            ("速度测试", self.show_speed_test_page),
            ("IP配置", self.show_ip_config_page),
            ("流量监控", self.show_traffic_monitor_page),
            ("DNS查询", self.show_dns_query_page),
            ("Wi-Fi扫描", self.show_wifi_scanner_page),
            ("网络拓扑", self.show_network_topology_page),
            ("子网计算", self.show_subnet_calculator_page),
            ("网络诊断", self.show_network_diagnostic_page),
            ("智能助手", self.show_ai_assistant_page),
            ("SNMP管理", self.show_snmp_page),
            ("VLAN配置", self.show_vlan_page),
            ("使用说明", self.show_help_page)
        ]
        
        # 模块图标映射（使用Unicode字符确保兼容性）
        module_icons = {
            "Ping测试": "●",
            "路由追踪": "→",
            "端口扫描": "◆",
            "速度测试": "⚡",
            "IP配置": "⚙",
            "流量监控": "◈",
            "DNS查询": "◎",
            "Wi-Fi扫描": "◉",
            "网络拓扑": "◊",
            "子网计算": "#",
            "网络诊断": "▣",
            "智能助手": "AI",
            "SNMP管理": "◐",
            "VLAN配置": "◑",
            "使用说明": "?"
        }
        
        for module_name, callback in modules:
            icon = module_icons.get(module_name, "•")
            button_text = f"[{icon}] {module_name}" if icon != "AI" else "[AI] 智能助手"
            button = QPushButton(button_text)
            button.setFont(QFont("Arial", 10))
            button.setMinimumHeight(44)
            button.setMaximumHeight(44)
            button.setCursor(Qt.PointingHandCursor)
            button.setProperty("selected", False)  # 添加选中属性
            button.clicked.connect(lambda checked=False, btn=button, cb=callback: self.on_nav_button_clicked(btn, cb))
            self.nav_buttons.append(button)
            self.nav_layout.addWidget(button)
    
    def on_nav_button_clicked(self, button, callback):
        """导航按钮点击处理"""
        # 取消之前选中的按钮
        if self.current_nav_button:
            self.current_nav_button.setProperty("selected", False)
            self.current_nav_button.style().unpolish(self.current_nav_button)
            self.current_nav_button.style().polish(self.current_nav_button)
        
        # 设置当前按钮为选中状态
        button.setProperty("selected", True)
        button.style().unpolish(button)
        button.style().polish(button)
        self.current_nav_button = button
        
        # 执行回调函数
        callback()
    
    def create_content_pages(self):
        """创建所有功能模块的内容页"""
        # 创建所有内容页
        self.ping_page = self.create_ping_content()
        self.traceroute_page = self.create_traceroute_content()
        self.port_scanner_page = self.create_port_scanner_content()
        self.speed_test_page = self.create_speed_test_content()
        self.ip_config_page = self.create_ip_config_content()
        self.traffic_monitor_page = self.create_traffic_monitor_content()
        self.dns_query_page = self.create_dns_query_content()
        self.wifi_scanner_page = self.create_wifi_scanner_content()
        self.network_topology_page = self.create_network_topology_content()
        self.subnet_calculator_page = self.create_subnet_calculator_content()
        self.network_diagnostic_page = self.create_network_diagnostic_content()
        self.ai_assistant_page = self.create_ai_assistant_content()
        self.snmp_page = self.create_snmp_content()
        self.vlan_page = self.create_vlan_content()
        self.help_page = self.create_help_content()
        
        # 初始显示Ping测试页面
        self.show_ping_page()
    
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def create_ping_content(self):
        """创建Ping测试内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("Ping测试")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("目标主机:"), 0, 0)
        self.ping_host_input = QLineEdit()
        self.ping_host_input.setPlaceholderText("输入IP地址或域名")
        input_layout.addWidget(self.ping_host_input, 0, 1)
        
        input_layout.addWidget(QLabel("次数:"), 0, 2)
        self.ping_count_spin = QSpinBox()
        self.ping_count_spin.setRange(1, 100)
        self.ping_count_spin.setValue(4)
        input_layout.addWidget(self.ping_count_spin, 0, 3)
        
        self.ping_button = QPushButton("开始Ping")
        self.ping_button.clicked.connect(self.start_ping)
        input_layout.addWidget(self.ping_button, 0, 4)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        self.ping_result = QTextEdit()
        # 使用跨平台兼容的等宽字体
        self.ping_result.setFont(QFont("Monaco", 10))
        self.ping_result.setReadOnly(True)
        layout.addWidget(self.ping_result)
        
        page.setLayout(layout)
        return page
    
    def show_ping_page(self):
        """显示Ping测试页面"""
        self.clear_content()
        self.content_layout.addWidget(self.ping_page)
        self.status_bar.showMessage("Ping测试模块")
    
    def create_traceroute_content(self):
        """创建路由追踪内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("路由追踪")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("目标主机:"), 0, 0)
        self.trace_host_input = QLineEdit()
        self.trace_host_input.setPlaceholderText("输入IP地址或域名")
        input_layout.addWidget(self.trace_host_input, 0, 1)
        
        input_layout.addWidget(QLabel("最大跳数:"), 0, 2)
        self.trace_hops_spin = QSpinBox()
        self.trace_hops_spin.setRange(1, 64)
        self.trace_hops_spin.setValue(30)
        input_layout.addWidget(self.trace_hops_spin, 0, 3)
        
        self.trace_button = QPushButton("开始追踪")
        self.trace_button.clicked.connect(self.start_traceroute)
        input_layout.addWidget(self.trace_button, 0, 4)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        self.trace_result = QTextEdit()
        self.trace_result.setFont(QFont("Monaco", 10))
        self.trace_result.setReadOnly(True)
        layout.addWidget(self.trace_result)
        
        page.setLayout(layout)
        return page
    
    def show_traceroute_page(self):
        """显示路由追踪页面"""
        self.clear_content()
        self.content_layout.addWidget(self.traceroute_page)
        self.status_bar.showMessage("路由追踪模块")
    
    def create_port_scanner_content(self):
        """创建端口扫描内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        quick_scan_group = QGroupBox("快速扫描")
        quick_scan_layout = QHBoxLayout()
        
        self.quick_scan_button = QPushButton("常用端口扫描")
        self.quick_scan_button.clicked.connect(self.quick_scan_ports)
        quick_scan_layout.addWidget(self.quick_scan_button)
        
        self.web_scan_button = QPushButton("Web服务端口")
        self.web_scan_button.clicked.connect(lambda: self.start_quick_scan([80, 443, 8080, 8443, 8888, 9090]))
        quick_scan_layout.addWidget(self.web_scan_button)
        
        self.database_scan_button = QPushButton("数据库端口")
        self.database_scan_button.clicked.connect(lambda: self.start_quick_scan([1433, 1521, 3306, 5432, 6379, 27017]))
        quick_scan_layout.addWidget(self.database_scan_button)
        
        self.mail_scan_button = QPushButton("邮件服务端口")
        self.mail_scan_button.clicked.connect(lambda: self.start_quick_scan([25, 110, 143, 465, 587, 993, 995]))
        quick_scan_layout.addWidget(self.mail_scan_button)
        
        quick_scan_group.setLayout(quick_scan_layout)
        layout.addWidget(quick_scan_group)
        
        input_group = QGroupBox("自定义端口扫描")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("目标主机:"), 0, 0)
        self.scan_host_input = QLineEdit()
        self.scan_host_input.setPlaceholderText("输入IP地址或域名")
        input_layout.addWidget(self.scan_host_input, 0, 1)
        
        input_layout.addWidget(QLabel("起始端口:"), 0, 2)
        self.start_port_spin = QSpinBox()
        self.start_port_spin.setRange(1, 65535)
        self.start_port_spin.setValue(1)
        input_layout.addWidget(self.start_port_spin, 0, 3)
        
        input_layout.addWidget(QLabel("结束端口:"), 0, 4)
        self.end_port_spin = QSpinBox()
        self.end_port_spin.setRange(1, 65535)
        self.end_port_spin.setValue(1024)
        input_layout.addWidget(self.end_port_spin, 0, 5)
        
        self.scan_button = QPushButton("开始扫描")
        self.scan_button.clicked.connect(self.start_port_scan)
        input_layout.addWidget(self.scan_button, 0, 6)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        progress_layout = QHBoxLayout()
        self.scan_progress = QProgressBar()
        progress_layout.addWidget(self.scan_progress)
        layout.addLayout(progress_layout)
        
        self.port_table = QTableWidget()
        self.port_table.setColumnCount(4)
        self.port_table.setHorizontalHeaderLabels(["端口", "服务", "协议", "状态"])
        self.port_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.port_table)
        
        page.setLayout(layout)
        return page
    
    def show_port_scanner_page(self):
        """显示端口扫描页面"""
        self.clear_content()
        self.content_layout.addWidget(self.port_scanner_page)
        self.status_bar.showMessage("端口扫描模块")
    
    def create_speed_test_content(self):
        """创建速度测试内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("速度测试")
        input_layout = QHBoxLayout()
        
        self.speed_test_button = QPushButton("开始速度测试")
        self.speed_test_button.clicked.connect(self.start_speed_test)
        input_layout.addWidget(self.speed_test_button)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        result_group = QGroupBox("测试结果")
        result_layout = QGridLayout()
        
        result_layout.addWidget(QLabel("下载速度:"), 0, 0)
        self.download_speed_label = QLabel("0 Mbps")
        self.download_speed_label.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout.addWidget(self.download_speed_label, 0, 1)
        
        result_layout.addWidget(QLabel("上传速度:"), 1, 0)
        self.upload_speed_label = QLabel("0 Mbps")
        self.upload_speed_label.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout.addWidget(self.upload_speed_label, 1, 1)
        
        result_layout.addWidget(QLabel("延迟:"), 2, 0)
        self.ping_label = QLabel("0 ms")
        self.ping_label.setFont(QFont("Arial", 12, QFont.Bold))
        result_layout.addWidget(self.ping_label, 2, 1)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        self.speed_log = QTextEdit()
        self.speed_log.setFont(QFont("Monaco", 10))
        self.speed_log.setReadOnly(True)
        layout.addWidget(self.speed_log)
        
        page.setLayout(layout)
        return page
    
    def show_speed_test_page(self):
        """显示速度测试页面"""
        self.clear_content()
        self.content_layout.addWidget(self.speed_test_page)
        self.status_bar.showMessage("速度测试模块")
    
    def create_ip_config_content(self):
        """创建IP配置内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.ip_config_button = QPushButton("查看IP配置")
        self.ip_config_button.clicked.connect(self.get_ip_config)
        button_layout.addWidget(self.ip_config_button)
        
        self.flush_dns_button = QPushButton("刷新DNS缓存")
        self.flush_dns_button.clicked.connect(self.flush_dns)
        button_layout.addWidget(self.flush_dns_button)
        
        layout.addLayout(button_layout)
        
        self.ip_config_result = QTextEdit()
        self.ip_config_result.setFont(QFont("Monaco", 10))
        self.ip_config_result.setReadOnly(True)
        layout.addWidget(self.ip_config_result)
        
        page.setLayout(layout)
        return page
    
    def show_ip_config_page(self):
        """显示IP配置页面"""
        self.clear_content()
        self.content_layout.addWidget(self.ip_config_page)
        self.status_bar.showMessage("IP配置模块")
    
    def create_traffic_monitor_content(self):
        """创建流量监控内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.start_monitor_button = QPushButton("开始监控")
        self.start_monitor_button.clicked.connect(self.start_traffic_monitor)
        button_layout.addWidget(self.start_monitor_button)
        
        self.stop_monitor_button = QPushButton("停止监控")
        self.stop_monitor_button.clicked.connect(self.stop_traffic_monitor)
        self.stop_monitor_button.setEnabled(False)
        button_layout.addWidget(self.stop_monitor_button)
        
        self.get_connections_button = QPushButton("查看网络连接")
        self.get_connections_button.clicked.connect(self.get_network_connections)
        button_layout.addWidget(self.get_connections_button)
        
        layout.addLayout(button_layout)
        
        stats_group = QGroupBox("流量统计")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("上传速度:"), 0, 0)
        self.upload_speed_value = QLabel("0 B/s")
        stats_layout.addWidget(self.upload_speed_value, 0, 1)
        
        stats_layout.addWidget(QLabel("下载速度:"), 0, 2)
        self.download_speed_value = QLabel("0 B/s")
        stats_layout.addWidget(self.download_speed_value, 0, 3)
        
        stats_layout.addWidget(QLabel("总上传:"), 1, 0)
        self.total_upload_value = QLabel("0 B")
        stats_layout.addWidget(self.total_upload_value, 1, 1)
        
        stats_layout.addWidget(QLabel("总下载:"), 1, 2)
        self.total_download_value = QLabel("0 B")
        stats_layout.addWidget(self.total_download_value, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.connection_table = QTableWidget()
        self.connection_table.setColumnCount(6)
        self.connection_table.setHorizontalHeaderLabels([
            "协议", "本地地址", "远程地址", "状态", "PID", "进程名"
        ])
        self.connection_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.connection_table)
        
        page.setLayout(layout)
        return page
    
    def show_traffic_monitor_page(self):
        """显示流量监控页面"""
        self.clear_content()
        self.content_layout.addWidget(self.traffic_monitor_page)
        self.status_bar.showMessage("流量监控模块")
    
    def create_dns_query_content(self):
        """创建DNS查询内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("DNS查询")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("域名/IP:"), 0, 0)
        self.dns_domain_input = QLineEdit()
        self.dns_domain_input.setPlaceholderText("输入域名或IP地址")
        input_layout.addWidget(self.dns_domain_input, 0, 1)
        
        input_layout.addWidget(QLabel("记录类型:"), 0, 2)
        self.dns_type_combo = QComboBox()
        self.dns_type_combo.addItems(['AUTO', 'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR'])
        self.dns_type_combo.setItemText(0, '自动识别')
        input_layout.addWidget(self.dns_type_combo, 0, 3)
        
        self.dns_query_button = QPushButton("查询")
        self.dns_query_button.clicked.connect(self.start_dns_query)
        input_layout.addWidget(self.dns_query_button, 0, 4)
        
        self.dns_resolve_button = QPushButton("解析域名")
        self.dns_resolve_button.clicked.connect(self.start_dns_resolve)
        input_layout.addWidget(self.dns_resolve_button, 0, 5)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        self.dns_result = QTextEdit()
        self.dns_result.setFont(QFont("Monaco", 10))
        self.dns_result.setReadOnly(True)
        layout.addWidget(self.dns_result)
        
        page.setLayout(layout)
        return page
    
    def show_dns_query_page(self):
        """显示DNS查询页面"""
        self.clear_content()
        self.content_layout.addWidget(self.dns_query_page)
        self.status_bar.showMessage("DNS查询模块")
    
    def create_wifi_scanner_content(self):
        """创建Wi-Fi扫描内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.scan_wifi_button = QPushButton("扫描Wi-Fi网络")
        self.scan_wifi_button.clicked.connect(self.scan_wifi)
        button_layout.addWidget(self.scan_wifi_button)
        
        layout.addLayout(button_layout)
        
        self.wifi_table = QTableWidget()
        self.wifi_table.setColumnCount(5)
        self.wifi_table.setHorizontalHeaderLabels([
            "SSID", "BSSID", "信号强度", "信道", "安全类型"
        ])
        self.wifi_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.wifi_table)
        
        page.setLayout(layout)
        return page
    
    def show_wifi_scanner_page(self):
        """显示Wi-Fi扫描页面"""
        self.clear_content()
        self.content_layout.addWidget(self.wifi_scanner_page)
        self.status_bar.showMessage("Wi-Fi扫描模块")
    
    def create_snmp_content(self):
        """创建SNMP管理内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("SNMP查询")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("设备IP:"), 0, 0)
        self.snmp_host_input = QLineEdit()
        self.snmp_host_input.setPlaceholderText("输入设备IP地址")
        input_layout.addWidget(self.snmp_host_input, 0, 1)
        
        input_layout.addWidget(QLabel("Community:"), 0, 2)
        self.snmp_community_input = QLineEdit()
        self.snmp_community_input.setText("public")
        input_layout.addWidget(self.snmp_community_input, 0, 3)
        
        input_layout.addWidget(QLabel("OID:"), 1, 0)
        self.snmp_oid_input = QLineEdit()
        self.snmp_oid_input.setText("1.3.6.1.2.1.1.1.0")
        input_layout.addWidget(self.snmp_oid_input, 1, 1)
        
        self.snmp_query_button = QPushButton("查询")
        self.snmp_query_button.clicked.connect(self.start_snmp_query)
        input_layout.addWidget(self.snmp_query_button, 1, 2)
        
        self.snmp_device_button = QPushButton("获取设备信息")
        self.snmp_device_button.clicked.connect(self.get_snmp_device_info)
        input_layout.addWidget(self.snmp_device_button, 1, 3)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        self.snmp_result = QTextEdit()
        self.snmp_result.setFont(QFont("Monaco", 10))
        self.snmp_result.setReadOnly(True)
        layout.addWidget(self.snmp_result)
        
        page.setLayout(layout)
        return page
    
    def show_snmp_page(self):
        """显示SNMP管理页面"""
        self.clear_content()
        self.content_layout.addWidget(self.snmp_page)
        self.status_bar.showMessage("SNMP管理模块")
    
    def create_vlan_content(self):
        """创建VLAN配置内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.get_vlan_button = QPushButton("查看VLAN信息")
        self.get_vlan_button.clicked.connect(self.get_vlan_info)
        button_layout.addWidget(self.get_vlan_button)
        
        layout.addLayout(button_layout)
        
        self.vlan_table = QTableWidget()
        self.vlan_table.setColumnCount(4)
        self.vlan_table.setHorizontalHeaderLabels([
            "名称", "VLAN ID", "接口", "状态"
        ])
        self.vlan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.vlan_table)
        
        page.setLayout(layout)
        return page
    
    def show_vlan_page(self):
        """显示VLAN配置页面"""
        self.clear_content()
        self.content_layout.addWidget(self.vlan_page)
        self.status_bar.showMessage("VLAN配置模块")
    
    def create_help_content(self):
        """创建使用说明内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("使用说明")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)
        
        # 软件信息
        info_group = QGroupBox("软件信息")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setHtml("""
        <h3>网络故障排查工具 v1.2</h3>
        <p><b>制作人：</b>@大笑无声</p>
        <p><b>功能：</b>提供一站式网络故障排查和网络工具服务</p>
        <p><b>特点：</b>简洁易用、功能全面、支持本地和云端AI助手</p>
        """)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 功能模块说明
        modules_group = QGroupBox("功能模块说明")
        modules_layout = QVBoxLayout()
        
        modules_text = QTextEdit()
        modules_text.setReadOnly(True)
        modules_text.setHtml("""
        <h3>网络诊断工具</h3>
        <ul>
        <li><b>Ping测试</b> - 测试网络连通性和延迟</li>
        <li><b>路由追踪</b> - 追踪数据包传输路径</li>
        <li><b>端口扫描</b> - 检测目标主机开放端口</li>
        <li><b>速度测试</b> - 测试网络带宽和速度</li>
        <li><b>IP配置</b> - 查看和刷新网络配置</li>
        <li><b>流量监控</b> - 实时监控网络流量</li>
        </ul>
        
        <h3>网络查询工具</h3>
        <ul>
        <li><b>DNS查询</b> - 查询域名DNS记录</li>
        <li><b>Wi-Fi扫描</b> - 扫描附近无线网络</li>
        <li><b>网络拓扑</b> - 生成网络结构图</li>
        <li><b>子网计算</b> - 计算子网信息</li>
        <li><b>网络诊断</b> - 全面网络状态检测</li>
        </ul>
        
        <h3>高级功能</h3>
        <ul>
        <li><b>智能助手</b> - AI网络故障诊断助手（支持豆包大模型）</li>
        <li><b>SNMP管理</b> - 网络设备SNMP管理</li>
        <li><b>VLAN配置</b> - 虚拟局域网配置查看</li>
        </ul>
        """)
        modules_layout.addWidget(modules_text)
        modules_group.setLayout(modules_layout)
        layout.addWidget(modules_group)
        
        # 快速入门
        quick_start_group = QGroupBox("快速入门")
        quick_start_layout = QVBoxLayout()
        
        quick_start_text = QTextEdit()
        quick_start_text.setReadOnly(True)
        quick_start_text.setMaximumHeight(200)
        quick_start_text.setHtml("""
        <h3>1. 基本网络诊断</h3>
        <p>点击左侧菜单的"Ping测试"，输入目标IP或域名（如 8.8.8.8 或 baidu.com），点击"开始Ping"即可测试网络连通性。</p>
        
        <h3>2. 测试网络速度</h3>
        <p>点击"速度测试"，工具会自动选择最优服务器进行测试，显示下载速度、上传速度和延迟。</p>
        
        <h3>3. 使用智能助手</h3>
        <p>点击"智能助手"，可以直接输入网络问题（如"网络很慢怎么办"），AI会提供解决方案。</p>
        <p>如需使用云端AI，请在配置中输入豆包API Key。</p>
        
        <h3>4. 生成网络拓扑</h3>
        <p>点击"网络拓扑"，输入目标IP，设置跳数，点击生成即可看到网络结构图。</p>
        """)
        quick_start_layout.addWidget(quick_start_text)
        quick_start_group.setLayout(quick_start_layout)
        layout.addWidget(quick_start_group)
        
        # 常见问题
        faq_group = QGroupBox("常见问题")
        faq_layout = QVBoxLayout()
        
        faq_text = QTextEdit()
        faq_text.setReadOnly(True)
        faq_text.setMaximumHeight(180)
        faq_text.setHtml("""
        <p><b>Q: 为什么某些功能需要管理员权限？</b><br>
        A: 部分网络操作（如刷新DNS缓存）需要系统权限，请以管理员身份运行程序。</p>
        
        <p><b>Q: 如何获取豆包API Key？</b><br>
        A: 访问火山引擎控制台 (console.volces.com)，注册账号后在模型推理服务中创建API Key。</p>
        
        <p><b>Q: 支持哪些操作系统？</b><br>
        A: 支持 Windows、macOS 和 Linux 系统。</p>
        
        <p><b>Q: 如何切换主题？</b><br>
        A: 点击左下角的"切换主题"按钮可在浅色和深色主题间切换。</p>
        """)
        faq_layout.addWidget(faq_text)
        faq_group.setLayout(faq_layout)
        layout.addWidget(faq_group)
        
        # 联系方式
        contact_group = QGroupBox("关于")
        contact_layout = QVBoxLayout()
        
        contact_label = QLabel("本软件由 @大笑无声 开发制作\n如有问题或建议，欢迎反馈！")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_layout.addWidget(contact_label)
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        page.setLayout(layout)
        return page
    
    def show_help_page(self):
        """显示使用说明页面"""
        self.clear_content()
        self.content_layout.addWidget(self.help_page)
        self.status_bar.showMessage("使用说明")
    
    def clear_content(self):
        """清空内容区域"""
        while self.content_layout.count() > 0:
            widget = self.content_layout.takeAt(0).widget()
            if widget:
                widget.hide()
                widget.deleteLater()
    
    def start_ping(self):
        host = self.ping_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        self.ping_result.clear()
        self.ping_result.append(f"正在Ping {host}...\n")
        self.status_bar.showMessage(f"正在Ping {host}...")
        
        self.ping_thread = PingThread(host, self.ping_count_spin.value())
        self.ping_thread.result_signal.connect(self.update_ping_result)
        self.ping_thread.finished_signal.connect(self.ping_finished)
        self.ping_thread.start()
    
    def update_ping_result(self, result):
        self.ping_result.append(result)
    
    def ping_finished(self, results):
        self.status_bar.showMessage("Ping完成")
    
    def start_traceroute(self):
        host = self.trace_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        self.trace_result.clear()
        self.trace_result.append(f"正在追踪到 {host} 的路由...\n")
        self.status_bar.showMessage(f"正在追踪到 {host} 的路由...")
        
        self.trace_thread = TracerouteThread(host, self.trace_hops_spin.value())
        self.trace_thread.result_signal.connect(self.update_trace_result)
        self.trace_thread.finished_signal.connect(self.trace_finished)
        self.trace_thread.start()
    
    def update_trace_result(self, result):
        self.trace_result.append(result)
    
    def trace_finished(self, results):
        self.status_bar.showMessage("路由追踪完成")
    
    def start_port_scan(self):
        host = self.scan_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        start_port = self.start_port_spin.value()
        end_port = self.end_port_spin.value()
        
        if start_port > end_port:
            QMessageBox.warning(self, "警告", "起始端口不能大于结束端口")
            return
        
        self.port_table.setRowCount(0)
        self.scan_progress.setValue(0)
        self.status_bar.showMessage(f"正在扫描 {host} 的端口 {start_port}-{end_port}...")
        
        self.scan_thread = PortScannerThread(host, start_port, end_port)
        self.scan_thread.progress_signal.connect(self.update_scan_progress)
        self.scan_thread.result_signal.connect(self.update_port_table)
        self.scan_thread.finished_signal.connect(self.scan_finished)
        self.scan_thread.start()
    
    def update_scan_progress(self, progress):
        self.scan_progress.setValue(progress)
    
    def update_port_table(self, port_info):
        row = self.port_table.rowCount()
        self.port_table.insertRow(row)
        self.port_table.setItem(row, 0, QTableWidgetItem(str(port_info['port'])))
        self.port_table.setItem(row, 1, QTableWidgetItem(port_info['service']))
        self.port_table.setItem(row, 2, QTableWidgetItem(port_info.get('protocol', 'Unknown')))
        self.port_table.setItem(row, 3, QTableWidgetItem(port_info['status']))
    
    def scan_finished(self, results):
        self.status_bar.showMessage(f"扫描完成，发现 {len(results)} 个开放端口")
    
    def quick_scan_ports(self):
        host = self.scan_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 161, 389, 443, 445, 465, 587, 636, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]
        
        self.port_table.setRowCount(0)
        self.scan_progress.setValue(0)
        self.status_bar.showMessage(f"正在快速扫描 {host} 的常用端口...")
        
        self.scan_thread = PortScannerThread(host, 1, 65535, max_threads=200)
        self.scan_thread.common_ports = common_ports
        self.scan_thread.progress_signal.connect(self.update_scan_progress)
        self.scan_thread.result_signal.connect(self.update_port_table)
        self.scan_thread.finished_signal.connect(self.scan_finished)
        self.scan_thread.start()
    
    def start_quick_scan(self, ports):
        host = self.scan_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入目标主机")
            return
        
        self.port_table.setRowCount(0)
        self.scan_progress.setValue(0)
        self.status_bar.showMessage(f"正在快速扫描 {host} 的指定端口...")
        
        self.scan_thread = PortScannerThread(host, 1, 65535, max_threads=50)
        self.scan_thread.common_ports = ports
        self.scan_thread.progress_signal.connect(self.update_scan_progress)
        self.scan_thread.result_signal.connect(self.update_port_table)
        self.scan_thread.finished_signal.connect(self.scan_finished)
        self.scan_thread.start()
    
    def start_speed_test(self):
        self.speed_log.clear()
        self.speed_log.append("开始速度测试...")
        self.status_bar.showMessage("正在进行速度测试...")
        self.speed_test_button.setEnabled(False)
        
        self.speed_thread = SpeedTestThread()
        self.speed_thread.progress_signal.connect(self.update_speed_log)
        self.speed_thread.result_signal.connect(self.update_speed_result)
        self.speed_thread.finished_signal.connect(self.speed_test_finished)
        self.speed_thread.start()
    
    def update_speed_log(self, message):
        self.speed_log.append(message)
    
    def update_speed_result(self, result):
        self.download_speed_label.setText(f"{result['download']:.2f} Mbps")
        self.upload_speed_label.setText(f"{result['upload']:.2f} Mbps")
        self.ping_label.setText(f"{result['ping']:.2f} ms")
    
    def speed_test_finished(self):
        self.speed_test_button.setEnabled(True)
        self.status_bar.showMessage("速度测试完成")
    
    def get_ip_config(self):
        self.ip_config_result.clear()
        self.ip_config_result.append("正在获取IP配置...\n")
        self.status_bar.showMessage("正在获取IP配置...")
        
        self.ip_config_thread = IPConfigThread()
        self.ip_config_thread.result_signal.connect(self.update_ip_config)
        self.ip_config_thread.finished_signal.connect(self.ip_config_finished)
        self.ip_config_thread.start()
    
    def update_ip_config(self, result):
        self.ip_config_result.append(result)
    
    def ip_config_finished(self, config):
        self.status_bar.showMessage("IP配置获取完成")
    
    def flush_dns(self):
        self.ip_config_result.clear()
        self.ip_config_result.append("正在刷新DNS缓存...\n")
        self.status_bar.showMessage("正在刷新DNS缓存...")
        
        self.dns_flush_thread = DNSFlushThread()
        self.dns_flush_thread.result_signal.connect(self.update_dns_flush)
        self.dns_flush_thread.finished_signal.connect(self.dns_flush_finished)
        self.dns_flush_thread.start()
    
    def update_dns_flush(self, result):
        self.ip_config_result.append(result)
    
    def dns_flush_finished(self):
        self.status_bar.showMessage("DNS缓存刷新完成")
    
    def start_traffic_monitor(self):
        self.start_monitor_button.setEnabled(False)
        self.stop_monitor_button.setEnabled(True)
        self.status_bar.showMessage("流量监控已启动")
        
        self.monitor_thread = TrafficMonitorThread()
        self.monitor_thread.update_signal.connect(self.update_traffic_stats)
        self.monitor_thread.start()
    
    def update_traffic_stats(self, stats):
        from utils.network_utils import format_bytes, format_speed
        
        self.upload_speed_value.setText(format_speed(stats['upload_speed']))
        self.download_speed_value.setText(format_speed(stats['download_speed']))
        self.total_upload_value.setText(format_bytes(stats['total_sent']))
        self.total_download_value.setText(format_bytes(stats['total_recv']))
    
    def stop_traffic_monitor(self):
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread = None
        
        self.start_monitor_button.setEnabled(True)
        self.stop_monitor_button.setEnabled(False)
        self.status_bar.showMessage("流量监控已停止")
    
    def get_network_connections(self):
        self.connection_table.setRowCount(0)
        self.status_bar.showMessage("正在获取网络连接...")
        
        self.connections_thread = NetworkConnectionsThread()
        self.connections_thread.result_signal.connect(self.update_connections_table)
        self.connections_thread.finished_signal.connect(self.connections_finished)
        self.connections_thread.start()
    
    def update_connections_table(self, connections):
        for conn in connections:
            row = self.connection_table.rowCount()
            self.connection_table.insertRow(row)
            self.connection_table.setItem(row, 0, QTableWidgetItem(conn['type']))
            self.connection_table.setItem(row, 1, QTableWidgetItem(conn['local_addr']))
            self.connection_table.setItem(row, 2, QTableWidgetItem(conn['remote_addr']))
            self.connection_table.setItem(row, 3, QTableWidgetItem(conn['status']))
            self.connection_table.setItem(row, 4, QTableWidgetItem(str(conn['pid'])))
            self.connection_table.setItem(row, 5, QTableWidgetItem(conn['process_name']))
    
    def connections_finished(self):
        self.status_bar.showMessage("网络连接获取完成")
    
    def start_dns_query(self):
        input_str = self.dns_domain_input.text()
        if not input_str:
            QMessageBox.warning(self, "警告", "请输入域名或IP地址")
            return
        
        record_type = self.dns_type_combo.currentText()
        self.dns_result.clear()
        self.dns_result.append(f"正在查询 {input_str} 的 {record_type} 记录...\n")
        self.status_bar.showMessage(f"正在查询 {input_str} 的 {record_type} 记录...")
        
        self.dns_query_thread = DNSQueryThread(input_str, record_type)
        self.dns_query_thread.result_signal.connect(self.update_dns_query_result)
        self.dns_query_thread.finished_signal.connect(self.dns_query_finished)
        self.dns_query_thread.start()
    
    def update_dns_query_result(self, result):
        if result['error']:
            self.dns_result.append(f"错误: {result['error']}")
        else:
            self.dns_result.append(f"查询对象: {result['input']}")
            self.dns_result.append(f"记录类型: {result['record_type']}")
            self.dns_result.append(f"查询结果:")
            
            if result['record_type'] == 'PTR':
                for record in result['records']:
                    self.dns_result.append(f"  域名: {record}")
            elif result['record_type'] == 'MX':
                for record in result['records']:
                    self.dns_result.append(f"  优先级: {record['preference']}, 服务器: {record['exchange']}")
            elif result['record_type'] == 'SOA':
                for record in result['records']:
                    self.dns_result.append(f"  主域名服务器: {record['mname']}")
                    self.dns_result.append(f"  管理员邮箱: {record['rname']}")
                    self.dns_result.append(f"  序列号: {record['serial']}")
                    self.dns_result.append(f"  刷新时间: {record['refresh']}")
                    self.dns_result.append(f"  重试时间: {record['retry']}")
                    self.dns_result.append(f"  过期时间: {record['expire']}")
                    self.dns_result.append(f"  最小TTL: {record['minimum']}")
            else:
                for record in result['records']:
                    self.dns_result.append(f"  {record}")
    
    def dns_query_finished(self):
        self.status_bar.showMessage("DNS查询完成")
    
    def start_dns_resolve(self):
        input_str = self.dns_domain_input.text()
        if not input_str:
            QMessageBox.warning(self, "警告", "请输入域名或IP地址")
            return
        
        self.dns_result.clear()
        self.dns_result.append(f"正在解析 {input_str}...\n")
        self.status_bar.showMessage(f"正在解析 {input_str}...")
        
        self.dns_resolve_thread = DNSResolveThread(input_str)
        self.dns_resolve_thread.result_signal.connect(self.update_dns_resolve_result)
        self.dns_resolve_thread.finished_signal.connect(self.dns_resolve_finished)
        self.dns_resolve_thread.start()
    
    def update_dns_resolve_result(self, result):
        if result['error']:
            self.dns_result.append(f"错误: {result['error']}")
        else:
            self.dns_result.append(f"查询对象: {result['input']}")
            self.dns_result.append(f"主机名/域名: {result['hostname']}")
            if result['ipv4']:
                self.dns_result.append("IPv4地址:")
                for ip in result['ipv4']:
                    self.dns_result.append(f"  {ip}")
            if result['ipv6']:
                self.dns_result.append("IPv6地址:")
                for ip in result['ipv6']:
                    self.dns_result.append(f"  {ip}")
    
    def dns_resolve_finished(self):
        self.status_bar.showMessage("域名解析完成")
    
    def scan_wifi(self):
        self.wifi_table.setRowCount(0)
        self.status_bar.showMessage("正在扫描Wi-Fi网络...")
        
        self.wifi_scan_thread = WifiScannerThread()
        self.wifi_scan_thread.result_signal.connect(self.update_wifi_table)
        self.wifi_scan_thread.finished_signal.connect(self.wifi_scan_finished)
        self.wifi_scan_thread.start()
    
    def update_wifi_table(self, networks):
        if not networks:
            # 没有发现网络
            row = self.wifi_table.rowCount()
            self.wifi_table.insertRow(row)
            self.wifi_table.setItem(row, 0, QTableWidgetItem('无可用WiFi网络'))
            for i in range(1, 5):
                self.wifi_table.setItem(row, i, QTableWidgetItem('N/A'))
            return
        
        # 检查是否有错误信息
        if len(networks) == 1 and 'error' in networks[0]:
            error_message = networks[0]['error']
            row = self.wifi_table.rowCount()
            self.wifi_table.insertRow(row)
            self.wifi_table.setItem(row, 0, QTableWidgetItem('错误'))
            self.wifi_table.setItem(row, 1, QTableWidgetItem(error_message))
            for i in range(2, 5):
                self.wifi_table.setItem(row, i, QTableWidgetItem('N/A'))
            return
        
        # 正常显示网络列表
        for network in networks:
            row = self.wifi_table.rowCount()
            self.wifi_table.insertRow(row)
            self.wifi_table.setItem(row, 0, QTableWidgetItem(network.get('ssid', 'Unknown')))
            self.wifi_table.setItem(row, 1, QTableWidgetItem(network.get('bssid', 'Unknown')))
            self.wifi_table.setItem(row, 2, QTableWidgetItem(network.get('signal', 'Unknown')))
            self.wifi_table.setItem(row, 3, QTableWidgetItem(network.get('channel', 'Unknown')))
            self.wifi_table.setItem(row, 4, QTableWidgetItem(network.get('security', 'Unknown')))
    
    def wifi_scan_finished(self):
        self.status_bar.showMessage("Wi-Fi扫描完成")
    
    def start_snmp_query(self):
        host = self.snmp_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入设备IP地址")
            return
        
        community = self.snmp_community_input.text()
        oid = self.snmp_oid_input.text()
        
        self.snmp_result.clear()
        self.snmp_result.append(f"正在查询 {host} 的 {oid}...\n")
        self.status_bar.showMessage(f"正在查询 {host}...")
        
        self.snmp_query_thread = SNMPQueryThread(host, community, oid)
        self.snmp_query_thread.result_signal.connect(self.update_snmp_result)
        self.snmp_query_thread.finished_signal.connect(self.snmp_query_finished)
        self.snmp_query_thread.start()
    
    def update_snmp_result(self, result):
        if result['error']:
            self.snmp_result.append(f"错误: {result['error']}")
        else:
            self.snmp_result.append(f"主机: {result['host']}")
            self.snmp_result.append(f"OID: {result['oid']}")
            self.snmp_result.append(f"值: {result['value']}")
    
    def snmp_query_finished(self):
        self.status_bar.showMessage("SNMP查询完成")
    
    def get_snmp_device_info(self):
        host = self.snmp_host_input.text()
        if not host:
            QMessageBox.warning(self, "警告", "请输入设备IP地址")
            return
        
        community = self.snmp_community_input.text()
        
        self.snmp_result.clear()
        self.snmp_result.append(f"正在获取 {host} 的设备信息...\n")
        self.status_bar.showMessage(f"正在获取设备信息...")
        
        self.snmp_device_thread = SNMPDeviceThread(host, community)
        self.snmp_device_thread.result_signal.connect(self.update_snmp_device_result)
        self.snmp_device_thread.finished_signal.connect(self.snmp_device_finished)
        self.snmp_device_thread.start()
    
    def update_snmp_device_result(self, result):
        if result.get('error'):
            self.snmp_result.append(f"错误: {result['error']}")
        else:
            self.snmp_result.append(f"主机: {result['host']}")
            self.snmp_result.append(f"系统描述: {result.get('sysDescr', 'N/A')}")
            self.snmp_result.append(f"系统名称: {result.get('sysName', 'N/A')}")
            self.snmp_result.append(f"系统位置: {result.get('sysLocation', 'N/A')}")
            self.snmp_result.append(f"系统联系人: {result.get('sysContact', 'N/A')}")
            self.snmp_result.append(f"运行时间: {result.get('sysUpTime', 'N/A')}")
    
    def snmp_device_finished(self):
        self.status_bar.showMessage("设备信息获取完成")
    
    def get_vlan_info(self):
        self.vlan_table.setRowCount(0)
        self.status_bar.showMessage("正在获取VLAN信息...")
        
        self.vlan_thread = VLANInfoThread()
        self.vlan_thread.result_signal.connect(self.update_vlan_table)
        self.vlan_thread.finished_signal.connect(self.vlan_finished)
        self.vlan_thread.start()
    
    def update_vlan_table(self, vlans):
        for vlan in vlans:
            row = self.vlan_table.rowCount()
            self.vlan_table.insertRow(row)
            self.vlan_table.setItem(row, 0, QTableWidgetItem(vlan.get('name', 'Unknown')))
            self.vlan_table.setItem(row, 1, QTableWidgetItem(str(vlan.get('vlan_id', 'N/A'))))
            self.vlan_table.setItem(row, 2, QTableWidgetItem(vlan.get('interface', 'Unknown')))
            self.vlan_table.setItem(row, 3, QTableWidgetItem(vlan.get('status', 'Unknown')))
    
    def vlan_finished(self):
        self.status_bar.showMessage("VLAN信息获取完成")
    
    def create_network_topology_content(self):
        """创建网络拓扑图内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("网络拓扑图")
        input_layout = QHBoxLayout()
        
        self.topology_target_ip = QLineEdit("8.8.8.8")
        self.topology_target_ip.setPlaceholderText("输入目标IP地址")
        input_layout.addWidget(QLabel("目标IP:"))
        input_layout.addWidget(self.topology_target_ip)
        
        self.topology_hops = QSpinBox()
        self.topology_hops.setRange(1, 5)
        self.topology_hops.setValue(3)
        input_layout.addWidget(QLabel("最大跳数:"))
        input_layout.addWidget(self.topology_hops)
        
        self.generate_topology_button = QPushButton("生成拓扑图")
        ButtonStyles.primary(self.generate_topology_button)
        self.generate_topology_button.clicked.connect(self.generate_network_topology)
        input_layout.addWidget(self.generate_topology_button)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 创建分割器，左侧显示文本信息，右侧显示图片
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：拓扑信息文本
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        self.topology_result = QTextEdit()
        self.topology_result.setReadOnly(True)
        info_layout.addWidget(self.topology_result)
        info_widget.setLayout(info_layout)
        splitter.addWidget(info_widget)
        
        # 右侧：拓扑图片显示
        image_widget = QWidget()
        image_layout = QVBoxLayout()
        
        # 图片标签
        self.topology_image_label = QLabel('点击"生成拓扑图"按钮生成网络拓扑图')
        self.topology_image_label.setAlignment(Qt.AlignCenter)
        self.topology_image_label.setMinimumSize(400, 300)
        self.topology_image_label.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #ccc;")
        
        # 添加滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.topology_image_label)
        
        image_layout.addWidget(scroll_area)
        image_widget.setLayout(image_layout)
        splitter.addWidget(image_widget)
        
        # 设置分割比例
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        page.setLayout(layout)
        return page
    
    def show_network_topology_page(self):
        """显示网络拓扑图页面"""
        self.clear_content()
        self.content_layout.addWidget(self.network_topology_page)
    
    def generate_network_topology(self):
        """生成网络拓扑图"""
        target_ip = self.topology_target_ip.text().strip()
        if not target_ip:
            QMessageBox.warning(self, "警告", "请输入目标IP地址")
            return
        
        max_hops = self.topology_hops.value()
        
        self.topology_result.clear()
        self.status_bar.showMessage("正在生成网络拓扑图...")
        
        # 创建网络拓扑生成器
        self.topology_generator = NetworkTopology()
        self.topology_generator.progress_signal.connect(self.update_topology_progress)
        self.topology_generator.topology_ready.connect(self.topology_generation_finished)
        
        # 在后台线程中生成拓扑
        import threading
        threading.Thread(target=self.topology_generator.generate_topology, args=(target_ip, max_hops), daemon=True).start()
    
    def update_topology_progress(self, message):
        """更新拓扑生成进度"""
        self.topology_result.append(message)
    
    def topology_generation_finished(self, graph):
        """拓扑生成完成"""
        if graph:
            # 获取拓扑数据
            topology_data = self.topology_generator.get_topology_data()
            
            # 清空之前的内容
            self.topology_result.clear()
            
            # 显示流程图
            flowchart = topology_data.get('flowchart', '')
            if flowchart:
                # 设置等宽字体以正确显示流程图
                self.topology_result.setStyleSheet("""
                    QTextEdit {
                        font-family: 'Courier New', 'Consolas', monospace;
                        font-size: 10pt;
                        background-color: #f8f9fa;
                    }
                """)
                self.topology_result.setPlainText(flowchart)
                
                # 右侧显示提示信息
                self.topology_image_label.setText("流程图已生成\n\n流程图显示在左侧区域\n\n包含：\n• 网络拓扑结构\n• 路由节点信息\n• 延迟数据")
                self.topology_image_label.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e9;
                        border: 2px solid #4caf50;
                        border-radius: 8px;
                        padding: 20px;
                        font-size: 12pt;
                        color: #2e7d32;
                    }
                """)
            else:
                self.topology_result.append("[错误] 流程图生成失败")
                self.topology_image_label.setText("流程图生成失败，请检查目标IP地址")
        else:
            self.topology_result.clear()
            self.topology_result.append("[错误] 拓扑生成失败")
            self.topology_image_label.setText("拓扑生成失败，请检查目标IP地址")
        
        self.status_bar.showMessage("网络拓扑图生成完成")
    
    def create_subnet_calculator_content(self):
        """创建子网计算器内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        input_group = QGroupBox("子网计算器")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("IP地址:"), 0, 0)
        self.subnet_ip = QLineEdit("192.168.1.1")
        input_layout.addWidget(self.subnet_ip, 0, 1)
        
        input_layout.addWidget(QLabel("子网掩码:"), 1, 0)
        self.subnet_mask = QLineEdit("255.255.255.0")
        input_layout.addWidget(self.subnet_mask, 1, 1)
        
        self.calculate_subnet_button = QPushButton("计算")
        self.calculate_subnet_button.clicked.connect(self.calculate_subnet)
        input_layout.addWidget(self.calculate_subnet_button, 2, 0, 1, 2)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout()
        
        self.subnet_result = QTextEdit()
        self.subnet_result.setReadOnly(True)
        result_layout.addWidget(self.subnet_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        page.setLayout(layout)
        return page
    
    def show_subnet_calculator_page(self):
        """显示子网计算器页面"""
        self.clear_content()
        self.content_layout.addWidget(self.subnet_calculator_page)
    
    def calculate_subnet(self):
        """计算子网信息"""
        ip = self.subnet_ip.text().strip()
        mask = self.subnet_mask.text().strip()
        
        if not ip or not mask:
            QMessageBox.warning(self, "警告", "请输入IP地址和子网掩码")
            return
        
        try:
            # 简单的子网计算
            def ip_to_int(ip_str):
                parts = list(map(int, ip_str.split('.')))
                return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]
            
            def int_to_ip(ip_int):
                return '.'.join(map(str, [(ip_int >> 24) & 0xFF, (ip_int >> 16) & 0xFF, (ip_int >> 8) & 0xFF, ip_int & 0xFF]))
            
            # 计算网络地址和广播地址
            ip_int = ip_to_int(ip)
            mask_int = ip_to_int(mask)
            network_int = ip_int & mask_int
            broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)
            
            # 计算主机数量
            host_bits = bin(mask_int).count('0')
            max_hosts = 2 ** host_bits - 2 if host_bits > 0 else 0
            
            # 计算子网前缀
            prefix = 32 - host_bits
            
            # 显示结果
            self.subnet_result.clear()
            self.subnet_result.append("📋 子网计算结果:")
            self.subnet_result.append(f"IP地址: {ip}")
            self.subnet_result.append(f"子网掩码: {mask}")
            self.subnet_result.append(f"CIDR: {ip}/{prefix}")
            self.subnet_result.append(f"网络地址: {int_to_ip(network_int)}")
            self.subnet_result.append(f"广播地址: {int_to_ip(broadcast_int)}")
            self.subnet_result.append(f"可用主机数: {max_hosts}")
            self.subnet_result.append(f"第一个可用IP: {int_to_ip(network_int + 1)}")
            self.subnet_result.append(f"最后一个可用IP: {int_to_ip(broadcast_int - 1)}")
            
        except Exception as e:
            self.subnet_result.setText(f"计算出错: {str(e)}")
    
    def create_network_diagnostic_content(self):
        """创建网络诊断内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # 批量Ping测试
        batch_ping_group = QGroupBox("批量Ping测试")
        batch_ping_layout = QVBoxLayout()
        
        self.batch_ping_input = QTextEdit()
        self.batch_ping_input.setPlaceholderText("每行输入一个IP地址，例如：\n192.168.1.1\n8.8.8.8\n114.114.114.114")
        self.batch_ping_input.setMinimumHeight(100)
        batch_ping_layout.addWidget(QLabel("IP地址列表:"))
        batch_ping_layout.addWidget(self.batch_ping_input)
        
        batch_ping_buttons = QHBoxLayout()
        self.start_batch_ping_button = QPushButton("开始批量Ping")
        self.start_batch_ping_button.clicked.connect(self.start_batch_ping)
        batch_ping_buttons.addWidget(self.start_batch_ping_button)
        
        batch_ping_layout.addLayout(batch_ping_buttons)
        batch_ping_group.setLayout(batch_ping_layout)
        layout.addWidget(batch_ping_group)
        
        # 网络诊断
        diagnostic_group = QGroupBox("网络诊断")
        diagnostic_layout = QHBoxLayout()
        
        self.start_diagnostic_button = QPushButton("开始网络诊断")
        self.start_diagnostic_button.clicked.connect(self.start_network_diagnostic)
        diagnostic_layout.addWidget(self.start_diagnostic_button)
        
        diagnostic_group.setLayout(diagnostic_layout)
        layout.addWidget(diagnostic_group)
        
        # 结果显示
        result_group = QGroupBox("测试结果")
        result_layout = QVBoxLayout()
        
        self.diagnostic_result = QTextEdit()
        self.diagnostic_result.setReadOnly(True)
        result_layout.addWidget(self.diagnostic_result)
        
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        page.setLayout(layout)
        return page
    
    def show_network_diagnostic_page(self):
        """显示网络诊断页面"""
        self.clear_content()
        self.content_layout.addWidget(self.network_diagnostic_page)
    
    def start_batch_ping(self):
        """开始批量Ping测试"""
        ip_list = self.batch_ping_input.toPlainText().strip().split('\n')
        ip_list = [ip.strip() for ip in ip_list if ip.strip()]
        
        if not ip_list:
            QMessageBox.warning(self, "警告", "请输入IP地址列表")
            return
        
        self.diagnostic_result.clear()
        self.status_bar.showMessage(f"正在Ping测试 {len(ip_list)} 个IP地址...")
        
        self.batch_ping_thread = BatchPingThread(ip_list)
        self.batch_ping_thread.progress_signal.connect(self.update_diagnostic_progress)
        self.batch_ping_thread.result_signal.connect(self.update_batch_ping_result)
        self.batch_ping_thread.finished_signal.connect(self.batch_ping_finished)
        
        self.batch_ping_thread.start()
    
    def start_network_diagnostic(self):
        """开始网络诊断"""
        self.diagnostic_result.clear()
        self.status_bar.showMessage("正在进行网络诊断...")
        
        self.diagnostic_thread = NetworkDiagnosticThread()
        self.diagnostic_thread.progress_signal.connect(self.update_diagnostic_progress)
        self.diagnostic_thread.result_signal.connect(self.update_diagnostic_result)
        self.diagnostic_thread.finished_signal.connect(self.diagnostic_finished)
        
        self.diagnostic_thread.start()
    
    def update_diagnostic_progress(self, message):
        """更新诊断进度"""
        self.diagnostic_result.append(message)
    
    def update_batch_ping_result(self, results):
        """更新批量Ping结果"""
        self.diagnostic_result.append("\n📊 批量Ping测试结果:")
        
        if '在线' in results:
            self.diagnostic_result.append("\n✅ 在线主机:")
            for ip, result in results['在线']:
                self.diagnostic_result.append(f"  • {ip} - 响应时间: {result['time']}ms - 丢包率: {result['packet_loss']}%")
        
        if '离线' in results:
            self.diagnostic_result.append("\n❌ 离线主机:")
            for ip, result in results['离线']:
                self.diagnostic_result.append(f"  • {ip}")
        
        if '超时' in results:
            self.diagnostic_result.append("\n⏱️ 超时主机:")
            for ip, result in results['超时']:
                self.diagnostic_result.append(f"  • {ip}")
        
        if '错误' in results:
            self.diagnostic_result.append("\n⚠️ 错误主机:")
            for ip, result in results['错误']:
                self.diagnostic_result.append(f"  • {ip} - 错误: {result['error']}")
    
    def update_diagnostic_result(self, results):
        """更新网络诊断结果"""
        self.diagnostic_result.append("\n📋 网络诊断结果:")
        
        # 总体状态
        overall = results.get('overall', {})
        self.diagnostic_result.append(f"\n🎯 总体状态: {overall.get('status', '未知')}")
        
        if overall.get('issues'):
            self.diagnostic_result.append("\n⚠️ 发现问题:")
            for issue in overall.get('issues', []):
                self.diagnostic_result.append(f"  • {issue}")
        
        # DNS测试
        dns = results.get('dns', {})
        self.diagnostic_result.append("\n🌐 DNS解析测试:")
        self.diagnostic_result.append(f"  状态: {'正常' if dns.get('status') else '异常'}")
        if dns.get('resolved_servers'):
            self.diagnostic_result.append(f"  可用DNS服务器: {len(dns['resolved_servers'])}/{dns['total_servers']}")
        
        # 网关测试
        gateway = results.get('gateway', {})
        self.diagnostic_result.append("\n🏠 网关连接测试:")
        self.diagnostic_result.append(f"  状态: {'正常' if gateway.get('status') else '异常'}")
        if gateway.get('gateway'):
            self.diagnostic_result.append(f"  网关地址: {gateway['gateway']}")
        
        # 互联网测试
        internet = results.get('internet', {})
        self.diagnostic_result.append("\n🌍 互联网连接测试:")
        self.diagnostic_result.append(f"  状态: {'正常' if internet.get('status') else '异常'}")
        if internet.get('reachable_hosts'):
            self.diagnostic_result.append(f"  可访问主机: {len(internet['reachable_hosts'])}/{internet['total_hosts']}")
        
        # 延迟测试
        latency = results.get('latency', {})
        self.diagnostic_result.append("\n⏱️ 网络延迟测试:")
        self.diagnostic_result.append(f"  状态: {'正常' if latency.get('status') else '异常'}")
        if latency.get('avg_latency'):
            self.diagnostic_result.append(f"  平均延迟: {latency['avg_latency']}ms")
    
    def batch_ping_finished(self):
        """批量Ping测试完成"""
        self.status_bar.showMessage("批量Ping测试完成")
    
    def diagnostic_finished(self):
        """网络诊断完成"""
        self.status_bar.showMessage("网络诊断完成")
    
    def create_ai_assistant_content(self):
        """创建智能助手内容页"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # AI配置区域
        config_group = QGroupBox("AI模型配置")
        config_layout = QGridLayout()
        
        # 模型选择
        config_layout.addWidget(QLabel("AI模型:"), 0, 0)
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItem("豆包 Lite 4K (免费)", "doubao-lite-4k")
        self.ai_model_combo.addItem("豆包 Pro 4K", "doubao-pro-4k")
        self.ai_model_combo.addItem("豆包 Lite 32K (免费)", "doubao-lite-32k")
        self.ai_model_combo.setCurrentIndex(0)  # 默认选择免费模型
        config_layout.addWidget(self.ai_model_combo, 0, 1)
        
        # API Key输入
        config_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.ai_api_key_input = QLineEdit()
        self.ai_api_key_input.setPlaceholderText("请输入豆包/火山引擎API Key (可选，不填则使用本地知识库)")
        self.ai_api_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.ai_api_key_input, 1, 1)
        
        # 使用云端模型选项
        self.use_cloud_model_checkbox = QCheckBox("使用云端AI模型")
        self.use_cloud_model_checkbox.setChecked(False)  # 默认使用本地知识库
        config_layout.addWidget(self.use_cloud_model_checkbox, 2, 0, 1, 2)
        
        # 保存配置按钮
        save_config_btn = QPushButton("保存配置")
        save_config_btn.clicked.connect(self.save_ai_config)
        config_layout.addWidget(save_config_btn, 3, 1)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # 智能助手标题
        assistant_group = QGroupBox("网络智能助手")
        assistant_layout = QVBoxLayout()
        
        # 聊天区域
        self.ai_chat = QTextEdit()
        self.ai_chat.setReadOnly(True)
        self.ai_chat.setMinimumHeight(300)
        self.ai_chat.setStyleSheet("font-family: 'Arial', sans-serif; font-size: 10pt;")
        
        # 初始欢迎消息
        self.ai_chat.append("[AI] 网络智能助手")
        self.ai_chat.append("欢迎使用网络智能助手！我可以帮您解决网络相关问题。")
        self.ai_chat.append("您可以询问关于网络故障排除、工具使用或网络命令的问题。")
        self.ai_chat.append("")
        
        assistant_layout.addWidget(self.ai_chat)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("输入您的问题...")
        self.ai_input.returnPressed.connect(self.send_ai_query)
        
        send_button = QPushButton("发送")
        ButtonStyles.primary(send_button)
        send_button.clicked.connect(self.send_ai_query)
        
        input_layout.addWidget(self.ai_input, 1)
        input_layout.addWidget(send_button)
        
        assistant_layout.addLayout(input_layout)
        
        assistant_group.setLayout(assistant_layout)
        
        # 建议问题
        suggestion_group = QGroupBox("建议问题")
        suggestion_layout = QVBoxLayout()
        
        self.suggestion_buttons = []
        suggestions = [
            '我的网络速度很慢，怎么办？',
            '如何使用端口扫描工具？',
            '常用的网络命令有哪些？',
            '网络断网了怎么排查？',
            'DNS解析失败怎么解决？'
        ]
        
        for suggestion in suggestions:
            button = QPushButton(suggestion)
            button.setStyleSheet("text-align: left;")
            button.clicked.connect(lambda _, s=suggestion: self.send_suggestion(s))
            self.suggestion_buttons.append(button)
            suggestion_layout.addWidget(button)
        
        suggestion_group.setLayout(suggestion_layout)
        
        # 添加到主布局
        layout.addWidget(config_group)
        layout.addWidget(assistant_group)
        layout.addWidget(suggestion_group)
        
        page.setLayout(layout)
        
        # 加载保存的配置
        self.load_ai_config()
        
        return page
    
    def show_ai_assistant_page(self):
        """显示智能助手页面"""
        self.clear_content()
        self.content_layout.addWidget(self.ai_assistant_page)
    
    def send_suggestion(self, suggestion):
        """发送建议问题"""
        self.ai_input.setText(suggestion)
        self.send_ai_query()
    
    def save_ai_config(self):
        """保存AI配置"""
        config = {
            'model': self.ai_model_combo.currentData(),
            'api_key': self.ai_api_key_input.text().strip(),
            'use_cloud_model': self.use_cloud_model_checkbox.isChecked()
        }
        
        # 保存到设置
        self.settings.setValue("ai_config", config)
        
        # 更新AI助手配置
        if hasattr(self, 'ai_assistant'):
            self.ai_assistant.update_config(config)
        
        QMessageBox.information(self, "配置保存", "AI配置已保存！")
    
    def load_ai_config(self):
        """加载AI配置"""
        config = self.settings.value("ai_config", {})
        
        if config:
            # 设置模型
            model = config.get('model', 'doubao-lite-4k')
            index = self.ai_model_combo.findData(model)
            if index >= 0:
                self.ai_model_combo.setCurrentIndex(index)
            
            # 设置API Key
            self.ai_api_key_input.setText(config.get('api_key', ''))
            
            # 设置云端模型选项
            self.use_cloud_model_checkbox.setChecked(config.get('use_cloud_model', True))
    
    def send_ai_query(self):
        """发送智能助手查询"""
        query = self.ai_input.text().strip()
        if not query:
            return
        
        # 显示用户输入
        self.ai_chat.append(f"[用户] {query}")
        self.ai_input.clear()
        
        # 处理查询
        self.status_bar.showMessage("智能助手正在思考...")
        
        # 获取配置
        config = {
            'model': self.ai_model_combo.currentData(),
            'api_key': self.ai_api_key_input.text().strip(),
            'use_cloud_model': self.use_cloud_model_checkbox.isChecked()
        }
        
        # 创建智能助手
        self.ai_assistant = NetworkAIAssistant(config)
        self.ai_assistant.response_signal.connect(self.update_ai_response)
        self.ai_assistant.error_signal.connect(self.update_ai_error)
        self.ai_assistant.finished_signal.connect(self.ai_query_finished)
        
        # 处理查询
        self.ai_assistant.process_query(query)
    
    def update_ai_response(self, response):
        """更新智能助手响应"""
        self.ai_chat.append(f"[AI] {response}")
        self.ai_chat.append("")
    
    def update_ai_error(self, error):
        """更新智能助手错误"""
        self.ai_chat.append(f"[系统] {error}")
        self.ai_chat.append("")
    
    def ai_query_finished(self):
        """智能助手查询完成"""
        self.status_bar.showMessage("智能助手查询完成")
    
    def closeEvent(self, event):
        if self.monitor_thread:
            self.monitor_thread.stop()
        self.save_window_state()
        event.accept()
