# GitHub SSH 配置与推送指南

这份文档记录的是:

- 如何在 Linux 终端里配置 GitHub SSH key
- 如何把本地 Git 仓库从 HTTPS 改成 SSH
- 如何把本地提交推送到 GitHub

这份指南特别适合下面这种场景:

- 你在 Ubuntu 终端里工作
- 可能是在真实 Linux 电脑上
- 也可能是 Windows 通过 SSH 连到 Linux/虚拟机
- 你想避免每次 `git push` 都输入 GitHub 用户名和密码

---

## 1. 先理解为什么推荐 SSH

GitHub 远端常见有两种写法:

### HTTPS

```bash
https://github.com/<用户名>/<仓库名>.git
```

特点:

- 容易看懂
- 但推送时常常要处理用户名、Token 或网页登录

### SSH

```bash
git@github.com:<用户名>/<仓库名>.git
```

特点:

- 配好一次后，后面推送更顺
- 更适合长期在 Linux 终端里开发

所以如果你经常在终端里 `git push`，推荐尽早改成 SSH。

---

## 2. 检查本机有没有 SSH key

先执行:

```bash
ls ~/.ssh
```

如果看到类似:

```text
id_ed25519
id_ed25519.pub
```

说明已经有一对 SSH key 了。

这里:

- `id_ed25519` 是私钥
- `id_ed25519.pub` 是公钥

---

## 3. 如果没有 SSH key，就先生成

如果 `~/.ssh` 里没有可用 key，可以执行:

```bash
ssh-keygen -t ed25519 -C "你的GitHub邮箱"
```

一路回车通常就可以。

生成后再检查一次:

```bash
ls ~/.ssh
```

---

## 4. 查看公钥内容

执行:

```bash
cat ~/.ssh/id_ed25519.pub
```

你会看到一整行，类似:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... your_email_or_comment
```

把这一整行完整复制下来。

注意:

- 一定要复制整行
- 不要漏掉开头的 `ssh-ed25519`
- 不要漏掉结尾的邮箱或注释

---

## 5. 把公钥添加到 GitHub

打开 GitHub 页面:

```text
https://github.com/settings/keys
```

然后:

1. 点击 `New SSH key`
2. `Title` 填一个你能认出来的名字
   例如: `mfj-virtualbox`
3. `Key type` 选择 `Authentication Key`
4. `Key` 里粘贴刚才复制的整行公钥
5. 点击 `Add SSH key`

如果 GitHub 跳到 `Confirm access` 页面，这是正常的。

你需要完成身份验证后，GitHub 才会真正保存这把 key。

验证方式可能包括:

- GitHub Mobile
- 输入密码
- 其他二次验证方式

---

## 6. 第一次连接 GitHub SSH 时的提示

第一次在终端执行:

```bash
ssh -T git@github.com
```

可能会看到类似:

```text
The authenticity of host 'github.com (...)' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

这不是报错，而是在确认 GitHub 主机身份。

这时输入:

```bash
yes
```

然后回车。

这样会把 GitHub 主机加入 `~/.ssh/known_hosts`。

---

## 7. 测试 SSH 是否配置成功

执行:

```bash
ssh -T git@github.com
```

如果成功，通常会看到类似:

```text
Hi <你的GitHub用户名>! You've successfully authenticated...
```

如果看到:

```text
Permission denied (publickey)
```

通常说明:

- GitHub 里还没有真正保存这把 key
- 或者保存的不是当前这把 key

这时回到:

```text
https://github.com/settings/keys
```

重新检查 SSH key 列表。

---

## 8. 把仓库远端从 HTTPS 改成 SSH

先进入你的项目目录:

```bash
cd /path/to/your/repo
```

查看当前远端:

```bash
git remote -v
```

如果现在是 HTTPS，比如:

```text
origin  https://github.com/fengjielab/learnning_hand.git (fetch)
origin  https://github.com/fengjielab/learnning_hand.git (push)
```

可以改成 SSH:

```bash
git remote set-url origin git@github.com:fengjielab/learnning_hand.git
```

再检查一次:

```bash
git remote -v
```

应该会变成:

```text
origin  git@github.com:fengjielab/learnning_hand.git (fetch)
origin  git@github.com:fengjielab/learnning_hand.git (push)
```

---

## 9. 推送到 GitHub

第一次推荐这样推:

```bash
git push -u origin main
```

这里的 `-u` 表示:

- 把本地 `main`
- 和远端 `origin/main`
- 建立默认跟踪关系

这样以后在这个仓库里通常就可以直接用:

```bash
git push
git pull
```

不用每次都把 `origin main` 写全。

---

## 10. 一个完整示例

假设你的仓库目录是:

```bash
/home/mfj/teletest_forcedimension
```

完整流程可以写成:

```bash
cd /home/mfj/teletest_forcedimension
git remote -v
ssh -T git@github.com
git remote set-url origin git@github.com:fengjielab/learnning_hand.git
git remote -v
git push -u origin main
```

---

## 11. 常见问题

### 问题 1: `Permission denied (publickey)`

含义:

- GitHub 不接受当前 SSH key

优先检查:

1. `~/.ssh/id_ed25519.pub` 是不是你刚才加的那把
2. GitHub 的 `SSH and GPG keys` 页面里是不是真的有这把 key
3. 你是不是完成了 GitHub 的身份确认步骤

---

### 问题 2: 第一次连接时要求输入 `yes`

这是正常的，不是报错。

输入:

```bash
yes
```

即可。

---

### 问题 3: 远端还是 HTTPS

检查:

```bash
git remote -v
```

如果还是 `https://...`，说明你还没有执行成功:

```bash
git remote set-url origin git@github.com:用户名/仓库名.git
```

---

### 问题 4: 我怎么查看已经添加的 SSH key

去这里管理:

```text
https://github.com/settings/keys
```

你可以在这个页面:

- 查看已有 key
- 删除旧 key
- 添加新 key
- 区分不同机器的 key

---

## 12. 最推荐的习惯

给每台机器都用不同的 `Title`。

例如:

- `office-linux`
- `mfj-virtualbox`
- `robot-pc`

这样以后哪台机器的 key 要删、要换，一眼就能认出来。

---

## 13. 一句话总结

如果你长期在 Linux 终端里开发，最推荐的 GitHub 推送方式是:

- 用 SSH key 登录 GitHub
- 把仓库远端改成 SSH
- 用 `git push -u origin main` 完成第一次推送

后面就会轻松很多。
