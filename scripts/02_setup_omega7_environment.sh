#!/bin/bash
# Omega.7 环境配置脚本
# 使用方法: sudo bash scripts/02_setup_omega7_environment.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "    Omega.7 力反馈设备环境配置脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 步骤 1: 安装系统依赖
# ============================================
echo ""
echo -e "${YELLOW}[步骤 1/6] 安装系统依赖${NC}"
echo "------------------------------------------"
echo "说明: 安装 libusb-1.0，这是与 USB 设备通信所需的库"
echo ""

apt-get update
apt-get install -y libusb-1.0-0-dev libusb-1.0-0

echo -e "${GREEN}✓ 系统依赖安装完成${NC}"

# ============================================
# 步骤 2: 配置 udev 规则 (USB 权限)
# ============================================
echo ""
echo -e "${YELLOW}[步骤 2/6] 配置 udev 规则${NC}"
echo "------------------------------------------"
echo "说明: 创建 udev 规则，允许普通用户访问 Omega.7 USB 设备"
echo "      这样就不需要每次都用 sudo 运行程序"
echo ""

UDEV_FILE="/etc/udev/rules.d/40-haptic-device-udev.rules"

# 检测 Omega.7 的 USB ID
echo "正在检测 Omega.7 USB 设备..."
USB_INFO=$(lsusb | grep -i "force\|dimension\|1451" || echo "")

if [ -n "$USB_INFO" ]; then
    echo "检测到设备: $USB_INFO"
    # 提取 ID (格式: ID 1451:0301)
    VENDOR_ID=$(echo "$USB_INFO" | grep -oP 'ID \K[0-9a-fA-F]{4}' | head -1)
    PRODUCT_ID=$(echo "$USB_INFO" | grep -oP 'ID [0-9a-fA-F]{4}:\K[0-9a-fA-F]{4}' | head -1)
else
    echo "未检测到设备，使用默认 ID (1451:0301)"
    VENDOR_ID="1451"
    PRODUCT_ID="0301"
fi

echo "使用 USB ID - 厂商: $VENDOR_ID, 产品: $PRODUCT_ID"

# 创建 udev 规则文件
cat > "$UDEV_FILE" << EOF
# Omega.7 力反馈设备 udev 规则
# 允许 plugdev 组的用户访问设备

ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="$PRODUCT_ID", MODE="0666", SYMLINK+="omega7_%k", GROUP="plugdev"
SUBSYSTEM=="usb", ACTION=="add", ENV{DEVTYPE}=="usb_device", ATTR{idVendor}=="$VENDOR_ID", ATTR{idProduct}=="$PRODUCT_ID", MODE="0664", GROUP="plugdev"
EOF

echo "udev 规则已写入: $UDEV_FILE"

# 重新加载 udev 规则
udevadm control --reload-rules
udevadm trigger

echo -e "${GREEN}✓ udev 规则配置完成${NC}"

# ============================================
# 步骤 3: 添加用户到 plugdev 组
# ============================================
echo ""
echo -e "${YELLOW}[步骤 3/6] 配置用户权限${NC}"
echo "------------------------------------------"
echo "说明: 将当前用户添加到 plugdev 组，获得 USB 设备访问权限"
echo ""

CURRENT_USER=${SUDO_USER:-$USER}
if [ "$CURRENT_USER" = "root" ]; then
    echo -e "${YELLOW}警告: 当前以 root 运行，跳过用户组配置${NC}"
    echo "请手动运行: sudo usermod -a -G plugdev <你的用户名>"
else
    usermod -a -G plugdev "$CURRENT_USER"
    echo "用户 '$CURRENT_USER' 已添加到 plugdev 组"
fi

echo -e "${GREEN}✓ 用户权限配置完成${NC}"

# ============================================
# 步骤 4: 安装 Python 依赖
# ============================================
echo ""
echo -e "${YELLOW}[步骤 4/6] 安装 Python 依赖${NC}"
echo "------------------------------------------"
echo "说明: 安装 forcedimension-core (SDK 的 Python 绑定) 和 numpy"
echo ""

# 检查是否在虚拟环境中
if [ -n "$VIRTUAL_ENV" ]; then
    echo "检测到虚拟环境: $VIRTUAL_ENV"
    pip install forcedimension-core numpy
else
    echo "未检测到虚拟环境，使用系统 Python"
    pip3 install forcedimension-core numpy
fi

echo -e "${GREEN}✓ Python 依赖安装完成${NC}"

# ============================================
# 步骤 5: 检查 SDK 库
# ============================================
echo ""
echo -e "${YELLOW}[步骤 5/6] 检查 Force Dimension SDK${NC}"
echo "------------------------------------------"
echo "说明: 检查 SDK 库文件是否已安装"
echo "      如果未找到，需要手动安装 SDK (从官网下载)"
echo ""

# 检查库文件
if ldconfig -p | grep -q libdhd; then
    echo -e "${GREEN}✓ SDK 库已安装${NC}"
    ldconfig -p | grep libdhd
else
    echo -e "${RED}✗ 未找到 SDK 库 (libdhd)${NC}"
    echo "请按以下步骤手动安装 SDK:"
    echo "  1. 从 https://forcedimension.com/software/sdk 下载 Linux SDK"
    echo "  2. 解压: tar -zxvf sdk-3.x.x-linux-x86_64-gcc.tar.gz"
    echo "  3. 进入 sdk 目录，执行以下命令:"
    echo ""
    echo "     sudo cp include/* /usr/local/include"
    echo "     sudo cp lib/release/lin-x86_64-gcc/* /usr/local/lib"
    echo "     sudo chmod 755 /usr/local/lib/libdhd.so.*"
    echo "     sudo chmod 755 /usr/local/lib/libdrd.so.*"
    echo "     sudo ln -sf /usr/local/lib/libdhd.so.3.* /usr/local/lib/libdhd.so"
    echo "     sudo ln -sf /usr/local/lib/libdrd.so.3.* /usr/local/lib/libdrd.so"
    echo "     sudo ldconfig"
fi

# ============================================
# 步骤 6: 更新动态链接库缓存
# ============================================
echo ""
echo -e "${YELLOW}[步骤 6/6] 更新动态链接库缓存${NC}"
echo "------------------------------------------"
echo "说明: 运行 ldconfig 使系统能找到新安装的库"
echo ""

ldconfig

echo -e "${GREEN}✓ 动态链接库缓存更新完成${NC}"

# ============================================
# 配置完成
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}    配置完成！${NC}"
echo "=========================================="
echo ""
echo "重要提示:"
echo "  1. ${YELLOW}请重新插拔 Omega.7 USB 线${NC} 或重启系统以应用 udev 规则"
echo "  2. ${YELLOW}请注销并重新登录${NC} 以使用户组更改生效"
echo ""
echo "测试设备连接:"
echo "  cd teletest_forcedimension"
echo "  python3 test_omega7_basic.py"
echo ""
