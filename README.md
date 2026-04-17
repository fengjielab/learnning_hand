# Omega.7 项目导航

这个项目已经按用途整理成了几类，后面你找文件会轻松很多。

## 目录作用

`docs/`

- 放说明文档和学习资料

`scripts/`

- 放安装和初始化脚本

`tests/`

- 放测试脚本，按从简单到复杂排序

`tools/`

- 放辅助工具，比如设备占用检查和释放

`handvenv/`

- 这是当前可用的 Python 虚拟环境
- 这次先不改名，避免把现有环境弄断

## 建议阅读顺序

1. [00_项目总览.md](/home/mfj/teletest_forcedimension/docs/00_项目总览.md)
2. [01_Linux宿主机环境配置指南.md](/home/mfj/teletest_forcedimension/docs/01_Linux宿主机环境配置指南.md)
3. 如果你还在 Windows + VirtualBox 环境，再看 [02_Windows到VirtualBox_USB排错.md](/home/mfj/teletest_forcedimension/docs/02_Windows到VirtualBox_USB排错.md)
4. 如果你要在新电脑上重建环境，再看 [09_新机器初始化步骤.md](/home/mfj/teletest_forcedimension/docs/09_新机器初始化步骤.md)
5. 运行测试前，先看 [tools/README.md](/home/mfj/teletest_forcedimension/tools/README.md)
6. 再按 `tests/` 里的编号顺序跑脚本

## 最常用的文件

- [01_basic_device_connection.py](/home/mfj/teletest_forcedimension/tests/01_basic_device_connection.py)
  最小连接测试
- [02_debug_device_connection.py](/home/mfj/teletest_forcedimension/tests/02_debug_device_connection.py)
  失败时更容易定位问题
- [03_force_feedback_modes.py](/home/mfj/teletest_forcedimension/tests/03_force_feedback_modes.py)
  力反馈测试
- [04_mujoco_view_control.py](/home/mfj/teletest_forcedimension/tests/04_mujoco_view_control.py)
  Mujoco 联动测试
- [device_manager.py](/home/mfj/teletest_forcedimension/tools/device_manager.py)
  检查设备、释放设备

## 环境重建

- [requirements.txt](/home/mfj/teletest_forcedimension/requirements.txt)
  新机器上安装 Python 依赖的入口
