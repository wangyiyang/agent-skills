# Core Patterns

## Few-Shot

当目标输出格式不稳定，或者模型容易忽略边界条件时，用 2 到 5 个高质量示例比长篇解释更有效。

适用场景：

- 结构化抽取
- 固定格式输出
- 边界条件多的分类任务

示例：

```markdown
Extract key information from support tickets.

Input: "My login doesn't work and I keep getting error 403"
Output: {"issue": "authentication", "error_code": "403", "priority": "high"}

Input: "Feature request: add dark mode to settings"
Output: {"issue": "feature_request", "error_code": null, "priority": "low"}

Now process:
"Can't upload files larger than 10MB, getting timeout"
```

规则：

- 示例必须覆盖你最担心的失败模式
- 示例风格必须和目标任务一致
- 示例越多越好是错的，够用即可

## Prompt Template

当同一模式会被多次复用时，不要复制粘贴 prompt，直接抽成模板。

示例：

```text
You are a {role}.

Task:
{task}

Constraints:
{constraints}

Input:
{input}

Output format:
{format}
```

规则：

- 固定骨架放模板
- 频繁变化的部分参数化
- 参数命名要直接反映业务含义

## Validation Loop

当任务高风险或高成本时，让模型在输出后做一次自检。

示例：

```markdown
Draft the answer.

Then verify:
1. It directly answers the user's question.
2. It uses only provided context.
3. It follows the required format.
4. It states uncertainty where evidence is missing.

If any check fails, revise once before returning the final answer.
```

适用场景：

- 基于上下文回答
- 严格格式输出
- 高可见度内容生产

注意：

- 自检项不宜太多，3 到 5 条足够
- 自检标准必须可判断，避免抽象表述

## Progressive Disclosure

先写最短可用 prompt，再逐步增加约束：

1. 直接指令
2. 加输出格式
3. 加硬约束
4. 加示例
5. 加校验回路

只有当前一层无法稳定达标时，才进入下一层。
