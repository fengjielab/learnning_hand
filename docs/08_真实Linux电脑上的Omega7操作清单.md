# 真实 Linux 电脑上的 Omega.7 操作清单

这份清单是给“明天直接把 Omega.7 带到真实 Linux 电脑上使用”准备的。

这里假设你的环境是:

- 一台真正的 Linux 电脑
- Omega.7 直接插在这台 Linux 电脑上
- 不再经过 Windows + VirtualBox

这很重要，因为这样会比虚拟机环境简单很多。

---

## 0. 先记住今天最重要的一句话

不要一上来就 Docker。

先证明:

- Linux 宿主机能识别 Omega.7
- Linux 宿主机上的 Python 能直接打开 Omega.7

宿主机通了以后，再考虑 Docker。

---

## 1. 把设备插好，先别急着跑脚本

先确认:

- Omega.7 USB 线已经插好
- Omega.7 已开机
- Linux 电脑已经启动完成

然后先执行:

```bash
lsusb
```

或者更直接一点:

```bash
lsusb | grep -i "1451\|force\|dimension"
```

### 你想看到什么

你希望看到类似:

```text
Bus 001 Device XXX: ID 1451:0402 Force Dimension
```

### 如果这里什么都看不到

先不要继续跑脚本。

优先检查:

1. USB 线是否接好
2. 设备是否开机
3. 是否换一个 USB 口
4. Linux 宿主机是否真的识别到设备

只有 `lsusb` 能看到设备，后面的步骤才值得继续。

---

## 2. 进入项目目录

执行:

```bash
cd /home/mfj/teletest_forcedimension
```

如果你的项目不在这个路径，就切到实际所在目录。

---

## 3. 运行环境初始化脚本

执行:

```bash
sudo bash scripts/02_setup_omega7_environment.sh
```

这个脚本会帮你做这些事情:

1. 安装 `libusb`
2. 写 `udev` 规则
3. 把用户加入 `plugdev`
4. 安装 Python 依赖
5. 检查 Force Dimension SDK 库
6. 更新动态链接库缓存

所以它是你明天最合适的主入口脚本。

---

## 4. 脚本跑完后，不要立刻判断成败

脚本跑完以后，有两类配置经常还需要“重新生效”。

### 4.1 `udev` 规则

可能需要:

- 重新插拔 Omega.7
- 或者重启系统

### 4.2 用户组权限

如果脚本把你加入了 `plugdev`，往往还需要:

- 注销重新登录
- 或者重新开一个新的终端会话

所以脚本跑完以后，建议至少做这件事:

1. 拔掉 Omega.7
2. 再重新插上
3. 重新打开一个终端

如果还是不顺，再考虑注销重登。

---

## 5. 再次确认宿主机还能看到设备

重新执行:

```bash
lsusb | grep -i "1451\|force\|dimension"
```

如果这里还能看到设备，说明宿主机层至少还是通的。

---

## 6. 先跑最小连接测试

优先跑最简单的测试，不要一上来就跑复杂脚本。

如果你继续使用当前虚拟环境，执行:

```bash
cd /home/mfj/teletest_forcedimension
source handvenv/bin/activate
python3 tests/01_basic_device_connection.py
```

这个脚本的目标只有一个:

- 验证 Python 能不能真正打开 Omega.7

### 成功时你会看到

类似:

```text
✅ 设备已连接！移动手柄查看数据
```

### 失败时你会看到

类似:

```text
❌ omega.7 未连接，请检查USB线
```

---

## 7. 如果最小测试不行，再跑调试版

执行:

```bash
python3 tests/02_debug_device_connection.py
```

这个脚本会更适合定位问题。

它会提示的常见原因包括:

1. Omega.7 未插 USB 线
2. Omega.7 未开机
3. 需要校准
4. `udev` 规则未生效
5. 设备没有被系统正确访问

---

## 8. 如果怀疑设备被占用，先释放设备

执行:

```bash
python3 tools/device_manager.py full
```

这个工具会做几件事:

1. 检查设备有没有被系统识别
2. 检查有没有 Python 进程占用设备
3. 终止可疑进程
4. 尝试打开并关闭设备，释放占用

这个步骤特别适合:

- 反复调试时
- 上一个程序没正常退出时
- 你按过 `Ctrl+Z` 把程序挂起过时

---

## 9. 最小连接成功后，再做更复杂的测试

顺序建议是:

### 先做力反馈测试

```bash
python3 tests/03_force_feedback_modes.py
```

### 再做 Mujoco 联动测试

```bash
python3 tests/04_mujoco_view_control.py
```

注意:

- Mujoco 测试通常需要桌面环境
- 不适合只在 SSH 纯终端里跑

---

## 10. 明天最推荐的完整命令顺序

你可以直接按下面这套走:

```bash
lsusb | grep -i "1451\|force\|dimension"
cd /home/mfj/teletest_forcedimension
sudo bash scripts/02_setup_omega7_environment.sh
lsusb | grep -i "1451\|force\|dimension"
source handvenv/bin/activate
python3 tests/01_basic_device_connection.py
python3 tests/02_debug_device_connection.py
python3 tools/device_manager.py full
python3 tests/03_force_feedback_modes.py
```

其中:

- `tests/01_basic_device_connection.py`
  是最关键的宿主机验证脚本
- 前面的都可以失败，但只要这一步不通，就不要急着上 Docker

---

## 11. 明天最可能遇到的问题

### 问题 1: `lsusb` 看不到设备

这说明问题还停留在硬件或宿主机层。

优先查:

- USB 线
- 电源
- USB 接口
- 设备是否开机

---

### 问题 2: `lsusb` 能看到，但 Python 打不开

这通常优先怀疑:

- `udev` 规则没生效
- 用户组权限没生效
- 设备需要重新插拔

---

### 问题 3: Python 包装好了，但底层 SDK 库有问题

这时重点看:

- `scripts/01_install_force_dimension_sdk.sh`
- `scripts/02_setup_omega7_environment.sh`

尤其关注:

- `libdhd`
- `libdrd`
- `ldconfig`

---

### 问题 4: 设备被占用

这时优先跑:

```bash
python3 tools/device_manager.py full
```

---

## 12. 明天不要做的事

下面这些事不建议一上来就做:

1. 不要先上 Docker
2. 不要先上 Mujoco 图形界面
3. 不要同时折腾机械臂、手柄、仿真、Docker
4. 不要跳过最小连接测试

明天最重要的目标不是“全部跑通”，而是:

**先证明真实 Linux 宿主机能稳定识别并打开 Omega.7。**

---

## 13. 明天成功的标准

如果你能做到下面这一步，就已经很成功了:

```bash
python3 tests/01_basic_device_connection.py
```

并且看到:

```text
✅ 设备已连接！移动手柄查看数据
```

只要这一步宿主机上稳定成立，后面 Docker 化就会容易很多。

---

## 14. 下一步是什么

一旦明天宿主机直连 Omega.7 成功，下一步才是:

1. 整理真正的 `hand_controller` 服务结构
2. 再考虑 Docker 访问 USB
3. 最后把它接进你的三服务系统

顺序不要反过来。
