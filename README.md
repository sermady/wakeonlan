# Wake-on-LAN 批量/单台唤醒脚本

## 功能简介
本脚本支持通过局域网批量或单台唤醒支持WOL的主机。可自动推算本机网段的广播地址，并支持检测目标主机是否成功上线。

- 支持单台唤醒和批量唤醒两种模式
- 支持多种MAC地址格式
- 可选检测目标主机是否上线（通过ping）
- 支持自定义端口和等待时间

## 依赖安装

请先安装依赖库：

```bash
pip install wakeonlan psutil
```

## 使用方法

### 1. 单台唤醒

只唤醒（不检测上线）：
```bash
python wakeonlan_script.py <MAC地址>
```

唤醒并检测上线（需指定目标主机IP）：
```bash
python wakeonlan_script.py <MAC地址> <目标主机IP>
```

可选参数：
- `--port` 发送唤醒包的端口，默认9
- `--wait` 检测目标主机上线的最大等待秒数，默认60秒

**示例：**
```bash
python wakeonlan_script.py AA:BB:CC:DD:EE:FF 192.168.9.101 --wait 90
```

### 2. 批量唤醒

准备一个文本文件（如`mac_list.txt`），每行一个MAC地址，后面可选填写目标主机IP（用于检测上线）：

```
AA:BB:CC:DD:EE:01 192.168.9.101
AA:BB:CC:DD:EE:02 192.168.9.102
AA:BB:CC:DD:EE:03
```

批量唤醒命令：
```bash
python wakeonlan_script.py --batch mac_list.txt
```

## 注意事项
- 目标主机需开启主板/网卡的Wake-on-LAN功能。
- 目标主机和发送唤醒包的主机需在同一局域网网段。
- 检测上线功能依赖于目标主机允许ICMP（ping）响应。
- 脚本会自动推算本机网段的广播地址。

## 参数说明
| 参数         | 说明                                   |
|--------------|----------------------------------------|
| MAC地址      | 目标主机的MAC地址，支持多种格式        |
| 目标主机IP   | 用于检测是否上线，可选                 |
| --batch      | 批量模式，指定MAC列表文件              |
| --port       | 唤醒包端口，默认9                      |
| --wait       | 检测上线最大等待秒数，默认60            |

## 典型用法

- 单台唤醒：
  ```bash
  python wakeonlan_script.py 48:E5:33:43:5C:7A
  ```
- 单台唤醒并检测上线：
  ```bash
  python wakeonlan_script.py 48:E5:33:43:5C:7A 192.168.9.101
  ```
- 批量唤醒：
  ```bash
  python wakeonlan_script.py --batch mac_list.txt
  ```

如有问题欢迎反馈！ 