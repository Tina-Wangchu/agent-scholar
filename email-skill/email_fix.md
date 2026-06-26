# Email Sender Skill — 问题排查与修复记录

> 这篇文档记录了在开发和调试 `email-sender` skill 过程中遇到的所有问题、排查思路和最终修复方案，用通俗易懂的方式解释，方便以后遇到类似问题时参考。

---

## 背景概述

我要创建一个 Hermes Agent 的 skill，通过自然对话让 Agent 帮我发邮件。使用 Gmail SMTP 发送，脚本用 Python 标准库 `smtplib` 编写。

**核心挑战：在国内网络环境下，无法直接连接 Gmail 的 SMTP 服务器。**

---

## 问题一：`WinError 10060` — 连接超时

### 现象

```
Retry 1/3 in 2s... (error: [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。)
```

### 这是什么意思？

就像你给 Gmail 邮局打电话，但电话线被切断了——你的电脑根本连不上 Gmail 的服务器。在国内，Google 的服务（包括 SMTP 邮件发送端口）是被屏蔽的。

### 排查过程

**第一步：确认是网络问题，不是代码问题**

先直接测试能不能连上 Gmail SMTP：

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(("smtp.gmail.com", 587))
```

结果：超时。说明确实是网络不通，不是代码写的有问题。

**第二步：尝试用 HTTP 代理**

很多人以为设置 HTTP 代理就能解决所有问题：

```powershell
$env:HTTPS_PROXY = "http://127.0.0.1:7897"
```

然后重试 → 还是超时。

**原因：HTTP 代理只对 HTTP/HTTPS 网页请求有效。SMTP 邮件发送用的是原始 TCP 连接（不是 HTTP），所以 HTTP 代理管不了它。**

这就像你有快递通道能寄包裹（HTTP），但你想打电话（SMTP），快递通道帮不了你。

**第三步：改用 SOCKS5 代理**

SOCKS5 是一种更底层的代理协议，可以代理任何类型的网络连接，包括 SMTP。

但 Python 的 `smtplib` 库不支持 SOCKS5 代理——它只支持直连。所以需要安装 `PySocks` 库来增加 SOCKS5 支持。

### 最终解决方案

1. 安装 PySocks：

```powershell
python -m pip install pysocks
```

2. 通过 PySocks 创建 SOCKS5 代理 socket，代替普通 socket：

```python
import socks
sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
sock.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
sock.connect(("smtp.gmail.com", 587))
# 用这个 sock 替代普通 socket 连接 SMTP
```

3. 设置环境变量告诉脚本使用 SOCKS5 代理：

```powershell
$env:SMTP_SOCKS_PROXY = "socks5://127.0.0.1:7897"
```

### 打个比方

| 方式 | 类比 | 能发邮件吗 |
|---|---|---|
| 直连 | 直接走公路到 Gmail 邮局 | ❌ 公路被封了 |
| HTTP 代理 ($env:HTTPS_PROXY) | 只能走快递通道 | ❌ 邮局不在快递路线上 |
| SOCKS5 代理 | 修了一条能到邮局的隧道 | ✅ 通过隧道到达 |

---

## 问题二：`STARTTLS extension not supported by server`

### 现象

```
Retry 1/3 in 2s... (error: STARTTLS extension not supported by server.)
```

### 这是什么意思？

SMTP 发送邮件需要先「升级」到加密连接（STARTTLS），就像进门后要换成内部电话线。Agent 以为服务器不支持这个功能——但实际上是 Agent 没有正确「听到」服务器的自我介绍。

### 排查过程

**第一步：确认 SOCKS5 代理本身能用**

先测试 PySocks 能不能通过代理连上 Gmail：

```python
import socks
s = socks.socksocket()
s.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
s.settimeout(10)
s.connect(("smtp.gmail.com", 587))
print("OK")
```

结果：打印 `OK`。代理连通性没问题。

**第二步：做完整的 SMTP 握手测试**

因为上面的测试只验证了「能连上」，没有验证 SMTP 协议能否正常工作：

```python
import socks, socket, smtplib

sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
sock.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
sock.settimeout(10)
sock.connect(("smtp.gmail.com", 587))

server = smtplib.SMTP()
server.sock = sock
server.file = sock.makefile("rwb")  # 创建读写通道
server.getreply()                    # 读取服务器欢迎语（关键！）
(code, msg) = server.ehlo()         # 发送 EHLO 命令
print(f"STARTTLS: {'starttls' in server.esmtp_features}")
```

结果：`STARTTLS: True`。

这说明 SOCKS5 + SMTP 完全可以工作！问题出在我的脚本代码里。

**第三步：对比找出差异**

测试代码和脚本代码的差异：

| 步骤 | 测试代码（✅ 成功） | 脚本代码（❌ 失败） |
|---|---|---|
| 创建 SOCKS5 socket 并连接 | ✅ | ✅ |
| 创建 SMTP() 实例 | ✅ | ✅ |
| 注入 socket | ✅ `server.sock = sock` | ✅ `server.sock = sock` |
| 创建读写通道 | ✅ `server.file = sock.makefile("rwb")` | ✅ `server.file = sock.makefile("rwb")` |
| **读取服务器欢迎语** | ✅ `server.getreply()` | ❌ **缺少这一步！** |

### 根本原因

SMTP 服务器在你连接后会先发一段「欢迎语」，就像你拨通电话后对方先说「你好，这里是 Gmail」。你**必须先听完这段欢迎语**，才能开始正常对话（发送 EHLO 命令等）。

我的脚本跳过了 `server.getreply()`（读取欢迎语），直接就开始 EHLO。结果 Agent 读到了欢迎语的内容，误把它当成 EHLO 的回复，自然找不到 STARTTLS 扩展。

### 修复

在 `_get_smtp_connection()` 中添加一行读取欢迎语：

```python
server = smtplib.SMTP()
server.sock = sock
server.file = sock.makefile("rwb")
server._host = SMTP_SERVER     # 记录服务器名称（后面 TLS 需要用）
server.getreply()              # 👈 读取 SMTP 欢迎语（关键！）
return server
```

---

## 问题三：`ValueError: server_hostname cannot be an empty string`

### 现象

```
ValueError: server_hostname cannot be an empty string or start with a leading dot.
```

### 这是什么意思？

STARTTLS 会把普通连接「升级」为加密连接（TLS）。升级时需要验证服务器证书，验证过程需要知道服务器的域名（比如 `smtp.gmail.com`）。

因为我是用「手动注入 socket」的方式创建 SMTP 实例的，smtplib 不知道服务器域名是什么（`_host` 属性是空的），所以 TLS 握手时报错。

### 修复

在注入 socket 后告诉 smtplib 服务器叫什么名字：

```python
server._host = SMTP_SERVER  # 即 "smtp.gmail.com"
```

### 打个比方

就像你去酒店check-in，前台问「请问先生贵姓？」。如果你不告诉它你叫什么（`_host` 为空），它就没法给你办入住手续（TLS 握手）。

---

## 完整的 SOCKS5 + SMTP 连接流程（最终正确版本）

```python
import socks
import socket
import smtplib

# 1. 通过 SOCKS5 代理创建 socket 并连接 Gmail
sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
sock.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
sock.settimeout(30)
sock.connect(("smtp.gmail.com", 587))

# 2. 创建 SMTP 实例（不自动连接），注入 SOCKS5 socket
server = smtplib.SMTP()         # 不传参数 = 不自动连接
server.sock = sock              # 注入 SOCKS5 代理 socket
server.file = sock.makefile("rwb")  # 创建读写通道
server._host = "smtp.gmail.com"   # 记录服务器域名（TLS 需要）

# 3. 读取服务器欢迎语
server.getreply()

# 4. 正常的 SMTP 流程
server.ehlo()          # 自我介绍
server.starttls()      # 升级到加密
server.ehlo()          # 加密后再自我介绍一次
server.login(...)      # 登录
server.sendmail(...)   # 发邮件
server.quit()          # 退出
```

### 为什么不能直接用 `smtplib.SMTP("smtp.gmail.com", 587)`？

因为 `smtplib.SMTP(host, port)` 在创建时会自动创建一个**普通 socket**（不经过代理）来连接。我们不想要这个普通 socket——我们要用自己的 **SOCKS5 代理 socket**。

所以必须：
1. 先用 PySocks 创建 SOCKS5 socket
2. 再手动注入到 SMTP 实例中
3. 手动补上 SMTP 自动连接时做的准备工作（读取欢迎语、记录主机名）

---

## 调试技巧总结

### 技巧 1：先分离问题，再合并

不要一上来就跑完整脚本。遇到问题时，把问题拆成最小单元测试：

```
Q: 连不上服务器？
→ 单独测试 socket 连接

Q: socket 能连，但 SMTP 握手有问题？
→ 单独测试 SMTP 协议流程

Q: SMTP 握手正常，但脚本跑不通？
→ 对比测试代码和脚本代码的差异
```

### 技巧 2：利用已有的成功案例

当我不知道怎么让 smtplib 用 SOCKS5 时，先确认了「PySocks + socket 能连上 Gmail」，然后在这个成功基础上，一步步添加 smtplib 相关代码，每加一步验证一次。

### 技巧 3：理解库的内部工作原理

很多 bug 是因为我不知道 smtplib 内部做了什么。比如：
- `SMTP(host, port)` 创建时会**自动连接**并**读取欢迎语**——我不知道，所以手动注入 socket 时漏掉了读取欢迎语
- STARTTLS 需要用 `_host` 属性验证证书——我不知道，所以漏掉了设置主机名

了解这些内部细节后，问题就迎刃而解了。

---

## 环境配置备忘

### 必须配置的环境变量

```powershell
# Gmail 凭据
$env:GMAIL_ADDRESS = "your_email@gmail.com"
$env:GMAIL_APP_PASSWORD = "your_16_char_app_password"

# SOCKS5 代理（国内必需）
$env:SMTP_SOCKS_PROXY = "socks5://127.0.0.1:7897"
```

### 必须安装的库

```powershell
python -m pip install pysocks
```

### Clash 代理设置要求

- 端口 7897（混合端口，同时支持 HTTP + SOCKS5）
- 确保 Clash 规则允许 smtp.gmail.com 的流量通过代理

---

## 测试脚本

### 快速验证 SOCKS5 代理连通性

```python
import socks
s = socks.socksocket()
s.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
s.settimeout(10)
s.connect(("smtp.gmail.com", 587))
print("OK")
```

### 完整 SMTP 握手验证

```python
import socks, socket, smtplib

sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
sock.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 7897)
sock.settimeout(10)
sock.connect(("smtp.gmail.com", 587))

server = smtplib.SMTP()
server.sock = sock
server.file = sock.makefile("rwb")
server._host = "smtp.gmail.com"
server.getreply()

(code, msg) = server.ehlo()
print(f"EHLO: {code}, STARTTLS: {'starttls' in server.esmtp_features}")
server.quit()
```

### 发送测试邮件

```powershell
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py --to your_email@gmail.com --subject "Test" --body-file "$env:TEMP\test_email.txt" --body-type plain
```
