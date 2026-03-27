# Omega.7 环境配置指南（通俗版）

## 类比：把 Omega.7 想象成一个"高级游戏手柄"

Omega.7 是一个力反馈设备，可以理解为：
- **普通游戏手柄**：你按按钮，游戏里有反应
- **Omega.7**：你移动手柄，电脑能感知位置；电脑也可以让手柄产生阻力/推力，给你"力反馈"

就像游戏手柄需要插USB、装驱动才能用，Omega.7 也需要配置环境。

---

## 配置步骤详解

### 步骤 1: 安装系统依赖 (`libusb-1.0`)

**干啥的？**
这是 Linux 系统用来和 USB 设备"说话"的工具包。

**通俗例子：**
> 你想和一个外国人交流，需要翻译。`libusb` 就是电脑和 USB 设备之间的"翻译官"。
> 没有它，电脑不知道 Omega.7 插在 USB 上想表达什么。

**做了什么？**
```bash
apt-get install libusb-1.0-0-dev
```
- 安装了 USB 通信的基础库
- 让系统能识别 USB 设备传来的数据

---

### 步骤 2: 配置 udev 规则

**干啥的？**
让普通用户（非管理员）也能使用 Omega.7，不需要每次都用 `sudo`。

**通俗例子：**
> 想象 USB 端口是一个"VIP房间"，默认只有老板(root)能进。
> udev 规则就是给保安的指令："看到这个设备(Omega.7)，让普通员工也能进"。

**做了什么？**
1. 检测 Omega.7 的 USB 身份证号（Vendor ID: 1451, Product ID: 0301）
2. 创建规则文件 `/etc/udev/rules.d/40-haptic-device-udev.rules`
3. 告诉系统："这个设备所有人都能用"

**规则文件内容解释：**
```
ATTR{idVendor}=="1451", ATTR{idProduct}=="0301", MODE="0666", GROUP="plugdev"
```
- `idVendor` / `idProduct`: 设备的"身份证号"
- `MODE="0666"`: 权限设为"所有人可读可写"
- `GROUP="plugdev"`: 属于 plugdev 组的人可以访问

---

### 步骤 3: 添加用户到 plugdev 组

**干啥的？**
让你当前登录的用户获得使用 USB 设备的权限。

**通俗例子：**
> 公司有一个"设备使用组"(plugdev)。
> 这一步就是把你加入到这个组里，这样你就能合法使用公司的设备了。

**做了什么？**
```bash
usermod -a -G plugdev <你的用户名>
```
- 把你的账号添加到 `plugdev` 组
- **注意**：需要注销并重新登录才能生效！

---

### 步骤 4: 安装 Python 依赖

**干啥的？**
安装 `forcedimension-core` —— 这是 Python 和 Omega.7 "对话" 的接口库。

**通俗例子：**
> 你想用微信和朋友聊天，需要先安装微信App。
> `forcedimension-core` 就是 Python 和 Omega.7 "聊天" 的 App。

**做了什么？**
```bash
pip install forcedimension-core numpy
```
- `forcedimension-core`: Omega.7 的官方 Python SDK
- `numpy`: 用于处理位置、力等数值数据

**代码中的使用：**
```python
import forcedimension_core.dhd as dhd

# 打开设备（就像打开微信开始聊天）
dhd.open()

# 获取位置（就像接收朋友发来的消息）
pos = np.zeros(3)
dhd.getPosition(pos)

# 设置力反馈（就像发送消息给朋友）
dhd.setForce([1.0, 0.0, 0.0])  # 在 X 方向施加 1N 的力
```

---

### 步骤 5: 检查 SDK 库

**干啥的？**
检查 Force Dimension 的 C/C++ 底层库是否已安装。

**通俗例子：**
> `forcedimension-core` 是微信App，但它需要操作系统支持网络连接。
> C/C++ SDK 就是操作系统的"网络驱动"。

**做了什么？**
- 检查 `/usr/local/lib` 下是否有 `libdhd.so` 等文件
- 如果没有，提示用户手动安装（需要从官网下载）

**为什么要手动安装？**
Force Dimension 是商业产品，SDK 需要注册下载，不能自动下载。

**安装方法（如果还没装）：**
```bash
# 1. 从官网下载 SDK，解压
tar -zxvf sdk-3.17.0-linux-x86_64-gcc.tar.gz
cd sdk-3.17.0

# 2. 复制头文件和库到系统目录
sudo cp include/* /usr/local/include
sudo cp lib/release/lin-x86_64-gcc/* /usr/local/lib

# 3. 创建软链接
sudo ln -s /usr/local/lib/libdhd.so.3.17.0 /usr/local/lib/libdhd.so
sudo ln -s /usr/local/lib/libdrd.so.3.17.0 /usr/local/lib/libdrd.so
```

---

### 步骤 6: 更新动态链接库缓存

**干啥的？**
让系统知道新安装的库在哪里。

**通俗例子：**
> 你搬家了，需要去邮局更新地址，这样信件才能寄到新地址。
> `ldconfig` 就是告诉系统："新的库文件在这里，记得找它们！"

**做了什么？**
```bash
ldconfig
```
- 扫描 `/usr/local/lib` 等目录
- 更新库文件索引缓存

---

## 配置流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    Omega.7 配置流程                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 安装 libusb          ← 让系统能和 USB 说话               │
│           ↓                                                 │
│  2. 配置 udev 规则       ← 让普通人能用设备                   │
│           ↓                                                 │
│  3. 添加用户到组         ← 把你加入"可以使用设备"的名单        │
│           ↓                                                 │
│  4. 安装 Python 库       ← 安装和 Omega.7 对话的接口          │
│           ↓                                                 │
│  5. 检查 C/C++ SDK       ← 检查底层驱动是否装好               │
│           ↓                                                 │
│  6. 更新库缓存           ← 让系统知道库在哪里                 │
│           ↓                                                 │
│     ✅ 配置完成！                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 常见问题

### Q: 为什么不用 sudo 就运行不了？
**A:** udev 规则没生效。尝试：
```bash
# 重新加载规则
sudo udevadm control --reload-rules
sudo udevadm trigger

# 或者重新插拔 USB，或重启电脑
```

### Q: `libdhd.so` 找不到怎么办？
**A:** 需要手动安装 Force Dimension SDK：
1. 去官网注册下载：https://forcedimension.com/software/sdk
2. 按上面的"步骤 5"安装

### Q: 提示 "权限 denied"？
**A:** 需要注销并重新登录，让用户组更改生效。

---

## 测试是否配置成功

```bash
cd teletest_forcedimension
python3 test_omega7_basic.py
```

如果看到：
- ✅ "设备已连接！" → 配置成功！
- ❌ "未连接，请检查USB线" → 检查硬件连接
- ❌ "找不到模块 forcedimension_core" → 步骤 4 没成功，重新安装 Python 库
