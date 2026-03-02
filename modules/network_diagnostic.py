import subprocess
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class BatchPingThread(QObject):
    """批量Ping测试线程"""
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self, ip_list, timeout=2, count=3):
        super().__init__()
        self.ip_list = ip_list
        self.timeout = timeout
        self.count = count
        self.results = {}
    
    def run(self):
        """执行批量Ping测试"""
        try:
            threads = []
            
            for ip in self.ip_list:
                thread = threading.Thread(target=self._ping_ip, args=(ip,))
                threads.append(thread)
                thread.start()
                # 避免同时启动太多线程
                time.sleep(0.1)
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            # 按结果排序
            sorted_results = {}
            for ip, result in self.results.items():
                status = result['status']
                if status not in sorted_results:
                    sorted_results[status] = []
                sorted_results[status].append((ip, result))
            
            self.result_signal.emit(sorted_results)
            self.finished_signal.emit()
            
        except Exception as e:
            self.progress_signal.emit(f"批量Ping测试出错: {str(e)}")
            self.finished_signal.emit()
    
    def _ping_ip(self, ip):
        """Ping单个IP地址"""
        result = {
            'status': '未知',
            'time': 0,
            'packet_loss': 100,
            'error': ''
        }
        
        try:
            # 构建Ping命令
            if subprocess.os.name == 'nt':  # Windows
                command = ['ping', '-n', str(self.count), '-w', str(int(self.timeout * 1000)), ip]
            else:  # Linux/Mac
                command = ['ping', '-c', str(self.count), '-W', str(self.timeout), ip]
            
            # 执行Ping命令
            start_time = time.time()
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout * 2
            )
            end_time = time.time()
            
            # 解析结果
            output = process.stdout
            
            if process.returncode == 0:
                result['status'] = '在线'
                result['time'] = round((end_time - start_time) * 1000, 2)
                
                # 提取丢包率
                if 'packet loss' in output:
                    import re
                    loss_match = re.search(r'([0-9.]+)% packet loss', output)
                    if loss_match:
                        result['packet_loss'] = float(loss_match.group(1))
                elif '丢失 =' in output:  # Windows格式
                    import re
                    loss_match = re.search(r'丢失 = (\d+)', output)
                    if loss_match:
                        loss_count = int(loss_match.group(1))
                        result['packet_loss'] = (loss_count / self.count) * 100
            else:
                result['status'] = '离线'
                result['error'] = output
        
        except subprocess.TimeoutExpired:
            result['status'] = '超时'
            result['error'] = 'Ping超时'
        except Exception as e:
            result['status'] = '错误'
            result['error'] = str(e)
        
        self.results[ip] = result
        self.progress_signal.emit(f"Ping测试完成: {ip} - {result['status']}")

class NetworkDiagnosticThread(QObject):
    """网络诊断线程"""
    progress_signal = pyqtSignal(str)
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        """执行网络诊断"""
        try:
            results = {
                'dns': self._test_dns(),
                'gateway': self._test_gateway(),
                'internet': self._test_internet(),
                'latency': self._test_latency()
            }
            
            # 计算总体状态
            overall_status = '正常'
            issues = []
            
            if not results['dns']['status']:
                overall_status = '异常'
                issues.append('DNS解析失败')
            if not results['gateway']['status']:
                overall_status = '异常'
                issues.append('网关连接失败')
            if not results['internet']['status']:
                overall_status = '异常'
                issues.append('互联网连接失败')
            if results['latency']['status'] and results['latency']['avg_latency'] > 100:
                overall_status = '警告'
                issues.append('网络延迟较高')
            
            results['overall'] = {
                'status': overall_status,
                'issues': issues
            }
            
            self.result_signal.emit(results)
            self.finished_signal.emit()
            
        except Exception as e:
            self.progress_signal.emit(f"网络诊断出错: {str(e)}")
            self.finished_signal.emit()
    
    def _test_dns(self):
        """测试DNS解析"""
        self.progress_signal.emit("正在测试DNS解析...")
        try:
            import socket
            # 测试多个DNS服务器
            dns_servers = ['8.8.8.8', '114.114.114.114', '202.96.128.166']
            resolved = []
            
            for dns in dns_servers:
                try:
                    socket.gethostbyname('baidu.com')
                    resolved.append(dns)
                except:
                    pass
            
            return {
                'status': len(resolved) > 0,
                'resolved_servers': resolved,
                'total_servers': len(dns_servers)
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def _test_gateway(self):
        """测试网关连接"""
        self.progress_signal.emit("正在测试网关连接...")
        try:
            # 获取默认网关
            import netifaces
            gateways = netifaces.gateways()
            default_gateway = gateways.get('default', {}).get(netifaces.AF_INET, [None])[0]
            
            if not default_gateway:
                return {
                    'status': False,
                    'error': '未找到默认网关'
                }
            
            # Ping网关
            if subprocess.os.name == 'nt':
                command = ['ping', '-n', '2', '-w', '1000', default_gateway]
            else:
                command = ['ping', '-c', '2', '-W', '1', default_gateway]
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            return {
                'status': process.returncode == 0,
                'gateway': default_gateway,
                'response': process.stdout
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def _test_internet(self):
        """测试互联网连接"""
        self.progress_signal.emit("正在测试互联网连接...")
        try:
            # 测试连接到多个公共服务器
            test_hosts = ['baidu.com', 'google.com', 'qq.com']
            reachable = []
            
            for host in test_hosts:
                try:
                    import socket
                    socket.gethostbyname(host)
                    reachable.append(host)
                except:
                    pass
            
            return {
                'status': len(reachable) > 0,
                'reachable_hosts': reachable,
                'total_hosts': len(test_hosts)
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
    
    def _test_latency(self):
        """测试网络延迟"""
        self.progress_signal.emit("正在测试网络延迟...")
        try:
            test_hosts = ['baidu.com', 'google.com']
            latencies = []
            
            for host in test_hosts:
                try:
                    if subprocess.os.name == 'nt':
                        command = ['ping', '-n', '3', '-w', '1000', host]
                    else:
                        command = ['ping', '-c', '3', '-W', '1', host]
                    
                    process = subprocess.run(
                        command,
                        capture_output=True,
                        text=True
                    )
                    
                    if process.returncode == 0:
                        # 提取延迟信息
                        import re
                        if 'average' in process.stdout:
                            match = re.search(r'average = (\d+)ms', process.stdout)
                            if match:
                                latencies.append(int(match.group(1)))
                        elif '平均' in process.stdout:  # 中文输出
                            match = re.search(r'平均 = (\d+)ms', process.stdout)
                            if match:
                                latencies.append(int(match.group(1)))
                except:
                    pass
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                return {
                    'status': True,
                    'avg_latency': avg_latency,
                    'latencies': latencies
                }
            else:
                return {
                    'status': False,
                    'error': '无法测试延迟'
                }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }