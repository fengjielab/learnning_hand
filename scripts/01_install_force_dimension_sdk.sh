#!/bin/bash
# Force Dimension SDK 自动安装脚本
# 使用方法: bash scripts/01_install_force_dimension_sdk.sh

set -e

SDK_VERSION="3.17.6"
SDK_FILE="${HOME}/下载/sdk-${SDK_VERSION}-linux-x86_64-gcc.tar.gz"

echo "=========================================="
echo "  Force Dimension SDK 安装脚本"
echo "  版本: $SDK_VERSION"
echo "=========================================="

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 步骤 1: 检查文件
echo ""
echo -e "${YELLOW}[步骤 1/4] 检查 SDK 文件...${NC}"
if [ ! -f "$SDK_FILE" ]; then
    echo "错误: 找不到文件 $SDK_FILE"
    echo "请确认文件路径正确"
    exit 1
fi
echo -e "${GREEN}✓ 找到 SDK 文件${NC}"

# 步骤 2: 解压
echo ""
echo -e "${YELLOW}[步骤 2/4] 解压 SDK...${NC}"
cd ~/下载
tar -zxvf sdk-${SDK_VERSION}-linux-x86_64-gcc.tar.gz
echo -e "${GREEN}✓ 解压完成${NC}"

# 步骤 3: 复制文件到系统目录
echo ""
echo -e "${YELLOW}[步骤 3/4] 安装库文件...${NC}"
echo "需要 sudo 权限..."

cd ~/下载/sdk-${SDK_VERSION}

# 复制头文件
sudo cp include/* /usr/local/include/
echo "  ✓ 头文件已复制"

# 复制库文件
sudo cp lib/release/lin-x86_64-gcc/* /usr/local/lib/
echo "  ✓ 库文件已复制"

# 创建软链接
cd /usr/local/lib
sudo ln -sf libdhd.so.${SDK_VERSION} libdhd.so
sudo ln -sf libdrd.so.${SDK_VERSION} libdrd.so
echo "  ✓ 软链接已创建"

echo -e "${GREEN}✓ 库文件安装完成${NC}"

# 步骤 4: 更新库缓存
echo ""
echo -e "${YELLOW}[步骤 4/4] 更新动态链接库缓存...${NC}"
sudo ldconfig
echo -e "${GREEN}✓ 缓存更新完成${NC}"

# 验证
echo ""
echo "=========================================="
echo "  验证安装..."
echo "=========================================="

if ldconfig -p | grep -q libdhd; then
    echo -e "${GREEN}✓ SDK 安装成功！${NC}"
    echo ""
    echo "已安装的文件:"
    ls -la /usr/local/lib/ | grep -E "dhd|drd" | awk '{print "  " $9 " -> " $11}'
else
    echo -e "${GREEN}✗ 安装可能失败，未找到 libdhd${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "  安装完成！现在可以运行测试程序了"
echo "=========================================="
echo ""
echo "测试命令:"
echo "  cd teletest_forcedimension"
echo "  source handvenv/bin/activate"
echo "  python test_omega7_force.py"
