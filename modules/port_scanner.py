#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口扫描和服务检测模块
功能：端口扫描、服务识别
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread, pyqtSignal


COMMON_PORTS = {
    21: 'FTP',
    22: 'SSH',
    23: 'Telnet',
    25: 'SMTP',
    53: 'DNS',
    80: 'HTTP',
    110: 'POP3',
    143: 'IMAP',
    443: 'HTTPS',
    445: 'SMB',
    993: 'IMAPS',
    995: 'POP3S',
    1433: 'MSSQL',
    1521: 'Oracle',
    3306: 'MySQL',
    3389: 'RDP',
    5432: 'PostgreSQL',
    5900: 'VNC',
    6379: 'Redis',
    8080: 'HTTP-Proxy',
    8443: 'HTTPS-Alt',
    27017: 'MongoDB'
}


class PortScannerThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, host, start_port=1, end_port=1024, max_threads=100):
        super().__init__()
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.max_threads = max_threads
        self.open_ports = []
        self.scanned_count = 0
        self.total_ports = end_port - start_port + 1
    
    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for port in range(self.start_port, self.end_port + 1):
                executor.submit(self.scan_port, port)
        
        self.finished_signal.emit(self.open_ports)
    
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((self.host, port))
            
            if result == 0:
                service = COMMON_PORTS.get(port, 'Unknown')
                banner = self.grab_banner(self.host, port)
                
                port_info = {
                    'port': port,
                    'service': service,
                    'banner': banner,
                    'status': 'Open'
                }
                self.open_ports.append(port_info)
                self.result_signal.emit(port_info)
            
            sock.close()
        except:
            pass
        finally:
            self.scanned_count += 1
            progress = int((self.scanned_count / self.total_ports) * 100)
            self.progress_signal.emit(progress)
    
    def grab_banner(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((host, port))
            sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            return banner[:100] if banner else 'No banner'
        except:
            return 'No banner'


def scan_single_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def get_service_name(port):
    return COMMON_PORTS.get(port, 'Unknown')


def scan_common_ports(host):
    results = []
    for port in COMMON_PORTS.keys():
        if scan_single_port(host, port):
            results.append({
                'port': port,
                'service': COMMON_PORTS[port],
                'status': 'Open'
            })
    return results
