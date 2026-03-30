---
name: agree-and-execute
description: Continue with the previously proposed plan after the user gives brief approval such as "好的", "继续", "按这个来", "请执行", "同意", or replies with option numbers like "1", "2", or "1 & 2" to approve previously proposed next steps. Use when the user is not asking for a new plan, but is approving the next concrete actions or explicitly mentions agree-and-execute.
---

# Agree And Execute

Treat brief approval from the user as permission to continue the already discussed next steps. Do not restate the whole plan unless the scope has changed or the prior proposal was ambiguous.

## When active

Use this skill when the user response is mainly approval, for example:

- "好的"
- "继续"
- "按这个来"
- "同意你的后续建议，请推动执行"
- "请直接做"
- "1"
- "1 & 2"

Do not use this skill when the user is introducing a new task, changing constraints, or partially disagreeing.

## Execution rules

1. Reconstruct the most recent concrete plan or recommendation from the conversation.
2. Continue directly into execution instead of asking the user to repeat approval.
3. If multiple next steps were proposed, choose the one on the critical path first.
4. If the prior proposal contained a risky assumption, surface that single assumption briefly and then execute if it is still a reasonable default.
5. If the user approval is ambiguous because there were multiple incompatible proposals, ask one short clarifying question instead of guessing.

## Response style

- Acknowledge the approval implicitly by acting.
- Prefer action over explanation.
- Keep commentary short and execution-focused.
- Avoid rehashing options that were already decided.

## Safety boundary

- Do not expand scope beyond the previously discussed plan.
- Do not interpret a generic "好的" as approval for destructive actions that were never proposed.
- If approval timing is unclear because the conversation changed topic, confirm before acting.
