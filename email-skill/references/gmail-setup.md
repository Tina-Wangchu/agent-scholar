# Gmail 应用专用密码获取指南

> Gmail SMTP 发送邮件必须使用**应用专用密码**，不能用 Gmail 登录密码。自 2025 年 5 月起，普通密码已彻底不可用。

## 前提条件：开启两步验证

1. 打开 [Google 账户安全设置](https://myaccount.google.com/security)
2. 找到「两步验证」并确认已开启
3. 如果未开启，按提示绑定手机号并验证

## 生成应用专用密码（3 分钟）

### 步骤 1：访问应用专用密码页面

https://myaccount.google.com/apppasswords

可能需要再次输入 Google 密码验证身份。

### 步骤 2：生成密码

1. 输入应用名称（如 `Hermes Agent` 或 `Python SMTP`）
2. 点击 **创建**
3. 复制显示的 **16 位密码**（格式如 `abcd efgh ijkl mnop`）

> ⚠️ **只显示一次，务必立即保存！**

### 步骤 3：配置环境变量

在 `~/.hermes/.env` 中添加：

```bash
GMAIL_ADDRESS=your_name@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

或在系统环境变量中设置：

```powershell
# PowerShell（临时，当前会话有效）
$env:GMAIL_ADDRESS = "your_name@gmail.com"
$env:GMAIL_APP_PASSWORD = "abcdefghijklmnop"

# 永久设置
[System.Environment]::SetEnvironmentVariable("GMAIL_ADDRESS", "your_name@gmail.com", "User")
[System.Environment]::SetEnvironmentVariable("GMAIL_APP_PASSWORD", "abcdefghijklmnop", "User")
```

## 验证配置

```bash
# 检查环境变量
echo $env:GMAIL_ADDRESS
echo $env:GMAIL_APP_PASSWORD

# 发送测试邮件
python ${HERMES_SKILL_DIR}/scripts/send_email.py --to your_email@gmail.com --subject "Test" --body-file /tmp/test.txt --body-type plain
```

## 常见问题

| 问题 | 解决 |
|---|---|
| 找不到「应用专用密码」选项 | 先确认两步验证已开启 |
| 密码无效 / 被拒绝 | 可能修改过 Google 密码，需重新生成应用专用密码 |
| 连接超时 | 国内需配置代理访问 smtp.gmail.com |
| 每天只能发 500 封 | Gmail 个人账户限制，不可提升 |
