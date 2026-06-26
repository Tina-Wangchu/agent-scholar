# Email Sender Skill 介绍与测试指南

> 一个为 Hermes Agent 设计的邮件发送技能，支持通过自然对话生成邮件内容、预览确认、自动发送。

---

## 一、Skill 概述

### 它是什么？

`email-sender` 是一个 Hermes Agent Skill，让你在 TUI 或微信中**用自然语言描述邮件需求**，Agent 会帮你完成全部流程：

```
你："帮我发一封邮件给 alice@gmail.com，这周完成了三个任务，用 HTML 格式，附上报告"
       ↓
Agent：收集需求 → 生成邮件内容 → 展示预览
       ↓
你："确认"
       ↓
Agent：发送邮件 → 报告结果 ✅
```

### 核心特性

| 特性 | 说明 |
|---|---|
| **自然语言交互** | 用中文或英文描述邮件需求，Agent 自动生成内容 |
| **预览确认** | 发送前展示完整邮件预览，你确认后才发送 |
| **HTML / 纯文本** | 支持两种邮件格式，默认 HTML |
| **附件支持** | 支持多个附件，自动检测文件是否存在 |
| **多收件人 / 抄送** | `--to` 支持多个收件人，`--cc` 支持抄送 |
| **失败自动重试** | 发送失败时自动重试 3 次（间隔 2s → 5s → 15s） |
| **发送记录** | 每次发送结果写入 `~/.hermes/email_log.json` |
| **零外部依赖** | 仅使用 Python 标准库（smtplib、email、json） |

### 文件结构

```
~/.hermes/skills/my-category/email-sender/
├── SKILL.md                        # 主指令文件（Agent 读取的规则）
├── scripts/
│   └── send_email.py                # 邮件发送脚本（Gmail SMTP）
└── references/
    └── gmail-setup.md               # Gmail 应用专用密码获取指南
```

### 技术栈

```
协议：SMTP (smtp.gmail.com:587 + STARTTLS)
认证：Gmail 应用专用密码
语言：Python 3.6+（标准库）
依赖：无
```

---

## 二、前置配置

### 2.1 开启 Gmail 两步验证

1. 打开 https://myaccount.google.com/security
2. 确认「两步验证」已开启

### 2.2 生成 Gmail 应用专用密码

1. 打开 https://myaccount.google.com/apppasswords
2. 输入应用名称（如 `Hermes Agent`）
3. 点击「创建」
4. 复制 **16 位密码**（只显示一次！）

### 2.3 配置环境变量

在 PowerShell 中执行：

```powershell
# 临时配置（当前会话有效）
$env:GMAIL_ADDRESS = "your_email@gmail.com"
$env:GMAIL_APP_PASSWORD = "your_16_char_app_password"

# 永久配置（推荐）
[System.Environment]::SetEnvironmentVariable("GMAIL_ADDRESS", "your_email@gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("GMAIL_APP_PASSWORD", "your_16_char_app_password", "User")
```

> ⚠️ 应用专用密码不是 Gmail 登录密码！自 2025 年 5 月起普通密码已无法用于 SMTP。

### 2.4 验证配置

```powershell
echo $env:GMAIL_ADDRESS
echo $env:GMAIL_APP_PASSWORD
```

---

## 三、测试方法

### 测试一：直接运行发送脚本（验证 SMTP 连通性）

这是最基础的测试，验证 Gmail SMTP 是否能正常工作。

```powershell
# 1. 创建测试邮件正文
Set-Content -Path "$env:TEMP\test_email.txt" -Value "This is a test email from Hermes Agent email-sender skill."

# 2. 发送到自己的邮箱（确保能收到）
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py `
  --to your_email@gmail.com `
  --subject "Email Sender Skill - Test" `
  --body-file "$env:TEMP\test_email.txt" `
  --body-type plain

# 3. 检查你的邮箱是否收到
```

**预期输出**：
```
Sending to: your_email@gmail.com
✅ Email sent successfully! (attempts: 1)
   Log: C:\Users\lanpi\.hermes\email_log.json
```

**如果失败**，常见错误对照：

| 错误信息 | 原因 | 解决 |
|---|---|---|
| `Authentication failed` | 应用专用密码错误或已失效 | 重新生成应用专用密码 |
| `Connection timed out` | 网络无法连接 Gmail | 配置代理 `$env:HTTPS_PROXY="http://127.0.0.1:7890"` |
| `Attachment not found` | 附件路径错误 | 检查文件路径是否存在 |
| `Missing credentials` | 环境变量未设置 | 重新执行 `$env:GMAIL_ADDRESS=...` |

### 测试二：发送 HTML 格式邮件

```powershell
# 创建 HTML 邮件
$html = @"
<html>
<body>
    <h2 style="color:#4A90D9;">测试邮件</h2>
    <p>这是一封 <b>HTML 格式</b> 的测试邮件。</p>
    <ul>
        <li>项目 A：✅ 完成</li>
        <li>项目 B：⏳ 进行中</li>
    </ul>
</body>
</html>
"@

Set-Content -Path "$env:TEMP\test_email.html" -Value $html -Encoding UTF8

# 发送
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py `
  --to your_email@gmail.com `
  --subject "HTML 邮件测试" `
  --body-file "$env:TEMP\test_email.html" `
  --body-type html
```

### 测试三：带附件发送

```powershell
# 先创建一个测试文件
"这是测试附件的内容" | Out-File -FilePath "$env:TEMP\test_attachment.txt" -Encoding UTF8

# 发送带附件的邮件
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py `
  --to your_email@gmail.com `
  --subject "带附件的测试" `
  --body-file "$env:TEMP\test_email.txt" `
  --body-type plain `
  --attach "$env:TEMP\test_attachment.txt"
```

### 测试四：多个收件人 + 抄送

```powershell
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py `
  --to alice@gmail.com bob@gmail.com `
  --cc boss@gmail.com `
  --subject "多收件人测试" `
  --body-file "$env:TEMP\test_email.txt" `
  --body-type plain
```

### 测试五：查看发送记录

```powershell
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py --log-show
```

**预期输出**：
```
✅ [2026-06-26T08:55:00+00:00] ['your_email@gmail.com'] — Email Sender Skill - Test
✅ [2026-06-26T08:56:00+00:00] ['your_email@gmail.com'] — HTML 邮件测试
```

或查看日志文件：

```powershell
Get-Content C:\Users\lanpi\.hermes\email_log.json | python -m json.tool
```

### 测试六：在 Hermes Agent 中测试（完整流程）

启动 Hermes Agent，在 TUI 或微信中发送：

```
/email-sender 帮我发一封邮件给 tinawangchu0615@gmail.com，主题是"Skill 测试"，内容是一句简单的话"这封邮件是通过 Hermes Agent 的 email-sender skill 发送的测试邮件"
```

**预期 Agent 行为**：

```
1. Agent 激活 email-sender skill
2. Agent 生成邮件正文
3. Agent 展示预览：

   📧 邮件预览：
     收件人: tinawangchu0615@gmail.com
     主题: Skill 测试
     格式: HTML
     ---
     正文预览...

   确认发送？(回复 "确认" 或 "修改")

4. 你回复 "确认"
5. Agent 调用 send_email.py 发送
6. Agent 报告 ✅ 发送成功
```

### 测试七：模拟失败重试

```powershell
# 故意使用错误的密码测试重试逻辑
$env:GMAIL_APP_PASSWORD = "wrong_password"
python C:\Users\lanpi\.hermes\skills\my-category\email-sender\scripts\send_email.py `
  --to your_email@gmail.com `
  --subject "重试测试" `
  --body-file "$env:TEMP\test_email.txt" `
  --body-type plain

# 预期：Authentication failed（认证错误不会重试，直接返回错误）

# 恢复正确密码
$env:GMAIL_APP_PASSWORD = "your_correct_password"
```

---

## 四、测试检查清单

| # | 测试项 | 命令 | 通过条件 |
|---|---|---|---|
| 1 | 环境变量配置 | `echo $env:GMAIL_ADDRESS` | 显示你的 Gmail 地址 |
| 2 | 纯文本发送 | 测试一 | ✅ 成功，邮箱收到邮件 |
| 3 | HTML 发送 | 测试二 | ✅ 成功，邮件有 HTML 格式 |
| 4 | 附件发送 | 测试三 | ✅ 成功，邮件包含附件 |
| 5 | 多收件人 | 测试四 | ✅ 成功，所有收件人收到 |
| 6 | 发送记录 | 测试五 | 日志文件有对应记录 |
| 7 | Hermes Agent 完整流程 | 测试六 | Agent 完成预览→确认→发送 |
| 8 | 错误处理 | 测试七 | 失败时显示清晰错误信息 |

---

## 五、故障排查

### 发送超时 / 连接不上 Gmail

国内直连 `smtp.gmail.com` 经常不通，需要代理：

```powershell
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
```

### 认证失败

```powershell
# 确认密码是应用专用密码，不是 Gmail 登录密码
# 确认两步验证已开启
# 尝试重新生成应用专用密码
```

### 发送成功但收不到邮件

检查 Gmail 发件箱的「已发送」文件夹，确认邮件是否实际发出。有时候会进入垃圾邮件文件夹。

### Hermes Agent 中 skill 不生效

```powershell
# 确认 skill 在正确目录
Test-Path C:\Users\lanpi\.hermes\skills\my-category\email-sender\SKILL.md

# 在 Hermes 中检查 skill 列表
/skills search email
```
