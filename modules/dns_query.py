#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DNS查询和分析模块
功能：DNS解析、DNS记录查询
"""

import socket
import dns.resolver
import dns.reversename
from PyQt5.QtCore import QThread, pyqtSignal


class DNSQueryThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self, domain, record_type='A'):
        super().__init__()
        self.domain = domain
        self.record_type = record_type.upper()
    
    def run(self):
        result = {
            'domain': self.domain,
            'record_type': self.record_type,
            'records': [],
            'error': None
        }
        
        try:
            if self.record_type == 'PTR':
                answers = self.reverse_dns_lookup(self.domain)
                result['records'] = answers
            else:
                answers = dns.resolver.resolve(self.domain, self.record_type)
                for rdata in answers:
                    if self.record_type in ['MX']:
                        result['records'].append({
                            'preference': rdata.preference,
                            'exchange': str(rdata.exchange)
                        })
                    elif self.record_type in ['NS', 'CNAME', 'PTR']:
                        result['records'].append(str(rdata))
                    elif self.record_type in ['TXT']:
                        result['records'].append(str(rdata).strip('"'))
                    elif self.record_type in ['SOA']:
                        result['records'].append({
                            'mname': str(rdata.mname),
                            'rname': str(rdata.rname),
                            'serial': rdata.serial,
                            'refresh': rdata.refresh,
                            'retry': rdata.retry,
                            'expire': rdata.expire,
                            'minimum': rdata.minimum
                        })
                    else:
                        result['records'].append(str(rdata))
        
        except dns.resolver.NoAnswer:
            result['error'] = f"没有找到 {self.record_type} 记录"
        except dns.resolver.NXDOMAIN:
            result['error'] = "域名不存在"
        except dns.resolver.NoNameservers:
            result['error'] = "无法连接到DNS服务器"
        except Exception as e:
            result['error'] = str(e)
        
        self.result_signal.emit(result)
        self.finished_signal.emit()
    
    def reverse_dns_lookup(self, ip):
        try:
            reverse_name = dns.reversename.from_address(ip)
            answers = dns.resolver.resolve(reverse_name, 'PTR')
            return [str(rdata) for rdata in answers]
        except:
            return []


class DNSResolveThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname
    
    def run(self):
        result = {
            'hostname': self.hostname,
            'ipv4': [],
            'ipv6': [],
            'error': None
        }
        
        try:
            ipv4_addresses = socket.getaddrinfo(self.hostname, None, socket.AF_INET)
            for addr in ipv4_addresses:
                ip = addr[4][0]
                if ip not in result['ipv4']:
                    result['ipv4'].append(ip)
        
        except socket.gaierror:
            pass
        
        try:
            ipv6_addresses = socket.getaddrinfo(self.hostname, None, socket.AF_INET6)
            for addr in ipv6_addresses:
                ip = addr[4][0]
                if ip not in result['ipv6']:
                    result['ipv6'].append(ip)
        
        except socket.gaierror:
            pass
        
        if not result['ipv4'] and not result['ipv6']:
            result['error'] = "无法解析域名"
        
        self.result_signal.emit(result)
        self.finished_signal.emit()


class DNSCacheThread(QThread):
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            import subprocess
            import platform
            
            if platform.system().lower() == 'windows':
                command = ['ipconfig', '/displaydns']
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                self.result_signal.emit(process.stdout)
            else:
                self.result_signal.emit("此功能仅支持Windows系统")
        
        except Exception as e:
            self.result_signal.emit(f"获取DNS缓存失败: {str(e)}")
        
        self.finished_signal.emit()


def dns_lookup(domain, record_type='A'):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return [str(rdata) for rdata in answers]
    except:
        return []


def reverse_dns(ip):
    try:
        reverse_name = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(reverse_name, 'PTR')
        return [str(rdata) for rdata in answers]
    except:
        return []


def resolve_hostname(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None


def resolve_hostname_ex(hostname):
    try:
        return socket.getaddrinfo(hostname, None)
    except:
        return []
