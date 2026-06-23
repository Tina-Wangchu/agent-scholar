# Hermes Agent 交互内容记录方法指南

## 📋 方法概述

本指南提供**6种记录方法**，从简单到自动化，你可以根据需要选择：

| 方法 | 难度 | 完整性 | 适用场景 | 推荐度 |
|------|------|--------|---------|--------|
| 1. PowerShell输出重定向 | ⭐ | ⭐⭐⭐ | 快速记录 | ⭐⭐⭐⭐⭐ |
| 2. 使用日志功能 | ⭐⭐ | ⭐⭐⭐⭐⭐ | 完整记录 | ⭐⭐⭐⭐⭐ |
| 3. 手动复制粘贴 | ⭐ | ⭐⭐ | 简单测试 | ⭐⭐⭐ |
| 4. 记录模板 | ⭐⭐ | ⭐⭐⭐⭐ | 结构化报告 | ⭐⭐⭐⭐ |
| 5. 截图+录屏 | ⭐ | ⭐⭐⭐ | 视觉展示 | ⭐⭐⭐⭐ |
| 6. 自动化脚本 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 重复测试 | ⭐⭐⭐⭐ |

---

## 🎯 方法1：PowerShell输出重定向（推荐新手）

### 原理
将终端的所有输出（输入和输出）自动保存到文件中。

### 方法A：使用Start-Transcript（最简单）

**优点**：
- ✅ 一行命令搞定
- ✅ 自动记录所有内容
- ✅ 包含时间戳
- ✅ 可以随时停止

**使用步骤**：

```powershell
# 1. 开始记录（在测试开始前）
Start-Transcript -Path "C:\hermes-test\logs\session-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# 输出示例：
# Transcript started, output file is: C:\hermes-test\logs\session-20250622-143022.log

# 2. 进行Hermes测试
hermes chat
# ... 所有交互都会被自动记录 ...

# 3. 停止记录（测试结束后）
Stop-Transcript

# 输出示例：
# Transcript stopped, output file is: C:\hermes-test\logs\session-20250622-143022.log
```

**查看记录**：
```powershell
# 查看日志文件
cat C:\hermes-test\logs\session-20250622-143022.log

# 或用记事本打开
notepad C:\hermes-test\logs\session-20250622-143022.log
```

**日志文件示例**：
```
**********************
Windows PowerShell transcript start
Start time: 20250622143022
**********************
Machine: DESKTOP-ABC123 (Microsoft Windows NT 10.0.19045.0)
User: Tina
RunAs User: DESKTOP-ABC123\Tina
Configuration Name:
**********************
Transcript started, output file is: C:\hermes-test\logs\session-20250622-143022.log
******

PS C:\hermes-test> hermes chat

Hermes Agent v1.0.0
Connected successfully!

你: 你好，你是谁？
Hermes: 你好！我是Hermes Agent，一个AI助手...

你: /code-review
Hermes: 正在审查代码...

你: exit
Goodbye!

PS C:\hermes-test> Stop-Transcript
**********************
Windows PowerShell transcript end
End time: 20250622144530
**********************
```

---

### 方法B：使用输出重定向符号

**优点**：
- ✅ 不需要额外命令
- ✅ 兼容性好
- ✅ 可自定义文件名

**使用步骤**：

```powershell
# 方法1：重定向到文件（只记录输出）
hermes chat > C:\hermes-test\logs\test-output.log

# 方法2：同时记录输出和错误
hermes chat > C:\hermes-test\logs\test-output.log 2>&1

# 方法3：追加模式（不覆盖之前的内容）
hermes chat >> C:\hermes-test\logs\test-output.log 2>&1
```

**缺点**：
- ❌ 只记录输出，不记录你的输入
- ❌ 没有时间戳
- ❌ 格式不够友好

---

## 🔍 方法2：使用Hermes日志功能（推荐完整记录）

### 原理
Hermes内置日志功能，可以记录所有交互的详细信息。

### 启用详细日志

**配置Hermes**：

```powershell
# 1. 创建日志目录
mkdir C:\hermes-test\hermes-logs

# 2. 配置Hermes使用详细日志
hermes config set log_level "debug"
hermes config set log_path "C:\hermes-test\hermes-logs"

# 3. 验证配置
hermes config get log_level
hermes config get log_path
```

**运行测试**：

```powershell
# 启动Hermes（会自动记录日志）
hermes chat

# 所有交互都会记录到日志文件
```

**查看日志**：

```powershell
# 查看最新的日志
Get-ChildItem C:\hermes-test\hermes-logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# 查看日志内容
cat C:\hermes-test\hermes-logs\hermes-debug.log

# 或使用实时监控
Get-Content C:\hermes-test\hermes-logs\hermes-debug.log -Wait
```

**日志内容示例**：

```json
{
  "timestamp": "2025-06-22T14:30:22.123Z",
  "level": "INFO",
  "message": "User input received",
  "content": {
    "input": "你好，你是谁？",
    "context": {
      "session_id": "abc-123",
      "turn_number": 1
    }
  }
},
{
  "timestamp": "2025-06-22T14:30:23.456Z",
  "level": "INFO",
  "message": "LLM response generated",
  "content": {
    "output": "你好！我是Hermes Agent...",
    "tokens_used": 150,
    "response_time_ms": 1234
  }
}
```

---

## 📝 方法3：手动复制粘贴（最简单）

### 适用场景
- 快速临时测试
- 只需要记录关键结果
- 不需要完整记录

### 操作步骤

**步骤1：在PowerShell中**

```powershell
# 进行测试
hermes chat

# 在测试过程中：
# 1. 用鼠标选中要复制的内容
# 2. 右键 > 复制（或按 Enter 键，PowerShell会自动复制选中内容）
# 3. 粘贴到文本编辑器
```

**步骤2：使用记录模板**

创建一个文本文件 `test-notes.txt`：

```
=== Hermes测试记录 ===
日期：2025-06-22
时间：14:30

测试1：基本对话
问题：你好，你是谁？
回答：你好！我是Hermes Agent...
结果：✅ 通过

测试2：代码审查
代码：[粘贴代码]
问题：[粘贴问题]
结果：✅ 通过

[继续记录...]
```

---

## 📄 方法4：使用结构化记录模板（推荐报告）

### 创建专业测试记录

**步骤1：下载记录模板**

我已经为你创建了详细的测试记录模板：
[hermes_terminal_test_guide.md](hermes_terminal_test_guide.md)

**步骤2：填写模板**

打开模板，按照以下结构填写：

```markdown
# Hermes Agent 交互测试记录

## 测试1：基本对话

**时间**：2025-06-22 14:30
**输入**：
```
你：你好，你是谁？
```

**输出**：
```
Hermes：你好！我是Hermes Agent，一个AI助手...
```

**结果**：✅ 通过

**备注**：回答准确，反应速度1.2秒

---

## 测试2：代码审查

**时间**：2025-06-22 14:35
**代码**：
```python
def divide(a, b):
    return a / b
```

**Hermes分析**：
```
发现问题：除零错误
建议：添加if检查
```

**结果**：✅ 通过

**质量评分**：4/5 ⭐
```

**步骤3：导出为最终报告**

完成后，将Markdown转换为PDF或Word：

```powershell
# 方法1：使用Typora（Markdown编辑器）
# 打开 .md 文件 > 文件 > 导出 > PDF

# 方法2：使用VS Code
# 安装 Markdown PDF 插件
# 打开 .md 文件 > Ctrl+Shift+P > Markdown PDF: Export

# 方法3：使用Pandoc（命令行）
pandoc test-report.md -o test-report.pdf
```

---

## 🖼️ 方法5：截图+录屏（视觉记录）

### 截图记录关键时刻

**使用Windows自带截图工具**：

```powershell
# 方法1：使用截图工具
# Win + Shift + S（选择区域截图）

# 方法2：使用PowerShell命令
# 获取当前窗口截图
Add-Type -AssemblyName System.Windows.Forms
$form = New-Object System.Windows.Forms.Form
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$img = New-Object System.Drawing.Bitmap $screen.Bounds.Width, $screen.Bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($img)
$graphics.CopyFromScreen($screen.Bounds.Location, [System.Drawing.DrawingPoint2D]::Empty, $img.Size)
$img.Save("C:\hermes-test\screenshots\screenshot-$(Get-Date -Format 'yyyyMMdd-HHmmss').png")
```

**保存到截图目录**：

```powershell
# 创建截图目录
mkdir C:\hermes-test\screenshots

# 每次重要测试时截图
# 文件命名格式：test-01-code-review.png
```

---

### 录屏记录完整流程

**使用Windows内置录屏**：

```powershell
# 方法1：使用Xbox Game Bar
# Win + G > 开始录制 > Win + Alt + R 停止

# 方法2：使用PowerShell + OBS（需安装OBS）
# 启动OBS > 设置录制区域 > 开始录制
```

**录屏文件命名**：

```
C:\hermes-test\recordings\
├── test-01-basic-chat.mp4
├── test-02-code-review.mp4
├── test-03-deep-research.mp4
└── test-04-security-review.mp4
```

---

## 🤖 方法6：自动化记录脚本（高级）

### 创建自动化测试脚本

**步骤1：创建测试脚本**

```powershell
# automated-test.ps1

# 配置
$LogDir = "C:\hermes-test\logs"
$TestDate = Get-Date -Format "yyyyMMdd-HHmmss"
$LogFile = "$LogDir\automated-test-$TestDate.log"

# 创建日志目录
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# 开始记录
Start-Transcript -Path $LogFile

Write-Host "=" * 60
Write-Host "Hermes Agent 自动化测试"
Write-Host "开始时间: $(Get-Date)"
Write-Host "=" * 60

# 测试函数
function Run-Test($TestName, $InputText) {
    Write-Host "`n[$(Get-Date)] 测试: $TestName" -ForegroundColor Cyan
    Write-Host "输入: $InputText" -ForegroundColor Yellow

    # 记录开始时间
    $StartTime = Get-Date

    # 执行测试（这里模拟，实际需要调用Hermes API）
    # $Response = hermes execute $InputText
    $Response = "模拟响应"

    # 记录结束时间
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalSeconds

    Write-Host "响应: $Response" -ForegroundColor Green
    Write-Host "耗时: $Duration 秒" -ForegroundColor Gray
    Write-Host "状态: ✅ 通过" -ForegroundColor Green

    # 等待用户确认
    Read-Host "`n按 Enter 继续下一个测试..."
}

# 运行测试套件
Run-Test "基本对话-自我介绍" "你好，你是谁？"
Run-Test "基本对话-知识问答" "什么是AI Agent？"
Run-Test "代码审查" "/code-review"
Run-Test "深度研究" "/deep-research LangChain vs AutoGen"

Write-Host "`n" + "=" * 60
Write-Host "测试完成"
Write-Host "结束时间: $(Get-Date)"
Write-Host "日志文件: $LogFile"
Write-Host "=" * 60

# 停止记录
Stop-Transcript

# 自动打开日志
notepad $LogFile
```

**步骤2：运行自动化测试**：

```powershell
# 执行测试脚本
.\automated-test.ps1

# 脚本会：
# 1. 自动创建日志文件
# 2. 依次执行每个测试
# 3. 记录所有输出
# 4. 计算响应时间
# 5. 自动打开日志文件供查看
```

---

## 🎯 推荐的记录策略

### 策略1：完整记录（第一次测试）

**组合方法**：
```powershell
# 1. 开启PowerShell转录
Start-Transcript -Path "C:\hermes-test\logs\first-test-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

# 2. 启动Hermes详细日志
hermes config set log_level "debug"

# 3. 进行测试
hermes chat

# 4. 测试结束后停止
Stop-Transcript
```

**优点**：
- ✅ 最完整的记录
- ✅ 包含所有细节
- ✅ 便于问题诊断

---

### 策略2：快速记录（日常测试）

**组合方法**：
```powershell
# 仅使用PowerShell转录
Start-Transcript -Path "C:\hermes-test\logs\quick-test.log"

# 测试
hermes chat

# 停止
Stop-Transcript
```

**优点**：
- ✅ 简单快速
- ✅ 足够日常使用
- ✅ 一行命令搞定

---

### 策略3：关键记录（特定问题）

**组合方法**：
```powershell
# 1. 复制关键输出到剪贴板
# 2. 粘贴到测试模板
# 3. 补充说明和截图
```

**适用场景**：
- 记录特定问题
- 报告bug
- 分享有趣发现

---

## 📊 记录文件组织建议

### 目录结构

```
C:\hermes-test\
├── logs\                          # 所有日志文件
│   ├── session-20250622-143022.log     # PowerShell转录日志
│   ├── hermes-debug.log                # Hermes调试日志
│   └── automated-test-20250622.log    # 自动化测试日志
│
├── screenshots\                    # 截图文件
│   ├── test-01-basic-chat.png
│   ├── test-02-code-review.png
│   └── test-03-error-example.png
│
├── recordings\                     # 录屏文件
│   ├── test-01-code-review.mp4
│   └── test-02-deep-research.mp4
│
├── reports\                        # 测试报告
│   ├── daily-test-20250622.md
│   ├── weekly-summary-20250622.md
│   └── final-report.pdf
│
└── test-cases\                     # 测试用例
    ├── bug-test.py
    ├── complex-code.py
    └── security-issues.py
```

### 文件命名规范

**日志文件**：
- `session-YYYYMMDD-HHMMSS.log` - 测试会话
- `hermes-debug.log` - 调试日志
- `error-YYYYMMDD.log` - 错误日志

**截图文件**：
- `test-01-description.png` - 按测试编号
- `error-bug-name.png` - 错误截图

**报告文件**：
- `daily-test-YYYYMMDD.md` - 每日测试
- `skill-review-YYYYMMDD.md` - Skill审查

---

## 🔍 查看和分析记录

### 快速查看命令

```powershell
# 查看最新的日志
Get-ChildItem C:\hermes-test\logs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { notepad $_.FullName }

# 搜索特定内容
Select-String -Path "C:\hermes-test\logs\*.log" -Pattern "ERROR"

# 查看测试统计
(Get-Content "C:\hermes-test\logs\session-20250622.log" | Select-String "✅ 通过").Count
```

### 分析工具

**创建分析脚本** `analyze-logs.ps1`：

```powershell
# 分析日志文件
$LogFile = "C:\hermes-test\logs\session-20250622.log"

# 统计测试数量
$TotalTests = (Get-Content $LogFile | Select-String "测试").Count
$PassedTests = (Get-Content $LogFile | Select-String "✅ 通过").Count
$FailedTests = (Get-Content $LogFile | Select-String "❌ 失败").Count

# 输出统计
Write-Host "测试统计："
Write-Host "总测试数: $TotalTests"
Write-Host "通过: $PassedTests"
Write-Host "失败: $FailedTests"
Write-Host "通过率: $([math]::Round($PassedTests / $TotalTests * 100, 2))%"
```

---

## ✅ 快速开始检查清单

### 今天就开始记录！

**最简单的方法**（1分钟设置）：
```powershell
# 1. 创建日志目录
mkdir C:\hermes-test\logs

# 2. 开始记录
Start-Transcript -Path "C:\hermes-test\logs\test-$(Get-Date -Format 'yyyyMMdd').log"

# 3. 开始测试
hermes chat

# 4. 结束后停止
Stop-Transcript
```

**推荐方法**（5分钟设置）：
```powershell
# 1. 完整目录结构
mkdir C:\hermes-test\logs
mkdir C:\hermes-test\screenshots
mkdir C:\hermes-test\reports

# 2. 开启详细记录
Start-Transcript -Path "C:\hermes-test\logs\test-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
hermes config set log_level "debug"

# 3. 进行测试
hermes chat

# 4. 保存关键截图（Win + Shift + S）

# 5. 结束记录
Stop-Transcript

# 6. 查看日志
notepad C:\hermes-test\logs\test-*.log
```

---

## 🎯 总结

**三种推荐方法**：

| 场景 | 推荐方法 | 设置时间 |
|------|---------|---------|
| 快速测试 | `Start-Transcript` | 1分钟 |
| 完整记录 | `Transcript + Hermes日志` | 5分钟 |
| 专业报告 | `Transcript + 截图 + 模板` | 10分钟 |

**选择建议**：
- 新手 → 方法1（PowerShell输出重定向）
- 完整测试 → 方法2（Hermes日志功能）
- 制作报告 → 方法4（记录模板）
- 高级用户 → 方法6（自动化脚本）

现在你可以开始记录了！建议从最简单的 `Start-Transcript` 开始，需要更详细的记录时再添加其他方法。

有任何问题随时告诉我！🚀
