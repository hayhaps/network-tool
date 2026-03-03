# -*- coding: utf-8 -*-
"""
HTTP Watch模块
监控HTTP/HTTPS请求和响应
Windows系统优先适配
"""

import socket
import threading
import time
import select
import platform
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal


def is_windows():
    """检查是否为Windows系统"""
    return platform.system() == 'Windows'


class HTTPWatchThread(QThread):
    """HTTP监控线程"""
    request_signal = pyqtSignal(dict)
    stats_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, port=8080, filter_host=None):
        super().__init__()
        self.port = port
        self.filter_host = filter_host
        self.running = False
        self.request_count = 0
        self.server_socket = None
        self.client_threads = []
        
    def run(self):
        """启动HTTP代理监听"""
        try:
            self.running = True
            self.request_count = 0
            
            # 创建代理服务器
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Windows下设置非阻塞模式
            if is_windows():
                self.server_socket.setblocking(False)
                
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(20)
            
            while self.running:
                try:
                    if is_windows():
                        # Windows使用select
                        readable, _, _ = select.select([self.server_socket], [], [], 1.0)
                        if not readable:
                            continue
                            
                    client_socket, client_addr = self.server_socket.accept()
                    client_socket.settimeout(10.0)
                    
                    # 在新线程中处理请求
                    handler_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    handler_thread.start()
                    self.client_threads.append(handler_thread)
                    
                    # 清理已结束的线程
                    self.client_threads = [t for t in self.client_threads if t.is_alive()]
                    
                except socket.timeout:
                    continue
                except OSError:
                    continue
                except Exception as e:
                    if self.running:
                        continue
                    
        except OSError as e:
            if "Address already in use" in str(e) or "10048" in str(e):
                self.error_signal.emit(f"端口 {self.port} 已被占用，请更换端口")
            else:
                self.error_signal.emit(f"启动HTTP代理失败: {str(e)}")
        except Exception as e:
            self.error_signal.emit(f"启动HTTP代理失败: {str(e)}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """清理资源"""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
            
    def handle_client(self, client_socket, client_addr):
        """处理客户端请求"""
        target_socket = None
        try:
            # 接收请求数据
            request_data = self.recv_all(client_socket, timeout=5.0)
                
            if not request_data:
                return
                
            # 解析HTTP请求
            request_info = self.parse_http_request(request_data)
            if not request_info:
                return
                
            # 检查过滤条件
            if self.filter_host and self.filter_host not in request_info.get('host', ''):
                return
                
            # 处理CONNECT方法（HTTPS）
            if request_info.get('method') == 'CONNECT':
                self.handle_connect(client_socket, request_info)
                return
                
            # 转发请求到目标服务器
            start_time = time.time()
            response_info = self.forward_request(request_info, request_data)
            duration = int((time.time() - start_time) * 1000)
            
            # 发送响应回客户端
            if response_info and 'raw_response' in response_info:
                try:
                    client_socket.sendall(response_info['raw_response'])
                except:
                    pass
                    
            # 发送请求信息到UI
            self.request_count += 1
            self.request_signal.emit({
                'id': self.request_count,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'method': request_info.get('method', 'GET'),
                'url': request_info.get('url', ''),
                'host': request_info.get('host', ''),
                'path': request_info.get('path', '/'),
                'status_code': response_info.get('status_code', 0) if response_info else 0,
                'status_text': response_info.get('status_text', '') if response_info else '',
                'request_size': len(request_data),
                'response_size': len(response_info.get('raw_response', b'')) if response_info else 0,
                'duration': duration
            })
            
            # 更新统计
            self.stats_signal.emit({
                'request_count': self.request_count
            })
            
        except Exception:
            pass
        finally:
            try:
                client_socket.close()
            except:
                pass
            if target_socket:
                try:
                    target_socket.close()
                except:
                    pass
                    
    def recv_all(self, sock, timeout=5.0):
        """接收所有数据"""
        data = b''
        sock.settimeout(timeout)
        
        try:
            while True:
                try:
                    chunk = sock.recv(8192)
                    if not chunk:
                        break
                    data += chunk
                    
                    # 检查是否接收完HTTP头部
                    if b'\r\n\r\n' in data:
                        # 检查Content-Length
                        header_end = data.find(b'\r\n\r\n')
                        headers = data[:header_end].decode('utf-8', errors='ignore').lower()
                        
                        # 查找Content-Length
                        content_length = 0
                        for line in headers.split('\r\n'):
                            if 'content-length:' in line:
                                try:
                                    content_length = int(line.split(':')[1].strip())
                                except:
                                    pass
                                break
                                
                        # 检查是否接收完所有数据
                        body_start = header_end + 4
                        body_received = len(data) - body_start
                        
                        if body_received >= content_length:
                            break
                            
                except socket.timeout:
                    break
                except:
                    break
                    
        except:
            pass
            
        return data
        
    def handle_connect(self, client_socket, request_info):
        """处理HTTPS CONNECT请求"""
        target_socket = None
        try:
            host = request_info.get('host', '')
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 443
                
            # 连接目标服务器
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10.0)
            target_socket.connect((host, port))
            
            # 发送200响应
            client_socket.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            
            # 记录请求
            self.request_count += 1
            self.request_signal.emit({
                'id': self.request_count,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'method': 'CONNECT',
                'url': f"https://{request_info.get('host', '')}",
                'host': request_info.get('host', ''),
                'path': '/',
                'status_code': 200,
                'status_text': 'Connection Established',
                'request_size': 0,
                'response_size': 0,
                'duration': 0
            })
            
            self.stats_signal.emit({'request_count': self.request_count})
            
            # 转发数据（简化处理，不解密）
            client_socket.setblocking(False)
            target_socket.setblocking(False)
            
            while self.running:
                try:
                    readable, _, _ = select.select([client_socket, target_socket], [], [], 1.0)
                    
                    for sock in readable:
                        try:
                            data = sock.recv(8192)
                            if not data:
                                return
                            if sock is client_socket:
                                target_socket.sendall(data)
                            else:
                                client_socket.sendall(data)
                        except:
                            return
                            
                except:
                    break
                    
        except Exception:
            pass
        finally:
            try:
                client_socket.close()
            except:
                pass
            if target_socket:
                try:
                    target_socket.close()
                except:
                    pass
                    
    def parse_http_request(self, data):
        """解析HTTP请求"""
        try:
            # 分离头部和主体
            header_end = data.find(b'\r\n\r\n')
            if header_end == -1:
                return None
                
            header_data = data[:header_end].decode('utf-8', errors='ignore')
            
            lines = header_data.split('\r\n')
            if not lines:
                return None
                
            # 解析请求行
            request_line = lines[0]
            parts = request_line.split(' ')
            if len(parts) < 2:
                return None
                
            method = parts[0]
            path = parts[1]
            
            # 解析头部
            headers = {}
            host = ''
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    headers[key] = value
                    
                    if key.lower() == 'host':
                        host = value
                        
            # 构建完整URL
            url = f"http://{host}{path}" if host else path
            
            return {
                'method': method,
                'path': path,
                'host': host,
                'url': url,
                'headers': headers
            }
            
        except Exception:
            return None
            
    def forward_request(self, request_info, request_data):
        """转发请求到目标服务器"""
        target_socket = None
        try:
            host = request_info.get('host', '')
            if not host:
                return None
                
            # 分离主机和端口
            if ':' in host:
                host, port = host.split(':')
                port = int(port)
            else:
                port = 80
                
            # 连接到目标服务器
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(15.0)
            target_socket.connect((host, port))
            
            # 发送请求
            target_socket.sendall(request_data)
            
            # 接收响应
            response_data = self.recv_all(target_socket, timeout=15.0)
            
            target_socket.close()
            target_socket = None
            
            # 解析响应
            response_info = self.parse_http_response(response_data)
            if response_info:
                response_info['raw_response'] = response_data
                
            return response_info
            
        except Exception as e:
            return {
                'status_code': 502,
                'status_text': f'Bad Gateway',
                'headers': {},
                'raw_response': b'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n'
            }
        finally:
            if target_socket:
                try:
                    target_socket.close()
                except:
                    pass
            
    def parse_http_response(self, data):
        """解析HTTP响应"""
        try:
            if not data:
                return None
                
            # 分离头部和主体
            header_end = data.find(b'\r\n\r\n')
            if header_end == -1:
                return None
                
            header_data = data[:header_end].decode('utf-8', errors='ignore')
            
            lines = header_data.split('\r\n')
            if not lines:
                return None
                
            # 解析状态行
            status_line = lines[0]
            parts = status_line.split(' ', 2)
            if len(parts) < 2:
                return None
                
            status_code = int(parts[1])
            status_text = parts[2] if len(parts) > 2 else ''
            
            # 解析头部
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
                    
            return {
                'status_code': status_code,
                'status_text': status_text,
                'headers': headers
            }
            
        except Exception:
            return None
            
    def stop(self):
        """停止HTTP监控"""
        self.running = False
        self.cleanup()
