"""
Omega.7 力反馈测试程序
测试不同方向的力反馈效果
"""

import numpy as np
import forcedimension_core.dhd as dhd
import time

print("=" * 60)
print("Omega.7 力反馈测试")
print("=" * 60)

# 打开设备
print("\n正在连接设备...")
result = dhd.open()
if result < 0:
    print(f"❌ 设备连接失败！错误码：{result}")
    exit()

print(f"✅ 设备已连接！设备 ID: {result}")

# 获取设备信息
device_type = dhd.getSystemType()
print(f"设备类型：{device_type}")
print("✅ Omega.7 支持 3D 力反馈")

print("\n" + "=" * 60)
print("测试模式选择：")
print("  1 - 重力补偿（默认，感觉不到设备重量）")
print("  2 - 虚拟墙（碰到边界会有阻力）")
print("  3 - 弹簧效果（把手柄拉回中心）")
print("  4 - 持续力（感受固定方向的力）")
print("  5 - 关闭力反馈")
print("=" * 60)

try:
    mode = input("\n请选择测试模式 (1-5，默认 1): ").strip()
    if not mode:
        mode = '1'
except:
    mode = '1'

pos = np.zeros(3)
force = np.zeros(3)

# 初始位置
dhd.getPosition(pos)
center_pos = pos.copy()
print(f"\n中心位置：[{center_pos[0]:.3f}, {center_pos[1]:.3f}, {center_pos[2]:.3f}]")

print("\n开始力反馈测试... (按 Ctrl+C 停止)")
print("移动手柄感受力反馈效果\n")

last_display_time = time.time()
count = 0

try:
    while True:
        dhd.getPosition(pos)
        count += 1
        
        # 根据模式计算力
        if mode == '1':
            # 重力补偿 - 抵消设备自身重量
            force = np.array([0.0, 0.0, 0.0])
            dhd.setForce(force)
            
        elif mode == '2':
            # 虚拟墙 - 在边界处产生阻力
            wall_limit = 0.1  # 墙的位置（米）
            wall_stiffness = 1000  # 墙的刚度
            
            force = np.zeros(3)
            for i in range(3):
                if pos[i] > wall_limit:
                    force[i] = -wall_stiffness * (pos[i] - wall_limit)
                elif pos[i] < -wall_limit:
                    force[i] = -wall_stiffness * (pos[i] + wall_limit)
            dhd.setForce(force)
            
        elif mode == '3':
            # 弹簧效果 - 拉回中心
            spring_k = 200  # 弹簧系数
            force = -spring_k * (pos - center_pos)
            dhd.setForce(force)
            
        elif mode == '4':
            # 持续力 - 固定方向的力
            force = np.array([0.5, 0.0, 0.2])  # X 方向 0.5N，Z 方向 0.2N
            dhd.setForce(force)
            
        elif mode == '5':
            # 关闭力反馈
            dhd.setForce(np.zeros(3))
        
        # 定期显示状态
        current_time = time.time()
        if current_time - last_display_time >= 0.2:
            last_display_time = current_time
            print(f"位置：[{pos[0]:7.3f}, {pos[1]:7.3f}, {pos[2]:7.3f}] m | "
                  f"力：[{force[0]:6.2f}, {force[1]:6.2f}, {force[2]:6.2f}] N    ", 
                  end="\r")
            
except KeyboardInterrupt:
    print("\n\n用户中断")
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()

finally:
    # 关闭力反馈
    print("\n正在关闭力反馈...")
    dhd.setForce(np.zeros(3))
    
    # 关闭设备
    print("正在关闭设备...")
    dhd.close()
    print("✅ 设备已关闭")

print("=" * 60)
print("测试完成！")
print("=" * 60)