---
name: agent-interaction-principle-user-constraint-protection
description: Agent must never modify user parameters without explicit permission. Always ask user first when zero results are returned.
metadata: 
  node_type: memory
  type: feedback
  project: agent-scholar
  originSessionId: f07c9d84-c2c4-4175-a7f9-62afaf97fc0c
---

# Agent Interaction Principle: User Constraint Protection

## Issue Description

When user requests "近一年的人工智能研究成果" (AI research in the past year), the Agent should:
1. Search with the exact 1-year time range
2. If zero results found → **INFORM user and ASK for permission to expand**
3. **NEVER** auto-expand to 3-5 years without user consent

## Incorrect Behavior (What happened)

```
User: "检索近一年的AI论文"
Agent: [Searching with 1y] → 0 results → [Auto-change to 5y] → Return results
Output: "时间范围筛选为近一年...但当前返回的论文年份集中在2021-2024，未满足筛选条件。我将改用近3年重新检索"
```

## Correct Behavior (What should happen)

```
User: "检索近一年的AI论文"
Agent: [Searching with 1y] → 0 results → Inform user
Agent: "⚠️ 近一年内未找到相关论文。是否扩大时间范围到3年或5年？"
User: "改为5年"
Agent: [Searching with 5y] → Return results
```

## Why This Matters

1. **User Intent**: User specified "近一年" for a reason (e.g., latest research only)
2. **Transparency**: User has right to know when their constraints cannot be met
3. **Control**: User may prefer "no results" over "older papers"
4. **Trust**: Autonomy violations undermine user trust in Agent

## Implementation Guidelines

### When Zero Results Are Returned

**DO NOT**:
- ❌ Auto-expand time range
- ❌ Auto-change keywords
- ❌ Auto-modify ANY user-specified parameter

**DO**:
- ✅ Inform user: "⚠️ 使用指定参数未找到相关论文"
- ✅ Show what was tried: "时间范围: 2025-07-01至2026-07-01, 关键词: xxx"
- ✅ Suggest options: "建议扩大时间范围到3年或5年，或调整关键词"
- ✅ Ask for permission: "是否需要调整参数？请说明您的偏好"

### Template Response

```
📊 检索结果：0篇论文

🔍 检索参数：
- 主题：人工智能
- 时间范围：近1年 (2025-07-01 至 2026-07-01)
- 关键词：AI, machine learning
- 数据源：Semantic Scholar, arXiv, CrossRef

💡 可能的原因：
- 时间范围过窄
- 关键词过于具体
- 该领域近期发表论文较少

🎯 建议的调整方案：
1. 扩大时间范围：3年 / 5年 / 10年
2. 调整关键词：更通用的术语
3. 更换检索策略

❓ 请选择：
- "扩大到3年" / "扩大到5年" / "不改，我要最新的" / "调整关键词为xxx"
```

## Affected Skills

This principle applies to ALL skills with user-specified constraints:

1. **paper-search**: time_range, keywords, domain, max_results
2. **paper-email-service**: All paper-search parameters
3. **report-generator**: Input from paper-search must respect user constraints

## Code Fix Required

Update `paper-email-service/SKILL.md` Pitfalls section to explicitly state:

```markdown
### 检索无结果
**问题**：关键词过于具体或时间范围过窄
**修复原则 - 用户约束保护**：
- ❌ **绝对禁止**擅自修改用户指定的参数
- ✅ **必须**告知用户检索结果为0
- ✅ **必须**说明使用的检索参数
- ✅ **必须**询问用户是否调整参数
- ✅ **必须**等待用户明确指示后再执行
```

## Related Issues

This is part of broader Agent interaction design:
- [[agent-communication-transparency]] (to be created)
- [[user-control-and-autonomy]] (to be created)

## Impact

- **Severity**: HIGH - Violates core user trust
- **Frequency**: COMMON - Happens when time ranges are restrictive
- **User Impact**: HIGH - Users receive irrelevant/outdated papers without knowing why
