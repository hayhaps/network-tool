#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNMP管理模块
功能：SNMP查询、设备信息获取
"""

from pysnmp.hlapi import *
from PyQt5.QtCore import QThread, pyqtSignal


class SNMPQueryThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self, host, community='public', oid='1.3.6.1.2.1.1.1.0', port=161, version=2):
        super().__init__()
        self.host = host
        self.community = community
        self.oid = oid
        self.port = port
        self.version = version
    
    def run(self):
        result = {
            'host': self.host,
            'oid': self.oid,
            'value': None,
            'error': None
        }
        
        try:
            if self.version == 2:
                error_indication, error_status, error_index, var_binds = next(
                    getCmd(SnmpEngine(),
                           CommunityData(self.community),
                           UdpTransportTarget((self.host, self.port)),
                           ContextData(),
                           ObjectType(ObjectIdentity(self.oid)))
                )
            else:
                error_indication, error_status, error_index, var_binds = next(
                    getCmd(SnmpEngine(),
                           UsmUserData('user', 'authKey', 'privKey'),
                           UdpTransportTarget((self.host, self.port)),
                           ContextData(),
                           ObjectType(ObjectIdentity(self.oid)))
                )
            
            if error_indication:
                result['error'] = str(error_indication)
            elif error_status:
                result['error'] = f'{error_status.prettyPrint()} at {error_index}'
            else:
                for var_bind in var_binds:
                    result['value'] = str(var_bind[1])
        
        except Exception as e:
            result['error'] = str(e)
        
        self.result_signal.emit(result)
        self.finished_signal.emit()


class SNMPWalkThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(list)
    
    def __init__(self, host, community='public', oid='1.3.6.1.2.1.1', port=161):
        super().__init__()
        self.host = host
        self.community = community
        self.oid = oid
        self.port = port
        self.results = []
    
    def run(self):
        try:
            for (error_indication, error_status, error_index, var_binds) in nextCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.host, self.port)),
                ContextData(),
                ObjectType(ObjectIdentity(self.oid)),
                lexicographicMode=False):
                
                if error_indication:
                    self.result_signal.emit({'error': str(error_indication)})
                    break
                elif error_status:
                    self.result_signal.emit({'error': f'{error_status.prettyPrint()}'})
                    break
                else:
                    for var_bind in var_binds:
                        result = {
                            'oid': str(var_bind[0]),
                            'value': str(var_bind[1])
                        }
                        self.results.append(result)
                        self.result_signal.emit(result)
            
            self.finished_signal.emit(self.results)
            
        except Exception as e:
            self.result_signal.emit({'error': str(e)})
            self.finished_signal.emit([])


class SNMPDeviceThread(QThread):
    result_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal()
    
    def __init__(self, host, community='public', port=161):
        super().__init__()
        self.host = host
        self.community = community
        self.port = port
    
    def run(self):
        device_info = {
            'host': self.host,
            'sysDescr': None,
            'sysObjectID': None,
            'sysUpTime': None,
            'sysContact': None,
            'sysName': None,
            'sysLocation': None,
            'error': None
        }
        
        oids = {
            'sysDescr': '1.3.6.1.2.1.1.1.0',
            'sysObjectID': '1.3.6.1.2.1.1.2.0',
            'sysUpTime': '1.3.6.1.2.1.1.3.0',
            'sysContact': '1.3.6.1.2.1.1.4.0',
            'sysName': '1.3.6.1.2.1.1.5.0',
            'sysLocation': '1.3.6.1.2.1.1.6.0'
        }
        
        try:
            for key, oid in oids.items():
                error_indication, error_status, error_index, var_binds = next(
                    getCmd(SnmpEngine(),
                           CommunityData(self.community),
                           UdpTransportTarget((self.host, self.port)),
                           ContextData(),
                           ObjectType(ObjectIdentity(oid)))
                )
                
                if not error_indication and not error_status:
                    for var_bind in var_binds:
                        device_info[key] = str(var_bind[1])
        
        except Exception as e:
            device_info['error'] = str(e)
        
        self.result_signal.emit(device_info)
        self.finished_signal.emit()


COMMON_OIDS = {
    'sysDescr': '1.3.6.1.2.1.1.1.0',
    'sysObjectID': '1.3.6.1.2.1.1.2.0',
    'sysUpTime': '1.3.6.1.2.1.1.3.0',
    'sysContact': '1.3.6.1.2.1.1.4.0',
    'sysName': '1.3.6.1.2.1.1.5.0',
    'sysLocation': '1.3.6.1.2.1.1.6.0',
    'ifNumber': '1.3.6.1.2.1.2.1.0',
    'ifTable': '1.3.6.1.2.1.2.2',
    'ipForwarding': '1.3.6.1.2.1.4.1.0',
    'ipDefaultTTL': '1.3.6.1.2.1.4.2.0',
    'tcpRtoAlgorithm': '1.3.6.1.2.1.5.1.0',
    'tcpRtoMin': '1.3.6.1.2.1.5.2.0',
    'tcpRtoMax': '1.3.6.1.2.1.5.3.0',
    'tcpMaxConn': '1.3.6.1.2.1.5.4.0',
    'udpInDatagrams': '1.3.6.1.2.1.7.1.0',
    'udpNoPorts': '1.3.6.1.2.1.7.2.0',
    'udpInErrors': '1.3.6.1.2.1.7.3.0',
    'udpOutDatagrams': '1.3.6.1.2.1.7.4.0'
}


def snmp_get(host, oid, community='public', port=161):
    try:
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((host, port)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )
        
        if error_indication:
            return None, str(error_indication)
        elif error_status:
            return None, f'{error_status.prettyPrint()}'
        else:
            for var_bind in var_binds:
                return str(var_bind[1]), None
    
    except Exception as e:
        return None, str(e)


def snmp_walk(host, oid, community='public', port=161):
    results = []
    try:
        for (error_indication, error_status, error_index, var_binds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((host, port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False):
            
            if error_indication or error_status:
                break
            
            for var_bind in var_binds:
                results.append({
                    'oid': str(var_bind[0]),
                    'value': str(var_bind[1])
                })
    
    except Exception as e:
        pass
    
    return results
