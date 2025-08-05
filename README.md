

# Raspberry Pi 5 调试与串口配置说明

## 1. 系统安装与首次启动

我们推荐使用 **[Raspberry Pi Imager](https://pidoc.cn/docs/computers/getting-started#%E4%BD%BF%E7%94%A8imager%E5%B7%A5%E5%85%B7%E5%AE%89%E8%A3%85)** 安装操作系统。  
安装完成后，插入网线或配置 Wi-Fi，并确认 IP 地址。

示例 IP：
```

128.238.175.101

````

### SSH 连接信息
```bash
ssh aboutberlin@128.238.175.101
# 密码
a1231111
````

---

## 2. SSH 配置修改

编辑 SSH 配置文件：

```bash
sudo nano /etc/ssh/sshd_config
```

找到：

```
PermitRootLogin prohibit-password
PasswordAuthentication no
```

修改为：

```
PermitRootLogin no
PasswordAuthentication yes
```

保存并重启 SSH 服务：

```bash
sudo systemctl restart ssh
```

---

## 3. 文件同步到树莓派

用 **rsync** 进行差量传输：

```bash
rsync -avz /home/joe/Desktop/SimToReal_Deployment_HipExo_zhimin/Higher_level_controllers/IEEE_RAM \
aboutberlin@128.238.175.101:/home/aboutberlin/Desktop/highernn
```

特点：

* 只传输新增或修改的文件
* 不会重复拷贝没变的文件
* 不会删除目标机上的额外文件（除非加 `--delete`）

---

## 4. 安装缺失依赖

```bash
pip3 install torch --break-system-packages
pip3 install pandas --break-system-packages
```

---

## 5. 串口配置（Pi 5 专用）
![Port Map](image/Raspberry-Pi-5-Pinout--1210x642.jpg)

编辑串口配置文件：

```bash
sudo nano /boot/firmware/config.txt
```

保持已有的：

```
dtparam=uart0=on
```

并 **添加**：

```
dtoverlay=disable-bt
```

禁用蓝牙串口服务：

```bash
sudo systemctl disable hciuart
```

---

## 6. 重启并验证串口

重启：

```bash
sudo reboot
```

检查串口指向：

```bash
ls -l /dev/serial0
```

可能结果：

* **正确（高性能 UART，GPIO14/15）**

  ```
  /dev/serial0 -> ttyAMA0
  ```
* **错误（未释放给主 UART）**

  ```
  /dev/serial0 -> ttyS0
  ```

---

## 7. Pi 5 串口注意事项

* 在 **Pi 5** 上：

  * `serial0` → 永远指向 **调试口** (`ttyAMA10`)，3-Pin 专用调试接口
  * `ttyAMA0` → 高性能 UART0，对应 **GPIO14(TXD0) / GPIO15(RXD0)**（40-Pin 8/10脚）

* 为什么建议用 `serial0` 或 `ttyAMA10`：

  * `ttyAMA10` 是专用调试串口，固定映射，不会因为硬件变动而变化
  * `serial0` 是 `ttyAMA10` 的别名，代码更通用

---

## 8. Python 串口调试示例

```python
import serial

ser = serial.Serial('/dev/ttyAMA10', 115200, timeout=1)
ser.write(b'Hello Pi5\r\n')
print(ser.readline().decode('utf-8', errors='ignore'))
ser.close()
```
