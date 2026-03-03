#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连通性测试模块
功能：Ping测试、Traceroute路由追踪
"""

import subprocess
import platform
import re
import socket
from PyQt5.QtCore import QThread, pyqtSignal


class PingThread(QThread):
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, host, count=4):
        super().__init__()
        self.host = host.strip()
        self.count = count
        self.results = []
    
    def is_valid_host(self, host):
        """验证主机名或IP地址是否有效"""
        if not host:
            return False, "主机地址不能为空"
        
        # 检查是否是有效的IP地址
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(ip_pattern, host)
        if match:
            # 验证每个段是否在0-255范围内
            for i in range(1, 5):
                octet = int(match.group(i))
                if octet < 0 or octet > 255:
                    return False, f"IP地址格式错误: 第{i}段数值必须在0-255之间"
            return True, None
        
        # 检查是否是有效的域名
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(domain_pattern, host):
            return True, None
        
        return False, f"无效的主机地址: {host}"
    
    def run(self):
        # 验证主机地址
        is_valid, error_msg = self.is_valid_host(self.host)
        if not is_valid:
            self.result_signal.emit(f"[错误] {error_msg}")
            self.finished_signal.emit([f"错误: {error_msg}"])
            return
        
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, str(self.count), self.host]
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.results.append(output.strip())
                    self.result_signal.emit(output.strip())
            
            self.finished_signal.emit(self.results)
        except Exception as e:
            self.result_signal.emit(f"Ping测试失败: {str(e)}")
            self.finished_signal.emit([f"错误: {str(e)}"])


class TracerouteThread(QThread):
    result_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, host, max_hops=30):
        super().__init__()
        self.host = host.strip()
        self.max_hops = max_hops
        self.results = []
        self.system = platform.system().lower()
    
    def is_valid_host(self, host):
        """验证主机名或IP地址是否有效"""
        if not host:
            return False, "主机地址不能为空"
        
        # 检查是否是有效的IP地址
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(ip_pattern, host)
        if match:
            for i in range(1, 5):
                octet = int(match.group(i))
                if octet < 0 or octet > 255:
                    return False, f"IP地址格式错误: 第{i}段数值必须在0-255之间"
            return True, None
        
        # 检查是否是有效的域名
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(domain_pattern, host):
            return True, None
        
        return False, f"无效的主机地址: {host}"
    
    def run(self):
        # 验证主机地址
        is_valid, error_msg = self.is_valid_host(self.host)
        if not is_valid:
            self.result_signal.emit(f"[错误] {error_msg}")
            self.finished_signal.emit([f"错误: {error_msg}"])
            return
        
        self.result_signal.emit(f"正在追踪到 {self.host} 的路由...\n")
        self.result_signal.emit(f"操作系统: {self.system.upper()}\n")
        
        if self.system == 'windows':
            self._traceroute_windows()
        elif self.system == 'darwin':
            self._traceroute_macos()
        else:
            self._traceroute_linux()
    
    def _traceroute_windows(self):
        """Windows系统使用tracert命令"""
        command = ['tracert', '-h', str(self.max_hops), self.host]
        self._execute_command(command)
    
    def _traceroute_macos(self):
        """macOS系统尝试多种方法"""
        self.result_signal.emit("尝试方法1: 使用traceroute (UDP)...\n")
        command = ['traceroute', '-m', str(self.max_hops), self.host]
        success = self._execute_command_with_fallback(command)
        
        if not success:
            self.result_signal.emit("\n尝试方法2: 使用traceroute -I (ICMP)...\n")
            command = ['traceroute', '-I', '-m', str(self.max_hops), self.host]
            success = self._execute_command_with_fallback(command)
        
        if not success:
            self.result_signal.emit("\n尝试方法3: 使用ping进行路由探测...\n")
            self._ping_trace()
    
    def _traceroute_linux(self):
        """Linux系统使用traceroute命令"""
        self.result_signal.emit("尝试方法1: 使用traceroute (UDP)...\n")
        command = ['traceroute', '-m', str(self.max_hops), self.host]
        success = self._execute_command_with_fallback(command)
        
        if not success:
            self.result_signal.emit("\n尝试方法2: 使用traceroute -I (ICMP)...\n")
            command = ['traceroute', '-I', '-m', str(self.max_hops), self.host]
            success = self._execute_command_with_fallback(command)
        
        if not success:
            self.result_signal.emit("\n尝试方法3: 使用ping进行路由探测...\n")
            self._ping_trace()
    
    def _execute_command_with_fallback(self, command):
        """执行命令并检查是否成功"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            has_output = False
            has_permission_error = False
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    has_output = True
                    self.results.append(output.strip())
                    self.result_signal.emit(output.strip())
            
            stderr_output = process.stderr.read()
            if stderr_output:
                if 'Operation not permitted' in stderr_output or 'permission' in stderr_output.lower():
                    has_permission_error = True
                    self.result_signal.emit(f"\n[提示] 此方法需要管理员权限")
                else:
                    self.result_signal.emit(f"\n[错误] {stderr_output.strip()}")
            
            if has_output and not has_permission_error:
                self.finished_signal.emit(self.results)
                return True
            elif has_permission_error:
                return False
            else:
                return False
                
        except PermissionError:
            self.result_signal.emit("\n[提示] 此方法需要管理员权限")
            return False
        except FileNotFoundError:
            self.result_signal.emit(f"\n[错误] 未找到命令: {command[0]}")
            return False
        except Exception as e:
            self.result_signal.emit(f"\n[错误] {str(e)}")
            return False
    
    def _execute_command(self, command):
        """执行命令（Windows专用）"""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.results.append(output.strip())
                    self.result_signal.emit(output.strip())
            
            stderr_output = process.stderr.read()
            if stderr_output:
                self.result_signal.emit(f"\n[错误] {stderr_output.strip()}")
            
            self.finished_signal.emit(self.results)
        except PermissionError:
            self.result_signal.emit("\n[错误] tracert需要管理员权限")
            self.result_signal.emit("请以管理员身份运行程序")
            self.finished_signal.emit(self.results)
        except Exception as e:
            self.result_signal.emit(f"Traceroute测试失败: {str(e)}")
            self.finished_signal.emit([f"错误: {str(e)}"])
    
    def _ping_trace(self):
        """使用ping进行简单的路由探测（替代方案）"""
        self.result_signal.emit("使用ping进行路由探测（无需特殊权限）\n")
        self.result_signal.emit("=" * 60 + "\n")
        
        try:
            for ttl in range(1, min(self.max_hops + 1, 16)):
                if self.system == 'windows':
                    command = ['ping', '-n', '1', '-i', str(ttl), self.host]
                else:
                    command = ['ping', '-c', '1', '-t', str(ttl), self.host]
                
                try:
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore',
                        timeout=3
                    )
                    
                    output = result.stdout
                    
                    if 'TTL expired' in output or 'Time to live exceeded' in output:
                        match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', output)
                        if match:
                            hop_ip = match.group(1)
                            self.result_signal.emit(f"{ttl:2d}  {hop_ip}")
                            self.results.append(f"{ttl:2d}  {hop_ip}")
                    elif 'Reply from' in output or 'bytes from' in output:
                        self.result_signal.emit(f"{ttl:2d}  {self.host} (目标已到达)")
                        self.results.append(f"{ttl:2d}  {self.host} (目标已到达)")
                        break
                    else:
                        self.result_signal.emit(f"{ttl:2d}  * * * 请求超时")
                        self.results.append(f"{ttl:2d}  * * * 请求超时")
                
                except subprocess.TimeoutExpired:
                    self.result_signal.emit(f"{ttl:2d}  * * * 请求超时")
                    self.results.append(f"{ttl:2d}  * * * 请求超时")
                except Exception as e:
                    self.result_signal.emit(f"{ttl:2d}  错误: {str(e)}")
                    self.results.append(f"{ttl:2d}  错误: {str(e)}")
            
            self.result_signal.emit("\n" + "=" * 60)
            self.result_signal.emit("\n提示: 这是使用ping进行的简化路由探测")
            self.result_signal.emit("如需更详细的路由信息，请在终端中运行:")
            if self.system == 'darwin':
                self.result_signal.emit(f"  sudo traceroute -I {self.host}")
            elif self.system == 'linux':
                self.result_signal.emit(f"  sudo traceroute {self.host}")
            else:
                self.result_signal.emit(f"  tracert {self.host}")
            
            self.finished_signal.emit(self.results)
            
        except Exception as e:
            self.result_signal.emit(f"\n路由探测失败: {str(e)}")
            self.finished_signal.emit([f"错误: {str(e)}"])


def ping_host(host, count=4):
    results = []
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(count), host]
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        results = process.stdout.split('\n')
    except Exception as e:
        results = [f"错误: {str(e)}"]
    
    return results


def traceroute_host(host, max_hops=30):
    results = []
    system = platform.system().lower()
    
    if system == 'windows':
        command = ['tracert', '-h', str(max_hops), host]
    else:
        command = ['traceroute', '-m', str(max_hops), host]
    
    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        results = process.stdout.split('\n')
    except Exception as e:
        results = [f"错误: {str(e)}"]
    
    return results


def check_host_reachable(host):
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, 80))
        return True
    except:
        return False
