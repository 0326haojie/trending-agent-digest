# trending-agent-digest

每天一份 GitHub Trending 中文简报，聚焦 AI Agent 与开发者工具。

Daily Chinese digest of GitHub Trending, focused on AI agents and developer tools.

## 它能干什么

- 抓取 GitHub Trending（daily / weekly）
- 按类别分类：AI Agent、开发者工具、学习资源、其他
- 输出一份可读的中文 Markdown 简报，包含项目名、简介和当日新增 star 数

## 快速开始

```bash
python3 trending.py --since daily
python3 trending.py --since daily --output report-2026-11-03.md
```

不需要安装任何第三方依赖，只用 Python 标准库。

## 示例输出

见 `examples/report-2026-11-03.md`，这是 2026-11-03 当日榜单的示例简报。

## 为什么做这个

今天的 Trending 有一个很明显的规律：上榜的不是大而全的框架，而是帮 Agent
记东西、管任务、操作电脑、并行干活的小而专的工具。这个项目就是把这个规律
变成一个每天都能复用的简报工具。

## 免责

本项目只做公开榜单的整理与分类，不复制任何上榜项目的代码。
