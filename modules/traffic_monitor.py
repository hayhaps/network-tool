#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流量分析和监控模块
功能：网络流量监控、连接状态查看
"""

import psutil
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


class TrafficMonitorThread(QThread):
    update_signal = pyqtSignal(dict)
    
    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.running = True
    
    def run(self):
        old_stats = psutil.net_io_counters()
        
        while self.running:
            time.sleep(self.interval)
            
            new_stats = psutil.net_io_counters()
            
            bytes_sent = new_stats.bytes_sent - old_stats.bytes_sent
            bytes_recv = new_stats.bytes_recv - old_stats.bytes_recv
            
            upload_speed = bytes_sent / self.interval
            download_speed = bytes_recv / self.interval
            
            data = {
                'upload_speed': upload_speed,
                'download_speed': download_speed,
                'total_sent': new_stats.bytes_sent,
                'total_recv': new_stats.bytes_recv,
                'packets_sent': new_stats.packets_sent,
                'packets_recv': new_stats.packets_recv,
                'error_in': new_stats.errin,
                'error_out': new_stats.errout,
                'drop_in': new_stats.dropin,
                'drop_out': new_stats.dropout
            }
            
            self.update_signal.emit(data)
            old_stats = new_stats
    
    def stop(self):
        self.running = False


class NetworkConnectionsThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            connections = psutil.net_connections(kind='inet')
            conn_list = []
            
            for conn in connections:
                if conn.status:
                    conn_info = {
                        'fd': conn.fd,
                        'family': 'IPv4' if conn.family == 2 else 'IPv6',
                        'type': 'TCP' if conn.type == 1 else 'UDP',
                        'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A',
                        'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else 'N/A',
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    
                    if conn.pid:
                        try:
                            process = psutil.Process(conn.pid)
                            conn_info['process_name'] = process.name()
                        except:
                            conn_info['process_name'] = 'Unknown'
                    else:
                        conn_info['process_name'] = 'N/A'
                    
                    conn_list.append(conn_info)
            
            self.result_signal.emit(conn_list)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit([])
            self.finished_signal.emit()


class NetworkInterfacesThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            interface_data = {}
            
            for name, addrs in interfaces.items():
                interface_data[name] = {
                    'addresses': [],
                    'is_up': stats[name].isup if name in stats else False,
                    'speed': stats[name].speed if name in stats else 0,
                    'mtu': stats[name].mtu if name in stats else 0
                }
                
                for addr in addrs:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    interface_data[name]['addresses'].append(addr_info)
            
            self.result_signal.emit(interface_data)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit({})
            self.finished_signal.emit()


def get_network_io_stats():
    try:
        stats = psutil.net_io_counters()
        return {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv,
            'error_in': stats.errin,
            'error_out': stats.errout,
            'drop_in': stats.dropin,
            'drop_out': stats.dropout
        }
    except:
        return {}


def get_network_connections():
    try:
        connections = psutil.net_connections(kind='inet')
        return connections
    except:
        return []


def get_network_interfaces():
    try:
        return psutil.net_if_addrs()
    except:
        return {}


def format_bytes(bytes_value):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
