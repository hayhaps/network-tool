import re
import json
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkAIAssistant(QObject):
    """网络智能助手"""
    response_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.knowledge_base = self._load_knowledge_base()
    
    def process_query(self, query):
        """处理用户查询"""
        query = query.strip().lower()
        
        # 分类查询类型
        query_type = self._classify_query(query)
        
        # 根据类型生成响应
        if query_type == 'greeting':
            response = self._handle_greeting()
        elif query_type == 'network_issue':
            response = self._handle_network_issue(query)
        elif query_type == 'tool_usage':
            response = self._handle_tool_usage(query)
        elif query_type == 'command':
            response = self._handle_command(query)
        elif query_type == 'troubleshooting':
            response = self._handle_troubleshooting(query)
        else:
            response = self._handle_general(query)
        
        self.response_signal.emit(response)
        self.finished_signal.emit()
    
    def _load_knowledge_base(self):
        """加载知识库"""
        return {
            'network_issues': {
                'slow_internet': [
                    '检查您的网络连接',
                    '重启路由器和调制解调器',
                    '检查是否有其他设备占用带宽',
                    '运行速度测试检查带宽',
                    '联系您的ISP确认服务状态'
                ],
                'no_internet': [
                    '检查物理连接是否正常',
                    '重启网络设备',
                    '检查路由器配置',
                    '尝试使用不同的设备连接',
                    '联系ISP技术支持'
                ],
                'dns_error': [
                    '尝试使用公共DNS服务器如8.8.8.8',
                    '清除DNS缓存',
                    '检查网络配置',
                    '重启网络服务'
                ]
            },
            'tools': {
                'port_scan': '端口扫描工具可以检测目标IP的开放端口，帮助您识别网络安全漏洞。',
                'speed_test': '速度测试工具可以测量您的网络下载和上传速度。',
                'ping': 'Ping测试工具可以检查网络连通性和响应时间。',
                'traceroute': 'Traceroute工具可以追踪网络数据包的传输路径。',
                'dns_query': 'DNS查询工具可以查询域名的DNS记录。',
                'wifi_scan': 'WiFi扫描工具可以检测附近的WiFi网络。',
                'subnet_calculator': '子网计算器可以帮助您计算IP地址和子网信息。',
                'network_topology': '网络拓扑工具可以生成网络结构可视化图表。'
            },
            'commands': {
                'ipconfig': 'ipconfig /all - 显示详细的网络配置信息',
                'ping': 'ping -t 192.168.1.1 - 持续Ping测试',
                'tracert': 'tracert 8.8.8.8 - 追踪网络路径',
                'netstat': 'netstat -an - 显示网络连接状态',
                'arp': 'arp -a - 显示ARP缓存表',
                'nslookup': 'nslookup google.com - DNS查询',
                'route': 'route print - 显示路由表'
            }
        }
    
    def _classify_query(self, query):
        """分类查询类型"""
        # 问候语
        if any(greet in query for greet in ['你好', '您好', 'hi', 'hello', '嗨']):
            return 'greeting'
        
        # 网络问题
        if any(issue in query for issue in ['网络', '连接', '速度', '慢', '断网', 'dns', '无法访问']):
            return 'network_issue'
        
        # 工具使用
        if any(tool in query for tool in ['工具', '怎么用', '如何使用', '功能']):
            return 'tool_usage'
        
        # 命令查询
        if any(cmd in query for cmd in ['命令', 'cmd', '终端', '命令行']):
            return 'command'
        
        # 故障排除
        if any(trouble in query for trouble in ['故障', '问题', '修复', '解决', '怎么办']):
            return 'troubleshooting'
        
        return 'general'
    
    def _handle_greeting(self):
        """处理问候语"""
        responses = [
            '你好！我是网络运维智能助手，有什么可以帮您的吗？',
            '您好！很高兴为您服务，请问有什么网络问题需要解决？',
            '嗨！我是您的网络助手，随时为您解答网络相关问题。'
        ]
        return responses[0]
    
    def _handle_network_issue(self, query):
        """处理网络问题"""
        if any(term in query for term in ['慢', '速度', '卡顿']):
            issue_type = 'slow_internet'
        elif any(term in query for term in ['断网', '无法连接', '没有网']):
            issue_type = 'no_internet'
        elif any(term in query for term in ['dns', '域名', '解析']):
            issue_type = 'dns_error'
        else:
            issue_type = 'slow_internet'
        
        solutions = self.knowledge_base['network_issues'].get(issue_type, [])
        response = f"针对您的网络问题，建议您尝试以下解决方案：\n"
        for i, solution in enumerate(solutions, 1):
            response += f"{i}. {solution}\n"
        return response
    
    def _handle_tool_usage(self, query):
        """处理工具使用问题"""
        tools = self.knowledge_base['tools']
        response = "我们提供以下网络工具：\n"
        for tool, description in tools.items():
            response += f"• {tool}: {description}\n"
        response += "\n您可以在左侧导航栏中找到这些工具。"
        return response
    
    def _handle_command(self, query):
        """处理命令查询"""
        commands = self.knowledge_base['commands']
        response = "常用网络命令：\n"
        for cmd, description in commands.items():
            response += f"• {description}\n"
        return response
    
    def _handle_troubleshooting(self, query):
        """处理故障排除"""
        response = "网络故障排除步骤：\n"
        response += "1. 检查物理连接是否正常\n"
        response += "2. 重启网络设备（路由器、调制解调器）\n"
        response += "3. 检查网络配置是否正确\n"
        response += "4. 运行网络诊断工具\n"
        response += "5. 联系ISP技术支持\n"
        return response
    
    def _handle_general(self, query):
        """处理一般查询"""
        responses = [
            '我是网络运维智能助手，可以帮您解决网络相关问题。',
            '请问您有什么网络问题需要帮助解决？',
            '您可以询问我关于网络故障排除、工具使用或网络命令的问题。'
        ]
        return responses[0]
    
    def get_suggestions(self):
        """获取建议问题"""
        return [
            '我的网络速度很慢，怎么办？',
            '如何使用端口扫描工具？',
            '常用的网络命令有哪些？',
            '网络断网了怎么排查？',
            'DNS解析失败怎么解决？'
        ]