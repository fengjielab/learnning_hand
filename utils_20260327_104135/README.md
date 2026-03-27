# Omega.7 设备管理指南

**创建时间：** 2026 年 3 月 27 日 10:41

---

## 问题：设备被占用

当您运行一个测试程序后，如果直接关闭终端或按 Ctrl+Z 挂起，设备可能仍被占用，导致新程序无法连接。

---

## 解决方案

### 方法 1：正确关闭程序（推荐）

**运行程序后，按 Ctrl+C 停止**（不要按 Ctrl+Z）：
- Ctrl+C：终止程序，正确关闭设备
- Ctrl+Z：挂起程序，设备仍被占用

---

### 方法 2：使用设备管理工具

**检查设备状态：**
```bash
cd teletest_forcedimension
source handvenv/bin/activate
python3 utils_20260327_104135/device_manager.py check
```

**完整释放设备（推荐）：**
```bash
python3 utils_20260327_104135/device_manager.py full
```

**仅终止占用进程：**
```bash
python3 utils_20260327_104135/device_manager.py kill
```

---

### 方法 3：手动释放设备

**1. 查找占用进程：**
```bash
ps aux | grep python | grep test_
```

**2. 终止进程：**
```bash
kill -9 <PID>
```

**3. 验证设备已释放：**
```bash
lsusb | grep 1451
```

---

### 方法 4：在代码中确保正确关闭

每个测试程序都包含 `finally` 块确保关闭设备：

```python
try:
    dhd.open()
    # ... 测试代码 ...
except KeyboardInterrupt:
    print("用户中断")
finally:
    # 确保关闭设备
    dhd.setForce(np.zeros(3))
    dhd.close()
    print("设备已关闭")
```

---

## 快速命令别名

在 `~/.bashrc` 中添加以下别名方便使用：

```bash
# Omega.7 设备管理
alias omega-check='cd /home/mfj/teletest_forcedimension && source handvenv/bin/activate && python3 utils_20260327_104135/device_manager.py check'
alias omega-release='cd /home/mfj/teletest_forcedimension && source handvenv/bin/activate && python3 utils_20260327_104135/device_manager.py full'
```

然后运行：
```bash
omega-check     # 检查设备状态
omega-release   # 释放设备
```

---

## 常见错误及解决

### 错误：`dhd.open() 返回值：-1`

**原因：** 设备被其他进程占用

**解决：**
```bash
python3 utils_20260327_104135/device_manager.py full
```

### 错误：`AttributeError: module 'forcedimension_core.dhd' has no attribute 'error'`

**原因：** SDK API 变化，代码中使用了不存在的函数

**解决：** 使用最新版本的测试程序

### 程序挂起后无法连接

**原因：** 按了 Ctrl+Z 而不是 Ctrl+C

**解决：**
```bash
# 查找挂起的进程
ps aux | grep -E "python.*test" | grep -v grep

# 终止进程
kill -9 <PID>
```

---

## 最佳实践

1. **运行程序前**先检查设备状态
2. **停止程序时**按 Ctrl+C，不要按 Ctrl+Z
3. **程序异常退出后**运行 `omega-release` 释放设备
4. **长时间不用时**关闭 Omega.7 电源