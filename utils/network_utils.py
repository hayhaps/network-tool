#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络工具函数模块
功能：通用网络工具函数
"""

import socket
import ipaddress
import re
import platform
import subprocess
from datetime import datetime


def validate_ip_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_ipv4_address(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


def validate_ipv6_address(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ValueError:
        return False


def validate_domain(domain):
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return re.match(pattern, domain) is not None


def validate_port(port):
    try:
        port = int(port)
        return 0 <= port <= 65535
    except ValueError:
        return False


def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


def get_hostname():
    try:
        return socket.gethostname()
    except:
        return "Unknown"


def resolve_ip_to_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None


def resolve_hostname_to_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None


def get_ip_range(network):
    try:
        net = ipaddress.ip_network(network, strict=False)
        return {
            'network': str(net.network_address),
            'broadcast': str(net.broadcast_address),
            'netmask': str(net.netmask),
            'num_addresses': net.num_addresses,
            'hosts': list(net.hosts())
        }
    except:
        return None


def calculate_subnet_mask(prefix_length):
    try:
        return str(ipaddress.IPv4Network(f'0.0.0.0/{prefix_length}').netmask)
    except:
        return None


def calculate_prefix_length(subnet_mask):
    try:
        return ipaddress.IPv4Network(f'0.0.0.0/{subnet_mask}').prefixlen
    except:
        return None


def is_port_open(host, port, timeout=1):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def get_service_by_port(port):
    try:
        return socket.getservbyport(port)
    except:
        return "Unknown"


def get_port_by_service(service):
    try:
        return socket.getservbyname(service)
    except:
        return None


def ping_check(host, timeout=2):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-w', str(timeout), host]
    
    try:
        output = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout + 1
        )
        return output.returncode == 0
    except:
        return False


def format_bytes(bytes_value):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_speed(bytes_per_second):
    return format_bytes(bytes_per_second) + "/s"


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_mac_address(mac_string):
    mac = re.sub(r'[^0-9A-Fa-f]', '', mac_string)
    if len(mac) == 12:
        return ':'.join([mac[i:i+2] for i in range(0, 12, 2)]).upper()
    return None


def is_valid_mac_address(mac):
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return re.match(pattern, mac) is not None


def get_network_class(ip):
    try:
        first_octet = int(ip.split('.')[0])
        if first_octet < 128:
            return 'A'
        elif first_octet < 192:
            return 'B'
        elif first_octet < 224:
            return 'C'
        elif first_octet < 240:
            return 'D (Multicast)'
        else:
            return 'E (Reserved)'
    except:
        return 'Unknown'


def ip_to_int(ip):
    try:
        return int(ipaddress.IPv4Address(ip))
    except:
        return None


def int_to_ip(integer):
    try:
        return str(ipaddress.IPv4Address(integer))
    except:
        return None


def get_whois_info(domain):
    try:
        import whois
        w = whois.whois(domain)
        return {
            'domain_name': w.domain_name,
            'registrar': w.registrar,
            'creation_date': str(w.creation_date),
            'expiration_date': str(w.expiration_date),
            'name_servers': w.name_servers
        }
    except:
        return None
