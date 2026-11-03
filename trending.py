#!/usr/bin/env python3
"""Fetch GitHub Trending and output a Chinese digest in Markdown.

No third-party dependencies. Only the public trending page is read.
Usage:
    python3 trending.py --since daily
    python3 trending.py --since daily --output report.md
"""
import argparse
import html
import re
import sys
import urllib.request
from datetime import date

TRENDING_URL = "https://github.com/trending?since={since}"

# Simple keyword-based categories. Keep it small and readable.
CATEGORIES = [
    ("AI Agent", ["agent", "claude", "copilot", "llm", "chatgpt", "memory", "worktree"]),
    ("开发者工具", ["cli", "browser", "scrap", "git", "tool", "framework", "library"]),
    ("学习资源", ["awesome", "learn", "book", "tutorial", "guide", "course"]),
]


def categorize(name: str, description: str) -> str:
    text = f"{name} {description}".lower()
    for label, keywords in CATEGORIES:
        if any(k in text for k in keywords):
            return label
    return "其他"


def fetch_trending(since: str):
    req = urllib.request.Request(
        TRENDING_URL.format(since=since),
        headers={"User-Agent": "trending-agent-digest/0.1"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_repos(page: str):
    """Parse repo blocks from the trending page.

    The page lists each repo as a link to /owner/repo, followed by a
    description and a star count for the period. This parser is intentionally
    tolerant: if GitHub changes its markup, it still returns what it can.
    """
    repos = []
    # Split on repo headings.
    blocks = re.split(r'<h2[^>]*>', page)
    for block in blocks[1:]:
        m = re.search(r'href="/([^"/]+/[^"/]+)"', block)
        if not m:
            continue
        name = m.group(1).strip()
        if name.startswith("sponsors/"):
            continue
        desc_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
        description = ""
        if desc_match:
            description = html.unescape(re.sub(r"<[^>]+>", "", desc_match.group(1))).strip()
            description = re.sub(r"\s+", " ", description)
            spaced = name.replace("/", " / ")
            if description.startswith(name):
                description = description[len(name):].strip()
            elif description.startswith(spaced):
                description = description[len(spaced):].strip()
        stars_match = re.search(r"([\d,]+)\s+stars\s+(today|this week)", block)
        stars = stars_match.group(1) if stars_match else "?"
        period = stars_match.group(2) if stars_match else ""
        repos.append({
            "name": name,
            "description": description,
            "stars": stars,
            "period": period,
            "category": categorize(name, description),
        })
    return repos


def render(repos, since: str) -> str:
    lines = [
        f"# GitHub Trending 简报 · {date.today().isoformat()} ({since})",
        "",
        "按类别整理今日上榜项目，star 数为该周期内新增数。",
        "",
    ]
    grouped = {}
    for repo in repos:
        grouped.setdefault(repo["category"], []).append(repo)
    for category in ["AI Agent", "开发者工具", "学习资源", "其他"]:
        items = grouped.get(category, [])
        if not items:
            continue
        lines.append(f"## {category}")
        lines.append("")
        for repo in items:
            desc = f"：{repo['description']}" if repo["description"] else ""
            lines.append(
                f"- **{repo['name']}**（+{repo['stars']} stars {repo['period']}）{desc}"
            )
        lines.append("")
    lines.append("来源：https://github.com/trending")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub Trending 中文简报")
    parser.add_argument("--since", choices=["daily", "weekly", "monthly"], default="daily")
    parser.add_argument("--output", help="输出 Markdown 文件路径，缺省打印到终端")
    args = parser.parse_args()

    try:
        page = fetch_trending(args.since)
    except Exception as exc:  # noqa: BLE001 - show a friendly error for a CLI tool
        print(f"抓取失败：{exc}", file=sys.stderr)
        return 1

    repos = parse_repos(page)
    if not repos:
        print("没有解析到项目，GitHub 页面结构可能已变化。", file=sys.stderr)
        return 1

    output = render(repos, args.since)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已写入 {args.output}，共 {len(repos)} 个项目。")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
