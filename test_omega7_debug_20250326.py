"""
Omega.7 设备测试程序（调试版）
创建时间: 2025-03-26
"""

import numpy as np
import forcedimension_core.dhd as dhd
import time

print("=" * 50)
print("Omega.7 设备测试（调试版）")
print("创建时间: 2025-03-26")
print("=" * 50)

# 尝试打开设备
print("\n正在尝试连接设备...")
try:
    result = dhd.open()
    print(f"dhd.open() 返回值: {result}")
    
    if result < 0:
        print(f"❌ 设备连接失败！错误码: {result}")
        print(f"错误信息: {dhd.error()}")
        print("\n可能原因：")
        print("  1. Omega.7 未插 USB 线")
        print("  2. Omega.7 未开机")
        print("  3. 需要校准（LED 闪烁）")
        print("  4. udev 规则未生效")
        exit()
    
    print(f"✅ 设备已连接！设备 ID: {result}")
    
    # 获取设备信息
    print("\n设备信息:")
    device_type = dhd.getSystemType()
    print(f"  设备类型: {device_type}")
    
    # 读取位置数据
    print("\n开始读取位置数据...")
    print("提示: 移动手柄查看数据变化 (Ctrl+C 停止)\n")
    
    pos = np.zeros(3)
    count = 0
    
    while True:
        dhd.getPosition(pos)
        count += 1
        
        # 每 20 次刷新一次显示
        if count % 20 == 0:
            print(f"位置: X:{pos[0]:7.3f} Y:{pos[1]:7.3f} Z:{pos[2]:7.3f} mm    ", end="\r")
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\n用户中断")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    # 确保关闭设备
    print("\n正在关闭设备...")
    try:
        dhd.close()
        print("✅ 设备已关闭")
    except:
        print("设备关闭时出错（可能已断开）")

print("=" * 50)
