#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络速度测试模块
功能：带宽测试、延迟测试
"""

import time
import socket
import urllib.request
import json
import speedtest
from PyQt5.QtCore import QThread, pyqtSignal


def get_public_ip_and_isp():
    """获取公网IP和运营商信息"""
    try:
        # 使用ipinfo.io API获取IP和ISP信息
        with urllib.request.urlopen('https://ipinfo.io/json', timeout=10) as response:
            data = json.loads(response.read().decode())
            return {
                'ip': data.get('ip', 'Unknown'),
                'isp': data.get('org', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'country': data.get('country', 'Unknown')
            }
    except:
        # 如果ipinfo.io失败，尝试其他API
        try:
            with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5) as response:
                data = json.loads(response.read().decode())
                return {
                    'ip': data.get('ip', 'Unknown'),
                    'isp': 'Unknown',
                    'city': 'Unknown',
                    'region': 'Unknown',
                    'country': 'Unknown'
                }
        except:
            return {
                'ip': 'Unknown',
                'isp': 'Unknown',
                'city': 'Unknown',
                'region': 'Unknown',
                'country': 'Unknown'
            }


def get_local_ip():
    """获取本地IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return 'Unknown'


class SpeedTestThread(QThread):
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.results = {}
        self.local_ip = get_local_ip()
        self.public_ip_info = get_public_ip_and_isp()
    
    def run(self):
        try:
            self.progress_signal.emit("=" * 50)
            self.progress_signal.emit("🚀 开始速度测试...")
            self.progress_signal.emit("=" * 50)
            
            # 显示IP和运营商信息
            self.progress_signal.emit("\n🌐 网络信息")
            self.progress_signal.emit("-" * 50)
            self.progress_signal.emit(f"🏠 本地IP: {self.local_ip}")
            self.progress_signal.emit(f"🌍 公网IP: {self.public_ip_info['ip']}")
            self.progress_signal.emit(f"📡 运营商: {self.public_ip_info['isp']}")
            self.progress_signal.emit(f"📍 位置: {self.public_ip_info['city']}, {self.public_ip_info['region']}, {self.public_ip_info['country']}")
            
            st = speedtest.Speedtest()
            
            self.progress_signal.emit("\n📡 正在获取服务器列表...")
            self.progress_signal.emit("-" * 50)
            st.get_servers()
            
            # 获取服务器列表
            servers = st.servers
            
            # 提取运营商关键词
            isp_keywords = self._extract_isp_keywords(self.public_ip_info['isp'])
            
            # 筛选同运营商服务器
            filtered_servers = []
            for server_list in servers.values():
                for server in server_list:
                    if self._is_same_isp(server.get('sponsor', ''), isp_keywords):
                        filtered_servers.append(server)
            
            if filtered_servers:
                self.progress_signal.emit(f"\n🎯 正在从 {len(filtered_servers)} 个同运营商服务器中选择最佳服务器...")
                # 按延迟排序，选择延迟最低的
                filtered_servers.sort(key=lambda x: x.get('latency', 9999))
                best = filtered_servers[0]
                # 手动设置最佳服务器
                st.results.server = best
            else:
                self.progress_signal.emit("\n🎯 未找到同运营商服务器，正在选择全局最佳服务器...")
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
    
    def _extract_isp_keywords(self, isp):
        """提取运营商关键词"""
        if not isp or isp == 'Unknown':
            return []
        
        # 常见运营商关键词映射
        isp_mappings = {
            'china mobile': ['mobile', '中国移动'],
            'china unicom': ['unicom', '中国联通'],
            'china telecom': ['telecom', '中国电信'],
            't-mobile': ['t-mobile', 'tmobile'],
            'at&t': ['at&t', 'att'],
            'verizon': ['verizon'],
            'comcast': ['comcast'],
            'centurylink': ['centurylink'],
            'charter': ['charter', 'spectrum'],
            'cox': ['cox'],
            'bt': ['bt'],
            'sky': ['sky'],
            'vodafone': ['vodafone'],
            'orange': ['orange'],
            'deutsche telekom': ['deutsche telekom', 'telekom'],
            'ntt': ['ntt'],
            'kddi': ['kddi'],
            'softbank': ['softbank'],
            'samsung': ['samsung'],
            'lg': ['lg'],
            'sk telecom': ['sk telecom', 'skt'],
            'kt': ['kt'],
            'lg uplus': ['lg uplus', 'uplus']
        }
        
        isp_lower = isp.lower()
        keywords = []
        
        # 匹配已知运营商
        for key, mappings in isp_mappings.items():
            if key in isp_lower:
                keywords.extend(mappings)
                break
        
        # 如果没有匹配到已知运营商，提取主要关键词
        if not keywords:
            # 移除常见后缀
            suffixes = ['inc', 'llc', 'ltd', 'co', 'corp', 'company', 'group', 'communications', 'telecom', 'networks', 'internet']
            words = isp_lower.split()
            for word in words:
                word = word.strip(',.')
                if word and word not in suffixes and len(word) > 2:
                    keywords.append(word)
                    if len(keywords) >= 2:
                        break
        
        return keywords
    
    def _is_same_isp(self, server_sponsor, isp_keywords):
        """判断服务器是否属于同一运营商"""
        if not server_sponsor or not isp_keywords:
            return False
        
        server_sponsor_lower = server_sponsor.lower()
        for keyword in isp_keywords:
            if keyword.lower() in server_sponsor_lower:
                return True
        
        return False


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
