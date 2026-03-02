import networkx as nx
import matplotlib.pyplot as plt
import socket
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class NetworkTopology(QObject):
    """网络拓扑图生成器"""
    progress_signal = pyqtSignal(str)
    topology_ready = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.graph = nx.Graph()
    
    def generate_topology(self, target_ip, max_hops=3):
        """生成网络拓扑图"""
        try:
            self.progress_signal.emit(f"开始生成网络拓扑，目标IP: {target_ip}")
            
            # 构建基础拓扑
            self._build_topology(target_ip, max_hops)
            
            # 分析网络结构
            self._analyze_topology()
            
            self.progress_signal.emit("网络拓扑生成完成")
            self.topology_ready.emit(self.graph)
            
        except Exception as e:
            self.progress_signal.emit(f"生成拓扑时出错: {str(e)}")
            self.topology_ready.emit(None)
    
    def _build_topology(self, target_ip, max_hops):
        """构建拓扑结构"""
        # 添加本地节点
        local_ip = self._get_local_ip()
        self.graph.add_node(local_ip, type="local", label="本地主机")
        
        # 模拟网络路径
        path = self._trace_route(target_ip, max_hops)
        
        # 添加路径节点和边
        prev_node = local_ip
        for i, (ip, host) in enumerate(path):
            node_id = ip
            node_label = host if host else ip
            node_type = "router" if i < len(path) - 1 else "target"
            
            self.graph.add_node(node_id, type=node_type, label=node_label, hop=i+1)
            self.graph.add_edge(prev_node, node_id, weight=1)
            
            # 添加一些额外的网络设备
            if i < len(path) - 1:
                self._add_network_devices(node_id, i)
            
            prev_node = node_id
    
    def _get_local_ip(self):
        """获取本地IP"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def _trace_route(self, target_ip, max_hops):
        """模拟路由追踪"""
        # 模拟路由路径
        path = []
        try:
            # 模拟几个路由节点
            path.append(("192.168.1.1", "家庭路由器"))
            path.append(("10.0.0.1", "ISP网关"))
            path.append(("203.0.113.1", "骨干路由器"))
            path.append((target_ip, socket.gethostbyaddr(target_ip)[0] if target_ip != "8.8.8.8" else "Google DNS"))
        except:
            path.append((target_ip, target_ip))
        
        return path[:max_hops]
    
    def _add_network_devices(self, router_ip, hop):
        """添加网络设备"""
        # 添加交换机
        switch_id = f"switch_{hop}"
        self.graph.add_node(switch_id, type="switch", label=f"交换机 {hop}")
        self.graph.add_edge(router_ip, switch_id, weight=0.5)
        
        # 添加一些设备
        for i in range(2):
            device_id = f"device_{hop}_{i}"
            device_label = f"设备 {i+1}"
            self.graph.add_node(device_id, type="device", label=device_label)
            self.graph.add_edge(switch_id, device_id, weight=0.3)
    
    def _analyze_topology(self):
        """分析网络拓扑"""
        # 计算节点度
        for node in self.graph.nodes():
            degree = self.graph.degree(node)
            self.graph.nodes[node]['degree'] = degree
        
        # 标记中心节点
        if self.graph.nodes():
            centrality = nx.degree_centrality(self.graph)
            max_centrality_node = max(centrality, key=centrality.get)
            self.graph.nodes[max_centrality_node]['central'] = True
    
    def get_topology_data(self):
        """获取拓扑数据"""
        nodes = []
        edges = []
        
        for node, attrs in self.graph.nodes(data=True):
            nodes.append({
                'id': node,
                'label': attrs.get('label', node),
                'type': attrs.get('type', 'unknown'),
                'hop': attrs.get('hop', 0),
                'degree': attrs.get('degree', 0),
                'central': attrs.get('central', False)
            })
        
        for u, v, attrs in self.graph.edges(data=True):
            edges.append({
                'source': u,
                'target': v,
                'weight': attrs.get('weight', 1)
            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def draw_topology(self, filename="network_topology.png"):
        """绘制拓扑图"""
        try:
            pos = nx.spring_layout(self.graph, seed=42)
            
            # 节点样式
            node_colors = {}
            for node, attrs in self.graph.nodes(data=True):
                node_type = attrs.get('type', 'unknown')
                if node_type == 'local':
                    node_colors[node] = '#4CAF50'  # 绿色
                elif node_type == 'target':
                    node_colors[node] = '#2196F3'  # 蓝色
                elif node_type == 'router':
                    node_colors[node] = '#FF9800'  # 橙色
                elif node_type == 'switch':
                    node_colors[node] = '#9C27B0'  # 紫色
                else:
                    node_colors[node] = '#607D8B'  # 灰色
            
            # 绘制节点
            nx.draw_networkx_nodes(
                self.graph, pos, 
                node_size=600,
                node_color=[node_colors[node] for node in self.graph.nodes()]
            )
            
            # 绘制边
            nx.draw_networkx_edges(
                self.graph, pos, 
                width=1.5,
                alpha=0.7
            )
            
            # 绘制标签
            labels = {node: attrs.get('label', node) for node, attrs in self.graph.nodes(data=True)}
            nx.draw_networkx_labels(
                self.graph, pos, 
                labels=labels,
                font_size=8,
                font_color='white',
                font_weight='bold'
            )
            
            # 设置图形属性
            plt.figure(figsize=(12, 8))
            plt.axis('off')
            plt.title('网络拓扑图')
            plt.tight_layout()
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            
            return filename
        except Exception as e:
            print(f"绘制拓扑图时出错: {str(e)}")
            return None