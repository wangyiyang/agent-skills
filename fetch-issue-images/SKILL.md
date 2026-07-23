---
name: fetch-issue-images
description: 从 GitHub Issue 中提取并下载截图/附件图片。当用户要求查看 Issue 里的截图、分析 Issue 附图、下载 Issue 附件时使用。核心原理：通过 `gh api` 的 `body_html` 响应（`Accept: application/vnd.github.html+json`）获取 CDN 直链（`private-user-images.githubusercontent.com`），绕过 `github.com` 直连限制。
---

# GitHub Issue 图片获取 Skill

## 前提

- `gh` CLI 已安装并已登录（`gh auth status` 验证）
- 目标 Issue 所在仓库可在本机用 `gh` 访问（有读取权限）

## 核心命令

```bash
# 获取 Issue 正文 HTML（含 CDN 签名 URL）
gh api repos/{owner}/{repo}/issues/{number} \
  --jq '.body_html' \
  -H "Accept: application/vnd.github.html+json"
```

## 工作原理

GitHub Issue 正文中的 `<img>` 标签直接引用 `github.com/user-attachments/assets/<uuid>`。
如果 `github.com` 不可达（如国内网络环境被墙），直链下载会超时/失败。

GitHub REST API 的 `body_html` 响应（media type `application/vnd.github.html+json`）返回的是
**经过服务端渲染的 HTML**，其中的图片 `src` 会被替换为 `private-user-images.githubusercontent.com`
CDN 域名 + JWT 签名临时 URL，该域名在国内网络通常可达。

## 标准流程

### 1. 提取图片 URL

```bash
# 单个 Issue
URL=$(gh api repos/{owner}/{repo}/issues/{number} \
  --jq '.body_html' \
  -H "Accept: application/vnd.github.html+json" 2>/dev/null \
  | grep -oP 'src="https://[^"]*\.png[^"]*"' \
  | sed 's/src="//;s/"//')

# 取第一张图
echo "$URL" | head -1
```

### 2. 下载图片

```bash
curl -sL -o image.png "$URL"
```

### 3. 批量下载 Issue 正文所有图片

```bash
# 目标：从指定 Issue 中将所有截图下载到本地
download_issue_images() {
  local owner=$1 repo=$2 number=$3 dir=${4:-.}
  mkdir -p "$dir"

  gh api "repos/$owner/$repo/issues/$number" \
    --jq '.body_html' \
    -H "Accept: application/vnd.github.html+json" 2>/dev/null \
    | grep -oP 'src="https://[^"]*(\.png|\.jpg|\.jpeg|\.gif|\.webp)[^"]*"' \
    | sed 's/src="//;s/"//' \
    | cat -n \
    | while read idx url; do
        ext=$(echo "$url" | grep -oP '\.(png|jpg|jpeg|gif|webp)')
        filename="${dir}/${number}_${idx}${ext}"
        echo "Downloading [$idx] $filename ..."
        curl -sL -o "$filename" "$url" || echo "  FAILED: $url"
      done
  echo "Done. $(ls "$dir"/*.png "$dir"/*.jpg 2>/dev/null | wc -l) images saved to $dir"
}
```

### 4. 批量分析多个 Issue

```bash
analyze_issue_images() {
  local owner=$1 repo=$2 dir=$3
  shift 3
  local numbers=("$@")
  mkdir -p "$dir"

  for num in "${numbers[@]}"; do
    echo "=== Issue #$num ==="
    local urls
    urls=$(gh api "repos/$owner/$repo/issues/$num" \
      --jq '.body_html' \
      -H "Accept: application/vnd.github.html+json" 2>/dev/null \
      | grep -oP 'src="https://[^"]*(\.png|\.jpg|\.jpeg|\.gif|\.webp)[^"]*"' \
      | sed 's/src="//;s/"//')

    echo "$urls" | cat -n | while read idx url; do
      local ext=$(echo "$url" | grep -oP '\.(png|jpg|jpeg|gif|webp)')
      curl -sL -o "${dir}/${num}_${idx}${ext}" "$url" && echo "  [${idx}] OK" || echo "  [${idx}] FAILED"
    done
  done

  echo "---"
  file "${dir}"/*.png "${dir}"/*.jpg 2>/dev/null
}
```

## JWT 有效期说明

`private-user-images.githubusercontent.com` 的签名 URL 内置 JWT token，有效期约 **5 分钟**。
- 提取 URL 后应尽快下载
- 如果下载 401 失败（token 过期），重新执行一次提取步骤获取新 URL

## 适用场景

1. **Issue 里的截图需要下载分析**（UI BUG、设计稿对比）
2. **`github.com` 不可达**（如国内网络），但 `api.github.com` 可通
3. **批量提取多个 Issue 的附件**（如 BUG 清单汇总分析）

## 注意事项

- 签名 URL 中的 JWT 有过期时间，长耗时批量下载时可能需要重新提取
- 该接口返回的 `body_html` 仅包含 Issue 正文中的图片，Issue 评论中的图片需通过 Comments API 单独获取
- 本方法依赖 GitHub REST API，需在仓库目录或有 `-R owner/repo` 参数时执行

## 参考资料

- [GitHub Issue REST API](https://docs.github.com/en/rest/issues/issues)
- [GitHub API Media Types](https://docs.github.com/en/rest/overview/media-types)
