# 虚拟环境问题排查与修复指南

## 问题：找不到 python 命令

当你遇到类似以下错误时：
```bash
找不到命令"python"，您的意思是：
"python3" 命令来自 Debian 软件包 python3
"python" 命令来自 Debian 软件包 python-is-python3
```

## 问题原因

`.venv` 虚拟环境配置损坏，通常是因为：
- `pyvenv.cfg` 中的 `home` 指向了错误或不存在的路径
- 虚拟环境创建时 Python 解释器链接失效

检查方法：
```bash
cat .venv/pyvenv.cfg
```

如果 `home` 指向了一个不存在的路径，说明虚拟环境已损坏。

## 修复步骤

### 方法 1: 删除并重新创建（推荐）

```bash
# 1. 先退出当前虚拟环境
deactivate

# 2. 删除损坏的虚拟环境
rm -rf .venv

# 3. 用 uv 重新创建
uv venv --python 3.10

# 4. 激活新的虚拟环境
source .venv/bin/activate

# 5. 验证 Python 是否存在
which python
python --version
```

### 方法 2: 使用自定义虚拟环境名称

如果你想用其他名字（比如 `testvenv`、`myenv` 等）：

```bash
# 1. 创建自定义名称的虚拟环境
uv venv testvenv --python 3.10

# 2. 激活（注意路径变了）
source testvenv/bin/activate

# 3. 验证
which python
```

### 方法 3: 手动创建符号链接（临时修复）

如果你不想重新创建虚拟环境：

```bash
# 创建 python 和 python3 的符号链接
ln -s /usr/bin/python3 .venv/bin/python3
ln -s /usr/bin/python3 .venv/bin/python
```

> ⚠️ 注意：这只是临时修复，建议使用方法 1 彻底重建虚拟环境。

## 检查虚拟环境是否正常

激活虚拟环境后，运行以下命令检查：

```bash
# 检查 Python 解释器路径
which python
# 应该输出类似：/home/username/project/.venv/bin/python

# 检查 Python 版本
python --version

# 检查是否在虚拟环境中
echo $VIRTUAL_ENV
# 应该输出虚拟环境的路径
```

## 常见问题

### Q: 为什么会出现这个问题？
A: 通常是因为：
1. 使用 `uv venv` 创建时，指定的 Python 路径后来发生了变化
2. 之前的虚拟环境被删除或移动
3. 系统 Python 升级导致路径变化

### Q: 如何避免这个问题？
A: 
1. 使用系统安装的 Python 创建虚拟环境：`uv venv --python python3`
2. 不要手动修改 `.venv/pyvenv.cfg`
3. 如果移动项目，最好重新创建虚拟环境

### Q: 可以用 python3 命令代替吗？
A: 可以临时用 `python3` 代替 `python`，但这会绕过虚拟环境，使用系统 Python。建议在虚拟环境中创建符号链接或重新创建虚拟环境。

### Q: 如何切换到其他虚拟环境？
A:
```bash
# 先退出当前环境
deactivate

# 激活另一个环境
source testvenv/bin/activate
# 或
source myenv/bin/activate
```

## uv 常用命令

```bash
# 创建虚拟环境（默认名称 .venv）
uv venv

# 创建指定 Python 版本的虚拟环境
uv venv --python 3.10

# 创建自定义名称的虚拟环境
uv venv testvenv
uv venv myenv

# 激活虚拟环境（根据你的环境名称调整）
source .venv/bin/activate
source testvenv/bin/activate

# 退出虚拟环境
deactivate

# 安装包
uv pip install package_name

# 查看已安装包
uv pip list

# 删除虚拟环境
rm -rf .venv
rm -rf testvenv
```

---

**记录时间**：2026-03-25  
**问题**：虚拟环境中缺少 python 解释器  
**原因**：pyvenv.cfg 指向了错误的路径
