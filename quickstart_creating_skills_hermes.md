> Documentation Index: https://agentskills.io/llms.txt
> Hermes 官方文档:
> - Working with Skills: https://hermes-agent.nousresearch.com/docs/guides/work-with-skills
> - Creating Skills: https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills
> - Skills System (完整技术参考): https://hermes-agent.nousresearch.com/docs/user-guide/features/skills

# Hermes Agent Skills 快速入门与创作指南

> Skills 是 Agent 在需要时可以加载的**按需知识文档**。它们遵循**渐进式披露**（progressive disclosure）模式以最小化 token 用量，并兼容 agentskills.io 开放标准。

---

## 一、Skill 是什么？

Skill 本质上是一个包含 `SKILL.md` 文件的文件夹，它告诉 Agent **如何处理特定任务**——从生成 ASCII 艺术到管理 GitHub PR。

### Skill vs Plugin vs Memory

| 维度 | Skills | Plugin | Memory |
|---|---|---|---|
| **本质** | Markdown 知识文档 | Python 代码扩展 | 事实性知识 |
| **内容** | 指令 / SOP / prompt 模板 | 可执行的工具、hook、命令 | 用户偏好、关键事实 |
| **加载方式** | 按需加载，用完即卸载 | 启动时加载，需重启生效 | 每次会话自动注入 |
| **Token 开销** | 未使用时为零 | 启动后持续占用 | 每轮都有小量消耗 |
| **谁创建** | 用户、Agent 自己、Hub 安装 | 开发者（需写 Python） | Agent 基于对话自动创建 |
| **类比** | 参考文档 / 操作手册 | VS Code Extension | 便利贴 |
| **何时用** | "怎么部署到 K8s" | 需要新的可调用工具 | "用户偏好深色模式" |

**经验法则：** 如果你会把它写在参考文档里 → 它是 Skill。如果你会把它贴在便利贴上 → 它是 Memory。如果需要新的可执行能力 → 它是 Plugin。

### 何时选择创建 Skill 而非 Tool

**做 Skill 当：**
- 能力可以用「指令 + shell 命令 + 现有工具」表达
- 它封装一个外部 CLI 或 API，Agent 可以通过 `terminal` 或 `web_extract` 调用
- 不需要自定义 Python 集成或内建的 API key 管理
- 例：arXiv 搜索、git 工作流、Docker 管理、PDF 处理、通过 CLI 发邮件

**做 Tool (Plugin) 当：**
- 需要 API key、认证流程、多组件配置的端到端集成
- 需要每次精确执行的自定义处理逻辑
- 处理二进制数据、流式传输、实时事件
- 例：浏览器自动化、TTS、视觉分析

---

## 二、发现与使用 Skills

### 查看已安装的 Skills

```bash
# 在聊天会话中
/skills

# 或从 CLI
hermes skills list
```

输出示例：
```
ascii-art         Generate ASCII art using pyfiglet, cowsay, boxes...
arxiv             Search and retrieve academic papers from arXiv...
github-pr-workflow Full PR lifecycle — create branches, commit...
plan              Plan mode — inspect context, write a markdown...
excalidraw        Create hand-drawn style diagrams using Excalidraw...
```

### 搜索 Skills

```bash
hermes skills search docker
hermes skills search music
```

### 使用 Skill

每个已安装的 skill 自动成为斜杠命令：

```bash
# 加载 skill 并给它一个任务
/ascii-art Make a banner that says "HELLO WORLD"
/plan Design a REST API for a todo app
/github-pr-workflow Create a PR for the auth refactor

# 只输入 skill 名称（不带任务），加载后 Agent 会询问你的需求
/excalidraw
```

也可以通过自然对话触发——告诉 Hermes 使用某个 skill，它会通过 `skill_view` 工具加载。

### 渐进式披露机制

Skills 使用节省 token 的加载模式：

```
Level 0: skills_list() → [{name, description, category}, ...]   (~3k tokens，会话开始时加载)
Level 1: skill_view(name) → 完整 SKILL.md 内容 + 元数据          (Agent 决定需要时才加载)
Level 2: skill_view(name, file_path) → 特定引用文件              (仅在需要时才加载)
```

**这意味着 Skills 在实际使用之前不消耗任何 token。**

---

## 三、安装 Skills

### 官方可选 Skills

```bash
# 从 CLI 安装
hermes skills install official/security/1password

# 在聊天会话中安装
/skills install official/creative/songwriting-and-ai-music

# 安装后需要新会话生效，或用 /reset 重置，或 --now 立即生效（消耗更多 token）
```

### Skills Hub 多源安装

```bash
# 浏览所有 hub skills
hermes skills browse
hermes skills browse --source official

# 搜索
hermes skills search kubernetes
hermes skills search react --source skills-sh

# 从不同来源安装
hermes skills install openai/skills/k8s                    # GitHub
hermes skills install skills-sh/vercel-labs/...            # skills.sh
hermes skills install well-known:https://mintlify.com/...  # well-known
hermes skills install https://sharethis.chat/SKILL.md      # 直接 URL

# 添加自定义 tap（GitHub 仓库）
hermes skills tap add myorg/skills-repo
```

### 信任级别

| 级别 | 来源 | 策略 |
|---|---|---|
| `builtin` | 随 Hermes 附带 | 始终受信任 |
| `official` | 仓库中的 `optional-skills/` | 内置信任 |
| `trusted` | openai/skills、anthropics/skills 等 | 更宽松的策略 |
| `community` | 其他所有来源 | 危险发现不可覆盖；非危险发现可用 `--force` |

---

## 四、SKILL.md 格式完整参考

### 目录结构

```
~/.hermes/skills/                          # 主目录，唯一可信来源
├── research/                             # 分类目录
│   ├── arxiv/
│   │   ├── SKILL.md                      # 主指令文件（必需）
│   │   ├── references/                   # 额外参考文档
│   │   │   └── api-docs.md
│   │   ├── templates/                    # 输出模板
│   │   │   └── output.yaml
│   │   ├── scripts/                      # Agent 可执行的辅助脚本
│   │   │   └── search_arxiv.py
│   │   └── assets/                       # 补充资源
│   └── literature-search/
│       └── SKILL.md
├── productivity/
│   └── ocr-and-documents/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
└── .hub/                                 # Skills Hub 状态
    ├── lock.json
    ├── quarantine/
    └── audit.log
```

### SKILL.md 完整模板

```yaml
---
# ==================== 基本字段 ====================
name: my-skill                              # 必需：skill 标识符，需匹配文件夹名
description: Brief description of what this skill does  # 必需：在搜索结果中展示，Agent 据此决定是否激活
version: 1.0.0                              # 可选：版本号
author: Your Name                           # 可选：作者
license: MIT                                # 可选：许可证

# ==================== 平台限制 ====================
platforms: [macos, linux]                   # 可选：限制 OS 平台
                                             #   有效值：macos, linux, windows
                                             #   省略则在所有平台加载（默认）

# ==================== 元数据 ====================
metadata:
  hermes:
    tags: [Category, Subcategory, Keywords]  # 可选：分类标签
    category: my-category                    # 可选：所属分类
    related_skills: [other-skill-name]      # 可选：关联 skill

    # --- 条件激活（可选） ---
    requires_toolsets: [web]                # 仅当 web toolset 可用时显示
    requires_tools: [web_search]            # 仅当 web_search 工具可用时显示
    fallback_for_toolsets: [browser]        # 仅当 browser toolset 不可用时显示（降级方案）
    fallback_for_tools: [browser_navigate]  # 仅当 browser_navigate 工具不存在时显示

    # --- 配置设置（可选，存入 config.yaml） ---
    config:
      - key: my.setting                     # 设置的键名（支持点号路径）
        description: "What this setting controls"  # 设置说明
        default: "sensible-default"          # 默认值
        prompt: "Display prompt for setup"   # hermes config migrate 时的提示文本

    # --- Blueprint 自动化（可选） ---
    blueprint:
      schedule: "0 9 * * *"                 # cron 表达式 / "every 2h" / ISO 时间戳
      deliver: origin                       # 投递方式（可选，默认 origin）
      prompt: "Task instruction for each run"  # 每次运行的指令（可选）
      no_agent: false                       # 可选

# ==================== 环境变量需求（可选） ====================
required_environment_variables:
  - name: MY_API_KEY                        # 环境变量名
    prompt: "Enter your API key"            # 提示文本
    help: "Get one at https://example.com"  # 帮助文本或 URL
    required_for: "API access"              # 哪个功能需要此变量

# ==================== 凭证文件需求（可选） ====================
required_credential_files:
  - path: google_token.json                 # 相对于 ~/.hermes/ 的文件路径
    description: Google OAuth2 token         # 说明
---
```

---

### Frontmatter 各字段详解

#### 基本字段

| 字段 | 必需 | 作用 |
|---|---|---|
| `name` | ✅ | skill 的短标识符。必须与文件夹名匹配。出现在 `skills_list()`、斜杠命令、搜索结果中。 |
| `description` | ✅ | 简短描述（一句话）。**这是 Agent 决定是否激活此 skill 的关键依据**。应清晰说明使用场景和触发条件。 |
| `version` | ❌ | 版本号，用于追踪更新。 |
| `author` | ❌ | 作者信息。 |
| `license` | ❌ | 许可证类型。 |

#### 平台限制

| 字段 | 有效值 | 作用 |
|---|---|---|
| `platforms` | `macos`, `linux`, `windows`（可多选） | 限制 skill 仅在指定平台加载。设置后，在不兼容平台上自动从系统提示词、`skills_list()` 和斜杠命令中隐藏。省略则在所有平台可用。 |

示例：
```yaml
platforms: [macos]           # 仅 macOS（如 iMessage、Apple Reminders）
platforms: [macos, linux]    # macOS 和 Linux
platforms: [windows]        # 仅 Windows
```

#### 条件激活字段

| 字段 | 行为 | 典型用途 |
|---|---|---|
| `requires_toolsets` | 当列出的 toolset **不可用**时，skill **隐藏** | 仅在有 web 工具时才显示网页抓取 skill |
| `requires_tools` | 当列出的工具 **不可用**时，skill **隐藏** | 仅在有特定工具时才显示 |
| `fallback_for_toolsets` | 当列出的 toolset **可用**时，skill **隐藏** | 免费替代方案，仅在高级工具不可用时显示 |
| `fallback_for_tools` | 当列出的工具 **存在**时，skill **隐藏** | 同上，但检查单个工具 |

典型示例：
```yaml
# duckduckgo-search：当 FIRECRAWL_API_KEY 未设置（web toolset 不可用）时自动出现
fallback_for_toolsets: [web]

# 某些 skill 仅在特定工具可用时才有意义
requires_toolsets: [web]
```

#### 配置设置 (`config`)

用于声明 **非密钥配置**（路径、偏好项等），存储在 `config.yaml` 中：

```yaml
metadata:
  hermes:
    config:
      - key: myplugin.path
        description: "Path to the plugin data directory"
        default: "~/myplugin-data"
        prompt: "Plugin data directory path"
```

工作原理：
1. 值写入 `config.yaml` 的 `skills.config.<key>` 下
2. `hermes config migrate` 扫描所有 skill 的未配置设置并提示用户
3. skill 加载时，配置值自动注入到上下文中：
   ```
   [Skill config (from ~/.hermes/config.yaml):
     myplugin.path = /home/user/my-data
   ]
   ```
4. 也可手动设置：`hermes config set skills.config.myplugin.path ~/my-data`

#### 环境变量需求 (`required_environment_variables`)

用于声明 **密钥/令牌**（API Key 等），存储在 `.env` 中：

```yaml
required_environment_variables:
  - name: TENOR_API_KEY
    prompt: "Tenor API key"
    help: "Get a key from https://developers.google.com/tenor"
    required_for: "full functionality"
```

关键特性：
- 缺失值 **不会** 从发现列表中隐藏 skill
- 仅在本地 CLI 实际加载 skill 时安全地请求输入
- 用户可以跳过设置并继续使用 skill
- 声明的环境变量 **自动传递** 到 `execute_code` 和 `terminal` 沙箱
- Gateway/消息平台不收集密钥，而是提示用 `hermes setup` 或 `.env` 配置

#### 凭证文件需求 (`required_credential_files`)

用于声明 **基于文件的凭证**（OAuth token 文件、客户端密钥、证书等）：

```yaml
required_credential_files:
  - path: google_token.json
    description: "Google OAuth2 token (created by setup script)"
  - path: google_client_secret.json
    description: "Google OAuth2 client credentials"
```

当 skill 加载时：
- 缺失文件触发 `setup_needed`
- 已有文件自动 **挂载到 Docker 容器**（只读绑定）
- **同步到 Modal 沙箱**（创建时 + 每次命令前）
- 本地后端无需特殊处理

---

## 五、SKILL.md 正文结构

正文是 Agent 加载 skill 后实际阅读的指令。推荐以下结构：

```markdown
# Skill Title

一句话介绍这个 skill 的功能。

## When to Use（何时使用）

触发条件 —— Agent 应该在什么情况下加载此 skill？
明确描述适用场景，帮助 Agent 快速判断。

## Quick Reference（快速参考）

常用命令或 API 调用的速查表。Agent 可以快速查找而不必阅读完整步骤。
| Action | Command |
|--------|---------|
| 搜索论文 | `curl "http://export.arxiv.org/api/query?search_query=..."` |
| 获取全文 | ... |

## Procedure（操作步骤）

Agent 遵循的分步指令。这是 skill 的核心内容。

1. **第一步**：检查先决条件是否可用
2. **第二步**：执行 `command --with-flags`
3. **第三步**：解析输出并呈现结果
4. **第四步**：...

## Pitfalls（常见陷阱）

已知的失败模式和应对方法。这是让 Agent 避坑的关键部分。**详见第八章「Pitfalls 深度指南」。**

每条陷阱应包含：**现象描述 → 原因分析 → 具体修复方案**。记录实践中真实遇到的失败，而非理论上的可能性。

- **常见错误**：[具体现象描述]。**原因**：[为什么会发生]。**解决方法**：[具体可执行的命令或操作]
- **注意**：[在什么条件下会触发的边界情况]
- **已知失败**：[具体失败场景]。**修复**：[具体修复步骤]

## Verification（验证）

Agent 如何确认操作成功？

运行 `check-command` 来验证结果是否正确。

[可选]
## References（引用）

对于 API 详情，加载参考文档：
`skill_view("my-skill", "references/api-docs.md")`
```

### 各部分的作用与写作要点

| 部分 | 作用 | 写作要点 |
|---|---|---|
| **Title + 简介** | 快速告诉 Agent 这个 skill 做什么 | 一句话概括核心功能 |
| **When to Use** | 触发条件，Agent 据此判断是否需要此 skill | 列出关键词、场景、用户意图。越具体越好，避免模糊描述 |
| **Quick Reference** | 常用操作的速查表，减少 token 消耗 | 用表格或简洁列表，只放最常用的命令 |
| **Procedure** | 核心操作步骤，Agent 的执行指南 | **最常用的流程放最前面**。步骤编号清晰，每步只做一件事。使用具体的命令和示例 |
| **Pitfalls** | 帮助 Agent 避开已知陷阱——**是许多 skill 中最高价值的内容** | 记录实践中真实遇到的失败，每条包含：现象→原因→具体修复方案。详见第八章深度指南 |
| **Verification** | 确认操作成功的检查方法 | 给出具体的验证命令或预期输出 |
| **References** | 指向更多细节的引用文件 | 用 `skill_view("name", "path")` 引用，避免正文过长 |

---

## 六、辅助文件

### scripts/ — 辅助脚本

对于 XML/JSON 解析或复杂逻辑，提供辅助脚本，**不要指望 LLM 每次内联写解析器**：

```bash
my-skill/
├── SKILL.md
├── scripts/
│   ├── search_arxiv.py          # 搜索逻辑
│   └── parse_results.py         # 解析逻辑
└── references/
    └── api-docs.md
```

在 SKILL.md 中引用脚本时，使用 `${HERMES_SKILL_DIR}` 模板变量：

```markdown
To analyse the input, run:

    node ${HERMES_SKILL_DIR}/scripts/analyse.js <input>
```

可用的模板变量：

| 变量 | 替换为 |
|---|---|
| `${HERMES_SKILL_DIR}` | skill 目录的绝对路径 |
| `${HERMES_SESSION_ID}` | 当前会话 ID（无会话时保持原样） |

### references/ — 参考文档

Agent 按需加载的详细参考：

```markdown
For API details, load the reference:
`skill_view("my-skill", "references/api-docs.md")`
```

### templates/ — 输出模板

Agent 生成内容时可参考的模板格式。

### 内联 Shell 片段（可选，默认关闭）

Skills 可以嵌入内联 shell 片段，使用 `` !`cmd` `` 语法：

```markdown
Current date: !`date -u +%Y-%m-%d`
Git branch: !`git -C ${HERMES_SKILL_DIR} rev-parse --abbrev-ref HEAD`
```

**默认关闭**（安全考虑），需在 `config.yaml` 中启用：

```yaml
skills:
  inline_shell: true
  inline_shell_timeout: 10   # 每个片段的超时秒数
```

---

## 七、创建 Skill 的步骤

### 1. 创建目录

```bash
mkdir -p ~/.hermes/skills/my-category/my-skill
```

### 2. 编写 SKILL.md

```yaml
---
name: my-skill
description: Brief description of what this skill does
version: 1.0.0
metadata:
  hermes:
    tags: [my-tag, automation]
    category: my-category
---

# My Skill

## When to Use
Use this skill when the user asks about [specific topic] or needs to [specific task].

## Procedure
1. First, check if [prerequisite] is available
2. Run `command --with-flags`
3. Parse the output and present results

## Pitfalls
- Common failure: [description]. Fix: [solution]
- Watch out for [edge case]

## Verification
Run `check-command` to confirm the result is correct.
```

### 3. 添加辅助文件（可选）

```
my-skill/
├── SKILL.md
├── references/
│   └── api-docs.md
├── templates/
│   └── config.yaml
└── scripts/
    └── setup.sh
```

### 4. 测试

```bash
hermes chat --toolsets skills -q "/my-skill help me with the thing"
```

> **无需注册！** 放入 `~/.hermes/skills/` 即生效，新会话自动可用。

---

## 八、Pitfalls 深度指南（★ 高价值章节）

> agentskills.io 的最佳实践文档如此评价：**"Gotchas sections 是许多 skill 中最高价值的内容（The highest-value content in many skills）"**。

### 为什么 Pitfalls 如此重要？

#### 1. Agent 的「合理假设」往往是错的

LLM 在执行任务时，会基于其训练数据做出大量隐式假设——而这些假设在特定环境、特定 API、特定项目中经常不成立。Pitfalls 的核心作用就是**显式纠正这些会被 Agent 默认做错的假设**。

例如：Agent 看到数据库里有一个 `users` 表，会自然假设 `SELECT * FROM users` 能返回所有活跃用户。但如果你的系统使用软删除，这个查询会返回大量已注销账户。不写 Pitfalls，Agent 每次都会犯这个错。

#### 2. 经验知识的载体

Procedure 告诉 Agent "怎么做"，Pitfalls 告诉 Agent "**哪些路走不通**"。后者往往来自实践中踩过的坑、调试数小时才发现的根因——这些知识无法从文档中推导，只能从经验中获取。

#### 3. 让 Skill 形成闭环

一个没有 Pitfalls 的 Skill 就像一个没有错误处理的程序——Happy Path 能跑通，但真实场景中到处碰壁。Pitfalls 将「理想流程」补全为「包含异常处理的健壮流程」。

#### 4. Agent 程序性记忆的精华

当 Agent 自己创建 Skill 时（`skill_manage`），它会自动将执行过程中发现的陷阱记录下来。这些陷阱是 Agent 从真实错误中学习的结果，是 Hermes「越用越聪明」学习循环的核心产出。

### Pitfalls 应该包含什么内容？

#### 核心原则：记录「违背合理假设」的具体事实

**❌ 差的 Pitfalls —— 模糊、理论化、没有可执行修复**

```markdown
## Pitfalls
- Errors may occur during API calls. Handle errors appropriately.
- Be careful with data types.
- Follow best practices for authentication.
- 注意可能出现超时。
```

为什么差？这些都是**泛泛的建议**，Agent 早就知道要"处理错误"。它们不包含 Agent 不知道的、特定于当前任务的事实。

**✅ 好的 Pitfalls —— 具体、可操作、纠正真实会犯的错**

```markdown
## Pitfalls

### 1. arXiv API 返回 Atom XML，不是 JSON
Agent 默认期望 REST API 返回 JSON，会尝试用 `json.tool` 解析而失败。
**修复**：必须用 XML 解析器（`xml.etree.ElementTree`）或 helper script `scripts/search_arxiv.py`。

### 2. `users` 表使用软删除
`SELECT * FROM users` 会包含 `deleted_at` 不为 NULL 的已注销账户。
**修复**：所有查询必须加 `WHERE deleted_at IS NULL`。

### 3. `/health` 端点不可靠
`/health` 只要 Web 服务器在运行就返回 200，即使数据库连接已断开。
**修复**：检查服务完整健康状态必须使用 `/ready` 端点。

### 4. 用户 ID 在不同服务中名称不同
数据库中是 `user_id`，认证服务中是 `uid`，计费 API 中是 `accountId`。
这三个字段指向同一个值，但名称完全不同，跨服务查询时必须手动映射。
```

为什么好？每一条都纠正了一个 **Agent 不被告知就一定会犯的错**，并给出了具体的修复方案。

### Pitfalls 的五大内容类别

根据实践，高质量的 Pitfalls 通常涵盖以下类别：

#### 类别 1：API / 接口陷阱

API 的行为与 Agent 的预期不一致的地方。

```markdown
### Semantic Scholar 有速率限制（1 req/sec）
无 API Key 时限制为每秒 1 次请求。超过会返回 429 错误。
**修复**：在批量查询之间加 `sleep 1`；或申请 API Key 提升到 100 req/sec。

### arXiv 论文可能被撤稿
论文提交后可能被撤回。此时 `<summary>` 字段会包含撤稿通知（包含 "withdrawn" 或 "retracted"）。
**修复**：始终检查摘要内容，确认不是撤稿通知后再作为有效论文处理。
```

**要点**：记录 API 的隐藏限制、非标准行为、版本差异。

#### 类别 2：数据 / 格式陷阱

数据格式、字段命名、编码等会误导 Agent 的细节。

```markdown
### arXiv 返回 Atom XML，不是 JSON
API 的 Content-Type 是 XML。Agent 如果用 `python3 -m json.tool` 解析会报错。
**修复**：使用 `scripts/search_arxiv.py` 辅助脚本，或用 `xml.etree.ElementTree` 解析。

### arXiv ID 有两种格式
旧格式：`hep-th/0601001`（分类前缀/编号）
新格式：`2402.03300`（纯数字）
**修复**：脚本中需兼容两种格式。URL 访问两种格式都支持。

### 论文版本漂移
`arxiv.org/abs/1706.03762` 始终解析到**最新版本**，内容可能已大幅修改。
**修复**：引用时使用带版本号的 URL（如 `1706.03762v1`）防止引用漂移。
```

**要点**：记录非显而易见的数据格式差异、编码问题、命名不一致。

#### 类别 3：环境 / 平台陷阱

特定环境下的行为差异。

```markdown
### Windows 上 curl 的引号处理不同
Windows PowerShell 中 curl 是 `Invoke-WebRequest` 的别名，引号规则与 bash 不同。
**修复**：Windows 上使用 `curl.exe` 显式调用原生 curl，或使用 PowerShell 的原生语法。

### 远程沙箱中环境变量不会自动传递
`execute_code` 沙箱默认不继承宿主机的环境变量。
**修复**：在 SKILL.md frontmatter 中声明 `required_environment_variables`，Hermes 会自动传递到沙箱。
```

**要点**：记录 OS 差异、容器/沙箱限制、路径差异。

#### 类别 4：工具 / 依赖陷阱

工具可用性、依赖缺失、版本兼容性等问题。

```markdown
### `pdfplumber` 可能未安装
如果系统未安装 `pdfplumber`，Agent 会尝试 `import pdfplumber` 并报 ModuleNotFoundError。
**修复**：在 Procedure 的第一步检查：`python3 -c "import pdfplumber"`，失败时提示安装或回退到 `pdf2image + pytesseract`。

### `grep -o` 在 macOS 和 Linux 行为一致，但在旧版 macOS (BSD grep) 不支持 -P (Perl regex)
**修复**：避免使用 `grep -P`，或检测平台后使用 `gnu-sed`（通过 `brew install gnu-sed`）。
```

**要点**：记录依赖缺失时的降级方案、版本兼容性问题。

#### 类别 5：流程 / 逻辑陷阱

工作流中的顺序依赖、原子性、幂等性等逻辑陷阱。

```markdown
### 必须先 `git pull` 再 push，否则会冲突
直接 push 到远程可能因远程有新提交而失败。
**修复**：Procedure 中必须包含 `git pull --rebase origin main` 作为 push 之前的步骤。

### 删除 skill 后 cron job 仍引用旧名称
如果 skill 被重命名或合并到 umbrella skill，已有的定时任务不会自动更新。
**修复**：重命名 skill 后检查并手动更新所有 cron job 的 skill 引用。
```

**要点**：记录操作顺序依赖、不可逆操作的风险、跨组件的影响。

### Pitfalls 的写作格式

推荐使用以下结构，让 Agent 能快速定位和执行修复：

#### 格式 A：问题-原因-修复（最常用）

```markdown
### [简短标题：描述核心问题]

[1-2 句描述现象：Agent 在什么条件下会犯什么错]
[1 句解释原因：为什么会发生]
**修复**：[具体的命令、代码或操作步骤]
```

#### 格式 B：条件触发式

```markdown
### 当 [条件] 时，[会出什么问题]

[描述]
**修复**：[方案]
```

#### 格式 C：对比式（对了解差异特别有效）

```markdown
### [概念] 在不同上下文中名称不同
- 数据库中：`user_id`
- 认证服务中：`uid`
- 计费 API 中：`accountId`
**修复**：跨服务查询时必须使用映射表。
```

### Pitfalls 的来源

#### 1. 从真实执行中提取

最佳来源是**你自己（或 Agent）实际执行任务时遇到的错误**：

- 你纠正了 Agent 的哪个操作？（"不对，用库 X 而不是 Y"）
- 哪个步骤 Agent 跳过了但应该执行？
- 哪个命令报错了，你是怎么修的？
- Agent 生成的什么输出格式不对，你怎么调整的？

> Hermes 的 Agent 在完成复杂任务后会自动提议将方法保存为 skill，**包括过程中发现的陷阱**。这些 Agent 创建的 Pitfalls 是最有价值的——因为它们是从真实失败中提炼的。

#### 2. 从项目文档中挖掘

- 团队的 Runbook 和故障排查手册
- Issue Tracker 中反复出现的问题
- Code Review 中经常被指出的错误模式
- Git history 中的 bug fix 提交（揭示了实际发生了什么问题）

#### 3. 从 API 文档的「已知问题」中提取

- Rate Limits
- Deprecated endpoints
- Breaking changes
- Platform-specific behaviors

### Pitfalls 的放置策略

#### 放在 SKILL.md 正文中（推荐大多数情况）

```markdown
## Pitfalls
- 陷阱 1
- 陷阱 2
```

**优点**：Agent 在执行 Procedure 之前就读到，可以在遇到问题之前就避免。
**适用**：Agent **无法自行判断是否会触发**的陷阱——问题不明显，Agent 看到现象时已经来不及了。

#### 放在 references/ 中（条件加载）

```markdown
## Pitfalls
- 最关键的 2-3 个陷阱放在正文（Agent 必须提前知道）

### 更多陷阱
遇到以下情况时，加载详细参考：
`skill_view("my-skill", "references/troubleshooting.md")`
```

**优点**：节省正文 token。
**适用**：Agent **能通过现象判断是否需要**的陷阱——比如"如果 API 返回 500，加载故障排查文档"。

> **关键原则**：如果 Agent 无法自行判断是否会触发该陷阱，就放在正文中。如果 Agent 能从错误信息中识别需要哪个陷阱的知识，则可以放在 references/ 中。

### 常见的 Pitfalls 写作误区

| 误区 | 问题 | 正确做法 |
|---|---|---|
| 写泛泛建议："注意错误处理" | Agent 早就知道，浪费 token | 写具体错误："API 返回 429 时必须等待 3 秒" |
| 只描述问题不给修复 | Agent 知道有问题但不知道怎么修 | 每条陷阱必须附带可执行的修复方案 |
| 写理论失败："可能会超时" | 不够具体，Agent 不知道何时发生 | 写具体条件："当结果超过 100 条时，API 会超时" |
| 堆砌太多陷阱 | 正文膨胀，稀释关键信息 | 只保留 **Agent 不被告知就一定会犯的** 2-5 条核心陷阱，其余放入 references/ |
| 把注意事项当陷阱 | "记得保存文件" 不是陷阱 | 陷阱是 "Agent 默认会做 X，但实际应该做 Y" 的纠正性知识 |
| 过度防御 | 每个步骤都加 warning | 只在 **真正违背 Agent 合理假设** 的地方加 Pitfalls |

### 实战示例：arxiv skill 的 Pitfalls

以下是 Hermes 内置 `arxiv` skill 中实际使用的 Notes 部分（作用等同于 Pitfalls），展示了优秀的陷阱记录：

```markdown
## Notes（陷阱与注意事项）

- arXiv 返回 Atom XML — 使用辅助脚本或解析代码片段获取干净输出
  （纠正：Agent 期望 JSON，实际是 XML）

- Semantic Scholar 返回 JSON — 通过 `python3 -m json.tool` 提高可读性

- arXiv ID 有两种格式：旧格式 (`hep-th/0601001`) vs 新格式 (`2402.03300`)

- PDF 地址：`https://arxiv.org/pdf/{id}` — 摘要地址：`https://arxiv.org/abs/{id}`
  — HTML（可用时）：`https://arxiv.org/html/{id}`

## ID Versioning（版本陷阱）

- `arxiv.org/abs/1706.03762` 始终解析到**最新**版本
- `arxiv.org/abs/1706.03762v1` 指向**特定**不可变版本
- 生成引用时保留你实际阅读的版本后缀，防止引用漂移
  （后续版本可能大幅修改内容）

## Withdrawn Papers（撤稿陷阱）

论文可以在提交后被撤回：
- `<summary>` 字段包含撤稿通知（查找 "withdrawn" 或 "retracted"）
- 元数据字段可能不完整
- 始终检查摘要，确认不是撤稿通知后再作为有效论文处理

## Rate Limits（速率陷阱）

| API | 速率 | 认证 |
|-----|------|------|
| arXiv | ~1 请求 / 3 秒 | 无需 |
| Semantic Scholar | 1 请求 / 秒 | 无（有 Key 可到 100/sec） |
```

注意这个示例的特点：
1. **每条都是 Agent 会被误导的具体事实**，不是泛泛建议
2. **覆盖了五大类别**：数据格式（XML/JSON）、接口差异（两种 ID 格式）、版本问题（引用漂移）、边界情况（撤稿论文）、环境限制（速率限制）
3. **修复方案内嵌在描述中**：看到 XML → 用辅助脚本；看到最新版 URL → 加版本后缀
4. **用表格整理量化信息**：速率限制用表格比文字更清晰

### 检查清单：你的 Pitfalls 写得好吗？

用以下检查清单审视你的 Pitfalls 部分：

- [ ] **每条陷阱都纠正了一个 Agent 不被告知就一定会犯的错？** （不是泛泛建议）
- [ ] **每条都包含具体的修复方案？** （不是只描述问题）
- [ ] **陷阱数量在 2-5 条？** （太多说明 skill 本身可能需要重构）
- [ ] **最关键的陷阱在 SKILL.md 正文中？** （Agent 能在犯错前读到）
- [ ] **次要陷阱在 references/ 中并告诉 Agent 何时加载？** （节省 token）
- [ ] **覆盖了实际遇到过的真实问题？** （不是想象的、理论上的可能失败）
- [ ] **来源多样？** （API 限制 + 数据格式 + 环境差异 + 流程依赖）
- [ ] **Agent 使用 skill 后，你能再补充新发现的陷阱？** （Skill 应该越用越好）

---

## 九、编写优秀 Skill 的原则

### 1. 保持聚焦（Focused）

❌ 一个涵盖 "所有 DevOps" 的 skill 太长太模糊
✅ 一个覆盖 "部署 Python 应用到 Fly.io" 的 skill 足够具体，真正有用

> A skill that tries to cover "all of DevOps" will be too long and too vague. A skill that covers "deploy a Python app to Fly.io" is specific enough to be genuinely useful.

### 2. 渐进式披露（Progressive Disclosure）

**最常用的流程放最前面**，边缘情况和高级用法放在底部。这样常见任务消耗最少的 token。

```
Quick Reference（最常用）→ Procedure（详细步骤）→ Pitfalls（遇到问题时再看）
```

### 3. 提供辅助脚本

对于 XML/JSON 解析或复杂逻辑，在 `scripts/` 下提供辅助脚本。不要期望 LLM 每次都内联写解析器——LLM 生成代码不可靠，而预写脚本稳定且可测试。

### 4. 无外部依赖

优先使用 Python 标准库、curl 和现有的 Hermes 工具（`web_extract`、`terminal`、`read_file`）。如果确实需要依赖，在 skill 中记录安装步骤。

### 5. 写好 Description

`description` 是 Agent 决定是否激活此 skill 的**唯一依据**（在 Level 0 阶段）。好的描述应该：
- 包含用户可能使用的**关键词**
- 说明**使用场景**和**触发条件**
- 避免模糊描述

示例：
```yaml
# ❌ 模糊
description: "A helpful tool for research"

# ✅ 具体
description: "Search and retrieve academic papers from arXiv via their free REST API. Use when asked to find papers, search arXiv, or look up academic research on a topic."
```

### 6. 记录陷阱 (Pitfalls)

**Pitfalls 是许多 skill 中最高价值的内容。** 它是让 skill 从 "能用" 变成 "好用" 的关键。详见第八章「Pitfalls 深度指南」。记录：
- 常见错误模式及其解决方案
- 边界条件和特殊情况
- Agent 在实际使用中发现的问题

> Agent 自己创建 skill 时会自动包含发现的陷阱——这是 Agent 程序性记忆的精华所在。

### 7. 使用分类

按分类组织 skills 到子目录（`~/.hermes/skills/devops/`、`~/.hermes/skills/research/` 等），保持列表可管理，帮助 Agent 更快找到相关 skill。

### 8. 及时更新

如果使用 skill 时遇到未覆盖的问题，告诉 Hermes 更新 skill。不维护的 skill 会变成负担而不是资产。

### 9. 让 Agent 自己创建 Skill

在完成复杂的多步骤任务后，Hermes 经常会主动提议将方法保存为 skill。**说 Yes**——这些 Agent 创建的 skill 捕获了精确的工作流程，包括过程中发现的陷阱。

---

## 十、配置 Skill 设置

### API Key / 密钥（环境变量）

```bash
# 交互式设置
hermes secrets set TENOR_API_KEY

# 或直接编辑 ~/.hermes/.env
TENOR_API_KEY=your_key_here
```

### 非密钥配置（config.yaml）

```bash
# 让 Hermes 提示所有未配置的设置
hermes config migrate

# 查看当前配置
hermes config show

# 手动设置
hermes config set skills.config.myplugin.path ~/my-data
```

---

## 十一、Skill Bundle（技能捆绑包）

Skill 捆绑包是将多个 skills 归组在单个斜杠命令下的 YAML 文件：

```yaml
# ~/.hermes/skill-bundles/backend-dev.yaml
name: backend-dev
description: Backend feature work — review, test, PR workflow
skills:
  - github-code-review
  - test-driven-development
  - github-pr-workflow
instruction: |
  Always start by writing failing tests, then implement.
  Open the PR through the standard workflow with co-author tags.
```

使用：
```bash
# 创建捆绑包
hermes bundles create backend-dev --skill github-code-review --skill test-driven-development

# 使用
/backend-dev refactor the auth middleware

# 管理
hermes bundles list
hermes bundles delete backend-dev
```

---

## 十二、Blueprint — 可自动化的 Skill

Blueprint 是一个普通 skill，但在 frontmatter 中额外声明了定时计划，使其成为可分享的可运行自动化：

```yaml
metadata:
  hermes:
    tags: [blueprint, email]
    blueprint:
      schedule: "0 8 * * *"                          # cron 表达式
      deliver: telegram                                # 投递方式（可选）
      prompt: "Summarize my unread email and calendar" # 每次运行的指令
```

安装 blueprint skill 时，它被注册为**建议的定时任务**（不会静默创建）：
```bash
hermes skills install owner/morning-brief
# → Blueprint detected. Run /suggestions to schedule or dismiss.

/suggestions           # 查看待处理的建议
/suggestions accept 1  # 创建定时任务
/suggestions dismiss 1 # 忽略
```

---

## 十三、外部 Skill 目录

如果你在 Hermes 之外维护 skills（如共享的 `~/.agents/skills/` 目录），可以让 Hermes 也扫描这些目录：

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - ~/.agents/skills
    - /home/shared/team-skills
    - ${SKILLS_REPO}/skills
```

行为规则：
- **本地优先**：同名 skill，本地版本优先
- **完整集成**：外部 skills 出现在系统提示词索引、斜杠命令中
- **可写则可改**：如果外部目录对 Hermes 可写，Agent 的 skill 更新可以修改其中的文件
- **不存在的路径被静默跳过**

---

## 十四、发布 Skills

### 发布到 Skills Hub

```bash
hermes skills publish skills/my-skill --to github --repo owner/repo
```

### 创建自定义 tap

```bash
hermes skills tap add owner/repo
```

用户可通过以下方式安装：
```bash
hermes skills search deploy
hermes skills install owner/repo/skills/my-workflow
```

### 安装后验证

```bash
hermes skills list | grep my-skill
hermes skills search my-skill
```

---

## 十五、Agent 自创建 Skills

Hermes 可以通过 `skill_manage` 工具创建、更新和删除自己的 skills——这是 Agent 的**程序性记忆**。

### Agent 创建 Skill 的时机

- 成功完成复杂任务后（5+ 次工具调用）
- 遇到错误/死路并找到可行路径时
- 用户纠正了其方法时
- 发现了非平凡的工作流时

### Agent 管理 Skill 的操作

| 操作 | 用途 | 关键参数 |
|---|---|---|
| `create` | 从头创建新 skill | `name`、`content`（完整 SKILL.md）、可选 `category` |
| `patch` | 针对性修复（**推荐更新方式**） | `name`、`old_string`、`new_string` |
| `edit` | 重大结构性重写 | `name`、`content`（完整 SKILL.md 替换） |
| `delete` | 完全删除一个 skill | `name` |
| `write_file` | 添加/更新支持文件 | `name`、`file_path`、`file_content` |
| `remove_file` | 删除支持文件 | `name`、`file_path` |

> `patch` 是更新的首选方式——比 `edit` 更省 token，因为工具调用中只包含变更的文本。

---

## 参考资料

- [Hermes Agent Skills System 官方文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- [Working with Skills 指南](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)
- [Creating Skills 开发指南](https://hermes-agent.nousresearch.com/docs/developer-guide/creating-skills)
- [Agent Skills 开放标准 (agentskills.io)](https://agentskills.io)
- [Hermes Agent GitHub 仓库](https://github.com/NousResearch/hermes-agent)
