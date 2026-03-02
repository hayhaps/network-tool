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
    QSplitter, QFrame, QAction, QMenu, QMenuBar
)
from PyQt5.QtCore import Qt, QThread, QSettings
from PyQt5.QtGui import QFont, QColor, QPalette

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("网络故障排查工具 v1.1")
        
        # 加载设置
        self.settings = QSettings("NetworkTool", "NetworkDiagnosticTool")
        
        # 恢复窗口大小和位置
        self.restore_window_state()
        
        self.monitor_thread = None
        self.is_dark_theme = False
        
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
        self.is_dark_theme = not self.is_dark_theme
        
        if self.is_dark_theme:
            # 深色主题
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(45, 45, 45))
            palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
            palette.setColor(QPalette.Base, QColor(30, 30, 30))
            palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
            palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
            palette.setColor(QPalette.Text, QColor(220, 220, 220))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
            
            self.setPalette(palette)
            self.settings.setValue("theme", "dark")
        else:
            # 浅色主题
            self.setPalette(self.style().standardPalette())
            self.settings.setValue("theme", "light")
    
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
        
        # 先创建状态栏
        self.create_status_bar()
        
        # 创建主布局（水平布局）
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧功能模块导航栏
        self.nav_widget = QWidget()
        self.nav_layout = QVBoxLayout()
        self.nav_widget.setLayout(self.nav_layout)
        self.nav_widget.setMinimumWidth(180)
        self.nav_widget.setMaximumWidth(220)
        
        # 添加导航标题
        nav_title = QLabel("功能模块")
        nav_title.setFont(QFont("Arial", 12, QFont.Bold))
        nav_title.setAlignment(Qt.AlignCenter)
        self.nav_layout.addWidget(nav_title)
        
        # 创建导航按钮
        self.nav_buttons = []
        self.create_nav_buttons()
        
        # 添加垂直 spacer，使按钮靠上
        self.nav_layout.addStretch()
        
        # 右侧内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
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
            ("SNMP管理", self.show_snmp_page),
            ("VLAN配置", self.show_vlan_page)
        ]
        
        for module_name, callback in modules:
            button = QPushButton(module_name)
            button.setFont(QFont("Arial", 10))
            button.setMinimumHeight(40)
            button.clicked.connect(callback)
            self.nav_buttons.append(button)
            self.nav_layout.addWidget(button)
    
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
        self.snmp_page = self.create_snmp_content()
        self.vlan_page = self.create_vlan_content()
        
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
        self.connection_table.setColumnCount(7)
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
        self.dns_type_combo.addItems(['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'PTR'])
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
        domain = self.dns_domain_input.text()
        if not domain:
            QMessageBox.warning(self, "警告", "请输入域名或IP地址")
            return
        
        record_type = self.dns_type_combo.currentText()
        self.dns_result.clear()
        self.dns_result.append(f"正在查询 {domain} 的 {record_type} 记录...\n")
        self.status_bar.showMessage(f"正在查询 {domain} 的 {record_type} 记录...")
        
        self.dns_query_thread = DNSQueryThread(domain, record_type)
        self.dns_query_thread.result_signal.connect(self.update_dns_query_result)
        self.dns_query_thread.finished_signal.connect(self.dns_query_finished)
        self.dns_query_thread.start()
    
    def update_dns_query_result(self, result):
        if result['error']:
            self.dns_result.append(f"错误: {result['error']}")
        else:
            self.dns_result.append(f"域名: {result['domain']}")
            self.dns_result.append(f"记录类型: {result['record_type']}")
            self.dns_result.append(f"记录:")
            for record in result['records']:
                self.dns_result.append(f"  {record}")
    
    def dns_query_finished(self):
        self.status_bar.showMessage("DNS查询完成")
    
    def start_dns_resolve(self):
        hostname = self.dns_domain_input.text()
        if not hostname:
            QMessageBox.warning(self, "警告", "请输入域名")
            return
        
        self.dns_result.clear()
        self.dns_result.append(f"正在解析 {hostname}...\n")
        self.status_bar.showMessage(f"正在解析 {hostname}...")
        
        self.dns_resolve_thread = DNSResolveThread(hostname)
        self.dns_resolve_thread.result_signal.connect(self.update_dns_resolve_result)
        self.dns_resolve_thread.finished_signal.connect(self.dns_resolve_finished)
        self.dns_resolve_thread.start()
    
    def update_dns_resolve_result(self, result):
        if result['error']:
            self.dns_result.append(f"错误: {result['error']}")
        else:
            self.dns_result.append(f"主机名: {result['hostname']}")
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
    
    def closeEvent(self, event):
        if self.monitor_thread:
            self.monitor_thread.stop()
        self.save_window_state()
        event.accept()
