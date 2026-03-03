# -*- coding: utf-8 -*-
"""
网络抓包模块
使用psutil实现网络连接监控
无需管理员权限
"""

import socket
import time
import platform
import threading
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def is_windows():
    """检查是否为Windows系统"""
    return platform.system() == 'Windows'


def get_protocol_name(protocol_num):
    """获取协议名称"""
    protocols = {
        socket.IPPROTO_TCP: 'TCP',
        socket.IPPROTO_UDP: 'UDP',
    }
    return protocols.get(protocol_num, f'IP-{protocol_num}')


def get_process_name(pid):
    """获取进程名称"""
    try:
        if pid and pid > 0:
            proc = psutil.Process(pid)
            return proc.name()
    except:
        pass
    return ''


class PacketCaptureThread(QThread):
    """网络连接监控线程"""
    packet_signal = pyqtSignal(dict)
    stats_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, interface=None, filter_protocol=None, filter_port=None):
        super().__init__()
        self.interface = interface
        self.filter_protocol = filter_protocol
        self.filter_port = filter_port
        self.running = False
        self.packet_count = 0
        self.byte_count = 0
        self.seen_connections = set()
        
    def run(self):
        """开始网络监控"""
        try:
            if not HAS_PSUTIL:
                self.error_signal.emit(
                    "需要安装psutil库！\n\n"
                    "请运行: pip install psutil"
                )
                return
                
            self.running = True
            self.packet_count = 0
            self.byte_count = 0
            self.seen_connections = set()
            
            # 获取初始网络IO统计
            net_io_start = psutil.net_io_counters()
            
            while self.running:
                try:
                    # 获取当前网络连接
                    connections = psutil.net_connections(kind='inet')
                    
                    for conn in connections:
                        if not self.running:
                            break
                            
                        # 创建连接标识
                        conn_id = (
                            conn.laddr.ip if conn.laddr else '',
                            conn.laddr.port if conn.laddr else 0,
                            conn.raddr.ip if conn.raddr else '',
                            conn.raddr.port if conn.raddr else 0,
                            conn.status,
                            conn.pid or 0
                        )
                        
                        # 只处理新连接
                        if conn_id in self.seen_connections:
                            continue
                            
                        self.seen_connections.add(conn_id)
                        
                        # 过滤条件
                        if not self.should_display_connection(conn):
                            continue
                            
                        # 构建数据包信息
                        packet_info = self.build_packet_info(conn)
                        if packet_info:
                            self.packet_count += 1
                            self.packet_signal.emit(packet_info)
                            
                    # 获取网络IO统计
                    net_io = psutil.net_io_counters()
                    self.byte_count = net_io.bytes_sent + net_io.bytes_recv
                    
                    self.stats_signal.emit({
                        'packet_count': self.packet_count,
                        'byte_count': self.byte_count
                    })
                    
                    # 短暂休眠
                    time.sleep(0.5)
                    
                except psutil.AccessDenied:
                    # 某些连接可能无法访问，跳过
                    continue
                except Exception:
                    continue
                    
        except Exception as e:
            self.error_signal.emit(f"网络监控错误: {str(e)}")
            
    def should_display_connection(self, conn):
        """检查是否应该显示该连接"""
        # 协议过滤
        if self.filter_protocol:
            proto_name = 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
            if proto_name != self.filter_protocol:
                return False
                
        # 端口过滤
        if self.filter_port:
            local_port = conn.laddr.port if conn.laddr else 0
            remote_port = conn.raddr.port if conn.raddr else 0
            if local_port != self.filter_port and remote_port != self.filter_port:
                return False
                
        # 只显示有远程地址的连接
        if not conn.raddr:
            return False
            
        return True
        
    def build_packet_info(self, conn):
        """构建连接信息"""
        try:
            proto_name = 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
            
            local_ip = conn.laddr.ip if conn.laddr else ''
            local_port = conn.laddr.port if conn.laddr else 0
            remote_ip = conn.raddr.ip if conn.raddr else ''
            remote_port = conn.raddr.port if conn.raddr else 0
            
            # 获取进程名
            process_name = get_process_name(conn.pid) if conn.pid else ''
            
            # 构建信息
            info = f"{local_port} → {remote_port}"
            if process_name:
                info += f" [{process_name}]"
            if conn.status:
                info += f" {conn.status}"
                
            return {
                'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
                'source_ip': local_ip,
                'dest_ip': remote_ip,
                'protocol': proto_name,
                'source_port': str(local_port),
                'dest_port': str(remote_port),
                'info': info,
                'process': process_name,
                'status': conn.status or ''
            }
            
        except Exception:
            return None
            
    def stop(self):
        """停止监控"""
        self.running = False


class NetworkTrafficMonitor(QThread):
    """网络流量监控线程"""
    traffic_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        
    def run(self):
        """开始流量监控"""
        try:
            if not HAS_PSUTIL:
                self.error_signal.emit("需要安装psutil库")
                return
                
            self.running = True
            old_stats = psutil.net_io_counters()
            
            while self.running:
                time.sleep(1.0)
                
                if not self.running:
                    break
                    
                new_stats = psutil.net_io_counters()
                
                # 计算速率
                bytes_sent_delta = new_stats.bytes_sent - old_stats.bytes_sent
                bytes_recv_delta = new_stats.bytes_recv - old_stats.bytes_recv
                packets_sent_delta = new_stats.packets_sent - old_stats.packets_sent
                packets_recv_delta = new_stats.packets_recv - old_stats.packets_recv
                
                # 转换为KB/s
                upload_speed = bytes_sent_delta / 1024
                download_speed = bytes_recv_delta / 1024
                
                self.traffic_signal.emit({
                    'upload_speed': upload_speed,
                    'download_speed': download_speed,
                    'upload_speed_str': f"{upload_speed:.2f} KB/s",
                    'download_speed_str': f"{download_speed:.2f} KB/s",
                    'total_upload': new_stats.bytes_sent,
                    'total_download': new_stats.bytes_recv,
                    'packets_sent': new_stats.packets_sent,
                    'packets_recv': new_stats.packets_recv
                })
                
                old_stats = new_stats
                
        except Exception as e:
            self.error_signal.emit(f"流量监控错误: {str(e)}")
            
    def stop(self):
        """停止监控"""
        self.running = False
