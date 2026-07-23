# Persuasion Principles

## 用途

当你编写的是“纪律型 prompt”而不是“普通说明型 prompt”时，可以用更明确的行为约束提升执行一致性。目标是减少漏步和拖延，不是操控用户。

## 常用原则

### Authority

适合安全要求、发布流程、测试要求这类不能模糊执行的场景。

示例：

```markdown
Run the verification steps before returning. Do not skip them.
```

### Commitment

适合多步骤工作流，需要 agent 先声明、再执行。

示例：

```markdown
Before editing files, state which files you will change and why.
```

### Scarcity

适合强调时序依赖，避免“之后再做”。

示例：

```markdown
Immediately validate the change after implementation. Do not defer testing.
```

### Social Proof

适合建立稳定的团队规范，但不要夸大。

示例：

```markdown
In this repo, unverified changes are treated as incomplete work.
```

### Unity

适合协作型 prompt，强调共同目标，而不是上下级命令关系。

示例：

```markdown
We are optimizing the same production workflow. Surface tradeoffs directly.
```

## 不建议默认使用

### Reciprocity

通常没必要，容易显得人为设计感过强。

### Liking

不适合拿来提升执行率，容易诱发迎合，而不是客观判断。

## 组合建议

| 场景 | 推荐 | 避免 |
| --- | --- | --- |
| 纪律型 skill | Authority + Commitment | Liking |
| 协作型 skill | Unity + Commitment | 过度 Authority |
| 参考文档 | Clarity only | 所有 persuasion 堆叠 |

## 伦理边界

- 不制造虚假紧迫感
- 不为了“提高服从度”而隐藏风险
- 不用 persuasion 替代清晰的任务定义

判断标准：

如果用户完整看到这套设计，也会认为它服务于任务本身，而不是服务于操控，那它通常是可接受的。
