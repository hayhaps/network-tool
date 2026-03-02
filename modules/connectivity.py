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
        self.host = host
        self.count = count
        self.results = []
    
    def run(self):
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
        self.host = host
        self.max_hops = max_hops
        self.results = []
    
    def run(self):
        if platform.system().lower() == 'windows':
            command = ['tracert', '-h', str(self.max_hops), self.host]
        else:
            command = ['traceroute', '-m', str(self.max_hops), self.host]
        
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
            
            # 检查stderr是否有错误
            stderr_output = process.stderr.read()
            if stderr_output and 'Operation not permitted' in stderr_output:
                self.result_signal.emit("\n[错误] traceroute需要管理员/root权限")
                self.result_signal.emit("请在终端中使用以下命令：")
                if platform.system().lower() == 'windows':
                    self.result_signal.emit("  以管理员身份运行程序")
                else:
                    self.result_signal.emit("  sudo traceroute -m {} {}".format(self.max_hops, self.host))
                self.result_signal.emit("\n或者尝试使用ping命令测试网络连通性")
            
            self.finished_signal.emit(self.results)
        except PermissionError:
            self.result_signal.emit("\n[错误] traceroute需要管理员/root权限")
            if platform.system().lower() == 'windows':
                self.result_signal.emit("请以管理员身份运行程序")
            else:
                self.result_signal.emit("请使用sudo运行: sudo traceroute -m {} {}".format(self.max_hops, self.host))
            self.result_signal.emit("\n或者尝试使用ping命令测试网络连通性")
            self.finished_signal.emit(self.results)
        except Exception as e:
            self.result_signal.emit(f"Traceroute测试失败: {str(e)}")
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
    if platform.system().lower() == 'windows':
        command = ['tracert', '-h', str(max_hops), self.host]
    else:
        command = ['traceroute', '-m', str(max_hops), self.host]
    
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
