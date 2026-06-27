---
name: report-generator
description: "Generate professional academic PDF reports from paper search results. Use when the user asks to create a report, generate PDF, export results, or produce a formatted document from paper searches — supports cover page, paper lists, analysis, and references in standard academic format."
version: 1.0.0
author: agent-scholar
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [academic, report, pdf, generation, formatting]
    category: my-category
required_environment_variables: []
---

# Report Generator — 学术论文报告生成器

将 paper_search.py 检索到的论文数据生成专业的学术 PDF 报告，包含封面页、检索概况、核心论文列表、研究趋势分析和参考文献。

## When to Use

当用户提出以下需求时激活：
- "帮我生成论文检索报告"
- "创建PDF报告"、"Generate PDF report"
- "导出检索结果"、"Export search results"
- "制作文献综述报告"、"Create literature review report"
- "生成正式的学术论文列表"

## Quick Reference

| 需求 | 操作 |
|---|---|
| 生成PDF报告 | `python generate_report.py --input papers.json --output report.pdf` |
| 生成Markdown报告 | `--format markdown --output report.md` |
| 查看示例 | 先用 paper_search.py 检索，然后用 generate_report.py 生成报告 |

## Procedure

### Step 1: 确认输入数据

确保已经通过 paper_search.py 生成了 JSON 格式的检索结果：

```bash
# 示例：先执行论文检索
python ${HERMES_SKILL_DIR}/../paper-search/scripts/paper_search.py \
  --topic "machine learning in education" \
  --time-range 3y \
  --max-results 10 \
  --output-format json \
  --output papers.json
```

### Step 2: 生成报告

使用 generate_report.py 生成报告：

```bash
# 生成 PDF 报告
python ${HERMES_SKILL_DIR}/scripts/generate_report.py \
  --input papers.json \
  --output report.pdf

# 或生成 Markdown 报告
python ${HERMES_SKILL_DIR}/scripts/generate_report.py \
  --input papers.json \
  --output report.md \
  --format markdown
```

### Step 3: 展示结果

报告生成完成后，告知用户：

```
✅ 学术报告已生成

📄 报告内容：
- 封面页（检索主题、时间、数据源）
- 检索概况（检索参数、结果统计）
- 核心论文列表（完整论文信息）
- 研究趋势分析（年份分布、数据源分布）
- 参考文献（GB/T 7714 格式）

📊 统计信息：
- 论文总数：XX 篇
- 数据源：Semantic Scholar, arXiv, CrossRef
- 时间范围：2021-06-28 至 2024-06-28
```

### Step 4: 交付报告

提供报告文件路径，并说明用途：

- **文献综述撰写**：可直接用于论文的文献综述部分
- **课题调研**：作为开题报告的附件
- **学术分享**：打印后用于学术讨论
- **数据备份**：保存检索结果供后续参考

## Report Structure

生成的 PDF 报告包含以下标准化章节：

### 1. 封面页 (Cover Page)
- 报告标题（基于检索主题）
- 检索主题、检索时间、文献数量
- 数据源信息
- 生成机构：Hermes Agent 学术检索系统

### 2. 检索概况 (Search Summary)
- 检索主题和查询语句
- 筛选条件（时间范围、文献类型等）
- 数据源覆盖范围
- 结果统计（文献数量、来源分布）

### 3. 核心论文列表 (Core Papers List)
按优先级排序，每篇论文包含：
- 论文标题
- 作者列表（前5位，如超过显示总数）
- 发表年份
- 期刊/会议名称
- DOI 链接
- 引用量（如有）
- 摘要（前500字）
- 原始URL

### 4. 研究趋势分析 (Research Trend Analysis)
- 年度发文量分布（表格形式）
- 数据源分布统计
- 研究洞察（最新研究年份、主要数据源）

### 5. 参考文献 (References)
按 GB/T 7714-2015 格式排序输出所有论文，格式：
```
[1] 作者. 论文标题. 期刊名, 年份. DOI: xxxxx
[2] 作者. 论文标题. 期刊名, 年份. DOI: xxxxx
```

## Data Requirements

### 输入格式

generate_report.py 接受 paper_search.py 输出的 JSON 格式文件，必须包含以下字段：

```json
{
  "status": "success",
  "query": "search query string",
  "total_found": 10,
  "sources_used": ["Semantic Scholar", "arXiv"],
  "papers": [
    {
      "title": "Paper Title",
      "authors": ["Author1", "Author2"],
      "year": 2023,
      "journal": "Journal Name",
      "doi": "10.xxxx/xxxxx",
      "citationCount": 100,
      "abstract": "Abstract text...",
      "url": "https://...",
      "source": "Semantic Scholar"
    }
  ],
  "filters_applied": {
    "time_range": {
      "start_date": "2021-06-28",
      "end_date": "2024-06-28"
    }
  },
  "timestamp": "2024-06-28T10:30:45.123Z"
}
```

## Parameters

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | ✅ | 无 | 输入 JSON 文件路径（来自 paper_search.py） |
| `--output` | ✅ | 无 | 输出报告文件路径 |
| `--format` | ❌ | `pdf` | 输出格式（pdf/markdown） |

## Output Formats

### PDF 格式 (默认)
- **优点**：专业排版、适合打印和提交、符合学术规范
- **要求**：安装 reportlab 库（`pip install reportlab`）
- **特点**：
  - A4 纸张，页边距 2cm
  - 学术蓝配色方案
  - 自动分页和页码
  - 支持超链接（DOI、URL）

### Markdown 格式
- **优点**：无需额外依赖、可编辑、兼容性强
- **要求**：无
- **特点**：
  - 结构清晰、易于阅读
  - 可导入 Word/LaTeX
  - 适合后续编辑和扩展

## Requirements

### Python 依赖

**PDF 生成**（推荐）：
```bash
pip install reportlab
```

**Markdown 生成**（无额外依赖）：
- 使用 Python 标准库

### 中文支持

**Windows**：
- 系统自带字体：SimSun（宋体）、SimHei（黑体）、Microsoft YaHei
- 无需额外安装

**Linux**：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei

# 或安装 Noto 字体
sudo apt-get install fonts-noto-cjk
```

**macOS**：
- 系统自带字体：PingFang、STHeiti
- 无需额外安装

## Pitfalls

### reportlab 未安装
如果用户未安装 reportlab，PDF 生成会失败。
**修复**：
1. 提示用户安装：`pip install reportlab`
2. 或降级使用 Markdown 格式：`--format markdown`

### 输入 JSON 格式错误
如果输入文件不是有效的 JSON 或缺少必需字段，会生成失败。
**修复**：
1. 检查输入文件是否来自 paper_search.py
2. 确认 JSON 包含 `status: "success"` 字段
3. 确认 `papers` 数组不为空

### 中文显示问题
在 Linux 上可能缺少中文字体，导致中文显示为方块。
**修复**：
1. 安装中文字体（见"中文支持"部分）
2. 或使用 Markdown 格式作为替代

### PDF 文件过大
如果论文数量过多（>50篇），PDF 文件可能很大。
**修复**：
1. 调整 paper_search.py 的 `--max-results` 参数
2. 或分批生成报告（如按年份分别生成）

## Complete Workflow

完整的论文检索 + 报告生成工作流：

```bash
# 步骤1：执行论文检索
python ${HERMES_SKILL_DIR}/../paper-search/scripts/paper_search.py \
  --topic "人工智能在医学影像中的应用" \
  --keywords "AI,medical imaging,deep learning" \
  --time-range 3y \
  --max-results 15 \
  --sort-by citation_count \
  --output-format json \
  --output medical_ai_papers.json

# 步骤2：生成 PDF 报告
python ${HERMES_SKILL_DIR}/scripts/generate_report.py \
  --input medical_ai_papers.json \
  --output medical_ai_report.pdf

# 步骤3：（可选）生成 Markdown 版本供后续编辑
python ${HERMES_SKILL_DIR}/scripts/generate_report.py \
  --input medical_ai_papers.json \
  --output medical_ai_report.md \
  --format markdown
```

**输出**：
- `medical_ai_papers.json` — 原始检索数据
- `medical_ai_report.pdf` — 专业学术报告（可直接打印或提交）
- `medical_ai_report.md` — Markdown 版本（可导入 Word 或 LaTeX）

## Verification

确认 skill 工作正常的测试步骤：

```bash
# 1. 先执行论文检索
python ${HERMES_SKILL_DIR}/../paper-search/scripts/paper_search.py \
  --topic "machine learning" \
  --time-range 3y \
  --max-results 5 \
  --output-format json \
  --output test_papers.json

# 2. 生成 PDF 报告
python ${HERMES_SKILL_DIR}/scripts/generate_report.py \
  --input test_papers.json \
  --output test_report.pdf

# 3. 验证输出文件
ls -la test_report.pdf
```

**预期结果**：
- `test_papers.json` 包含有效的检索结果
- `test_report.pdf` 文件大小 > 0
- 打开 PDF 文件，显示专业排版的内容

## Integration with LaTeX

如需将报告内容导出为 LaTeX 格式（用于论文写作）：

1. 先生成 Markdown 版本
2. 使用 Pandoc 转换为 LaTeX：
```bash
pandoc report.md -o report.tex --standalone
```
3. 在 LaTeX 中进一步编辑和格式化

## Extensions

### 未来可扩展功能

1. **图表生成**：
   - 年度发文量趋势图（折线图）
   - 高频关键词共现网络（知识图谱）
   - 核心作者与机构分布图

2. **高级分析**：
   - 自动提取研究方法和结论
   - 识别研究热点和空白
   - 生成研究建议和未来方向

3. **格式导出**：
   - LaTeX 格式（用于学术论文）
   - Word 格式（docx）
   - PowerPoint 格式（学术汇报）

4. **模板定制**：
   - 支持自定义报告模板
   - 机构Logo和品牌信息
   - 多语言支持（中英文报告）

5. **文献管理集成**：
   - 导出 BibTeX 格式
   - 生成 Zotero 可导入文件
   - EndNote 格式兼容
