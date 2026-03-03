# -*- coding: utf-8 -*-
"""
网络智能助手模块
支持云端大模型（豆包/火山引擎）
"""

import re
import json
import os
from PyQt5.QtCore import QObject, pyqtSignal


class NetworkAIAssistant(QObject):
    """网络智能助手 - 支持云端大模型"""
    response_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.use_cloud_model = self.config.get('use_cloud_model', True)
        self.api_key = self.config.get('api_key', '')
        self.model_name = self.config.get('model', 'doubao-lite-4k')
    
    def process_query(self, query):
        """处理用户查询"""
        try:
            query = query.strip()
            
            # 使用云端大模型
            if self.use_cloud_model and self.api_key:
                self._process_with_cloud_model(query)
            else:
                # 如果没有API密钥，提示用户配置
                self.error_signal.emit("请先配置豆包API Key才能使用智能助手功能。\n\n获取方式：\n1. 访问火山引擎控制台 (console.volces.com)\n2. 注册账号并创建API Key\n3. 在智能助手页面配置API Key")
                self.finished_signal.emit()
                
        except Exception as e:
            self.error_signal.emit(f"处理查询时出错: {str(e)}")
            self.finished_signal.emit()
    
    def _process_with_cloud_model(self, query):
        """使用云端大模型处理查询"""
        try:
            import urllib.request
            import urllib.error
            
            # 豆包/火山引擎 API 配置
            api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
            
            # 构建请求体
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的网络运维助手，擅长解答网络故障排查、网络配置、网络工具使用等问题。请用中文回答，回答要简洁实用。"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.7
            }
            
            # 发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            # 设置超时
            response = urllib.request.urlopen(req, timeout=30)
            result = json.loads(response.read().decode('utf-8'))
            
            # 提取回答
            if 'choices' in result and len(result['choices']) > 0:
                answer = result['choices'][0]['message']['content']
                self.response_signal.emit(answer)
            else:
                self.error_signal.emit("云端模型返回异常，请稍后重试")
                
        except urllib.error.HTTPError as e:
            error_msg = f"API请求失败: {e.code}"
            if e.code == 401:
                error_msg = "API密钥无效，请检查配置"
            elif e.code == 429:
                error_msg = "请求过于频繁，请稍后再试"
            self.error_signal.emit(error_msg)
        except Exception as e:
            self.error_signal.emit(f"云端模型调用失败: {str(e)}")
        finally:
            self.finished_signal.emit()
