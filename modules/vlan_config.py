#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLAN配置模块
功能：VLAN信息查看、配置管理
"""

import subprocess
import platform
import re
from PyQt5.QtCore import QThread, pyqtSignal


class VLANInfoThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            if platform.system().lower() == 'windows':
                vlans = self.get_windows_vlan()
            elif platform.system().lower() == 'linux':
                vlans = self.get_linux_vlan()
            else:
                vlans = self.get_macos_vlan()
            
            self.result_signal.emit(vlans)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit([])
            self.finished_signal.emit()
    
    def get_windows_vlan(self):
        vlans = []
        
        try:
            command = ['powershell', 'Get-NetAdapter', '-IncludeHidden']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            for line in lines:
                if 'VLAN' in line or 'vEthernet' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        vlans.append({
                            'name': parts[0],
                            'interface': parts[1] if len(parts) > 1 else 'Unknown',
                            'status': parts[2] if len(parts) > 2 else 'Unknown'
                        })
        
        except:
            pass
        
        return vlans
    
    def get_linux_vlan(self):
        vlans = []
        
        try:
            command = ['cat', '/proc/net/vlan/config']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            for line in lines[2:]:
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 3:
                        vlans.append({
                            'name': parts[0].strip(),
                            'vlan_id': parts[1].strip(),
                            'interface': parts[2].strip()
                        })
        
        except:
            pass
        
        try:
            command = ['ip', 'link', 'show', 'type', 'vlan']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            
            vlan_pattern = r'(\d+):\s+(\S+).*vlan\s+id\s+(\d+)'
            matches = re.findall(vlan_pattern, output)
            
            for match in matches:
                vlans.append({
                    'index': match[0],
                    'name': match[1],
                    'vlan_id': match[2]
                })
        
        except:
            pass
        
        return vlans
    
    def get_macos_vlan(self):
        vlans = []
        
        try:
            command = ['networksetup', '-listVLANs']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            current_vlan = None
            for line in lines:
                line = line.strip()
                
                if line.startswith('VLAN'):
                    if current_vlan:
                        vlans.append(current_vlan)
                    current_vlan = {'name': line.split(':')[1].strip()}
                
                elif current_vlan:
                    if 'Tag' in line:
                        current_vlan['vlan_id'] = line.split(':')[1].strip()
                    elif 'Device' in line:
                        current_vlan['device'] = line.split(':')[1].strip()
            
            if current_vlan:
                vlans.append(current_vlan)
        
        except:
            pass
        
        return vlans


class NetworkInterfaceThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            if platform.system().lower() == 'windows':
                interfaces = self.get_windows_interfaces()
            elif platform.system().lower() == 'linux':
                interfaces = self.get_linux_interfaces()
            else:
                interfaces = self.get_macos_interfaces()
            
            self.result_signal.emit(interfaces)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit([])
            self.finished_signal.emit()
    
    def get_windows_interfaces(self):
        interfaces = []
        
        try:
            command = ['powershell', 'Get-NetAdapter']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            for line in lines[3:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        interfaces.append({
                            'name': parts[0],
                            'status': parts[2],
                            'mac': parts[7] if len(parts) > 7 else 'Unknown'
                        })
        
        except:
            pass
        
        return interfaces
    
    def get_linux_interfaces(self):
        interfaces = []
        
        try:
            command = ['ip', 'link', 'show']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            
            interface_pattern = r'(\d+):\s+(\S+):\s+<(\S+)>\s+.*link/ether\s+([0-9a-fA-F:]+)'
            matches = re.findall(interface_pattern, output)
            
            for match in matches:
                interfaces.append({
                    'index': match[0],
                    'name': match[1],
                    'status': 'UP' if 'UP' in match[2] else 'DOWN',
                    'mac': match[3]
                })
        
        except:
            pass
        
        return interfaces
    
    def get_macos_interfaces(self):
        interfaces = []
        
        try:
            command = ['ifconfig']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            current_interface = None
            for line in lines:
                if line and not line.startswith('\t') and not line.startswith(' '):
                    if current_interface:
                        interfaces.append(current_interface)
                    
                    parts = line.split(':')
                    current_interface = {
                        'name': parts[0],
                        'status': 'Unknown',
                        'mac': 'Unknown'
                    }
                
                elif current_interface:
                    if 'status:' in line.lower():
                        current_interface['status'] = line.split(':')[1].strip().split(',')[0]
                    elif 'ether' in line.lower():
                        match = re.search(r'ether\s+([0-9a-fA-F:]+)', line)
                        if match:
                            current_interface['mac'] = match.group(1)
            
            if current_interface:
                interfaces.append(current_interface)
        
        except:
            pass
        
        return interfaces


def get_vlan_info():
    thread = VLANInfoThread()
    thread.start()
    thread.wait()
    return thread.result


def get_network_interfaces():
    thread = NetworkInterfaceThread()
    thread.start()
    thread.wait()
    return thread.result


def create_vlan_linux(interface, vlan_id, name=None):
    try:
        if not name:
            name = f"{interface}.{vlan_id}"
        
        commands = [
            ['ip', 'link', 'add', 'link', interface, 'name', name, 'type', 'vlan', 'id', str(vlan_id)],
            ['ip', 'link', 'set', 'dev', name, 'up']
        ]
        
        for cmd in commands:
            subprocess.run(cmd, capture_output=True)
        
        return True, f"VLAN {vlan_id} 创建成功"
    except Exception as e:
        return False, f"创建VLAN失败: {str(e)}"


def delete_vlan_linux(name):
    try:
        command = ['ip', 'link', 'delete', name]
        subprocess.run(command, capture_output=True)
        return True, f"VLAN {name} 删除成功"
    except Exception as e:
        return False, f"删除VLAN失败: {str(e)}"
