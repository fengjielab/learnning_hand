import numpy as np
import forcedimension_core.dhd as dhd
import time

if dhd.open() < 0:
    print("❌ omega.7 未连接，请检查USB线")
    exit()

print("✅ 设备已连接！移动手柄查看数据 (Ctrl+C 停止)")
try:
    while True:
        pos = np.zeros(3)
        dhd.getPosition(pos)
        print(f"X:{pos[0]:.3f} Y:{pos[1]:.3f} Z:{pos[2]:.3f}", end="\r")
        time.sleep(0.05)
except KeyboardInterrupt:
    dhd.close()
    print("\n设备已关闭")
