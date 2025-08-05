

# Raspberry Pi 5 调试与串口配置说明

## 1. 系统安装与首次启动

我们推荐使用 **[Raspberry Pi Imager](https://pidoc.cn/docs/computers/getting-started#%E4%BD%BF%E7%94%A8imager%E5%B7%A5%E5%85%B7%E5%AE%89%E8%A3%85)** 安装操作系统。  
安装完成后，插入网线或配置 Wi-Fi，并确认 IP 地址。根据提示，输入账户密码，其他都随便你咋样

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
默认很可能不给ssh，你先检查，而且记得一定要两个电脑都有线连接，无线不行

hostname -I


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
前面如果有#，记得去掉

保存并重启 SSH 服务：

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl restart ssh
```
sudo systemctl is-enabled ssh
sudo systemctl status ssh 检查，active就成功了
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
  /dev/serial0 -> ttyAMA10
  ```
* **错误（未释放给主 UART）**

  ```
  /dev/serial0 -> ttyS0
  ```

---

## 7. Pi 5 串口注意事项

**Pi 5 的“serial0”永远指向调试口 (`ttyAMA10`)——这不是 Bug，而是官方的默认设计**。

最重要的是： ser = serial.Serial('/dev/ttyAMA10', 115200, timeout=1)
串口设备，/dev/ttyAMA10 (serial0 别名)，调试专用 3-Pin 端子
/dev/ttyAMA0，PL011 UART0	GPIO14(TXD0) / GPIO15(RXD0)，也就是 40-Pin 的 8/10 号脚
而且为什么要用serial0和ttyAMA10呢？因为ttyAMA10是跟着不同班子走的，serial0可以无视不同班子

因此，你要用ttyAMA0，也就是ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)，确定

* 在 **Pi 5** 上：

  * `serial0` → 永远指向 **调试口** (`ttyAMA10`)，3-Pin 专用调试接口
  * `ttyAMA0` → 高性能 UART0，对应 **GPIO14(TXD0) / GPIO15(RXD0)**（40-Pin 8/10脚）

* 为什么建议用 `serial0` 或 `ttyAMA10`：

  * `ttyAMA10` 是专用调试串口，固定映射，不会因为硬件变动而变化
  * `serial0` 是 `ttyAMA10` 的别名，代码更通用

---

# 树莓派 5 串口调试注意事项

## 1. IP 地址
- **IP 地址经常会变**，每次连接前请先确认。
- 推荐使用 **VSCode Remote SSH** 进行连接，方便开发与调试。

---

## 2. 串口简单测试方法

1. 将 **GPIO14 (TXD0)** 与 **GPIO15 (RXD0)** 用杜邦线连接在一起（回环测试）。
2. 在树莓派 5 上：
   - `ttyAMA0` → 高性能 UART0  
   - GPIO14(TXD0) → 40-Pin 第 8 脚  
   - GPIO15(RXD0) → 40-Pin 第 10 脚
3. 确认能从 GPIO14 发出数据，并由 GPIO15 接收。

---

## 3. 测试代码
我帮你把你这段 **树莓派开机自启动 main.py（带时间戳日志）** 的流程整理成一份简洁的中文 **Markdown**，方便你直接保存或运行：

---

````markdown
# 树莓派开机自启动 main.py（systemd + 日志）

## 1. 环境信息
- 测试代码路径：`/home/aboutberlin/Desktop/IEEE_RAM/main.py`
- Python 路径：
```bash
which python3
# 输出：
/usr/bin/python3
````

---

## 2. 创建启动脚本

```bash
nano /home/aboutberlin/Desktop/IEEE_RAM/start.sh
```

写入：

```bash
#!/bin/bash
# 日志目录
LOG_DIR="/home/aboutberlin/Desktop/IEEE_RAM/logs"
mkdir -p "$LOG_DIR"

# 日志文件（按日期命名）
LOG_FILE="$LOG_DIR/$(date +'%Y-%m-%d_%H-%M-%S').log"

# 进入项目目录
cd /home/aboutberlin/Desktop/IEEE_RAM

# 运行 main.py，把 stdout 和 stderr 都记录到日志
/usr/bin/python3 main.py >> "$LOG_FILE" 2>&1
```

保存并赋权：

```bash
chmod +x /home/aboutberlin/Desktop/IEEE_RAM/start.sh
```

---

## 3. 创建 systemd 服务

```bash
sudo nano /etc/systemd/system/ieee_ram.service
```

写入：

```ini
[Unit]
Description=IEEE RAM Main Python Script
After=network.target

[Service]
ExecStart=/home/aboutberlin/Desktop/IEEE_RAM/start.sh
WorkingDirectory=/home/aboutberlin/Desktop/IEEE_RAM
StandardOutput=journal
StandardError=journal
Restart=always
RestartSec=5
User=aboutberlin

[Install]
WantedBy=multi-user.target
```

**说明：**

* `Restart=always`：脚本异常退出会重启
* `RestartSec=5`：延迟 5 秒重启
* `User=aboutberlin`：使用你的账号运行
* 日志保存在 `/home/aboutberlin/Desktop/IEEE_RAM/logs`，也能用 `journalctl` 查看

---

## 4. 启用 & 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable ieee_ram.service
sudo systemctl start ieee_ram.service
```

---

## 5. 确认后台运行

查看服务状态：

```bash
sudo systemctl status ieee_ram.service
```

查看 systemd 实时日志：

```bash
journalctl -u ieee_ram.service -f
```

查看自定义时间戳日志：

```bash
ls /home/aboutberlin/Desktop/IEEE_RAM/logs
cat /home/aboutberlin/Desktop/IEEE_RAM/logs/最新的文件.log
```


sudo systemctl status ieee_ram.service

ps aux | grep python

aboutbe+    1661 52.3  6.4 800544 267184 ?       Rl   22:53   0:12 /usr/bin/python3 main.py
aboutbe+    1897  0.0  0.0   6240  1616 pts/6    S+   22:53   0:00 grep --color=auto python

sudo systemctl status ieee_ram.service


● ieee_ram.service - IEEE RAM Main Python Script
     Loaded: loaded (/etc/systemd/system/ieee_ram.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-08-05 22:49:30 BST; 4min 32s ago
   Main PID: 1658 (start.sh)
      Tasks: 5 (limit: 4752)
        CPU: 25.780s
     CGroup: /system.slice/ieee_ram.service
             ├─1658 /bin/bash /home/aboutberlin/Desktop/IEEE_RAM/start.sh
             └─1661 /usr/bin/python3 main.py

Aug 05 22:49:30 raspberrypi systemd[1]: Started ieee_ram.service - IEEE RAM Main Python Script.
