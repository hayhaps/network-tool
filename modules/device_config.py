#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络设备配置管理模块
功能：IP配置查看、DNS配置、网络适配器管理
"""

import subprocess
import platform
import re
from PyQt5.QtCore import QThread, pyqtSignal


class IPConfigThread(QThread):
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.config_data = {}
    
    def run(self):
        try:
            if platform.system().lower() == 'windows':
                command = ['ipconfig', '/all']
            else:
                command = ['ifconfig']
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            self.result_signal.emit(output)
            
            self.config_data = self.parse_ipconfig(output)
            self.finished_signal.emit(self.config_data)
            
        except Exception as e:
            self.result_signal.emit(f"获取IP配置失败: {str(e)}")
            self.finished_signal.emit({})
    
    def parse_ipconfig(self, output):
        config = {}
        adapters = []
        current_adapter = None
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            if 'adapter' in line.lower() and ':' in line:
                if current_adapter:
                    adapters.append(current_adapter)
                adapter_name = line.split(':')[0].strip()
                current_adapter = {'name': adapter_name}
            
            elif current_adapter:
                if 'IPv4' in line or 'IP Address' in line:
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if match:
                        current_adapter['ipv4'] = match.group(1)
                
                elif 'Subnet' in line or 'Mask' in line:
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if match:
                        current_adapter['subnet'] = match.group(1)
                
                elif 'Gateway' in line:
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if match:
                        current_adapter['gateway'] = match.group(1)
                
                elif 'DNS' in line:
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                    if match:
                        if 'dns' not in current_adapter:
                            current_adapter['dns'] = []
                        current_adapter['dns'].append(match.group(1))
        
        if current_adapter:
            adapters.append(current_adapter)
        
        config['adapters'] = adapters
        return config


class DNSFlushThread(QThread):
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            if platform.system().lower() == 'windows':
                command = ['ipconfig', '/flushdns']
            else:
                command = ['sudo', 'systemd-resolve', '--flush-caches']
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            self.result_signal.emit(process.stdout)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit(f"DNS刷新失败: {str(e)}")
            self.finished_signal.emit()


class NetworkAdapterThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            adapters = []
            
            if platform.system().lower() == 'windows':
                command = ['netsh', 'interface', 'show', 'interface']
                process = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
                
                lines = process.stdout.split('\n')
                for line in lines[3:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            adapters.append({
                                'name': ' '.join(parts[3:]),
                                'status': parts[0],
                                'type': parts[2]
                            })
            
            self.result_signal.emit(adapters)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit([])
            self.finished_signal.emit()


def get_ip_config():
    try:
        if platform.system().lower() == 'windows':
            command = ['ipconfig', '/all']
        else:
            command = ['ifconfig']
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return process.stdout
    except Exception as e:
        return f"错误: {str(e)}"


def flush_dns():
    try:
        if platform.system().lower() == 'windows':
            command = ['ipconfig', '/flushdns']
        else:
            command = ['sudo', 'systemd-resolve', '--flush-caches']
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return process.stdout
    except Exception as e:
        return f"错误: {str(e)}"


def release_ip():
    try:
        if platform.system().lower() == 'windows':
            command = ['ipconfig', '/release']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return process.stdout
        else:
            return "此功能仅支持Windows系统"
    except Exception as e:
        return f"错误: {str(e)}"


def renew_ip():
    try:
        if platform.system().lower() == 'windows':
            command = ['ipconfig', '/renew']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return process.stdout
        else:
            return "此功能仅支持Windows系统"
    except Exception as e:
        return f"错误: {str(e)}"
