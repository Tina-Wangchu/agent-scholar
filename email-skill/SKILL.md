---
name: email-sender
description: "Send emails via Gmail SMTP. Use when the user asks to send an email, write an email, compose a message, notify someone via email, or draft and send email — supports plain text, HTML, and attachments."
version: 1.0.0
author: agent-scholar
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, smtp, gmail, communication, notification]
    category: my-category
required_environment_variables:
  - name: GMAIL_ADDRESS
    prompt: "Your Gmail address"
    help: "Your full Gmail address, e.g. you@gmail.com"
    required_for: "Sending emails"
  - name: GMAIL_APP_PASSWORD
    prompt: "Gmail App Password (16 chars)"
    help: "Generate at https://myaccount.google.com/apppasswords — NOT your Gmail login password"
    required_for: "SMTP authentication"
---

# Email Sender — Gmail 邮件发送

通过 Gmail SMTP 发送邮件。支持纯文本、HTML 格式和附件，带失败自动重试和发送记录。

## When to Use

当用户提出以下需求时激活：
- "帮我发一封邮件"、"Send an email to..."
- "写封邮件给..."、"Draft an email..."
- "发个通知邮件"、"Email notification to..."
- "把这个发给..."（附有要发送的内容）
- "邮件通知一下..."

## Quick Reference

| 需求 | 操作 |
|---|---|
| 发送纯文本邮件 | 生成 body → 写入临时文件 → `python send_email.py --body-type plain` |
| 发送 HTML 邮件 | 生成 HTML body → 写入临时文件 → `python send_email.py --body-type html` |
| 带附件 | 加 `--attach file1.pdf file2.xlsx` |
| 多个收件人 | `--to a@x.com b@x.com` |
| 抄送 | `--cc boss@x.com` |
| 查看发送记录 | `python send_email.py --log-show` |
| 发件人显示名 | `--from-name "张三"` |

## Procedure

### Step 1: 收集需求

向用户确认以下信息（未提及的可根据上下文推断或合理默认）：

- **收件人**（必需）：一个或多个邮箱地址
- **主题**（必需）：邮件标题
- **正文内容**（必需）：根据用户描述生成
- **格式**：默认 HTML；用户要求纯文本时用 `plain`
- **附件**：用户提到的文件路径
- **抄送**：用户要求时添加
- **发件人显示名**：可选，从环境或上下文推断

### Step 2: 生成邮件内容

根据用户描述生成完整的邮件正文，注意：
- 匹配用户语言（中文描述 → 中文邮件，英文描述 → 英文邮件）
- 根据用户指示的语气和风格生成
- 如果是 HTML，使用简洁专业的排版
- 如果用户提供了具体内容要点，确保全部包含

### Step 3: 写入临时文件

将生成的邮件正文写入临时文件：

```bash
# Windows
echo. > $env:TEMP\email_body.html
```

然后使用 `write_file` 或 `terminal` 的写入命令将正文内容写入该文件。

或者直接用 hermes 的文件写入工具创建临时文件。

### Step 4: 展示预览，等待确认

以清晰的格式展示完整邮件信息，**等待用户明确确认后再发送**：

```
📧 邮件预览：

  收件人: alice@example.com
  抄送: (无)
  主题: 本周项目进度报告
  格式: HTML
  附件: (无)

  --- 正文预览 ---

  [显示完整邮件内容]

  ----------------
  确认发送以上邮件？(回复 "确认" 或 "send" 发送，"修改" 调整内容)
```

**重要：不要跳过确认步骤。即使用户说"直接发"，也要展示预览让用户有机会检查。**

### Step 5: 发送邮件

用户确认后，执行发送命令：

```bash
python ${HERMES_SKILL_DIR}/scripts/send_email.py \
  --to recipient@example.com \
  --subject "邮件主题" \
  --body-file $env:TEMP/email_body.html \
  --body-type html
```

带附件时：
```bash
python ${HERMES_SKILL_DIR}/scripts/send_email.py \
  --to recipient@example.com \
  --subject "邮件主题" \
  --body-file $env:TEMP/email_body.html \
  --body-type html \
  --attach C:\path\to\file.pdf
```

带抄送和发件人名称时：
```bash
python ${HERMES_SKILL_DIR}/scripts/send_email.py \
  --to recipient@example.com \
  --cc boss@example.com \
  --subject "邮件主题" \
  --body-file $env:TEMP/email_body.html \
  --body-type html \
  --from-name "张三"
```

### Step 6: 报告结果

根据脚本返回的结果告知用户：

- **成功**："✅ 邮件已成功发送至 recipient@example.com，主题：XXX"
- **失败**："❌ 发送失败：[具体错误]。[解决建议]"
- **重试中**：脚本会自动重试 3 次（间隔 2s → 5s → 15s），告知用户等待结果

### 查看发送历史

```bash
python ${HERMES_SKILL_DIR}/scripts/send_email.py --log-show
```

## Pitfalls

### Gmail 必须使用应用专用密码，不能用登录密码
2025 年 5 月起 Google 已彻底关闭普通密码 SMTP 登录。必须使用 16 位应用专用密码。
**修复**：引导用户前往 https://myaccount.google.com/apppasswords 生成。详见 `skill_view("email-sender", "references/gmail-setup.md")`。

### 修改 Google 密码后应用专用密码自动失效
每次修改 Google 账户密码，所有应用专用密码都会被吊销。
**修复**：重新生成应用专用密码并更新环境变量。

### 每日发送上限 500 封
个人 Gmail 账户每天最多发送 500 封邮件，超出会被临时封禁 24 小时。
**修复**：批量发送时注意控制频率（每封间隔 2 秒以上），监控发送数量。

### 附件不能超过 25MB
Gmail 单封邮件附件总大小上限 25MB。
**修复**：超过时提示用户使用云盘链接替代。

### 网络连接问题（国内访问 Gmail）
国内直连 smtp.gmail.com 会被阻断。**HTTP 代理无效**（只代理网页请求，不能代理 SMTP 的原始 TCP 连接），必须使用 **SOCKS5 代理**。
**前置条件**：安装 PySocks（`python -m pip install pysocks`）。
**配置**：设置 SOCKS5 代理环境变量（`7897` 是 Clash 混合端口，根据实际修改）：
```bash
$env:SMTP_SOCKS_PROXY = "socks5://127.0.0.1:7897"
```
**验证代理可用**：如果发送失败且错误为连接超时（WinError 10060），让用户先测试代理：
```bash
python -c "import socks; s = socks.socksocket(); s.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 7897); s.settimeout(10); s.connect(('smtp.gmail.com', 587)); print('OK')"
```
如果超时则不是脚本问题，而是代理本身无法到达 Gmail（检查 Clash 是否在运行、端口是否正确）。

### STARTTLS 是必须的
Gmail 端口 587 必须先执行 `starttls()` 升级到加密连接，否则会被拒绝（错误码 530）。
脚本中已处理此步骤，Agent 无需额外操作。

## Verification

确认 skill 工作正常的测试步骤：

```bash
# 1. 检查环境变量是否配置
echo $env:GMAIL_ADDRESS
echo $env:GMAIL_APP_PASSWORD

# 2. 查看发送日志
python ${HERMES_SKILL_DIR}/scripts/send_email.py --log-show

# 3. 发送测试邮件（先写一个测试 body 文件）
echo "Test email from Hermes Agent" > $env:TEMP/test_email.txt
python ${HERMES_SKILL_DIR}/scripts/send_email.py --to your_own_email@gmail.com --subject "Hermes Test" --body-file $env:TEMP/test_email.txt --body-type plain
```
