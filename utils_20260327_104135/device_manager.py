"""
Omega.7 设备管理工具
用于检查设备占用状态、释放设备、正确关闭设备
"""

import subprocess
import sys
import forcedimension_core.dhd as dhd
import numpy as np

def check_device_connected():
    """检查设备是否连接到系统"""
    result = subprocess.run(['lsusb'], capture_output=True, text=True)
    if '1451:0402' in result.stdout or 'Force Dimension' in result.stdout:
        print("✅ 设备已在系统中识别")
        return True
    else:
        print("❌ 设备未在系统中识别")
        print("   请检查：")
        print("   1. Omega.7 是否已开机")
        print("   2. USB 线是否连接")
        print("   3. 在 VirtualBox 中是否已挂载设备")
        return False

def check_process_using_device():
    """检查是否有 Python 进程可能占用设备"""
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    lines = result.stdout.split('\n')
    
    using_processes = []
    for line in lines:
        if 'python' in line.lower() and ('test_' in line or 'omega' in line.lower()):
            if 'grep' not in line:
                using_processes.append(line)
    
    if using_processes:
        print("⚠️  发现可能占用设备的进程：")
        for proc in using_processes:
            parts = proc.split()
            if len(parts) >= 11:
                pid = parts[1]
                cmd = ' '.join(parts[10:])
                print(f"   PID {pid}: {cmd}")
        return using_processes
    else:
        print("✅ 没有发现占用设备的进程")
        return []

def kill_processes(processes):
    """终止指定的进程"""
    for proc in processes:
        parts = proc.split()
        if len(parts) >= 2:
            pid = parts[1]
            print(f"正在终止进程 {pid}...")
            subprocess.run(['kill', '-9', pid], capture_output=True)

def test_close_device():
    """测试连接并关闭设备（释放设备占用）"""
    print("\n尝试连接并关闭设备...")
    result = dhd.open()
    if result >= 0:
        print(f"✅ 设备已连接（ID: {result}），正在关闭...")
        dhd.setForce(np.zeros(3))
        dhd.close()
        print("✅ 设备已关闭")
        return True
    else:
        print(f"❌ 无法连接设备（错误码：{result}）")
        print("   设备可能仍被其他进程占用")
        return False

def main():
    print("=" * 60)
    print("Omega.7 设备管理工具")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        print("\n可用命令:")
        print("  check    - 检查设备状态")
        print("  kill     - 查找并终止占用设备的进程")
        print("  release  - 释放设备（连接并关闭）")
        print("  full     - 完整释放流程（推荐）")
        print("\n示例：python3 device_manager.py full")
        return
    
    if command == 'check':
        check_device_connected()
        check_process_using_device()
        
    elif command == 'kill':
        processes = check_process_using_device()
        if processes:
            kill_processes(processes)
            print("✅ 进程已终止")
        else:
            print("无需终止任何进程")
            
    elif command == 'release':
        test_close_device()
        
    elif command == 'full':
        print("\n=== 步骤 1: 检查设备连接 ===")
        if not check_device_connected():
            print("❌ 设备未连接，请先连接设备")
            return
        
        print("\n=== 步骤 2: 查找占用进程 ===")
        processes = check_process_using_device()
        if processes:
            print("\n=== 步骤 3: 终止占用进程 ===")
            kill_processes(processes)
            print("✅ 进程已终止")
        
        print("\n=== 步骤 4: 释放设备 ===")
        test_close_device()
        
        print("\n" + "=" * 60)
        print("✅ 设备释放完成！现在可以运行新程序了")
        print("=" * 60)
    else:
        print(f"未知命令：{command}")

if __name__ == '__main__':
    main()