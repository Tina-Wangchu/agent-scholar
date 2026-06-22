# AI Agent 快速入门指南（2-3天）

> 🎯 **目标**：快速掌握 AI Agent 核心概念，能够动手构建简单的 Agent
>
> ⏱️ **时间**：2-3天快速入门，后续边做边学
>
> 📚 **方式**：核心概念 + 实践项目 + 边做边学资源

---

## 📋 学习路径（2-3天）

```
Day 1 上午：核心概念速览
  ├── AI Agent 是什么？
  ├── 四大核心组件
  └── 工作原理

Day 1 下午：LangChain 快速上手
  ├── 环境搭建
  ├── 创建第一个 Agent
  └── 添加工具

Day 2 全天：实践项目
  ├── 文档问答 Agent
  ├── 代码实现
  └── 测试运行

Day 3 及以后：边做边学
  ├── 推荐项目方向
  ├── 学习资源
  └── 实践方法
```

---

## 🚀 Day 1 上午：核心概念速览（2-3小时）

### 1. AI Agent 是什么？

**一句话解释：**
AI Agent = LLM（大脑）+ Tools（手脚）+ Memory（记忆）+ Planning（规划）

**与传统聊天机器人的区别：**

| 聊天机器人 | AI Agent |
|-----------|----------|
| 只能聊天 | 可以执行任务 |
| 无状态 | 记住上下文 |
| 被动回答 | 主动规划行动 |
| 只用文本 | 可以调用工具 |

**实际例子：**
```
用户：帮我查北京天气

聊天机器人：
"我无法查询实时信息，建议您查看天气应用。"

AI Agent：
1. 思考：需要调用天气API
2. 行动：调用天气工具
3. 观察：获得"北京晴15度"
4. 回答："北京今天晴天，温度15度，适合穿薄外套。"
```

### 2. 四大核心组件

#### State（状态）- 记忆上下文

**为什么需要：**
```
第1轮：用户说"我喜欢Python"
第2轮：用户问"推荐什么编程语言？"

如果没有状态管理，Agent 就不知道"推荐"是基于用户的偏好。
有了状态，Agent 会记住："哦，用户喜欢Python，我应该推荐Python相关的语言。"
```

#### Tools（工具）- 执行能力

**常见工具类型：**
- 🔍 **搜索工具**：Google Search, Bing Search
- 🧮 **计算工具**：Python 代码执行
- 📊 **数据工具**：数据库查询、API 调用
- 📄 **文档工具**：PDF 读取、向量搜索

**为什么需要工具：**
```
LLM 本身：
- 知识截止到训练时间
- 无法访问实时数据
- 无法执行实际操作

LLM + Tools：
- 可以获取实时信息
- 可以处理复杂数据
- 可以执行实际任务
```

#### Planning（规划）- 任务分解

**示例：**
```
用户任务：策划一次去东京的旅行

Agent 规划：
步骤1：查询最佳旅游季节
步骤2：搜索热门景点
步骤3：查询机票价格
步骤4：制定行程计划
步骤5：预算估算
```

#### Memory（记忆）- 经验积累

**记忆类型：**
- **短期记忆**：当前对话（"我们刚才讨论了X"）
- **长期记忆**：持久化存储（"用户喜欢Python"）

### 3. Agent 工作原理（ReAct 模式）

```
┌─────────────────────────────┐
│  Thought（思考）              │
│  "我需要做什么？用什么工具？"  │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  Action（行动）              │
│  "调用天气API查询北京"       │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  Observation（观察）          │
│  "返回：晴天，15度"          │
└──────────┬──────────────────┘
           ↓
    回到思考，继续或结束
```

**完整示例：**
```
用户：查北京天气，然后告诉我适合穿什么

Thought1: 需要查天气，调用 weather_tool
Action1: weather_tool("北京")
Observation1: 晴天，15度

Thought2: 知道温度了，判断穿衣建议
Action2: 不需要工具，基于常识
Observation2: 15度适合薄外套

Thought3: 已完成所有任务
Final Answer: 北京晴天15度，适合穿薄外套或长袖
```

### 核心概念检查清单

- [ ] 理解 AI Agent 和聊天机器人的区别
- [ ] 知道四大核心组件：State、Tools、Planning、Memory
- [ ] 理解 ReAct 工作模式（思考→行动→观察）
- [ ] 知道为什么需要工具

---

## 🛠️ Day 1 下午：LangChain 快速上手（3-4小时）

### 环境搭建（30分钟）

#### 1. 安装依赖

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 安装 LangChain 和相关包
pip install langchain langchain-openai
pip install langchain-community
pip install openai

# 可选：后续项目需要
pip install chromadb pypdf python-dotenv
```

#### 2. 设置 API 密钥

**方法1：环境变量（推荐）**
```bash
# macOS/Linux
export OPENAI_API_KEY="your-api-key"

# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key"
```

**方法2：.env 文件**
```bash
# 创建 .env 文件
echo "OPENAI_API_KEY=your-api-key" > .env
```

### 创建第一个 Agent（1小时）

#### Hello World Agent

```python
# hello_agent.py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

# 1. 定义一个简单工具
def get_current_time(query: str) -> str:
    """获取当前时间"""
    from datetime import datetime
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"

# 2. 创建工具列表
tools = [
    Tool(
        name="get_time",
        func=get_current_time,
        description="获取当前时间。输入可以是任意字符串。"
    )
]

# 3. 创建 LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# 4. 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),  # Agent 思考过程
])

# 5. 创建 Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 6. 创建 Executor（管理状态）
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 显示思考过程
    max_iterations=5
)

# 7. 运行
if __name__ == "__main__":
    print("=" * 60)
    print("我的第一个 Agent")
    print("=" * 60)

    # 测试
    result = executor.invoke({"input": "现在几点了？"})
    print(f"\n回答：{result['output']}")
```

**运行：**
```bash
python hello_agent.py
```

**你会看到类似输出：**
```
> Entering new AgentExecutor chain...

Thought: 用户问现在几点，我需要调用 get_time 工具
Action: get_time
Action Input: ""

Observation: 当前时间：2026-06-17 14:30:25

Thought: 我已经有了当前时间，可以回答用户
Final Answer: 现在是 2026年6月17日 14:30:25

> Finished chain.
```

### 添加更多工具（1-2小时）

#### 增强版 Agent

```python
# enhanced_agent.py
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import requests

# 1. 定义多个工具

def search_engine(query: str) -> str:
    """模拟搜索引擎"""
    # 实际应用中可以使用真实搜索API
    return f"关于'{query}'的搜索结果：这是一些示例信息..."

def calculator(expression: str) -> str:
    """计算器"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{str(e)}"

def get_weather(city: str) -> str:
    """查询天气（模拟）"""
    # 实际应用中使用真实天气API
    weather_data = {
        "北京": "晴天，15度",
        "上海": "多云，20度",
        "深圳": "晴天，28度"
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

# 2. 创建工具列表
tools = [
    Tool(
        name="get_time",
        func=lambda x: __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        description="获取当前时间"
    ),
    Tool(
        name="search",
        func=search_engine,
        description="搜索互联网信息。输入为搜索关键词。"
    ),
    Tool(
        name="calculator",
        func=calculator,
        description="执行数学计算。输入为数学表达式，如 '2+2' 或 '10*5'。"
    ),
    Tool(
        name="weather",
        func=get_weather,
        description="查询城市天气。输入为城市名，如 '北京'、'上海'。"
    )
]

# 3. 创建 LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# 4. 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手，可以使用各种工具来帮助用户。"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 5. 创建 Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 6. 创建 Executor
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
)

# 7. 测试多个场景
if __name__ == "__main__":
    print("=" * 60)
    print("多功能 Agent 测试")
    print("=" * 60)

    test_cases = [
        "现在几点了？",
        "帮我查一下北京的天气",
        "计算 365 * 24",
        "搜索 Python 的最新版本"
    ]

    for i, question in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"测试 {i}: {question}")
        print('=' * 60)

        try:
            result = executor.invoke({"input": question})
            print(f"\nAgent 回答：{result['output']}")
        except Exception as e:
            print(f"\n错误：{e}")
```

**运行测试：**
```bash
python enhanced_agent.py
```

### 理解 Agent 的思考过程

当 `verbose=True` 时，你会看到 Agent 的完整思考过程：

```
用户：帮我查北京天气，然后计算2024减去2010

> Entering new AgentExecutor chain...

Thought: 用户问了两个任务，我需要先查天气，再计算

Action: weather
Action Input: "北京"

Observation: 晴天，15度

Thought: 现在我需要计算第二个问题

Action: calculator
Action Input: "2024-2010"

Observation: 计算结果：14

Thought: 两个任务都完成了
Final Answer: 北京今天晴天，温度15度。2024减去2010等于14年。
```

### Day 1 下午检查清单

- [ ] 成功安装所有依赖
- [ ] 设置好 API 密钥
- [ ] 运行了第一个 Agent
- [ ] 理解 Agent 的思考过程（verbose 输出）
- [ ] 成功创建带多个工具的 Agent

---

## 🎯 Day 2：实践项目（1天）

### 项目目标

构建一个**文档问答 Agent**，能够：
1. 加载 PDF 文档
2. 回答文档相关问题
3. 显示答案来源

### 完整代码（可直接使用）

```python
# document_qa_agent.py
"""
文档问答 Agent - Day 2 实践项目
功能：加载PDF文档，回答相关问题
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
import os
from pathlib import Path

# 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_PERSIST_DIR = "./chroma_db"

class DocumentQAAgent:
    def __init__(self):
        """初始化 Agent"""
        # 创建向量存储
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.vectorstore = Chroma(
            collection_name="documents",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )

        # 创建记忆
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # 创建工具
        self.tools = self._create_tools()

        # 创建 LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=OPENAI_API_KEY
        )

        # 创建 Agent
        self.executor = self._create_agent()

    def _create_tools(self):
        """创建工具列表"""
        return [
            Tool(
                name="load_document",
                func=self._load_document,
                description="加载PDF文档到向量数据库。输入为PDF文件路径。"
            ),
            Tool(
                name="search_document",
                func=self._search_document,
                description="在文档中搜索相关内容。输入为搜索查询。"
            )
        ]

    def _load_document(self, file_path: str) -> str:
        """加载文档"""
        try:
            path = Path(file_path)

            if not path.exists():
                return f"文件不存在：{file_path}"

            if path.suffix != ".pdf":
                return f"只支持PDF文件，当前文件：{path.suffix}"

            # 加载PDF
            loader = PyPDFLoader(str(path))
            documents = loader.load()

            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)

            # 添加到向量数据库
            self.vectorstore.add_documents(splits)

            return f"✅ 成功加载文档：{path.name}，共 {len(splits)} 个片段"

        except Exception as e:
            return f"❌ 加载失败：{str(e)}"

    def _search_document(self, query: str) -> str:
        """搜索文档"""
        try:
            # 相似度搜索
            results = self.vectorstore.similarity_search(query, k=3)

            if not results:
                return "未找到相关内容"

            # 格式化结果
            output = []
            for i, doc in enumerate(results, 1):
                content = doc.page_content[:300]
                output.append(f"片段 {i}：\n{content}...\n")

            return "\n".join(output)

        except Exception as e:
            return f"搜索失败：{str(e)}"

    def _create_agent(self):
        """创建 Agent Executor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个文档问答助手。你可以帮助用户：

1. 加载PDF文档
2. 搜索文档内容
3. 回答文档相关问题

请始终基于文档内容回答。如果文档中没有相关信息，明确告知用户。"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=False,  # 设为 True 可以看到思考过程
            max_iterations=5
        )

    def run(self):
        """运行交互循环"""
        print("=" * 60)
        print("📚 文档问答 Agent")
        print("=" * 60)
        print("\n使用说明：")
        print("1. 输入PDF文件路径加载文档")
        print("2. 输入问题查询文档内容")
        print("3. 输入 'quit' 退出\n")

        while True:
            user_input = input("👤 您：").strip()

            if user_input.lower() == 'quit':
                print("再见！")
                break

            if not user_input:
                continue

            try:
                result = self.executor.invoke({"input": user_input})
                print(f"\n🤖 Agent：{result['output']}\n")
            except Exception as e:
                print(f"\n❌ 错误：{e}\n")

def main():
    """主函数"""
    agent = DocumentQAAgent()
    agent.run()

if __name__ == "__main__":
    main()
```

### 使用示例

```bash
# 1. 准备一个测试PDF文件
# 2. 运行 Agent
python document_qa_agent.py

# 3. 交互示例
👤 您：加载 test.pdf
🤖 Agent：✅ 成功加载文档：test.pdf，共 25 个片段

👤 您：这个文档讲了什么？
🤖 Agent：根据文档内容，这个文档主要讲述了...

👤 您：文档中提到了哪些关键概念？
🤖 Agent：从搜索结果来看，文档中提到的关键概念包括...
```

### 测试清单

- [ ] 能够成功加载PDF文档
- [ ] 能够回答文档相关问题
- [ ] 能够显示答案来源
- [ ] 支持多轮对话
- [ ] 优雅处理错误

### Day 2 检查清单

- [ ] 理解项目完整代码
- [ ] 成功运行项目
- [ ] 完成基本测试
- [ ] 代码可以正常工作

---

## 📚 Day 3 及以后：边做边学

### 边做边学的理念

**核心思想：**
- 先动手做，遇到问题再学习
- 通过实际项目驱动学习
- 不追求完美，先让它工作
- 在实践中理解概念

### 推荐项目方向

#### 1. 数据分析助手

**功能：** 上传数据文件，用自然语言查询

```python
# 核心代码示例
@tool
def analyze_data(query: str, file_path: str) -> str:
    """分析数据文件"""
    import pandas as pd

    # 加载数据
    df = pd.read_csv(file_path)

    # 让 LLM 生成分析代码
    code = generate_pandas_code(query, df)

    # 执行代码
    result = execute_code(code, df)

    return result
```

**学习资源：**
- [Pandas 文档](https://pandas.pydata.org/docs/)
- LangChain Data Analysis 教程

#### 2. 多Agent协作系统

**功能：** 多个专门Agent协作完成任务

```python
# 示例：代码生成和审查
from autogen import AssistantAgent

coder = AssistantAgent(
    name="coder",
    system_message="你负责编写代码"
)

reviewer = AssistantAgent(
    name="reviewer",
    system_message="你负责审查代码"
)

# 协作完成编程任务
```

**学习资源：**
- [AutoGen 文档](https://microsoft.github.io/autogen/)
- [Multi-Agent Tutorial](https://www.youtube.com/watch?v=muSam6Yy8lM)

#### 3. 自动化工作流Agent

**功能：** 自动执行重复性任务

```python
# 示例：自动化邮件处理
@tool
def process_email(email_id: str) -> str:
    """处理邮件"""
    # 读取邮件
    email = read_email(email_id)

    # 分类
    category = classify_email(email)

    # 采取行动
    if category == "紧急":
        send_notification(email)
    elif category == "订阅":
        unsubscribe(email)

    return f"已处理：{email.subject}"
```

**学习资源：**
- LangChain Workflow 教程
- Automation 最佳实践

### 实用学习资源

#### 官方文档

**LangChain：**
- [官方文档](https://docs.langchain.com/)
- [Agent 教程](https://python.langchain.ac.cn/docs/tutorials/agents/)
- [快速开始](https://python.langchain.ac.cn/docs/get_started/introduction)

**其他框架：**
- [AutoGen](https://microsoft.github.io/autogen/)
- [TaskWeaver](https://github.com/microsoft/TaskWeaver)

#### 视频教程

**推荐观看：**
1. [Microsoft Generative AI for Beginners](https://www.youtube.com/watch?v=yAXVW-lUINc)
2. [LangChain Tutorial for Beginners](https://www.youtube.com/watch?v=AOQyRiwydyo)
3. [Build Multi-Agent with AutoGen](https://www.youtube.com/watch?v=muSam6Yy8lM)

#### 社区资源

**获取帮助：**
- [LangChain Discord](https://discord.gg/6eadmxEEX2)
- [Stack Overflow - langchain](https://stackoverflow.com/questions/tagged/langchain)
- [GitHub Discussions](https://github.com/langchain-ai/langchain/discussions)

**学习案例：**
- [LangChain Examples](https://github.com/langchain-ai/langchain/tree/master/cookbook)
- [Awesome LangChain](https://github.com/karpathy/awesome-langchain)

### 边做边学的方法

#### 1. 项目驱动学习

**步骤：**
1. 选择一个小项目（2-3天能完成）
2. 列出需要的技能
3. 边做边查，遇到问题学习
4. 完成后总结学到的知识

**示例项目：**
```
项目：构建一个邮件分类Agent

需要学习的技能：
✓ 读取邮件（imaplib 库）
✓ 文本分类（LLM 或传统ML）
✓ 自动操作（发邮件、移动邮件）
✓ LangChain Agent 集成

学习方式：
1. 先查 imaplib 如何使用
2. 实现读取邮件功能
3. 再查如何用 LLM 分类
4. 实现分类功能
5. 最后集成到 Agent 中
```

#### 2. 复制改进学习

**步骤：**
1. 找一个开源项目
2. 复制核心代码
3. 理解每一行
4. 尝试修改和改进

**推荐项目：**
- [LangChain Cookbooks](https://github.com/langchain-ai/langchain/tree/master/cookbook)
- [AutoGen Examples](https://microsoft.github.io/autogen/0.2/docs/examples/)

#### 3. 问题驱动学习

**遇到问题时：**
1. 先尝试自己解决（搜索文档）
2. 在社区提问
3. 记录解决方案
4. 形成自己的知识库

**常用资源：**
- Google 搜索技巧："langchain [问题描述]"
- GitHub Issues 搜索
- Stack Overflow

### 实践建议

#### ✅ 推荐做法

1. **从小项目开始**
   - 第一个项目：2-3天能完成
   - 第二个项目：1周能完成
   - 逐步增加复杂度

2. **记录学习过程**
   ```markdown
   # 项目日志

   ## 2026-06-17
   - 学习了 LangChain 基础
   - 创建了第一个 Agent
   - 遇到问题：API 密钥配置
   - 解决：使用 .env 文件

   ## 2026-06-18
   - 实现了文档问答 Agent
   - 学习了向量数据库
   - 下一步：添加更多功能
   ```

3. **分享和交流**
   - 写技术博客
   - 在 GitHub 分享项目
   - 参与社区讨论

#### ❌ 避免的陷阱

1. **不要试图一次性学完**
   - 知识太多，永远学不完
   - 先学核心，用到什么学什么

2. **不要追求完美代码**
   - 先让它工作
   - 再优化和重构
   - 完美是迭代的产物

3. **不要忽视文档**
   - 官方文档是最好的学习资料
   - 遇到问题先查文档

### 进阶学习路径

**第1个月：**
- 完成 3-5 个小项目
- 熟悉 LangChain 核心功能
- 理解常见模式

**第2-3个月：**
- 深入一个框架（LangChain/AutoGen）
- 学习高级特性（LangGraph, RAG）
- 参与开源项目

**第4-6个月：**
- 构建生产级应用
- 学习部署和监控
- 关注最新发展

---

## 🎯 快速检查清单

### Day 1 完成

- [ ] 理解 AI Agent 核心概念
- [ ] 知道四大组件：State, Tools, Planning, Memory
- [ ] 理解 ReAct 工作模式
- [ ] 成功运行第一个 Agent
- [ ] 理解 Agent 的思考过程

### Day 2 完成

- [ ] 完成文档问答 Agent 项目
- [ ] 能够加载 PDF 文档
- [ ] 能够回答文档相关问题
- [ ] 代码可以正常运行
- [ ] 理解项目完整流程

### Day 3 及以后

- [ ] 选择一个实践方向
- [ ] 开始边做边学
- [ ] 记录学习过程
- [ ] 加入社区交流
- [ ] 持续迭代改进

---

## 🆘 常见问题

### Q1: 没有API密钥怎么办？

**A:** 可以使用本地模型
```bash
# 安装 Ollama
curl https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2

# 在代码中使用
from langchain.llms import Ollama
llm = Ollama(model="llama2")
```

### Q2: 遇到错误怎么办？

**A:**
1. 仔细阅读错误信息
2. 搜索错误信息 + "langchain"
3. 检查 API 密钥配置
4. 查看官方文档的 FAQ 部分

### Q3: 项目做不出来怎么办？

**A:**
1. 降低复杂度，做最小版本
2. 参考开源项目代码
3. 在社区提问
4. 先完成基本功能，再优化

### Q4: 如何判断自己掌握了？

**A:**
- 不看文档能写出简单 Agent
- 能解释 Agent 的工作原理
- 能独立完成一个小项目
- 知道去哪里查答案

---

## 📝 总结

**通过这2-3天的快速入门，您已经：**

1. ✅ 理解了 AI Agent 的核心概念
2. ✅ 掌握了 LangChain 的基本使用
3. ✅ 完成了一个实践项目
4. ✅ 建立了边做边学的习惯

**下一步：**

1. 选择一个项目方向
2. 开始边做边学
3. 在实践中深入理解
4. 加入社区持续成长

**记住：**
- 实践是最好的学习方式
- 不要害怕犯错
- 从小项目开始
- 持续迭代改进

**祝您在 AI Agent 的学习和实践道路上越走越远！** 🚀

---

**文档信息：**
- 创建时间：2026-06-17
- 适用对象：2-3天快速入门
- 后续：边做边学
- 维护者：Claude Code Assistant
