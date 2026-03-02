#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wi-Fi信号强度检测模块
功能：Wi-Fi扫描、信号强度检测
"""

import subprocess
import platform
import re
from PyQt5.QtCore import QThread, pyqtSignal


class WifiScannerThread(QThread):
    result_signal = pyqtSignal(list)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            if platform.system().lower() == 'windows':
                networks = self.scan_windows()
            elif platform.system().lower() == 'darwin':
                networks = self.scan_macos()
            else:
                networks = self.scan_linux()
            
            self.result_signal.emit(networks)
            self.finished_signal.emit()
            
        except Exception as e:
            self.result_signal.emit([])
            self.finished_signal.emit()
    
    def scan_windows(self):
        networks = []
        
        try:
            command = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            current_network = None
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('SSID'):
                    if current_network:
                        networks.append(current_network)
                    ssid = line.split(':')[1].strip()
                    current_network = {
                        'ssid': ssid,
                        'signal': 'Unknown',
                        'channel': 'Unknown',
                        'security': 'Unknown',
                        'bssid': 'Unknown'
                    }
                
                elif current_network:
                    if 'Signal' in line:
                        match = re.search(r'(\d+)%', line)
                        if match:
                            current_network['signal'] = match.group(1) + '%'
                    
                    elif 'Channel' in line:
                        match = re.search(r'(\d+)', line)
                        if match:
                            current_network['channel'] = match.group(1)
                    
                    elif 'Authentication' in line:
                        auth = line.split(':')[1].strip()
                        current_network['security'] = auth
                    
                    elif 'BSSID' in line:
                        bssid = line.split(':')[1].strip()
                        current_network['bssid'] = bssid
            
            if current_network:
                networks.append(current_network)
        
        except Exception as e:
            pass
        
        return networks
    
    def scan_macos(self):
        networks = []
        
        try:
            command = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 7:
                        networks.append({
                            'ssid': parts[0],
                            'bssid': parts[1],
                            'signal': parts[2],
                            'channel': parts[3],
                            'security': parts[6] if len(parts) > 6 else 'Unknown'
                        })
        
        except:
            pass
        
        return networks
    
    def scan_linux(self):
        networks = []
        
        try:
            command = ['nmcli', 'dev', 'wifi', 'list']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            lines = output.split('\n')
            
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 8:
                        networks.append({
                            'ssid': parts[1],
                            'signal': parts[6],
                            'channel': parts[4],
                            'security': parts[7] if len(parts) > 7 else 'Unknown',
                            'bssid': 'Unknown'
                        })
        
        except:
            pass
        
        return networks


class WifiSignalMonitorThread(QThread):
    update_signal = pyqtSignal(dict)
    
    def __init__(self, interface=None, interval=2):
        super().__init__()
        self.interface = interface
        self.interval = interval
        self.running = True
    
    def run(self):
        while self.running:
            try:
                if platform.system().lower() == 'windows':
                    signal_info = self.get_windows_signal()
                elif platform.system().lower() == 'darwin':
                    signal_info = self.get_macos_signal()
                else:
                    signal_info = self.get_linux_signal()
                
                self.update_signal.emit(signal_info)
                
            except Exception as e:
                self.update_signal.emit({'error': str(e)})
            
            time.sleep(self.interval)
    
    def get_windows_signal(self):
        try:
            command = ['netsh', 'wlan', 'show', 'interfaces']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            signal_info = {
                'ssid': 'Unknown',
                'signal': 'Unknown',
                'state': 'Unknown'
            }
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'SSID' in line and 'BSSID' not in line:
                    signal_info['ssid'] = line.split(':')[1].strip()
                elif 'Signal' in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        signal_info['signal'] = match.group(1) + '%'
                elif 'State' in line:
                    signal_info['state'] = line.split(':')[1].strip()
            
            return signal_info
        
        except:
            return {'error': '无法获取Wi-Fi信号信息'}
    
    def get_macos_signal(self):
        try:
            command = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            signal_info = {
                'ssid': 'Unknown',
                'signal': 'Unknown',
                'state': 'Unknown'
            }
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'SSID' in line:
                    signal_info['ssid'] = line.split(':')[1].strip()
                elif 'agrCtlRSSI' in line:
                    signal_info['signal'] = line.split(':')[1].strip() + ' dBm'
                elif 'state' in line.lower():
                    signal_info['state'] = line.split(':')[1].strip()
            
            return signal_info
        
        except:
            return {'error': '无法获取Wi-Fi信号信息'}
    
    def get_linux_signal(self):
        try:
            command = ['nmcli', '-t', '-f', 'ACTIVE,SSID,SIGNAL', 'dev', 'wifi', 'list']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = process.stdout
            for line in output.split('\n'):
                if line.startswith('yes:'):
                    parts = line.split(':')
                    return {
                        'ssid': parts[1] if len(parts) > 1 else 'Unknown',
                        'signal': parts[2] + '%' if len(parts) > 2 else 'Unknown',
                        'state': 'Connected'
                    }
            
            return {'ssid': 'Unknown', 'signal': 'Unknown', 'state': 'Disconnected'}
        
        except:
            return {'error': '无法获取Wi-Fi信号信息'}
    
    def stop(self):
        self.running = False


def scan_wifi_networks():
    scanner = WifiScannerThread()
    scanner.start()
    scanner.wait()
    return scanner.result


def get_current_wifi_signal():
    try:
        if platform.system().lower() == 'windows':
            command = ['netsh', 'wlan', 'show', 'interfaces']
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return process.stdout
        else:
            return "此功能主要支持Windows系统"
    except Exception as e:
        return f"错误: {str(e)}"
