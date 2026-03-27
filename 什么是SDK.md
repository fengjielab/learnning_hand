# SDK 是什么？通俗解释

## 一句话
**SDK 是 "让 Omega.7 硬件和电脑说话" 的底层驱动程序。**

---

## 类比理解

### 例子 1：打印机和驱动
- **Omega.7 硬件** = 打印机
- **Python 代码** = Word 文档
- **SDK (C 库)** = 打印机驱动程序

你想用 Word 打印文件，需要：
1. Word 能调用打印功能 → Python 库 (`forcedimension-core`)
2. 打印机驱动让电脑认识打印机 → SDK (`libdhd.so`)

没有驱动，Word 再智能也指挥不了打印机。

---

### 例子 2：游戏手柄
- **Omega.7** = PS5 手柄
- **Python 程序** = 游戏程序
- **SDK** = 手柄驱动

你想在游戏中用手柄：
1. 游戏支持手柄操作 → Python 库
2. 系统能识别手柄 → SDK 驱动

---

## SDK 里有什么？

```
sdk-3.17.0/
├── include/           # 头文件（告诉程序有哪些功能可用）
│   ├── dhd.h          # 位置、力控制相关
│   └── drd.h          # 机器人控制相关
│
├── lib/               # 编译好的库文件（实际执行的代码）
│   └── release/
│       └── lin-x86_64-gcc/
│           ├── libdhd.so.3.17.0    # 核心库（位置/力控制）
│           ├── libdrd.so.3.17.0    # 机器人控制库
│           └── ...
│
├── bin/               # 可执行程序
│   └── HapticDesk     # 官方测试软件
│
└── examples/          # C/C++ 示例代码
```

---

## 为什么 Python 需要 C 库？

Python 运行慢，控制硬件需要**实时性**（几毫秒内响应）。

所以架构是：

```
你的 Python 代码
      ↓ 调用
forcedimension-core (Python 库)
      ↓ 调用
libdhd.so (C 库，SDK 提供)
      ↓ 通过 USB
Omega.7 硬件
```

**错误 `ImportError: There were problems loading libdrd` 的意思：**
Python 库想调用底层 C 库，但找不到文件！

就像微信想发消息，但发现手机没装 SIM 卡。

---

## 安装后会发生什么？

### 安装前
```bash
$ ls /usr/local/lib/ | grep dhd
(空，什么都没有)

$ python test.py
ImportError: There were problems loading libdrd
```

### 安装 SDK 后
```bash
$ ls /usr/local/lib/ | grep dhd
libdhd.so          ← 软链接
libdhd.so.3.17.0   ← 实际文件
libdrd.so
libdrd.so.3.17.0

$ python test.py
✅ 设备已连接！
```

---

## 总结

| 组件 | 作用 | 类比 |
|------|------|------|
| Omega.7 硬件 | 物理设备 | 打印机 |
| SDK (C 库) | 底层驱动 | 打印机驱动程序 |
| forcedimension-core | Python 接口 | Word 的打印菜单 |
| 你的 Python 代码 | 应用程序 | Word 文档 |

**现在懂了吗？SDK 就是让硬件和软件能 "沟通" 的桥梁！**
