# VirtualBox USB 设备挂载故障排除指南（Windows 宿主机版）

## 问题现象
VirtualBox 提示"不能挂载 USB 设备"，Omega.7 无法在虚拟机中识别。

---

## 解决方案（Windows 宿主机）

### 步骤 1: 安装 VirtualBox 扩展包（Extension Pack）

USB 2.0/3.0 支持需要安装扩展包：

1. 下载 VirtualBox Extension Pack：
   - 访问：https://www.virtualbox.org/wiki/Downloads
   - 下载 "VirtualBox Oracle VM VirtualBox Extension Pack"

2. 安装扩展包：
   - 打开 VirtualBox
   - 菜单 → 管理 → 工具 → 包管理器
   - 点击"安装"，选择下载的 `.vbox-extpack` 文件
   - 接受许可协议

### 步骤 2: 配置虚拟机 USB 设置

1. **关闭虚拟机**（如果正在运行）

2. 右键虚拟机 → 设置 → USB

3. 勾选"启用 USB 控制器"

4. 选择 **USB 3.0 (xHCI) 控制器**

5. 点击右侧的"+"图标（添加新的 USB 过滤器）

6. 从列表中选择 Omega.7 设备
   - 可能显示为 "Force Dimension" 
   - 或 VID:PID 1451:0301
   - 或 "Omega.7"

7. 点击"确定"保存设置

### 步骤 3: 启动虚拟机并挂载设备

1. 启动 Ubuntu 虚拟机

2. 确保 Omega.7 已开机并连接 USB

3. 在虚拟机运行时，点击 VirtualBox 菜单：
   **设备 → USB → 勾选 Omega.7/Force Dimension 设备**

4. 如果设备显示为灰色或无法勾选，尝试：
   - 拔掉 USB 重新插入
   - 重启 Omega.7（关机再开机）

### 步骤 4: 在虚拟机中检查设备

在 Ubuntu 虚拟机终端执行：

```bash
# 查看 USB 设备列表
lsusb

# 查找 Force Dimension 设备
lsusb | grep -i "1451\|force\|dimension"
```

如果看到类似输出，说明设备已识别：
```
Bus 001 Device 004: ID 1451:0301 Force Dimension
```

### 步骤 5: 配置 udev 规则（虚拟机内）

在虚拟机中执行：

```bash
# 检查 udev 规则文件是否存在
ls -l /etc/udev/rules.d/40-haptic-device-udev.rules

# 如果不存在，创建它
echo 'ATTR{idVendor}=="1451", ATTR{idProduct}=="0301", MODE="0666", GROUP="plugdev" | sudo tee /etc/udev/rules.d/40-haptic-device-udev.rules

# 重新加载规则
sudo udevadm control --reload-rules
sudo udevadm trigger

# 重新插拔 USB 设备
```

---

## 常见问题

### Q: USB 设备列表中没有 Omega.7？
**A:** 
1. 确保 Omega.7 电源已打开（底部开关）
2. 尝试更换 USB 端口（优先使用 USB 3.0 蓝色端口）
3. 在 Windows 设备管理器中检查是否有未知设备

### Q: 设备显示但无法勾选/挂载？
**A:** 
1. 关闭虚拟机，重新配置 USB 过滤器
2. 确保 Extension Pack 已正确安装
3. 以管理员身份运行 VirtualBox 再试

### Q: Windows 设备管理器显示未知设备？
**A:** 
1. 不要安装 Force Dimension 的 Windows 驱动（会与虚拟机冲突）
2. 在设备管理器中右键该设备 → 卸载设备
3. 然后在 VirtualBox 中重新挂载

---

## 快速检查清单

- [ ] VirtualBox Extension Pack 已安装
- [ ] 虚拟机 USB 3.0 控制器已启用
- [ ] Omega.7 已添加到 USB 过滤器
- [ ] Omega.7 已开机（底部开关打开）
- [ ] 在 VirtualBox 设备菜单中勾选了 Omega.7
- [ ] 虚拟机内执行 `lsusb` 能看到设备

---

## 测试连接

完成以上配置后，运行测试程序：

```bash
cd teletest_forcedimension
source handvenv/bin/activate
python3 test_omega7_debug.py
```

如果看到"✅ 设备已连接！"，说明配置成功！