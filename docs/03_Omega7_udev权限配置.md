# Omega.7 udev 权限配置指南

**生成时间：** 2026 年 3 月 27 日 09:48:29

---

## 问题背景

虽然 `lsusb` 能看到 Omega.7 设备，但 Python 程序连接失败（返回错误码 -1）。这是因为 Linux 系统默认不允许普通用户直接访问 USB 设备，需要配置 udev 规则来解决权限问题。

---

## 配置步骤

### 步骤 1：创建 udev 规则文件

**命令：**
```bash
echo 'ATTR{idVendor}=="1451", ATTR{idProduct}=="0402", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/40-haptic-device-udev.rules
```

**作用说明：**
- 在 `/etc/udev/rules.d/` 目录下创建规则文件 `40-haptic-device-udev.rules`
- 规则内容解析：
  - `ATTR{idVendor}=="1451"` - 匹配 Vendor ID 为 1451 的设备（Force Dimension）
  - `ATTR{idProduct}=="0402"` - 匹配 Product ID 为 0402 的设备（Omega.7）
  - `MODE="0666"` - 设置设备权限为所有人可读可写
  - `GROUP="plugdev"` - 设置设备所属组为 plugdev

**类比：** 就像给系统保安下指令："看到这个设备（Omega.7），让所有人都能使用，不要拦着"

---

### 步骤 2：重新加载 udev 规则

**命令：**
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

**作用说明：**
- `--reload-rules` - 让系统重新读取所有 udev 规则文件（包括刚创建的那个）
- `--trigger` - 触发设备事件，让新规则立即生效
- 这样不需要重启就能应用新规则

**类比：** 就像通知所有保安："新规则已经发布了，马上执行！"

---

### 步骤 3：重新插拔/挂载设备

**操作：**
1. 在 VirtualBox 菜单中，点击 **设备 → USB**
2. 先**取消勾选** Omega.7 设备
3. 等待 5 秒
4. 再**重新勾选** Omega.7 设备

**作用说明：**
- 让 udev 规则应用到 Omega.7 设备上
- 设备重新连接时会应用新的权限设置

---

### 步骤 4：验证配置

**命令：**
```bash
ls -l /dev/bus/usb/*/* | grep 1451
```

**预期输出：**
```
crw-rw-rw- 1 root plugdev ... /dev/bus/usb/001/XXX
```

如果权限显示为 `crw-rw-rw-`（所有人可读写），说明配置成功。

---

### 步骤 5：测试连接

**命令：**
```bash
cd teletest_forcedimension
source handvenv/bin/activate
python3 test_omega7_debug.py
```

**预期输出：**
```
==================================================
Omega.7 设备测试（调试版）
==================================================

正在尝试连接设备...
dhd.open() 返回值：0
✅ 设备已连接！设备 ID: 0

设备信息:
  设备类型：omega7.x

开始读取位置数据...
提示：移动手柄查看数据变化 (Ctrl+C 停止)

位置：X:  -1.234 Y:  12.567 Z:  -3.891 mm
```

如果看到"✅ 设备已连接！"，说明配置成功！

---

## 快速执行（一键命令）

如果想一次性执行所有步骤，可以运行：

```bash
# 创建 udev 规则
echo 'ATTR{idVendor}=="1451", ATTR{idProduct}=="0402", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/40-haptic-device-udev.rules

# 重新加载规则
sudo udevadm control --reload-rules && sudo udevadm trigger

# 验证配置
ls -l /dev/bus/usb/*/* | grep 1451
```

然后在 VirtualBox 中重新挂载 Omega.7 设备，再运行测试程序。

---

## 故障排除

### Q: 规则文件创建失败？
**A:** 确保使用 sudo 权限，或检查 `/etc/udev/rules.d/` 目录是否存在。

### Q: 重新挂载后还是连接失败？
**A:** 
1. 检查规则文件是否存在：`cat /etc/udev/rules.d/40-haptic-device-udev.rules`
2. 尝试重启虚拟机
3. 确保 Omega.7 已开机（底部开关打开）

### Q: 权限还是不对？
**A:** 尝试将用户添加到 plugdev 组：
```bash
sudo usermod -a -G plugdev $USER
```
然后注销并重新登录。

---

## 文件清单

本配置目录包含：
- `03_Omega7_udev权限配置.md` - 本配置文件
- （可选）执行脚本

---

## 参考资料

- [Windows 到 VirtualBox USB 排错](./02_Windows到VirtualBox_USB排错.md)
- [Linux 宿主机环境配置指南](./01_Linux宿主机环境配置指南.md)
