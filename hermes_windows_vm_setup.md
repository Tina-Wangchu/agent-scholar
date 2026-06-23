# Hermes Agent Windows虚拟机部署与内置Skills测试攻略

## 📋 文档概述

**目标**：在Windows虚拟机上部署Hermes Agent，测试所有内置skills

**适用场景**：
- 在隔离环境中测试Agent平台
- 学习Agent框架的工作原理
- 测试各种内置skills的功能
- 为后续Agent开发做准备

---

## 🖥️ Part 1: Windows虚拟机准备

### 1.1 虚拟机软件选择

#### 推荐选项

| 软件 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **VMware Workstation Player** | 免费（个人使用）、性能好、快照功能 | 需要注册 | ⭐⭐⭐⭐⭐ |
| **VirtualBox** | 完全免费、开源 | 性能稍弱 | ⭐⭐⭐⭐ |
| **Hyper-V** | Windows内置、性能好 | 仅限Win Pro/Enterprise | ⭐⭐⭐⭐ |

#### 推荐配置

**VMware Workstation Player**（个人免费）
- 下载地址：https://www.vmware.com/products/workstation-player/workstation-player-evaluation.html
- 适合初学者，界面友好

---

### 1.2 Windows系统选择

#### 推荐配置

**Windows 11 专业版（推荐）**
- 内存：至少 8GB（推荐16GB）
- 硬盘：至少 100GB
- CPU：至少 2核（推荐4核）
- 网络：NAT模式（共享主机网络）

**Windows 10 专业版**
- 最低配置即可运行
- 适合资源受限的环境

---

### 1.3 虚拟机创建步骤（VMware为例）

#### Step 1: 创建新虚拟机

```
1. 打开 VMware Workstation Player
2. 点击 "Create a New Virtual Machine"
3. 选择 "Installer disc image file (iso)"
4. 浏览并选择Windows ISO文件
```

#### Step 2: 配置虚拟机硬件

```
推荐配置：
- 内存：8192 MB (8GB) 或更高
- 处理器：2个或更多核心
- 硬盘：100 GB（拆分为多个文件）
- 网络：NAT 模式
- 其他默认即可
```

#### Step 3: 安装Windows

```
1. 启动虚拟机
2. 按照Windows安装向导操作
3. 选择专业版（Pro）
4. 创建用户账户（建议使用密码）
```

#### Step 4: 安装VMware Tools（重要！）

```
1. 启动Windows虚拟机
2. 在VMware菜单: Player > Manage > Install VMware Tools
3. 在虚拟机中运行安装程序
4. 重启虚拟机
```

**为什么重要？**
- 支持剪贴板共享（复制粘贴）
- 支持文件拖拽
- 支持自动调整分辨率
- 提升整体性能

---

### 1.5 虚拟机优化配置

#### 启用必要的Windows功能

打开PowerShell（管理员）并运行：

```powershell
# 启用WSL（Windows Subsystem for Linux）
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启虚拟机
Restart-Computer
```

---

## 🚀 Part 2: Hermes Agent 环境部署

### 2.1 安装必要软件

#### Step 1: 安装Python

**下载Python：**
- 访问：https://www.python.org/downloads/
- 下载 Windows installer (推荐 Python 3.10 或 3.11)

**安装要点：**
```
✅ 勾选 "Add Python to PATH"
✅ 勾选 "Install for all users"
⏬ 点击 "Install Now"
```

**验证安装：**
```powershell
# 打开 PowerShell 或 CMD
python --version
pip --version
```

#### Step 2: 安装Git

**下载Git：**
- 访问：https://git-scm.com/downloads
- 下载 Windows 版本

**安装配置：**
```
- 默认编辑器：选择 VS Code
- PATH环境变量：勾选 "Git from the command line"
- 行结束符：选择 "Checkout Windows-style, commit Unix-style"
```

**验证安装：**
```powershell
git --version
```

#### Step 3: 安装Node.js（MCP服务器需要）

**下载Node.js：**
- 访问：https://nodejs.org/
- 下载 LTS 版本（推荐 18.x 或 20.x）

**验证安装：**
```powershell
node --version
npm --version
```

---

### 2.2 安装Hermes Agent

#### 方法A：从GitHub克隆（推荐）

```powershell
# 克隆仓库
git clone https://github.com/your-hermes-repo/hermes-agent.git
cd hermes-agent

# 安装依赖
pip install -r requirements.txt

# 安装Hermes CLI
npm install -g @hermes/cli
```

#### 方法B：使用包管理器

```powershell
# 使用pip直接安装
pip install hermes-agent

# 初始化配置
hermes init
```

#### 方法C：使用Docker（最简单）

```powershell
# 安装Docker Desktop for Windows
# 下载地址：https://www.docker.com/products/docker-desktop

# 拉取Hermes镜像
docker pull hermesagent/hermes:latest

# 运行Hermes容器
docker run -d -p 8080:8080 --name hermes hermesagent/hermes:latest
```

---

### 2.3 配置Hermes Agent

#### 创建配置文件

在用户目录创建 `.hermes/config.yaml`：

```powershell
# 创建配置目录
mkdir $env:USERPROFILE\.hermes

# 创建配置文件
@"
api_base: "https://api.openai.com/v1"
api_key: "YOUR_API_KEY_HERE"
model: "gpt-4"
max_tokens: 2000
temperature: 0.7
"@ | Out-File -FilePath "$env:USERPROFILE\.hermes\config.yaml" -Encoding utf8
```

#### 设置环境变量

```powershell
# 临时设置（当前会话）
$env:OPENAI_API_KEY="your-api-key"
$env:DASHSCOPE_API_KEY="your-dashscope-key"

# 永久设置（添加到系统环境变量）
# 1. 右键 "此电脑" > 属性 > 高级系统设置
# 2. 环境变量 > 新建（用户变量）
# 3. 添加 OPENAI_API_KEY 和 DASHSCOPE_API_KEY
```

---

## 🧪 Part 3: 内置Skills测试攻略

### 3.1 测试前准备

#### 检查Hermes是否正常运行

```powershell
# 启动Hermes服务
hermes start

# 查看运行状态
hermes status

# 查看可用skills
hermes list-skills
```

#### 创建测试工作区

```powershell
# 创建测试项目目录
mkdir C:\hermes-test
cd C:\hermes-test

# 初始化测试项目
hermes init test-project
cd test-project
```

---

### 3.2 基础配置类Skills测试

#### Skill 1: `/init` - 初始化项目文档

**测试目的：** 验证能否生成CLAUDE.md

**测试步骤：**
```powershell
# 在测试目录中
cd C:\hermes-test\test-project

# 调用skill
hermes run init

# 或通过CLI
/init
```

**预期结果：**
```
✓ CLAUDE.md 文件已创建
✓ 包含项目结构说明
✓ 包含关键文件列表
```

**验证：**
```powershell
# 检查文件是否存在
Get-ChildItem CLAUDE.md

# 查看文件内容
cat CLAUDE.md
```

---

#### Skill 2: `/update-config` - 配置管理

**测试目的：** 验证配置修改功能

**测试场景A：添加全局权限**
```
对话示例：
你: /update-config
Hermes: 我可以帮你修改配置。你想做什么？
你: 允许npm命令
Hermes: ✓ 已添加npm到允许列表
```

**验证配置文件：**
```powershell
# 查看配置文件
cat $env:USERPROFILE\.claude\settings.json

# 或
cat .claude\settings.json
```

**测试场景B：设置环境变量**
```
对话示例：
你: /update-config
你: set DEBUG=true
Hermes: ✓ DEBUG环境变量已设置为true
```

---

#### Skill 3: `/keybindings-help` - 快捷键配置

**测试步骤：**
```
对话示例：
你: /keybindings-help
你: 我想把保存快捷键改成Ctrl+S
Hermes: 我来帮你配置...
```

**验证：**
```powershell
# 查看快捷键配置
cat $env:USERPROFILE\.claude\keybindings.json
```

---

### 3.3 代码审查类Skills测试

#### 准备测试代码

创建包含bug的测试文件：

```powershell
# 创建测试Python文件
@"
def divide(a, b):
    return a / b  # 没有除零检查

def process_list(items):
    result = []
    for i in range(len(items)):
        item = items[i]
        if len(item) > 5:  # 可能出错
            result.append(item)
    return result

# 测试代码
print(divide(10, 0))
print(process_list(["hello", "world", "hi"]))
"@ | Out-File -FilePath test_bugs.py -Encoding utf8
```

---

#### Skill 4: `/code-review` - 代码审查

**基础测试：**
```
对话示例：
你: /code-review
Hermes: 正在审查代码...
     发现以下问题：
     1. divide()函数没有除零检查
     2. process_list()假设item是字符串
     3. 缺少错误处理
```

**带参数测试：**
```
# 高级审查（更全面）
/code-review --high

# 最多审查（最全面，可能包含不确定的发现）
/code-review --max

# 自动修复
/code-review --fix
```

**预期结果：**
```
✓ 识别出除零错误
✓ 建议添加类型检查
✓ 提供--fix时自动修复代码
```

---

#### Skill 5: `/simplify` - 代码简化

**创建复杂代码：**
```powershell
@"
def calculate_sum(numbers):
    result = 0
    for i in range(len(numbers)):
        num = numbers[i]
        if num > 0:
            result = result + num
    return result

def get_max_value(data):
    max_val = None
    for item in data:
        if max_val is None or item > max_val:
            max_val = item
    return max_val
"@ | Out-File -FilePath test_complex.py -Encoding utf8
```

**测试步骤：**
```
对话示例：
你: /simplify
Hermes: 正在优化代码...
     建议以下改进：
     1. calculate_sum可用sum()简化
     2. get_max_value可用max()简化
```

**预期结果：**
```python
# 简化后的代码
def calculate_sum(numbers):
    return sum(n for n in numbers if n > 0)

def get_max_value(data):
    return max(data) if data else None
```

---

#### Skill 6: `/security-review` - 安全审查

**创建不安全代码：**
```powershell
@"
import os

def execute_command(user_input):
    # 危险！直接执行用户输入
    os.system(user_input)

def query_database(sql):
    # 危险！SQL注入风险
    cursor.execute(sql)

def save_file(filename, content):
    # 危险！路径遍历风险
    with open(filename, 'w') as f:
        f.write(content)
"@ | Out-File -FilePath test_security.py -Encoding utf8
```

**测试步骤：**
```
对话示例：
你: /security-review
Hermes: 安全审查发现以下问题：

🔴 高危：
1. execute_command() - 命令注入风险
   - 用户输入直接执行系统命令
   - 建议：使用subprocess.run()并参数化

2. query_database() - SQL注入风险
   - SQL语句未使用参数化查询
   - 建议：使用占位符

🟡 中危：
3. save_file() - 路径遍历风险
   - 未验证文件路径
   - 建议：使用os.path.basename()限制范围
```

---

### 3.4 项目运行类Skills测试

#### Skill 7: `/run` - 运行项目

**准备测试项目：**
```powershell
# 创建简单Web应用
mkdir web-test
cd web-test

@"
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Hermes Agent!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
"@ | Out-File -FilePath app.py -Encoding utf8

# 创建requirements.txt
@"
flask==2.3.0
"@ | Out-File -FilePath requirements.txt -Encoding utf8
```

**测试步骤：**
```
对话示例：
你: /run
Hermes: 我检测到这是一个Flask应用
     正在安装依赖...
     正在启动服务器...
     ✓ 应用已启动：http://localhost:5000
```

**验证：**
```powershell
# 浏览器访问
Start-Process http://localhost:5000

# 或使用curl
curl http://localhost:5000
```

---

#### Skill 8: `/verify` - 验证变更

**场景1：验证代码修复**
```powershell
# 1. 故意引入bug
@"
def buggy_function(x):
    return 1 / x
"@ | Out-File -FilePath buggy.py -Encoding utf8

# 2. 修复bug
@"
def buggy_function(x):
    if x == 0:
        raise ValueError("x不能为0")
    return 1 / x
"@ | Out-File -FilePath fixed.py -Encoding utf8
```

**测试步骤：**
```
对话示例：
你: /verify
你: 确认bug修复有效
Hermes: 正在验证...
     ✓ 测试通过：bug已修复
     ✓ 所有测试用例通过
```

---

### 3.5 研究类Skills测试

#### Skill 9: `/deep-research` - 深度研究

**测试步骤：**
```
对话示例：
你: /deep-research
你: LLM Agent框架对比研究
Hermes: 开始深度研究...

正在从多个角度搜索：
✓ LangChain框架特点
✓ AutoGen框架特点
✓ Agent开发最佳实践
✓ 性能对比分析

正在交叉验证...
✓ 验证来源1：官方文档
✓ 验证来源2：社区讨论
✓ 验证来源3：性能测试报告

研究完成！

【研究报告】

## LLM Agent框架对比

### LangChain
- 优点：生态丰富、文档完善
- 缺点：学习曲线陡峭
- 适用场景：快速原型开发

### AutoGen
- 优点：多Agent协作强大
- 缺点：相对小众
- 适用场景：复杂Agent系统

### 性能对比
- 吞吐量：AutoGen > LangChain
- 易用性：LangChain > AutoGen

【来源列表】
1. https://python.langchain.com/
2. https://microsoft.github.io/autogen/
3. https://github.com/langchain-ai/langchain/discussions
```

**验证要点：**
- ✓ 包含多个搜索角度
- ✓ 有引用来源
- ✓ 内容有依据
- ✓ 提供来源列表

---

### 3.6 自动化类Skills测试

#### Skill 10: `/loop` - 定时任务

**测试步骤：**
```
对话示例：
你: /loop 1m /verify
Hermes: ✓ 已设置定时任务
     间隔：每1分钟
     命令：/verify
     任务ID：loop_001

     正在监控...
     [12:00] 执行verify... ✓ 通过
     [12:01] 执行verify... ✓ 通过
     [12:02] 执行verify... ✓ 通过
```

**查看运行状态：**
```powershell
# 查看所有任务
hermes list-tasks

# 停止任务
hermes stop-task loop_001
```

---

#### Skill 11: `/review` - PR审查

**准备工作：**
```powershell
# 模拟PR场景
git init
git config user.name "Test User"
git config user.email "test@example.com"

# 创建分支
git checkout -b feature-test

# 创建一些更改
@"
# New feature
def new_feature():
    return "Hello"
"@ | Out-File -FilePath new_feature.py -Encoding utf8

git add .
git commit -m "Add new feature"
```

**测试步骤：**
```
对话示例：
你: /review
Hermes: 正在审查分支 feature-test...

审查报告：

✓ 代码质量
- 新增函数结构清晰
- 命名规范

⚠ 建议改进
- 添加函数文档字符串
- 考虑添加单元测试

✓ 功能完整性
- 提交信息清晰
- 变更符合预期

总体评价：良好，建议补充测试
```

---

### 3.7 反馈类Skills测试

#### Skill 12: `/glm-plan-usage:usage-query` - 使用统计

**测试步骤：**
```
对话示例：
你: /glm-plan-usage:usage-query
Hermes: 正在查询使用统计...

【使用统计报告】

时间范围：本月
总Token使用：125,000
请求次数：42
平均响应时间：1.2s

费用详情：
- 输入Token：80,000
- 输出Token：45,000
- 预计费用：$0.25

趋势分析：
- 使用量较上月+15%
- 高峰时段：9:00-11:00
```

---

#### Skill 13: `/glm-plan-bug:case-feedback` - 问题反馈

**测试步骤：**
```
对话示例：
你: /glm-plan-bug:case-feedback
你: 发现code-review有时会误报
Hermes: 收到反馈！

反馈内容：
- 类型：功能问题
- 描述：code-review误报
- 状态：已记录

✓ 反馈已提交
✓ 感谢您的反馈！
```

---

### 3.8 辅助类Skills测试

#### Skill 14: `/fewer-permission-prompts` - 减少权限提示

**测试步骤：**
```
对话示例：
你: /fewer-permission-prompts
Hermes: 正在分析常用命令...

分析结果：
发现以下常用只读命令：
- Get-ChildItem (ls)
- Get-Content (cat)
- Get-Location (pwd)
- git status
- git log

建议添加到允许列表：
✓ PowerShell基本命令
✓ Git只读命令

是否应用这些建议？(y/n)
```

**验证配置更新：**
```powershell
# 查看更新后的配置
cat .claude\settings.json
```

---

## 📊 Part 4: 综合测试场景

### 场景1：完整开发工作流

**目标：** 测试skills的协同工作

**步骤：**
```
1. 创建新项目
   /init

2. 编写代码
   # 在编辑器中编写代码

3. 审查代码
   /code-review --fix

4. 简化优化
   /simplify

5. 安全检查
   /security-review

6. 运行测试
   /run

7. 验证功能
   /verify

8. 查看使用统计
   /glm-plan-usage:usage-query
```

**预期结果：**
- ✓ 所有skill顺利执行
- ✓ 工作流顺畅衔接
- ✓ 最终代码质量高
- ✓ 功能正常运行

---

### 场景2：自动化持续测试

**目标：** 测试自动化监控功能

**步骤：**
```
1. 设置定时验证
   /loop 5m /verify

2. 修改代码
   # 编辑代码文件

3. 观察自动验证
   # 每5分钟自动执行验证

4. 查看任务列表
   /tasks

5. 停止定时任务
   # Ctrl+C 或 /stop-task
```

---

### 场景3：代码迁移测试

**目标：** 测试大规模代码审查

**步骤：**
```
1. 拉取待审查的代码
   git clone https://github.com/user/repo.git
   cd repo

2. 执行全面审查
   /code-review --max

3. 简化代码
   /simplify

4. 安全审查
   /security-review

5. PR审查
   /review
```

---

## 🔧 Part 5: 故障排查

### 5.1 常见问题

#### 问题1：Hermes无法启动

**症状：**
```powershell
hermes start
# 错误：Hermes启动失败
```

**解决方案：**
```powershell
# 1. 检查依赖
pip check

# 2. 重新安装
pip uninstall hermes-agent
pip install hermes-agent

# 3. 检查配置
hermes config --validate

# 4. 查看日志
hermes logs
```

---

#### 问题2：Skill调用失败

**症状：**
```
你: /code-review
Hermes: ❌ Skill执行失败
```

**诊断步骤：**
```powershell
# 1. 检查skill是否可用
hermes list-skills

# 2. 检查权限
hermes permissions --check

# 3. 查看详细错误
hermes run code-review --verbose

# 4. 重置配置
hermes config --reset
```

---

#### 问题3：网络连接问题

**症状：**
```
❌ 无法连接到API服务器
```

**解决方案：**
```powershell
# 1. 测试网络连接
Test-NetConnection api.openai.com -Port 443

# 2. 配置代理（如果需要）
$env:HTTP_PROXY="http://proxy:port"
$env:HTTPS_PROXY="http://proxy:port"

# 3. 切换API endpoint
hermes config set api_base "https://api.openai.com/v1"

# 4. 使用备用API
hermes config set api_base "https://api.bigmodel.cn/v4"
```

---

#### 问题4：权限错误

**症状：**
```
❌ 拒绝访问
```

**解决方案：**
```powershell
# 1. 以管理员身份运行PowerShell
# 右键 > 以管理员身份运行

# 2. 检查文件权限
Get-Acl .hermes\config.yaml | Format-List

# 3. 修改权限
icacls .hermes /grant "$env:USERNAME:(OI)(CI)F"

# 4. 禁用只读属性
attrib -R .hermes\config.yaml
```

---

#### 问题5：虚拟机性能问题

**症状：**
- Hermes运行缓慢
- 虚拟机卡顿

**解决方案：**
```
1. 增加虚拟机内存
   VMware: VM Settings > Memory > 8GB+

2. 增加CPU核心
   VMware: VM Settings > Processor > 2+ cores

3. 启用硬件虚拟化
   BIOS: Intel VT-x / AMD-V

4. 优化磁盘性能
   使用SSD存储虚拟机文件

5. 禁用不必要的Windows服务
```

---

## 📝 Part 6: 测试检查清单

### 环境部署检查

- [ ] 虚拟机已创建（Windows 11 Pro）
- [ ] VMware Tools已安装
- [ ] Python已安装（版本≥3.10）
- [ ] Git已安装
- [ ] Node.js已安装
- [ ] Hermes Agent已安装
- [ ] API密钥已配置
- [ ] 网络连接正常

### 基础Skills测试

- [ ] `/init` - 成功生成CLAUDE.md
- [ ] `/update-config` - 成功修改配置
- [ ] `/keybindings-help` - 成功配置快捷键

### 代码审查Skills测试

- [ ] `/code-review` - 成功识别bug
- [ ] `/code-review --fix` - 成功自动修复
- [ ] `/simplify` - 成功简化代码
- [ ] `/security-review` - 成功发现安全问题

### 项目运行Skills测试

- [ ] `/run` - 成功启动项目
- [ ] `/verify` - 成功验证变更

### 研究Skills测试

- [ ] `/deep-research` - 成功生成研究报告
- [ ] 结果包含引用来源
- [ ] 内容有依据

### 自动化Skills测试

- [ ] `/loop` - 成功设置定时任务
- [ ] 任务按计划执行
- [ ] 可以停止任务

### 反馈Skills测试

- [ ] `/glm-plan-usage:usage-query` - 查询成功
- [ ] `/glm-plan-bug:case-feedback` - 反馈提交成功

### 综合场景测试

- [ ] 完整开发工作流
- [ ] 自动化持续测试
- [ ] 代码迁移测试

---

## 🎯 Part 7: 进阶使用

### 7.1 自定义Skills开发

**创建自定义Skill：**
```powershell
# 创建skill目录
mkdir .hermes\skills\my-skill
cd .hermes\skills\my-skill

# 创建skill配置
@"
name: my-skill
description: 我的自定义skill
version: 1.0.0
"@ | Out-File -FilePath skill.yaml -Encoding utf8

# 创建skill代码
@"
def run(args):
    # Skill逻辑
    return "执行成功"
"@ | Out-File -FilePath main.py -Encoding utf8
```

---

### 7.2 集成外部API

**示例：集成天气API**
```python
# weather_skill.py
import requests

def run(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
    response = requests.get(url)
    data = response.json()
    return f"{city}当前温度：{data['current']['temp_c']}°C"
```

---

### 7.3 多Agent协作

**配置多个Hermes实例：**
```powershell
# 启动多个Agent
hermes start --name agent1 --port 8081
hermes start --name agent2 --port 8082

# Agent间通信
hermes send agent1 "Hello"
hermes send agent2 "World"
```

---

## 📚 Part 8: 参考资源

### 官方文档

- [Hermes Agent 官方文档](https://docs.hermes-agent.io/)
- [Skills开发指南](https://docs.hermes-agent.io/skills)
- [API参考](https://docs.hermes-agent.io/api)

### 社区资源

- [Hermes Discord](https://discord.gg/hermes)
- [GitHub Issues](https://github.com/hermes-agent/hermes/issues)
- [Stack Overflow - hermes](https://stackoverflow.com/questions/tagged/hermes-agent)

### 学习资源

- [Agent开发教程](https://www.youtube.com/watch?v=example)
- [LangChain文档](https://python.langchain.com/)
- [AutoGen文档](https://microsoft.github.io/autogen/)

---

## ✅ 总结

通过本攻略，你已经学会了：

1. **环境准备**
   - ✓ 创建Windows虚拟机
   - ✓ 安装必要软件
   - ✓ 部署Hermes Agent

2. **Skills测试**
   - ✓ 14个内置skills的详细测试方法
   - ✓ 预期结果和验证方法
   - ✓ 综合场景测试

3. **问题排查**
   - ✓ 常见问题及解决方案
   - ✓ 诊断步骤

4. **进阶使用**
   - ✓ 自定义skill开发
   - ✓ 外部API集成
   - ✓ 多Agent协作

**下一步建议：**
1. 按照攻略逐步测试每个skill
2. 记录测试结果和遇到的问题
3. 尝试开发自己的skill
4. 集成到实际项目中

祝你在Hermes Agent的学习和实践中取得成功！🚀
