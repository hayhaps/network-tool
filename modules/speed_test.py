#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络速度测试模块
功能：带宽测试、延迟测试
"""

import time
import socket
import urllib.request
import speedtest
from PyQt5.QtCore import QThread, pyqtSignal


class SpeedTestThread(QThread):
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.results = {}
    
    def run(self):
        try:
            self.progress_signal.emit("正在初始化速度测试...")
            st = speedtest.Speedtest()
            
            self.progress_signal.emit("正在选择最佳服务器...")
            st.get_best_server()
            
            self.progress_signal.emit("正在测试下载速度...")
            download_speed = st.download() / 1_000_000
            
            self.progress_signal.emit("正在测试上传速度...")
            upload_speed = st.upload() / 1_000_000
            
            self.results = {
                'download': download_speed,
                'upload': upload_speed,
                'ping': st.results.ping,
                'server': st.results.server['sponsor'],
                'location': st.results.server['name']
            }
            
            self.result_signal.emit(self.results)
            self.finished_signal.emit()
            
        except Exception as e:
            self.progress_signal.emit(f"速度测试失败: {str(e)}")
            self.finished_signal.emit()


class LatencyTestThread(QThread):
    result_signal = pyqtSignal(float)
    finished_signal = pyqtSignal()
    
    def __init__(self, host, count=10):
        super().__init__()
        self.host = host
        self.count = count
    
    def run(self):
        latencies = []
        
        for i in range(self.count):
            try:
                start = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((self.host, 80))
                end = time.time()
                latency = (end - start) * 1000
                latencies.append(latency)
                sock.close()
                self.result_signal.emit(latency)
            except Exception as e:
                self.result_signal.emit(-1)
            
            time.sleep(0.5)
        
        self.finished_signal.emit()


class BandwidthTestThread(QThread):
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(float)
    finished_signal = pyqtSignal()
    
    def __init__(self, test_url=None, test_size=1024*1024):
        super().__init__()
        self.test_url = test_url or "http://speedtest.tele2.net/1MB.zip"
        self.test_size = test_size
    
    def run(self):
        try:
            start_time = time.time()
            
            def report_hook(count, block_size, total_size):
                downloaded = count * block_size
                if total_size > 0:
                    progress = int((downloaded / total_size) * 100)
                    self.progress_signal.emit(progress)
            
            urllib.request.urlretrieve(self.test_url, '/dev/null', reporthook=report_hook)
            
            end_time = time.time()
            duration = end_time - start_time
            speed = (self.test_size / duration) / 1_000_000
            
            self.result_signal.emit(speed)
            self.finished_signal.emit()
            
        except Exception as e:
            self.progress_signal.emit(-1)
            self.finished_signal.emit()


def measure_latency(host, port=80, timeout=2):
    try:
        start = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        end = time.time()
        sock.close()
        return (end - start) * 1000
    except:
        return -1


def measure_bandwidth(url, timeout=10):
    try:
        start = time.time()
        response = urllib.request.urlopen(url, timeout=timeout)
        data = response.read()
        end = time.time()
        
        size = len(data)
        duration = end - start
        speed = (size / duration) / 1_000_000
        
        return speed
    except:
        return -1
