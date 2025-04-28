import re
import argparse
import ipaddress
import socket
import psutil
import time
import subprocess
from wakeonlan import send_magic_packet

def normalize_mac(mac):
    # 去除所有非十六进制字符
    mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
    if len(mac) != 12:
        raise ValueError('MAC地址格式不正确')
    # 统一格式为AA:BB:CC:DD:EE:FF
    mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
    return mac.upper()

def get_local_ip_and_mask():
    for iface, addrs in psutil.net_if_addrs().items():
        ip = None
        mask = None
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ip = addr.address
                mask = addr.netmask
                if ip and mask:
                    return ip, mask
    raise RuntimeError("未找到有效的本地IP和子网掩码")

def calc_broadcast(ip_str, mask_str):
    net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
    return str(net.broadcast_address)

def wake(mac_address, ip_address, port=9):
    norm_mac = normalize_mac(mac_address)
    send_magic_packet(norm_mac, ip_address=ip_address, port=port)
    print(f"已发送唤醒包到 {norm_mac}，广播地址 {ip_address}:{port}")

def ping_host(ip, timeout=1, count=2):
    import platform
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    wait = '-w' if platform.system().lower() == 'windows' else '-W'
    success = 0
    for _ in range(count):
        cmd = ['ping', param, '1', wait, str(timeout * 1000 if platform.system().lower() == 'windows' else timeout), ip]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            success += 1
        time.sleep(1)
    return success == count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wake-on-LAN 脚本（支持单台和批量唤醒）")
    parser.add_argument("mac", nargs="?", default=None, help="目标主机的MAC地址（单台模式）")
    parser.add_argument("target_ip", nargs="?", default=None, help="目标主机的IP地址（用于检测是否唤醒成功，可选）")
    parser.add_argument("--batch", help="批量唤醒模式，指定包含MAC地址的文件路径")
    parser.add_argument("--port", type=int, default=9, help="端口号，默认9")
    parser.add_argument("--wait", type=int, default=60, help="检测目标主机上线的最大等待秒数，默认60秒")
    args = parser.parse_args()

    try:
        local_ip, local_mask = get_local_ip_and_mask()
        broadcast_ip = calc_broadcast(local_ip, local_mask)
        print(f"本机IP: {local_ip}，子网掩码: {local_mask}，推算广播地址: {broadcast_ip}")

        if args.batch:
            with open(args.batch, encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts or not parts[0]:
                        continue
                    mac = parts[0]
                    ip = parts[1] if len(parts) > 1 else None
                    wake(mac, broadcast_ip, args.port)
                    if ip:
                        print(f"正在检测目标主机 {ip} 是否上线（最多等待{args.wait}秒）...")
                        for i in range(args.wait):
                            if ping_host(ip):
                                print(f"目标主机 {ip} 已上线，唤醒成功！")
                                break
                            time.sleep(1)
                        else:
                            print(f"目标主机 {ip} 未响应，可能未唤醒或未联网。")
                    else:
                        print("已发送唤醒包（未检测目标主机是否上线，因为未指定目标主机IP）。")
        elif args.mac:
            wake(args.mac, broadcast_ip, args.port)
            if args.target_ip:
                print(f"正在检测目标主机是否上线（最多等待{args.wait}秒）...")
                for i in range(args.wait):
                    if ping_host(args.target_ip):
                        print(f"目标主机 {args.target_ip} 已上线，唤醒成功！")
                        break
                    time.sleep(1)
                else:
                    print(f"目标主机 {args.target_ip} 未响应，可能未唤醒或未联网。")
            else:
                print("已发送唤醒包（未检测目标主机是否上线，因为未指定目标主机IP）。")
        else:
            print("请指定MAC地址或批量文件。")
    except Exception as e:
        print(f"错误: {e}") 