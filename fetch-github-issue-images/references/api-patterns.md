# 获取 Issue 图片的 API 模式参考

## Issue 正文图片

```bash
gh api repos/{owner}/{repo}/issues/{number} \
  --jq '.body_html' \
  -H "Accept: application/vnd.github.html+json"
```

返回的 HTML 中，`<img>` 的 `src` 指向 `private-user-images.githubusercontent.com` CDN。

## Issue 评论图片

Issue 评论中的图片通过 Comments API 获取：

```bash
gh api repos/{owner}/{repo}/issues/{number}/comments \
  --jq '.[] | .body_html' \
  -H "Accept: application/vnd.github.html+json"
```

提取图片 URL 的方式相同：

```bash
gh api repos/{owner}/{repo}/issues/{number}/comments \
  --jq '.[] | .body_html' \
  -H "Accept: application/vnd.github.html+json" 2>/dev/null \
  | grep -oP 'src="https://[^"]*(\.png|\.jpg|\.jpeg|\.gif|\.webp)[^"]*"' \
  | sed 's/src="//;s/"//'
```

## 支持的图片格式

- `.png`（最常见，Issue 粘贴截图默认格式）
- `.jpg` / `.jpeg`
- `.gif`
- `.webp`

## 常见错误处理

| 现象 | 原因 | 解决 |
|------|------|------|
| `curl` 下载返回空文件 | JWT 过期 | 重新提取 URL |
| `gh api` 返回空 | 无 read 权限 / Issue 不存在 | 检查 `gh auth status` 和 Issue 号 |
| `body_html` 无 `<img>` 标签 | Issue 正文未嵌入图片 | 检查 Comments API |
