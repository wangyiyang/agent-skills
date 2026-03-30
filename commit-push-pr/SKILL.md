---
name: commit-push-pr
description: Organize current git changes into one or more commits, push the branch to origin, and create a GitHub pull request. Use when the user asks to "提交 PR", "发起 PR", "帮我 commit 并 push", "提交pr", "commit push pr", "帮我开个 PR", or explicitly mentions commit-push-pr.
---

# Commit Push PR

Handle the full git delivery flow from local changes to remote pull request. Prefer a safe, reviewable path and keep commits scoped to one logical change.

## Workflow

1. Confirm repository and branch state.
2. Inspect the diff and decide whether changes should be split into multiple commits.
3. If currently on `main` or `master`, create a topic branch before committing.
4. Stage the appropriate files.
5. Create one or more clear commit messages.
6. Push the branch to `origin`.
7. Create a PR against `main`.
8. Return branch, commit hashes, PR URL, and validation summary.

## Rules

- Follow GitHub Flow: do not push feature work directly to `main` or `master`.
- Prefer Conventional Commits such as `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- Keep unrelated changes out of the same commit.
- If there is a linked issue, include `Fixes #<issue-number>` in the PR body when appropriate.
- If branch naming is not obvious, choose a short descriptive branch name based on the change.

## Checks before writing

- Run `git rev-parse --show-toplevel`.
- Run `git status -sb`.
- Run `git diff`.
- If anything is already staged, run `git diff --staged`.

## Commit and PR behavior

- If changes are already on a non-main branch, reuse it unless the branch is clearly wrong for the task.
- Prefer `gh pr create` when GitHub CLI is available and authenticated.
- If PR creation cannot be completed automatically, provide the compare URL and a ready-to-use title/body draft.

## Output

Report:

- branch name
- commit list with hash and summary
- PR URL
- brief validation or reason no validation was run

## Safety boundary

- Do not rewrite history unless the user explicitly asks.
- Do not sweep unrelated dirty changes into the commit.
- If the base branch is unclear and there is no obvious repository convention, ask one concise question.
