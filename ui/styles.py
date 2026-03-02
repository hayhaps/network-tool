# -*- coding: utf-8 -*-
"""
现代化UI样式模块
提供美观的界面主题和样式
"""

# 工程师风格主题
ENGINEER_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 10pt;
}

/* 导航按钮样式 */
QPushButton {
    background-color: #2d2d2d;
    color: #00ff00;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 140px;
    text-align: left;
}

QPushButton:hover {
    background-color: #3d3d3d;
    border-color: #00ff00;
    box-shadow: 0 0 8px rgba(0, 255, 0, 0.3);
}

QPushButton:pressed {
    background-color: #4d4d4d;
}

QPushButton:disabled {
    background-color: #1e1e1e;
    color: #666666;
    border-color: #2d2d2d;
}

/* 导航按钮选中状态 */
QPushButton[selected="true"] {
    background-color: #00ff00;
    color: #1e1e1e;
    border-color: #00ff00;
    font-weight: 700;
    box-shadow: 0 0 12px rgba(0, 255, 0, 0.5);
}

QPushButton[selected="true"]:hover {
    background-color: #00cc00;
    border-color: #00cc00;
}

/* 主要操作按钮 */
QPushButton#primaryButton {
    background-color: #00ff00;
    color: #1e1e1e;
    border: 1px solid #00ff00;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background-color: #00cc00;
    border-color: #00cc00;
    box-shadow: 0 0 16px rgba(0, 255, 0, 0.4);
}

/* 危险操作按钮 */
QPushButton#dangerButton {
    background-color: #ff4444;
    color: #ffffff;
    border: 1px solid #ff4444;
}

QPushButton#dangerButton:hover {
    background-color: #cc0000;
    border-color: #cc0000;
    box-shadow: 0 0 16px rgba(255, 68, 68, 0.4);
}

/* 成功操作按钮 */
QPushButton#successButton {
    background-color: #44ff44;
    color: #1e1e1e;
    border: 1px solid #44ff44;
}

QPushButton#successButton:hover {
    background-color: #00cc00;
    box-shadow: 0 0 16px rgba(68, 255, 68, 0.4);
}

/* 分组框样式 */
QGroupBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: #00ff00;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: #00ff00;
    font-size: 10pt;
}

/* 输入框样式 */
QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px 12px;
    color: #00ff00;
    selection-background-color: #00ff00;
    selection-color: #1e1e1e;
}

QLineEdit:focus {
    border-color: #00ff00;
    box-shadow: 0 0 4px rgba(0, 255, 0, 0.3);
}

QLineEdit:disabled {
    background-color: #1a1a1a;
    color: #666666;
}

/* 文本编辑框样式 */
QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 10px;
    color: #00ff00;
    line-height: 1.5;
}

QTextEdit:focus {
    border-color: #00ff00;
}

/* 下拉框样式 */
QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px 12px;
    color: #00ff00;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #00ff00;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid #00ff00;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    selection-background-color: #00ff00;
    selection-color: #1e1e1e;
}

/* 表格样式 */
QTableWidget {
    background-color: #1e1e1e;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    gridline-color: #2d2d2d;
    selection-background-color: #00ff00;
    selection-color: #1e1e1e;
}

QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #2d2d2d;
    color: #00ff00;
}

QTableWidget::item:selected {
    background-color: #00ff00;
    color: #1e1e1e;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #00ff00;
    padding: 10px;
    border: none;
    border-bottom: 1px solid #3d3d3d;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #3d3d3d;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #1e1e1e;
    text-align: center;
    color: #00ff00;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #00ff00;
    border-radius: 3px;
}

/* 标签样式 */
QLabel {
    color: #00ff00;
    font-weight: 500;
}

QLabel#titleLabel {
    font-size: 16pt;
    font-weight: 700;
    color: #00ff00;
}

QLabel#subtitleLabel {
    font-size: 11pt;
    color: #888888;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #2d2d2d;
    color: #00ff00;
    border-top: 1px solid #3d3d3d;
    padding: 4px 12px;
}

/* 菜单栏样式 */
QMenuBar {
    background-color: #2d2d2d;
    border-bottom: 1px solid #3d3d3d;
    padding: 2px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
    color: #00ff00;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
    color: #00ff00;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
    color: #00ff00;
}

QMenu::item:selected {
    background-color: #00ff00;
    color: #1e1e1e;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #3d3d3d;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00ff00;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #3d3d3d;
    border-radius: 5px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00ff00;
}

/* 分割器样式 */
QSplitter::handle {
    background-color: #3d3d3d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* 工具提示样式 */
QToolTip {
    background-color: #2d2d2d;
    color: #00ff00;
    border: 1px solid #00ff00;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 9pt;
}
"""

# 现代浅色主题
LIGHT_THEME = """
QMainWindow {
    background-color: #f5f7fa;
}

QWidget {
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    font-size: 10pt;
}

/* 导航按钮样式 */
QPushButton {
    background-color: #ffffff;
    color: #2c3e50;
    border: 1px solid #e0e6ed;
    border-radius: 8px;
    padding: 12px 20px;
    font-weight: 500;
    min-width: 120px;
    transition: all 0.3s ease;
}

QPushButton:hover {
    background-color: #3498db;
    color: white;
    border-color: #3498db;
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

QPushButton:pressed {
    background-color: #2980b9;
    border-color: #2980b9;
}

QPushButton:disabled {
    background-color: #ecf0f1;
    color: #95a5a6;
    border-color: #bdc3c7;
}

/* 主要操作按钮 */
QPushButton#primaryButton {
    background-color: #3498db;
    color: white;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #2980b9;
    box-shadow: 0 4px 16px rgba(52, 152, 219, 0.4);
}

/* 危险操作按钮 */
QPushButton#dangerButton {
    background-color: #e74c3c;
    color: white;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #c0392b;
    box-shadow: 0 4px 16px rgba(231, 76, 60, 0.4);
}

/* 成功操作按钮 */
QPushButton#successButton {
    background-color: #27ae60;
    color: white;
    border: none;
}

QPushButton#successButton:hover {
    background-color: #229954;
    box-shadow: 0 4px 16px rgba(39, 174, 96, 0.4);
}

/* 分组框样式 */
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    color: #2c3e50;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 12px;
    color: #3498db;
    font-size: 11pt;
}

/* 输入框样式 */
QLineEdit {
    background-color: #ffffff;
    border: 2px solid #e0e6ed;
    border-radius: 8px;
    padding: 10px 14px;
    color: #2c3e50;
    selection-background-color: #3498db;
}

QLineEdit:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

QLineEdit:disabled {
    background-color: #ecf0f1;
    color: #95a5a6;
}

/* 文本编辑框样式 */
QTextEdit {
    background-color: #ffffff;
    border: 2px solid #e0e6ed;
    border-radius: 8px;
    padding: 12px;
    color: #2c3e50;
    line-height: 1.6;
}

QTextEdit:focus {
    border-color: #3498db;
}

/* 下拉框样式 */
QComboBox {
    background-color: #ffffff;
    border: 2px solid #e0e6ed;
    border-radius: 8px;
    padding: 10px 14px;
    color: #2c3e50;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #3498db;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #7f8c8d;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
    border-radius: 8px;
    selection-background-color: #3498db;
    selection-color: white;
}

/* 表格样式 */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
    border-radius: 8px;
    gridline-color: #ecf0f1;
    selection-background-color: #3498db;
    selection-color: white;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #ecf0f1;
}

QTableWidget::item:selected {
    background-color: #3498db;
}

QHeaderView::section {
    background-color: #f8f9fa;
    color: #2c3e50;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #e0e6ed;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #ecf0f1;
}

/* 进度条样式 */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #ecf0f1;
    text-align: center;
    color: #2c3e50;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 6px;
}

/* 标签样式 */
QLabel {
    color: #2c3e50;
    font-weight: 500;
}

QLabel#titleLabel {
    font-size: 18pt;
    font-weight: 700;
    color: #2c3e50;
}

QLabel#subtitleLabel {
    font-size: 12pt;
    color: #7f8c8d;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #ffffff;
    color: #7f8c8d;
    border-top: 1px solid #e0e6ed;
    padding: 6px 16px;
}

/* 菜单栏样式 */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e0e6ed;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
}

QMenuBar::item:selected {
    background-color: #ecf0f1;
    color: #2c3e50;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
    border-radius: 8px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 24px;
    border-radius: 6px;
}

QMenu::item:selected {
    background-color: #3498db;
    color: white;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #f8f9fa;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #bdc3c7;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #95a5a6;
}

/* 分割器样式 */
QSplitter::handle {
    background-color: #e0e6ed;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* 工具提示样式 */
QToolTip {
    background-color: #2c3e50;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
}
"""

# 深色主题
DARK_THEME = """
QMainWindow {
    background-color: #1a1a2e;
}

QWidget {
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    font-size: 10pt;
}

/* 导航按钮样式 */
QPushButton {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 12px 20px;
    font-weight: 500;
    min-width: 120px;
}

QPushButton:hover {
    background-color: #e94560;
    color: white;
    border-color: #e94560;
    box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
}

QPushButton:pressed {
    background-color: #c13651;
    border-color: #c13651;
}

QPushButton:disabled {
    background-color: #16213e;
    color: #4a4a6a;
    border-color: #0f3460;
}

/* 主要操作按钮 */
QPushButton#primaryButton {
    background-color: #e94560;
    color: white;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #c13651;
    box-shadow: 0 4px 16px rgba(233, 69, 96, 0.4);
}

/* 危险操作按钮 */
QPushButton#dangerButton {
    background-color: #ff6b6b;
    color: white;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #ee5a5a;
    box-shadow: 0 4px 16px rgba(255, 107, 107, 0.4);
}

/* 成功操作按钮 */
QPushButton#successButton {
    background-color: #00d9ff;
    color: #1a1a2e;
    border: none;
    font-weight: 600;
}

QPushButton#successButton:hover {
    background-color: #00b8d4;
    box-shadow: 0 4px 16px rgba(0, 217, 255, 0.4);
}

/* 分组框样式 */
QGroupBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 600;
    color: #eaeaea;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 12px;
    color: #e94560;
    font-size: 11pt;
}

/* 输入框样式 */
QLineEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 10px 14px;
    color: #eaeaea;
    selection-background-color: #e94560;
}

QLineEdit:focus {
    border-color: #e94560;
    box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.1);
}

QLineEdit:disabled {
    background-color: #0f3460;
    color: #4a4a6a;
}

/* 文本编辑框样式 */
QTextEdit {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 12px;
    color: #eaeaea;
    line-height: 1.6;
}

QTextEdit:focus {
    border-color: #e94560;
}

/* 下拉框样式 */
QComboBox {
    background-color: #16213e;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 10px 14px;
    color: #eaeaea;
    min-width: 120px;
}

QComboBox:hover {
    border-color: #e94560;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #7f8c8d;
    width: 0;
    height: 0;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    selection-background-color: #e94560;
    selection-color: white;
}

/* 表格样式 */
QTableWidget {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    gridline-color: #0f3460;
    selection-background-color: #e94560;
    selection-color: white;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #0f3460;
    color: #eaeaea;
}

QTableWidget::item:selected {
    background-color: #e94560;
}

QHeaderView::section {
    background-color: #0f3460;
    color: #eaeaea;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #e94560;
    font-weight: 600;
}

QHeaderView::section:hover {
    background-color: #1a1a2e;
}

/* 进度条样式 */
QProgressBar {
    border: none;
    border-radius: 6px;
    background-color: #0f3460;
    text-align: center;
    color: #eaeaea;
    font-weight: 600;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 6px;
}

/* 标签样式 */
QLabel {
    color: #eaeaea;
    font-weight: 500;
}

QLabel#titleLabel {
    font-size: 18pt;
    font-weight: 700;
    color: #eaeaea;
}

QLabel#subtitleLabel {
    font-size: 12pt;
    color: #7f8c8d;
}

/* 状态栏样式 */
QStatusBar {
    background-color: #16213e;
    color: #7f8c8d;
    border-top: 1px solid #0f3460;
    padding: 6px 16px;
}

/* 菜单栏样式 */
QMenuBar {
    background-color: #16213e;
    border-bottom: 1px solid #0f3460;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
    color: #eaeaea;
}

QMenuBar::item:selected {
    background-color: #0f3460;
    color: #eaeaea;
}

QMenu {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    padding: 8px;
}

QMenu::item {
    padding: 10px 24px;
    border-radius: 6px;
    color: #eaeaea;
}

QMenu::item:selected {
    background-color: #e94560;
    color: white;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 6px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #16213e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #0f3460;
    border-radius: 6px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #e94560;
}

/* 分割器样式 */
QSplitter::handle {
    background-color: #0f3460;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* 工具提示样式 */
QToolTip {
    background-color: #e94560;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 9pt;
}
"""

# 按钮样式类
class ButtonStyles:
    """按钮样式预设"""
    
    @staticmethod
    def primary(button):
        """设置主要按钮样式"""
        button.setObjectName("primaryButton")
        button.setStyleSheet("""
            QPushButton#primaryButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 11pt;
            }
            QPushButton#primaryButton:hover {
                background-color: #2980b9;
            }
            QPushButton#primaryButton:pressed {
                background-color: #1f5f8b;
            }
        """)
    
    @staticmethod
    def danger(button):
        """设置危险按钮样式"""
        button.setObjectName("dangerButton")
        button.setStyleSheet("""
            QPushButton#dangerButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
            }
            QPushButton#dangerButton:hover {
                background-color: #c0392b;
            }
            QPushButton#dangerButton:pressed {
                background-color: #a93226;
            }
        """)
    
    @staticmethod
    def success(button):
        """设置成功按钮样式"""
        button.setObjectName("successButton")
        button.setStyleSheet("""
            QPushButton#successButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
            }
            QPushButton#successButton:hover {
                background-color: #229954;
            }
            QPushButton#successButton:pressed {
                background-color: #1e8449;
            }
        """)
    
    @staticmethod
    def warning(button):
        """设置警告按钮样式"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
    
    @staticmethod
    def info(button):
        """设置信息按钮样式"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)

# 卡片样式
CARD_STYLE = """
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e0e6ed;
    border-radius: 12px;
    padding: 16px;
}
"""

# 导航栏样式
NAV_STYLE = """
QFrame#navFrame {
    background-color: #ffffff;
    border-right: 1px solid #e0e6ed;
    padding: 16px;
}
"""

# 内容区域样式
CONTENT_STYLE = """
QFrame#contentFrame {
    background-color: #f5f7fa;
    padding: 20px;
}
"""

# 图标按钮样式
ICON_BUTTON_STYLE = """
QPushButton#iconButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 8px;
    font-size: 16pt;
}

QPushButton#iconButton:hover {
    background-color: #ecf0f1;
}

QPushButton#iconButton:pressed {
    background-color: #bdc3c7;
}
"""