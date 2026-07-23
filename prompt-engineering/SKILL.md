---
name: prompt-engineering
description: Use this skill when writing or refining prompts, commands, hooks, skills, sub-agent prompts, or other LLM instructions, including prompt optimization, reusable templates, and production prompt design.
---

# Prompt Engineering

将模糊需求压缩成稳定、可复用、可验证的 LLM 指令资产。默认假设模型已经足够聪明，只补充它无法稳定推断的内容。

## 何时使用

- 编写或修改 `prompt`
- 编写 `command`、`hook`、`skill`
- 设计 sub-agent prompt
- 优化生产级模板的稳定性、成本或可维护性
- 为同一任务建立可测试、可复用的提示词结构

## 默认工作流

1. 先定义目标行为：模型最终必须产出什么，什么算失败。
2. 再定义约束边界：允许自由发挥的部分，和绝不能越界的部分。
3. 选择合适的 prompt 结构：直接指令、few-shot、模板、校验回路。
4. 写出最小可用版本，不先堆太多背景。
5. 用代表性输入验证，再按失败模式增量补强。

## 设计规则

### 1. 先结果，后约束，最后示例

推荐结构：

```text
[角色/上下文]
[任务目标]
[硬约束]
[输入数据]
[输出格式]
[示例]
```

只有当示例明显提升稳定性时再加示例。

### 2. 上下文窗口是公共资源

- 删除模型本来就知道的解释
- 删除不会改变输出的背景
- 把稳定规则放前面，把可变输入放后面
- 大型知识不要塞进主 prompt，拆到引用材料

### 3. 约束强度要匹配风险

- 高自由度：适合代码评审、头脑风暴、方案比较
- 中自由度：适合模板化文案、结构化分析、报告生成
- 低自由度：适合迁移脚本、发布流程、安全检查

风险越高，指令越具体；风险越低，给模型越多裁量空间。

### 4. 用失败模式驱动迭代

不要抽象地“优化 prompt”，要记录：

- 输出太散，还是太死
- 漏字段，还是格式不稳
- 幻觉，还是忽略上下文
- 延迟高，还是 token 成本高

每次只修一类失败模式，避免一轮改动引入多个变量。

### 5. 把 prompt 当成可维护资产

- 给模板命名，并说明用途
- 记录为什么有这条约束
- 如果 prompt 很长，拆成主模板 + references
- 如果存在多个场景，按场景拆分而不是堆在一个文件里

## 输出要求

使用本 skill 时，默认交付物应包含以下内容中的大部分：

- 修订后的 prompt/skill/command 文本
- 设计理由，重点说明新增或删除了哪些约束
- 推荐的验证样例或测试用例
- 已知边界：什么场景仍可能失败

## 何时读取附加参考

- 需要 few-shot、模板化、校验回路时：看 `references/core-patterns.md`
- 需要编写 agent/skill/command/hook 时：看 `references/agent-prompting.md`
- 需要用更强的行为约束推动执行一致性时：看 `references/persuasion-principles.md`

## 边界

- 不为了“显得专业”而增加冗长背景
- 不把 persuasion 技巧用于误导用户或制造虚假紧迫感
- 不默认加入思维链展示，除非任务真的需要显式推理过程
