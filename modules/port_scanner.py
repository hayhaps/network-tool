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
    # IANA公有协议端口
    20: ('FTP-Data', 'FTP'),
    21: ('FTP', 'FTP'),
    22: ('SSH', 'SSH'),
    23: ('Telnet', 'TELNET'),
    25: ('SMTP', 'SMTP'),
    53: ('DNS', 'DNS'),
    67: ('DHCP-Server', 'DHCP'),
    68: ('DHCP-Client', 'DHCP'),
    69: ('TFTP', 'TFTP'),
    80: ('HTTP', 'HTTP'),
    110: ('POP3', 'POP3'),
    119: ('NNTP', 'NNTP'),
    123: ('NTP', 'NTP'),
    135: ('MSRPC', 'RPC'),
    137: ('NetBIOS-NS', 'NetBIOS'),
    138: ('NetBIOS-DGM', 'NetBIOS'),
    139: ('NetBIOS-SSN', 'NetBIOS'),
    143: ('IMAP', 'IMAP'),
    161: ('SNMP', 'SNMP'),
    162: ('SNMP-Trap', 'SNMP'),
    179: ('BGP', 'BGP'),
    194: ('IRC', 'IRC'),
    389: ('LDAP', 'LDAP'),
    443: ('HTTPS', 'HTTPS'),
    445: ('SMB', 'SMB'),
    465: ('SMTPS', 'SMTP'),
    514: ('Syslog', 'SYSLOG'),
    515: ('LPD', 'LPD'),
    587: ('SMTP-Submission', 'SMTP'),
    631: ('IPP', 'IPP'),
    636: ('LDAPS', 'LDAP'),
    873: ('rsync', 'RSYNC'),
    993: ('IMAPS', 'IMAP'),
    995: ('POP3S', 'POP3'),
    1080: ('SOCKS', 'SOCKS'),
    1194: ('OpenVPN', 'VPN'),
    1433: ('MSSQL', 'MSSQL'),
    1434: ('MSSQL-UDP', 'MSSQL'),
    1521: ('Oracle', 'ORACLE'),
    1723: ('PPTP', 'PPTP'),
    2049: ('NFS', 'NFS'),
    2082: ('cPanel', 'HTTP'),
    2083: ('cPanel-SSL', 'HTTPS'),
    2181: ('Zookeeper', 'ZOOKEEPER'),
    2375: ('Docker', 'DOCKER'),
    2376: ('Docker-TLS', 'DOCKER'),
    3000: ('Node.js', 'HTTP'),
    3306: ('MySQL', 'MYSQL'),
    3389: ('RDP', 'RDP'),
    4369: ('Erlang-Port', 'ERLANG'),
    5060: ('SIP', 'SIP'),
    5061: ('SIPS', 'SIP'),
    5432: ('PostgreSQL', 'POSTGRESQL'),
    5672: ('RabbitMQ', 'AMQP'),
    5900: ('VNC', 'VNC'),
    6379: ('Redis', 'REDIS'),
    6443: ('Kubernetes', 'KUBERNETES'),
    6667: ('IRC', 'IRC'),
    8000: ('HTTP-Alt', 'HTTP'),
    8008: ('HTTP-Alt', 'HTTP'),
    8080: ('HTTP-Proxy', 'HTTP'),
    8443: ('HTTPS-Alt', 'HTTPS'),
    8888: ('HTTP-Proxy', 'HTTP'),
    9000: ('PHP-FPM', 'HTTP'),
    9090: ('Web-Admin', 'HTTP'),
    9200: ('Elasticsearch', 'HTTP'),
    9300: ('Elasticsearch', 'HTTP'),
    11211: ('Memcached', 'MEMCACHED'),
    27017: ('MongoDB', 'MONGODB'),
    27018: ('MongoDB-Server', 'MONGODB'),
    27019: ('MongoDB-Config', 'MONGODB'),
    28017: ('MongoDB-Web', 'HTTP'),
}


class PortScannerThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, host, start_port=1, end_port=1024, max_threads=200):
        super().__init__()
        self.host = host
        self.start_port = start_port
        self.end_port = end_port
        self.max_threads = max_threads
        self.open_ports = []
        self.scanned_count = 0
        self.common_ports = None
        self.total_ports = end_port - start_port + 1
        self.lock = threading.Lock()
    
    def run(self):
        if self.common_ports:
            ports_to_scan = self.common_ports
            self.total_ports = len(ports_to_scan)
        else:
            ports_to_scan = range(self.start_port, self.end_port + 1)
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for port in ports_to_scan:
                executor.submit(self.scan_port, port)
        
        self.finished_signal.emit(self.open_ports)
    
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex((self.host, port))
            
            if result == 0:
                service_info = COMMON_PORTS.get(port, ('Unknown', 'Unknown'))
                service = service_info[0] if isinstance(service_info, tuple) else service_info
                protocol = service_info[1] if isinstance(service_info, tuple) else 'Unknown'
                banner = self.grab_banner(self.host, port)
                
                port_info = {
                    'port': port,
                    'service': service,
                    'protocol': protocol,
                    'banner': banner,
                    'status': 'Open'
                }
                with self.lock:
                    self.open_ports.append(port_info)
                self.result_signal.emit(port_info)
            
            sock.close()
        except:
            pass
        finally:
            with self.lock:
                self.scanned_count += 1
                progress = int((self.scanned_count / self.total_ports) * 100) if self.total_ports > 0 else 100
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
