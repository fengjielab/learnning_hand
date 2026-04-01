实验环境：
Ubuntu 20.04
omega.7

🛠️ Linux 下主手配置
1. SDK 下载
官网(https://forcedimension.com/software/sdk)下载对应版本 sdk，并解压。

tar -zxvf sdk-3.17.0-linux-x86_64-gcc.tar.gz
\bin：包含示例的可执行程序和运行 omega.x 所需的二进制文件
\examples：包含了一些演示程序
\doc：所有的说明文档和注意事项
\lib,\include：编译使用 Force Dimension SDK 所需要的库
2. 驱动安装
sudo apt install libusb-1.0
3. 坐标系
平移坐标系如图所示，实际的原点是整个设备的中心，是一个虚拟的点。

image.png

手腕的旋转方向如图所示，能够实现绕三个轴的旋转。

image.png

手指处可以返回夹爪角度，若是右手操作涉及的 omega.7 设备，如上图所示，则返回一个正角度。

下方圆盘上的三个孔位由左到右依次是

力按钮
力 LED
状态 LED（灭代表系统关闭、亮代表系统准备就绪、快速闪烁代表系统需要标定、缓慢闪烁代表腕部需要手动标定）
4. 标定
设备每次开机都需要校准一次，来保证末端执行器的准确和重复定位。

位置校准：校准时需要将校准杆放在校准孔中（圆盘中心处的空位），设备检测到达校准位置后自行校准，状态 LED 会停止闪烁。

姿态校准：为了校准手腕关节，必须将手腕处的三个旋转轴和夹爪控制轴移动到各自的行程终点，设备检测到后会自行完成校准。

自动校准的过程中不要触摸设备，校准完成后 LED 停止闪烁时再移动设备。

5. HapticDesk 可视化测试
打开 Omega.7 电源，并完成标定。

进入 sdk-3.17.0\bin 目录，使用 sudo ./HapticDesk 命令启动可视化窗口，操作 Omega.7 主手移动，可以看到界面上方的位置、转角、夹爪转角随之变化。

image.png

💻 相关程序
1. 配置环境
创建 conda 环境

conda create -n omega python=3.8
conda activate omega
python3 -m pip install forcedimension-core numpy
安装库

下载最新版本的 SDK，进入 sdk 目录，并进行手动安装（注意版本号是否正确）

cd sdk-3.17.0

sudo cp include/* /usr/local/include
sudo cp lib/release/*/* /usr/local/lib
sudo chmod 755 /usr/local/lib/libdhd.so.3.17.0
sudo chmod 755 /usr/local/lib/libdrd.so.3.17.0
sudo chmod 755 /usr/local/lib/libdhd.a
sudo chmod 755 /usr/local/lib/libdrd.a
sudo ln -s /usr/local/lib/libdhd.so.3.17.0 /usr/local/lib/libdhd.so
sudo ln -s /usr/local/lib/libdrd.so.3.17.0 /usr/local/lib/libdrd.so
如果需要卸载，使用类似的方法

sudo rm /usr/local/include/dhdc.h
sudo rm /usr/local/include/drdc.h
sudo rm /usr/local/lib/libdhd.a
sudo rm /usr/local/lib/libdhd.so.3.17.0
sudo rm /usr/local/lib/libdhd.so
sudo rm /usr/local/lib/libdrd.a
sudo rm /usr/local/lib/libdrd.so.3.17.0
sudo rm /usr/local/lib/libdrd.so
配置权限，主要是为了让普通用户访问 usb 设备，用于 ros 和 python 控制

在 /etc/udev/rules.d/ 下为设备添加 udev 规则。创建一个名为 40-haptic-device-udev.rules 的文件

sudo gedit /etc/udev/rules.d/40-haptic-device-udev.rules
然后粘贴以下模板

TTR{idVendor}=="", ATTR{idProduct}=="", MODE="0666", SYMLINK+="haptic_device_%k", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="", ATTR{idProduct}=="", MODE="0664", GROUP="plugdev"
使用 lsusb 可以查看供应商 ID 和产品 ID，格式为 idVendor:idProduct

使用设备名称（不带空格）替换掉 SYMLINK+="haptic_device_%k" 中的 haptic_device
在 ATTR{idVendor} 和 ATTR{idProduct} 的双引号中填写自己的供应商 ID 和产品 ID
修改完成后的示例如下：

ATTR{idVendor}=="1451", ATTR{idProduct}=="0301", MODE="0666", SYMLINK+="haptic_device_%k", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="1451", ATTR{idProduct}=="0301", MODE="0664", GROUP="plugdev"
执行以下命令重新加载 udev 规则

sudo udevadm control --reload-rules && sudo udevadm trigger
2. 基本程序
使用下面程序打印主手的位置

import forcedimension_core.containers as containers
import forcedimension_core.dhd as dhd

dhd.open()
pos = containers.Vec3()

# Equivalent to: dhd.getPosition(out=pos)
dhd.direct.getPosition(out=pos)

print(pos)
3. 主手控制 mujoco 机器人
fold
import gym
import numpy as np
from gym import error, spaces

import diffusion_policy.env.gym_envs
from diffusion_policy.env.gym_envs.utils import ctrl_set_action, mocap_set_action
import cv2
import mujoco_py
from diffusion_policy.env.gym_envs import rotations

from scipy.spatial.transform import Rotation as R

import forcedimension_core.containers as containers
import forcedimension_core.dhd as dhd
import forcedimension_core.drd as drd

import ctypes

#################### 初始化设备 ####################
# 打开设备
dhd.open()

# 全局变量，位置、旋转矩阵、夹爪角度、线速度、角速度
pos = np.zeros(3)
matrix = np.zeros((3, 3))
gripper_pointer = ctypes.pointer(ctypes.c_double(0.0))
linear_velocity = np.zeros(3)
angular_velocity = np.zeros(3)
euler = np.zeros(3)

# 力控配置
devicePosition = np.zeros(3)
deviceRotation = np.zeros((3, 3))
deviceLinearVelocity = np.zeros(3)
deviceAngularVelocity = np.zeros(3)

flagHoldPosition = True
flagHoldPositionReady = True
holdPosition = np.zeros(3)
holdRotation = np.zeros((3, 3))
last_display_time = dhd.os_independent.getTime()

# # 连续控制
# pos_continus = np.zeros(3)
# pos_result = np.zeros(3)
# flag_continus = False

# Drd 初始化
if drd.open() < 0:
    print("无法打开设备: " + drd.error())
    dhd.os_independent.sleep(2)
if not drd.isInitialized() and drd.autoInit() < 0:
    print("无法初始化设备: " + drd.error())
    dhd.os_independent.sleep(2)
if drd.start() < 0:
    print("无法启动设备: " + drd.error())
    dhd.os_independent.sleep(2)
if drd.moveToPos(pos, block=True) < 0:
    print("无法移动到位置: " + drd.error())
    dhd.os_independent.sleep(2)
if drd.moveToRot(euler, block=True) < 0:
    print("无法移动到旋转矩阵: " + drd.error())
    dhd.os_independent.sleep(2)
if drd.stop(True) < 0:
    print("无法停止设备: " + drd.error())
    dhd.os_independent.sleep(2)

# 记录相邻动作
last_action = np.array([1.17, 0.75, 0.70, -np.pi, 0., -np.pi/2, 0.])
action_list = []

#################### 常用函数 ####################

def quaternion2euler(quaternion):
    r = R.from_quat(quaternion)
    euler = r.as_euler('xyz', degrees=True)
    return euler


def euler2quaternion(euler):
    r = R.from_euler('xyz', euler, degrees=True)
    quaternion = r.as_quat()
    return quaternion


test_env = gym.make('PutInDrawer-v0')
test_env.reset()
# obs = test_env.reset()
# episode_acs = []
# episode_obs = []
# episode_info = []
# episode_obs.append(obs)    # 存储初始观察值
# idx = 0
# time_step = 0   # 记录总的时间步数
i=0
# viewer2 = mujoco_py.MjRenderContextOffscreen(test_env.sim, 0)
while True:
    ######################### 读取设备状态 #########################
    # 获取位置、旋转矩阵
    dhd.getPositionAndOrientationFrame(pos, matrix)
    # 获取夹爪角度
    dhd.getGripperAngleDeg(gripper_pointer)
    gripper = gripper_pointer.contents.value
    # 获取线速度
    dhd.getLinearVelocity(linear_velocity)
    # 获取角速度
    dhd.getAngularVelocityDeg(angular_velocity)

    ######################### 控制设备位置 #########################
    # 设置设备状态
    devicePosition = pos
    deviceRotation = matrix
    deviceLinearVelocity = linear_velocity
    deviceAngularVelocity = angular_velocity
    deviceForce = np.zeros(3)
    deviceTorque = np.zeros(3)
    deviceGripperForce = 0.0

    # 设置刚度和阻尼
    Kp = 2000.0
    Kv = 10.0
    Kr = 5.0
    Kw = 0.05

    # 保持设备位置
    if flagHoldPosition:
        if flagHoldPositionReady:
            # 计算反作用力
            force = -Kp * (devicePosition - holdPosition) - Kv * deviceLinearVelocity
            # 计算反作用力矩
            deltaRotation = np.transpose(deviceRotation) @ holdRotation
            axis, angle = np.zeros(3), 0.0
            # 计算旋转轴和角度
            angle = np.arccos((np.trace(deltaRotation) - 1) / 2)
            if angle > 1e-6:
                axis = np.array([deltaRotation[2, 1] - deltaRotation[1, 2],
                                 deltaRotation[0, 2] - deltaRotation[2, 0],
                                 deltaRotation[1, 0] - deltaRotation[0, 1]]) / (2 * np.sin(angle))
            torque = deviceRotation @ ((Kr * angle) * axis) - Kw * deviceAngularVelocity

            # 加上所有力
            deviceForce = deviceForce + force
            deviceTorque = deviceTorque + torque
        else:
            holdPosition = devicePosition
            holdRotation = deviceRotation
            flagHoldPositionReady = True

    # 设置设备力
    MaxTorque = 0.3
    if np.linalg.norm(deviceTorque) > MaxTorque:
        deviceTorque = MaxTorque * deviceTorque / np.linalg.norm(deviceTorque)
    # dhd.setForceAndTorqueAndGripperForce(deviceForce, deviceTorque, deviceGripperForce)

    if dhd.setForceAndTorqueAndGripperForce(np.zeros(3), np.zeros(3), 0.0) < 0:
        print("无法设置力和力矩: " + dhd.error())
        dhd.os_independent.sleep(2)
        break

    ######################### 键盘控制 #########################
    if dhd.os_independent.kbHit():
        keyboard = dhd.os_independent.kbGet()
        if keyboard == ' ':
            continue
        if keyboard == 'q':
            break

    # 周期打印设备状态，并刷新输出
    device_time = dhd.os_independent.getTime()
    if device_time - last_display_time > 0.1:
        last_display_time = device_time
        print("Pos (%.3f %.3f %.3f) m | Gripper %.3f deg | Rot (%.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f) | Force (%.3f %.3f %.3f) N | Freq %.2f kHz \r" 
              % (pos[0], pos[1], pos[2], gripper, matrix[0, 0], matrix[0, 1], matrix[0, 2], matrix[1, 0], matrix[1, 1], matrix[1, 2], matrix[2, 0], matrix[2, 1], matrix[2, 2], deviceForce[0], deviceForce[1], deviceForce[2], dhd.getComFreq()), end="\r", flush=True)

    # action = np.array([0, 0., 0, 0., 0., 0., 0.])
    # print(action)
    action_pos = pos
    action_matrix = matrix
    action_gripper = gripper

	# 将主手的运动范围映射到mujoco机器人工作空间
    # x从[-0.05,0.05]映射到[0.8,1.5]
    action_pos[0] = pos[0]*7    # + 1.15
    # y从[-0.1,0.1]映射到[0,1.2]
    action_pos[1] = pos[1]*6    # + 0.6
    # z从[-0.05,0.1]映射到[0.4,1.0]
    action_pos[2] = pos[2]*4    # + 0.6

    # 将旋转矩阵转换为四元数
    action_matrix *= 0.05
    # 绕x轴旋转180度的旋转矩阵
    matrix_rotation_x_180 = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    # 绕z轴旋转-90度的旋转矩阵
    matrix_rotation_z_n90 = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    # 旋转矩阵乘法
    action_matrix = np.dot(action_matrix, matrix_rotation_x_180)
    action_matrix = np.dot(action_matrix, matrix_rotation_z_n90)


    action_quat = rotations.mat2quat(action_matrix)
    
    # 将夹爪角度从[0,30](0为夹爪关闭)，归一化到[0,1](0为夹爪打开)
    action_gripper = abs((action_gripper - 30.0) / 30.0)

    # test_env.sim.step()             # 执行一步仿真，模拟环境中物体的运动和交互
    action = np.concatenate([action_pos, action_quat, [action_gripper]])
    test_env.step(action)             # 执行一步仿真，模拟环境中物体的运动和交互

    # gym 渲染
    test_env.render(mode="human")

    # 获取action
    action_list.append(action)
    
# 将动作列表转换为numpy数组并保存为文件
action_list = np.array(action_list)
# np.save("data/put_in_drawer/habtic_actions.npy", action_list)

if drd.close() < 0:
    print("无法关闭设备: " + drd.error())
    dhd.os_independent.sleep(2)
print("\n设备已关闭")
【设备使用】omega.7主手配置与使用方法
https://www.mahaofei.com/post/omega7.html
作者
马浩飞
发布于
2024-03-20
更新于
2024-03-20
许可协议
CC BY-NC-SA 4.0
机器人模仿设备使用
 打赏
cover of previous post
上一篇
【论文笔记】ACT 使用低成本硬件的双手操作模仿学习
cover of next post
下一篇
Python识别图片中文字和数字_easyocr
