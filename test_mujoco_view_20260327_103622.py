"""
Omega.7 主手控制 Mujoco 机器人测试程序
使用 Omega.7 力反馈设备控制 Mujoco 仿真环境中的机械臂
"""

import numpy as np
import forcedimension_core.dhd as dhd
import mujoco
import mujoco.viewer
import time
from scipy.spatial.transform import Rotation as R

print("=" * 60)
print("Omega.7 控制 Mujoco 机器人测试")
print("=" * 60)

# ==================== 初始化 Omega.7 设备 ====================
print("\n正在连接 Omega.7 设备...")
result = dhd.open()
if result < 0:
    print(f"❌ 设备连接失败！错误码：{result}")
    exit()
print(f"✅ Omega.7 已连接！设备 ID: {result}")

# 初始化变量
pos = np.zeros(3)
matrix = np.zeros((3, 3))
gripper_angle = 0.0

# ==================== 创建 Mujoco 环境 ====================
print("\n正在创建 Mujoco 环境...")

# 创建一个简单的机械臂环境 XML
xml_content = """
<mujoco model="robot_arm">
  <option timestep="0.002"/>
  
  <visual>
    <headlight ambient="0.4 0.4 0.4" diffuse="0.8 0.8 0.8" specular="0.1 0.1 0.1"/>
    <map znear="0.1"/>
  </visual>
  
  <asset>
    <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
    <texture name="texplane" type="2d" builtin="checker" rgb1="0.2 0.3 0.4" rgb2="0.1 0.15 0.2" width="512" height="512"/>
    <material name="MatPlane" reflectance="0.5" texture="texplane" texrepeat="1 1" texuniform="true"/>
  </asset>
  
  <worldbody>
    <!-- 地面 -->
    <geom name="floor" size="0 0 0.05" type="plane" material="MatPlane"/>
    
    <!-- 机械臂基座 -->
    <body name="base" pos="0 0 0.1">
      <geom name="base_geom" type="cylinder" size="0.05 0.05" rgba="0.3 0.3 0.3 1"/>
      
      <!-- 关节 1 -->
      <body name="link1" pos="0 0 0.1">
        <joint name="joint1" type="hinge" axis="0 0 1" limited="true" range="-3.14 3.14"/>
        <geom name="link1_geom" type="cylinder" size="0.03 0.1" pos="0 0 0.1" rgba="0.8 0.2 0.2 1"/>
        
        <!-- 关节 2 -->
        <body name="link2" pos="0 0 0.2">
          <joint name="joint2" type="hinge" axis="1 0 0" limited="true" range="-1.57 1.57"/>
          <geom name="link2_geom" type="cylinder" size="0.025 0.15" pos="0 0 0.15" rgba="0.2 0.8 0.2 1"/>
          
          <!-- 关节 3 -->
          <body name="link3" pos="0 0 0.3">
            <joint name="joint3" type="hinge" axis="1 0 0" limited="true" range="-1.57 1.57"/>
            <geom name="link3_geom" type="cylinder" size="0.02 0.1" pos="0 0 0.1" rgba="0.2 0.2 0.8 1"/>
            
            <!-- 夹爪 -->
            <body name="gripper" pos="0 0 0.2">
              <joint name="gripper_joint" type="slide" axis="0 1 0" limited="true" range="0 0.05"/>
              <geom name="finger1_geom" type="box" size="0.01 0.02 0.05" pos="0 0.02 0" rgba="0.8 0.8 0.2 1"/>
            </body>
          </body>
        </body>
      </body>
    </body>
    
    <!-- 目标物体 -->
    <body name="target" pos="0.2 0.2 0.2">
      <geom name="target_geom" type="sphere" size="0.03" rgba="1 0.5 0 0.5"/>
      <light name="target_light" pos="0 0 0.5"/>
    </body>
  </worldbody>
  
  <!-- 执行器 -->
  <actuator>
    <motor name="motor1" joint="joint1" ctrlrange="-1 1" ctrllimited="true"/>
    <motor name="motor2" joint="joint2" ctrlrange="-1 1" ctrllimited="true"/>
    <motor name="motor3" joint="joint3" ctrlrange="-1 1" ctrllimited="true"/>
    <motor name="gripper_motor" joint="gripper_joint" ctrlrange="-0.5 0.5" ctrllimited="true"/>
  </actuator>
  
  <!-- 传感器 -->
  <sensor>
    <jointpos name="joint1_pos" joint="joint1"/>
    <jointpos name="joint2_pos" joint="joint2"/>
    <jointpos name="joint3_pos" joint="joint3"/>
  </sensor>
</mujoco>
"""

# 加载模型
model = mujoco.MjModel.from_xml_string(xml_content)
data = mujoco.MjData(model)

# 检查模型
if model.nu < 4:
    print("⚠️ 警告：模型执行器数量不足")

print("✅ Mujoco 环境创建成功！")
print(f"  - 自由度：{model.nq}")
print(f" - 执行器：{model.nu}")

# ==================== 控制参数 ====================
# Omega.7 工作空间到 Mujoco 的映射
pos_scale = np.array([10.0, 10.0, 10.0])  # 位置缩放
pos_offset = np.array([0.0, 0.0, 0.2])    # 位置偏移

# PD 控制参数
Kp = 100.0  # 比例增益
Kd = 10.0   # 微分增益

print("\n" + "=" * 60)
print("控制说明:")
print("  - 移动 Omega.7 手柄控制机械臂末端位置")
print("  - X 轴：左右移动")
print("  - Y 轴：前后移动")
print("  - Z 轴：上下移动")
print("  - 夹爪：捏合手柄夹爪控制机械臂夹爪")
print("=" * 60)
print("\n按 Ctrl+C 退出\n")

# ==================== 主控制循环 ====================
last_time = time.time()
gripper_prev = 0.0

try:
    with mujoco.viewer.launch_passive(model, data) as viewer:
        print("✅ Mujoco 查看器已启动")
        
        while viewer.is_running():
            # 读取 Omega.7 状态
            dhd.getPositionAndOrientationFrame(pos, matrix)
            dhd.getGripperAngleDeg(gripper_angle)
            
            # 计算目标关节角度（逆运动学简化版）
            # 这里使用简化的映射，实际应用中需要完整的逆运动学
            
            # 将 Omega.7 位置映射到机械臂工作空间
            target_pos = pos * pos_scale + pos_offset
            
            # 简化的控制：直接映射位置到关节角度
            data.ctrl[0] = np.arctan2(target_pos[1], target_pos[0]) * 0.5  # 关节 1：基座旋转
            data.ctrl[1] = -target_pos[2] * 2.0  # 关节 2：肩膀
            data.ctrl[2] = target_pos[2] * 2.0  # 关节 3：肘部
            
            # 夹爪控制：将 Omega.7 夹爪角度 (0-30 度) 映射到机械臂夹爪 (0-0.05m)
            gripper_normalized = np.clip((30.0 - gripper_angle) / 30.0, 0, 1)
            data.ctrl[3] = gripper_normalized * 0.05
            
            # 步进仿真
            mujoco.mj_step(model, data)
            
            # 更新查看器
            viewer.sync()
            
            # 限制帧率
            elapsed = time.time() - last_time
            if elapsed < 0.016:  # ~60Hz
                time.sleep(0.016 - elapsed)
            last_time = time.time()
            
            # 显示状态
            if int(last_time * 10) % 10 == 0:
                print(f"\rOmega.7 位置：[{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] m | "
                      f"夹爪：{gripper_angle:5.1f}°    ", end="", flush=True)
                
except KeyboardInterrupt:
    print("\n\n用户中断")
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()

finally:
    # 关闭设备
    print("\n正在关闭 Omega.7...")
    dhd.setForce(np.zeros(3))
    dhd.close()
    print("✅ 设备已关闭")

print("=" * 60)
print("测试完成！")
print("=" * 60)