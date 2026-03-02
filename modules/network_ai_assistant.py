# -*- coding: utf-8 -*-
"""
网络智能助手模块
支持本地知识库和云端大模型（豆包/火山引擎）
"""

import re
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal


class NetworkAIAssistant(QObject):
    """网络智能助手 - 支持本地知识库和云端大模型"""
    response_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        # 默认优先使用本地知识库
        self.use_cloud_model = self.config.get('use_cloud_model', False)
        self.api_key = self.config.get('api_key', '')
        self.model_name = self.config.get('model', 'doubao-lite-4k')
        
        # 加载知识库（包括本地文档）
        self.knowledge_base = self._load_knowledge_base()
        self.local_doc_content = self._load_local_document()
    
    def process_query(self, query):
        """处理用户查询"""
        try:
            query = query.strip()
            
            # 如果启用了云端大模型且有API密钥，优先使用云端模型
            if self.use_cloud_model and self.api_key:
                self._process_with_cloud_model(query)
            else:
                # 使用本地知识库
                self._process_with_local_kb(query)
                
        except Exception as e:
            self.error_signal.emit(f"处理查询时出错: {str(e)}")
            self.finished_signal.emit()
    
    def _process_with_cloud_model(self, query):
        """使用云端大模型处理查询"""
        try:
            import urllib.request
            import urllib.error
            
            # 豆包/火山引擎 API 配置
            api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            
            # 构建请求体
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的网络运维助手，擅长解答网络故障排查、网络配置、网络工具使用等问题。请用中文回答，回答要简洁实用。"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.7
            }
            
            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            # 设置超时
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            # 提取回答
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                self.response_signal.emit(answer)
            else:
                # 如果云端模型返回异常，回退到本地知识库
                self._process_with_local_kb(query)
                
        except urllib.error.HTTPError as e:
            error_msg = f"API请求失败: {e.code}"
            if e.code == 401:
                error_msg = "API密钥无效，请检查配置"
            elif e.code == 429:
                error_msg = "请求过于频繁，请稍后再试"
            self.error_signal.emit(error_msg)
            # 回退到本地知识库
            self._process_with_local_kb(query)
        except Exception as e:
            self.error_signal.emit(f"云端模型调用失败: {str(e)}，已切换到本地模式")
            # 回退到本地知识库
            self._process_with_local_kb(query)
        finally:
            self.finished_signal.emit()
    
    def _process_with_local_kb(self, query):
        """使用本地知识库处理查询"""
        query_lower = query.lower()
        
        # 分类查询类型
        query_type = self._classify_query(query_lower)
        
        # 根据类型生成响应
        if query_type == 'greeting':
            response = self._handle_greeting()
        elif query_type == 'network_issue':
            response = self._handle_network_issue(query_lower)
        elif query_type == 'tool_usage':
            response = self._handle_tool_usage(query_lower)
        elif query_type == 'command':
            response = self._handle_command(query_lower)
        elif query_type == 'troubleshooting':
            response = self._handle_troubleshooting(query_lower)
        else:
            response = self._handle_general(query)
        
        self.response_signal.emit(response)
        self.finished_signal.emit()
    
    def _load_local_document(self):
        """加载本地网络故障排查文档"""
        try:
            # 获取文档路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            doc_path = os.path.join(os.path.dirname(current_dir), 'data', 'network_troubleshooting_guide.md')
            
            if os.path.exists(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            else:
                return ""
        except Exception as e:
            print(f"加载本地文档失败: {e}")
            return ""
    
    def _search_in_document(self, query, max_chars=2000):
        """在本地文档中搜索相关内容"""
        if not self.local_doc_content:
            return None
        
        query_lower = query.lower()
        
        # 定义关键词映射
        keyword_sections = {
            '无法连接': ['无法连接互联网', '排查步骤', '解决方案'],
            '断网': ['无法连接互联网', '排查步骤'],
            '速度慢': ['网络速度慢', '可能原因', '解决方案'],
            '卡顿': ['网络速度慢', '延迟'],
            'dns': ['DNS解析失败', 'DNS查询', '解决方案', 'DNS故障'],
            '域名': ['DNS解析失败', 'DNS查询'],
            'wifi': ['WiFi连接问题', '无线网络优化', '无线局域网（WiFi）故障'],
            '无线': ['WiFi连接问题', '无线网络优化', '无线局域网（WiFi）故障'],
            '信号': ['WiFi信号弱', '无线网络优化'],
            'ping': ['Ping测试', '网络命令', '软件工具'],
            'tracert': ['Traceroute', '路由追踪', '软件工具'],
            '路由': ['Traceroute', '路由表', '路由故障'],
            '端口': ['端口扫描', '常见端口', '端口占用故障'],
            '安全': ['网络安全基础', '防护措施', '防火墙故障'],
            '攻击': ['网络安全基础', '常见网络攻击'],
            '优化': ['网络优化建议', '无线网络优化'],
            '命令': ['网络命令参考', '常用命令', '软件工具'],
            'cmd': ['网络命令参考', 'Windows常用命令'],
            '术语': ['常用网络术语'],
            'vlan': ['VLAN', '虚拟局域网'],
            'vpn': ['VPN', '虚拟专用网络', 'VPN故障'],
            'nat': ['NAT', '网络地址转换'],
            'dhcp': ['DHCP', '动态主机配置', 'IP地址配置故障'],
            'arp': ['ARP', 'ARP欺骗'],
            '防火墙': ['防火墙', '防护措施', '防火墙故障'],
            '网卡': ['终端网卡故障'],
            '网线': ['网线/光纤故障'],
            '光纤': ['网线/光纤故障'],
            '设备': ['网络设备供电/硬件故障'],
            '光猫': ['网络设备供电/硬件故障'],
            '交换机': ['网络设备供电/硬件故障'],
            '路由器': ['网络设备供电/硬件故障'],
            'ip': ['IP地址配置故障'],
            '网关': ['网关故障'],
            'tcp': ['TCP/UDP连接异常'],
            'udp': ['TCP/UDP连接异常'],
            '浏览器': ['浏览器无法访问网页'],
            '网页': ['浏览器无法访问网页'],
            '共享': ['局域网共享故障'],
            '局域网': ['局域网共享故障'],
            '物理': ['物理层故障'],
            '网络层': ['网络层故障'],
            '传输层': ['传输层故障'],
            '应用层': ['应用层故障'],
            '排查': ['排查前准备', '信息收集'],
            '准备': ['排查前准备', '工具准备'],
            '工具': ['工具准备', '软件工具'],
            '信息': ['信息收集'],
            '故障': ['故障现象'],
        }
        
        # 查找匹配的关键词
        matched_sections = []
        for keyword, sections in keyword_sections.items():
            if keyword in query_lower:
                matched_sections.extend(sections)
        
        if not matched_sections:
            # 如果没有匹配到关键词，返回文档的前一部分作为概览
            return self.local_doc_content[:max_chars] + "\n\n[文档内容过长，已截断]"
        
        # 在文档中查找相关章节
        results = []
        lines = self.local_doc_content.split('\n')
        current_section = []
        in_matching_section = False
        
        for line in lines:
            # 检查是否是章节标题
            if line.startswith('#') or line.startswith('##') or line.startswith('###'):
                # 保存之前的章节
                if in_matching_section and current_section:
                    results.append('\n'.join(current_section))
                
                current_section = [line]
                in_matching_section = any(section in line for section in matched_sections)
            else:
                if in_matching_section:
                    current_section.append(line)
        
        # 添加最后一个章节
        if in_matching_section and current_section:
            results.append('\n'.join(current_section))
        
        if results:
            combined_result = '\n\n'.join(results)
            # 限制长度
            if len(combined_result) > max_chars:
                combined_result = combined_result[:max_chars] + "\n\n[内容过长，已截断]"
            return combined_result
        
        return None
    
    def _load_knowledge_base(self):
        """加载本地知识库"""
        return {
            'network_issues': {
                'slow_internet': {
                    'title': '网络速度慢',
                    'solutions': [
                        '检查您的网络连接是否正常',
                        '重启路由器和调制解调器',
                        '检查是否有其他设备占用带宽',
                        '运行速度测试检查实际带宽',
                        '联系您的ISP确认服务状态',
                        '尝试更换DNS服务器（如8.8.8.8或114.114.114.114）',
                        '检查是否有后台程序占用网络'
                    ]
                },
                'no_internet': {
                    'title': '无法连接互联网',
                    'solutions': [
                        '检查物理连接是否正常（网线、WiFi）',
                        '重启路由器和光猫',
                        '检查路由器配置和拨号状态',
                        '尝试使用不同的设备连接测试',
                        '检查是否欠费或ISP服务中断',
                        '联系ISP技术支持'
                    ]
                },
                'dns_error': {
                    'title': 'DNS解析错误',
                    'solutions': [
                        '尝试使用公共DNS服务器：8.8.8.8 或 114.114.114.114',
                        '清除DNS缓存（ipconfig /flushdns）',
                        '检查hosts文件是否被篡改',
                        '重启网络服务',
                        '检查防火墙设置'
                    ]
                },
                'wifi_weak': {
                    'title': 'WiFi信号弱',
                    'solutions': [
                        '调整路由器位置，避免障碍物',
                        '更换WiFi信道，避免干扰',
                        '考虑使用WiFi信号放大器',
                        '升级到支持5GHz的路由器',
                        '检查是否有干扰源（微波炉、蓝牙设备等）'
                    ]
                }
            },
            'tools': {
                'port_scan': {
                    'name': '端口扫描',
                    'description': '检测目标IP的开放端口，帮助识别网络安全漏洞和开放服务。',
                    'usage': '输入目标IP地址，选择扫描端口范围，点击开始扫描。'
                },
                'speed_test': {
                    'name': '速度测试',
                    'description': '测量网络下载和上传速度，以及网络延迟。',
                    'usage': '点击开始测试，等待测试完成查看结果。'
                },
                'ping': {
                    'name': 'Ping测试',
                    'description': '检查网络连通性和响应时间。',
                    'usage': '输入目标IP或域名，设置超时时间和次数，开始测试。'
                },
                'traceroute': {
                    'name': '路由追踪',
                    'description': '追踪网络数据包的传输路径，显示经过的路由节点。',
                    'usage': '输入目标地址，点击开始追踪。'
                },
                'dns_query': {
                    'name': 'DNS查询',
                    'description': '查询域名的DNS记录，包括A记录、MX记录、NS记录等。',
                    'usage': '输入域名，选择查询类型，点击查询。'
                },
                'wifi_scan': {
                    'name': 'WiFi扫描',
                    'description': '扫描附近的WiFi网络，显示信号强度和加密方式。',
                    'usage': '点击扫描按钮，等待扫描结果显示。'
                },
                'subnet_calculator': {
                    'name': '子网计算器',
                    'description': '计算IP地址和子网信息，包括网络地址、广播地址、可用主机数等。',
                    'usage': '输入IP地址和子网掩码，点击计算。'
                },
                'network_topology': {
                    'name': '网络拓扑',
                    'description': '生成网络结构可视化图表，显示网络设备和连接关系。',
                    'usage': '输入目标IP，设置最大跳数，点击生成拓扑图。'
                },
                'network_diagnostic': {
                    'name': '网络诊断',
                    'description': '全面的网络状态检测，包括批量Ping、DNS测试、网关测试等。',
                    'usage': '输入IP列表进行批量Ping，或点击网络诊断进行全面检测。'
                }
            },
            'commands': {
                'ipconfig': {
                    'cmd': 'ipconfig /all',
                    'desc': '显示详细的网络配置信息，包括IP地址、子网掩码、网关、DNS等'
                },
                'ping': {
                    'cmd': 'ping -t 192.168.1.1',
                    'desc': '持续Ping测试，按Ctrl+C停止'
                },
                'tracert': {
                    'cmd': 'tracert 8.8.8.8',
                    'desc': '追踪到目标地址的网络路径'
                },
                'netstat': {
                    'cmd': 'netstat -an',
                    'desc': '显示所有网络连接和监听端口'
                },
                'arp': {
                    'cmd': 'arp -a',
                    'desc': '显示ARP缓存表，查看IP和MAC地址对应关系'
                },
                'nslookup': {
                    'cmd': 'nslookup google.com',
                    'desc': '查询域名的DNS信息'
                },
                'route': {
                    'cmd': 'route print',
                    'desc': '显示路由表信息'
                },
                'flushdns': {
                    'cmd': 'ipconfig /flushdns',
                    'desc': '清除DNS缓存'
                }
            }
        }
    
    def _classify_query(self, query):
        """分类查询类型"""
        # 问候语
        if any(greet in query for greet in ['你好', '您好', 'hi', 'hello', '嗨', '在吗']):
            return 'greeting'
        
        # 网络问题
        if any(issue in query for issue in ['网络', '连接', '速度', '慢', '断网', 'dns', '无法访问', '连不上']):
            return 'network_issue'
        
        # 工具使用
        if any(tool in query for tool in ['工具', '怎么用', '如何使用', '功能', '扫描', '测试']):
            return 'tool_usage'
        
        # 命令查询
        if any(cmd in query for cmd in ['命令', 'cmd', '终端', '命令行', 'dos']):
            return 'command'
        
        # 故障排除
        if any(trouble in query for trouble in ['故障', '问题', '修复', '解决', '怎么办', '排查']):
            return 'troubleshooting'
        
        return 'general'
    
    def _handle_greeting(self):
        """处理问候语"""
        responses = [
            '你好！我是网络运维智能助手，可以帮您解决网络相关问题。\n\n我可以：\n• 诊断网络故障\n• 介绍工具使用方法\n• 提供网络命令参考\n• 解答网络配置问题\n\n请问有什么可以帮您的吗？',
            '您好！我是您的网络助手，随时为您解答网络相关问题。\n\n您可以直接描述遇到的问题，或者询问如何使用某个功能。',
            '嗨！我是网络运维助手，擅长处理各种网络问题。\n\n无论是网络故障排查还是工具使用，我都可以帮您！'
        ]
        return responses[0]
    
    def _handle_network_issue(self, query):
        """处理网络问题"""
        # 首先在本地文档中搜索
        doc_content = self._search_in_document(query)
        
        if doc_content:
            response = "【根据网络故障排查指南】\n\n"
            response += doc_content
            response += "\n\n[以上内容来自本地知识库文档]"
            return response
        
        # 如果文档中没有找到，使用内置知识库
        # 确定问题类型
        if any(term in query for term in ['慢', '速度', '卡顿', '延迟']):
            issue_type = 'slow_internet'
        elif any(term in query for term in ['断网', '无法连接', '没有网', '连不上']):
            issue_type = 'no_internet'
        elif any(term in query for term in ['dns', '域名', '解析', '找不到']):
            issue_type = 'dns_error'
        elif any(term in query for term in ['wifi', '无线', '信号']):
            issue_type = 'wifi_weak'
        else:
            issue_type = 'slow_internet'
        
        issue_data = self.knowledge_base['network_issues'].get(issue_type, {})
        
        if not issue_data:
            return "抱歉，我没有找到相关问题的解决方案。请尝试描述更具体的问题。"
        
        response = f"【{issue_data.get('title', '网络问题')}】\n\n"
        response += "建议您尝试以下解决方案：\n\n"
        
        for i, solution in enumerate(issue_data.get('solutions', []), 1):
            response += f"{i}. {solution}\n"
        
        response += "\n如果以上方法都无法解决问题，建议联系网络管理员或ISP技术支持。"
        
        return response
    
    def _handle_tool_usage(self, query):
        """处理工具使用问题"""
        # 识别具体工具
        tool_key = None
        tool_keywords = {
            'port_scan': ['端口', '扫描'],
            'speed_test': ['速度', '测速'],
            'ping': ['ping', '连通'],
            'traceroute': ['路由', '追踪', 'tracert'],
            'dns_query': ['dns', '域名'],
            'wifi_scan': ['wifi', '无线', '扫描'],
            'subnet_calculator': ['子网', '计算'],
            'network_topology': ['拓扑', '结构'],
            'network_diagnostic': ['诊断', '检测']
        }
        
        for key, keywords in tool_keywords.items():
            if any(kw in query for kw in keywords):
                tool_key = key
                break
        
        if tool_key and tool_key in self.knowledge_base['tools']:
            tool = self.knowledge_base['tools'][tool_key]
            response = f"【{tool['name']}】\n\n"
            response += f"功能：{tool['description']}\n\n"
            response += f"使用方法：{tool['usage']}"
            return response
        
        # 返回所有工具列表
        response = "我们提供以下网络工具：\n\n"
        for key, tool in self.knowledge_base['tools'].items():
            response += f"• {tool['name']}：{tool['description'][:30]}...\n"
        
        response += "\n您可以询问具体工具的使用方法，例如：\"如何使用端口扫描？\""
        return response
    
    def _handle_command(self, query):
        """处理命令查询"""
        # 首先在本地文档中搜索
        doc_content = self._search_in_document(query)
        
        if doc_content:
            response = "【根据网络故障排查指南】\n\n"
            response += doc_content
            response += "\n\n[以上内容来自本地知识库文档]"
            return response
        
        # 如果文档中没有找到，使用内置命令列表
        response = "常用网络命令参考：\n\n"
        
        for key, cmd_info in self.knowledge_base['commands'].items():
            response += f"【{key}】\n"
            response += f"命令：{cmd_info['cmd']}\n"
            response += f"说明：{cmd_info['desc']}\n\n"
        
        response += "提示：在命令提示符(cmd)或PowerShell中运行这些命令。"
        return response
    
    def _handle_troubleshooting(self, query):
        """处理故障排除"""
        # 首先在本地文档中搜索
        doc_content = self._search_in_document(query)
        
        if doc_content:
            response = "【根据网络故障排查指南】\n\n"
            response += doc_content
            response += "\n\n[以上内容来自本地知识库文档]"
            return response
        
        # 如果文档中没有找到，使用默认响应
        response = "【网络故障排除指南】\n\n"
        response += "通用排查步骤：\n\n"
        response += "1️⃣ 检查物理连接\n"
        response += "   • 确认网线插好，指示灯正常\n"
        response += "   • 检查WiFi是否连接正确\n\n"
        response += "2️⃣ 重启网络设备\n"
        response += "   • 关闭路由器和光猫电源\n"
        response += "   • 等待30秒后重新开启\n"
        response += "   • 等待设备完全启动（约2分钟）\n\n"
        response += "3️⃣ 检查网络配置\n"
        response += "   • 运行ipconfig查看IP配置\n"
        response += "   • 确认IP地址、网关、DNS设置正确\n\n"
        response += "4️⃣ 测试网络连通性\n"
        response += "   • Ping网关地址（通常是192.168.1.1）\n"
        response += "   • Ping公网地址（如8.8.8.8）\n"
        response += "   • 使用本工具的Ping测试功能\n\n"
        response += "5️⃣ 检查DNS解析\n"
        response += "   • 使用nslookup测试域名解析\n"
        response += "   • 尝试更换DNS服务器\n\n"
        response += "6️⃣ 联系技术支持\n"
        response += "   • 如果以上步骤无法解决，请联系ISP或网络管理员\n"
        
        return response
    
    def _handle_general(self, query):
        """处理一般查询"""
        responses = [
            '我是网络运维智能助手，可以帮您解决以下问题：\n\n'
            '• 网络故障诊断和排查\n'
            '• 网络工具使用指导\n'
            '• 网络命令参考\n'
            '• 网络配置建议\n\n'
            '请描述您遇到的具体问题，我会尽力帮助您！',
            
            '您好！我可以协助您处理各种网络相关的问题。\n\n'
            '您可以这样问我：\n'
            '• "网络很慢怎么办？"\n'
            '• "如何使用端口扫描？"\n'
            '• "常用的网络命令有哪些？"\n'
            '• "无法上网怎么排查？"',
            
            '我是您的网络助手！无论是网络故障、工具使用还是配置问题，我都可以为您提供帮助。\n\n'
            '请告诉我您需要什么帮助？'
        ]
        return responses[0]
    
    def update_config(self, config):
        """更新配置"""
        self.config = config
        self.use_cloud_model = config.get('use_cloud_model', True)
        self.api_key = config.get('api_key', '')
        self.model_name = config.get('model', 'doubao-lite-4k')
    
    def get_suggestions(self):
        """获取建议问题"""
        return [
            '我的网络速度很慢，怎么办？',
            '如何使用端口扫描工具？',
            '常用的网络命令有哪些？',
            '网络断网了怎么排查？',
            'DNS解析失败怎么解决？',
            'WiFi信号弱怎么优化？',
            '如何查看本机IP地址？',
            '网络拓扑图怎么生成？'
        ]
    
    def get_model_list(self):
        """获取支持的模型列表"""
        return {
            'doubao-lite-4k': {
                'name': '豆包 Lite 4K',
                'desc': '轻量级模型，响应快速，适合简单问答',
                'free': True
            },
            'doubao-pro-4k': {
                'name': '豆包 Pro 4K',
                'desc': '专业级模型，回答更准确详细',
                'free': False
            },
            'doubao-lite-32k': {
                'name': '豆包 Lite 32K',
                'desc': '支持长文本，适合复杂问题',
                'free': True
            }
        }