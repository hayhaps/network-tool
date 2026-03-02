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
            self.progress_signal.emit("=" * 50)
            self.progress_signal.emit("🚀 开始速度测试...")
            self.progress_signal.emit("=" * 50)
            
            st = speedtest.Speedtest()
            
            self.progress_signal.emit("\n📡 正在获取服务器列表...")
            self.progress_signal.emit("-" * 50)
            st.get_servers()
            
            self.progress_signal.emit("\n🎯 正在选择最佳服务器...")
            self.progress_signal.emit("-" * 50)
            best = st.get_best_server()
            
            server_info = f"📍 服务器: {best.get('name', 'N/A')}"
            server_info += f"\n🏢 运营商: {best.get('sponsor', 'N/A')}"
            server_info += f"\n🌍 位置: {best.get('country', 'N/A')}, {best.get('location', 'N/A')}"
            server_info += f"\n📏 距离: {best.get('d', 0):.2f} km"
            server_info += f"\n⏱️ 延迟: {best.get('latency', 0):.2f} ms"
            self.progress_signal.emit(server_info)
            
            self.progress_signal.emit("\n⬇️  正在测试下载速度...")
            self.progress_signal.emit("-" * 50)
            download_speed = st.download() / 1_000_000
            self.progress_signal.emit(f"   📊 当前下载速度: {download_speed:.2f} Mbps")
            
            self.progress_signal.emit("\n⬆️  正在测试上传速度...")
            self.progress_signal.emit("-" * 50)
            upload_speed = st.upload() / 1_000_000
            self.progress_signal.emit(f"   📊 当前上传速度: {upload_speed:.2f} Mbps")
            
            self.results = {
                'download': download_speed,
                'upload': upload_speed,
                'ping': st.results.ping,
                'server': best.get('sponsor', 'N/A'),
                'location': best.get('name', 'N/A'),
                'country': best.get('country', 'N/A'),
                'distance': best.get('d', 0)
            }
            
            self.progress_signal.emit("\n" + "=" * 50)
            self.progress_signal.emit("📋 测试结果汇总")
            self.progress_signal.emit("=" * 50)
            self.progress_signal.emit(f"🏠 服务器位置: {best.get('country', 'N/A')} - {best.get('name', 'N/A')}")
            self.progress_signal.emit(f"📶 延迟: {st.results.ping:.2f} ms")
            self.progress_signal.emit(f"⬇️  下载速度: {download_speed:.2f} Mbps")
            self.progress_signal.emit(f"⬆️  上传速度: {upload_speed:.2f} Mbps")
            self.progress_signal.emit("=" * 50)
            self.progress_signal.emit("✅ 速度测试完成!")
            
            self.result_signal.emit(self.results)
            self.finished_signal.emit()
            
        except Exception as e:
            self.progress_signal.emit(f"\n❌ 速度测试失败: {str(e)}")
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
