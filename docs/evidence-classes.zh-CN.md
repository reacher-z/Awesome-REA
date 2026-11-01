# 精选条目证据档位（Class 0-3，v1）

状态：v1，自动生成后人工覆盖修订。口径版本：`evidence-class-v1`。生成脚本：[`scripts/classify_evidence_classes.py`](../scripts/classify_evidence_classes.py)。数据：[`data/evidence-classes.json`](../data/evidence-classes.json)。

本文件定义主页精选目录全部 529 个条目的**证据档位**。档位衡量"公开证据能支撑多强的结论"：文档覆盖度、下载方式、图片或视频演示。它**不是**复现完整度或质量判断；档位也不代表本目录安装、运行或验证过任何条目。

档位展示在主页每张卡片的 `C0`–`C3` 徽章上，筛选栏下方有档位图例，并可通过"证据档位"下拉筛选。

## 1. 档位定义

| 档位 | 定义 | 徽章 |
| --- | --- | --- |
| Class 0 | 文档讲完整功能，有下载方式，有图片或视频 demo | C0 |
| Class 1 | 有下载方式和图片视频 demo，但更多是部分功能或功能补丁，不够完整复现 | C1 |
| Class 2 | 缺少 demo 或下载方式，但至少有 code 和文档；不确定能不能 build | C2 |
| Class 3 | 无 code 或无文档，只是进度记录或笔记分享 | C3 |

判定只依赖可观察信号，全部来自条目 URL 的公开内容：

| 信号 | 含义 | 来源 |
| --- | --- | --- |
| `code` | URL 指向代码仓库（GitHub API），或页面链接到代码仓库 | GitHub REST API / 页面抓取 |
| `docs` | README 或页面正文 ≥ 400 字节 | 同上 |
| `docs_full` | 文档结构完整：同时有安装/构建与使用章节，或 ≥ 3 类章节（安装、使用、功能、演示） | README 章节标题 |
| `download` | 下载方式：`release-assets`（Release 附产物）、`release`（Release tag）、`package`（包管理器安装命令）、`file-links`（可执行产物直链）、`download-section` | GitHub releases / README |
| `demo` | 演示：`image`（非徽章图片）、`video`（视频平台链接）、`demo-link`（demo/playable 链接） | README / 页面 |

判定规则（按顺序）：

1. 无 code 或无 docs → **Class 3**。
2. 有 code + docs，但缺 demo 或缺 download → **Class 2**。
3. download + demo 都有时：
   - `kind: case-study`：描述明说完整重实现（reimplements / complete implementation 等）且 `docs_full` → **Class 0**，否则 → **Class 1**（案例默认按部分范围计）。
   - 其他 kind：描述含部分功能标记（单个规则/函数/移植/补丁/试点）→ **Class 1**；`docs_full` → **Class 0**；否则 → **Class 1**。

## 2. 方法与局限

- GitHub 条目（490 个）读取仓库元数据、releases（含产物数）和 README；其他条目（39 个，如 `rea.tools`、博客、文档站）抓取页面本身，并检测页面内的仓库链接、图片与视频。
- 图片过滤掉徽章类（shields.io、CI badge、logo 等），避免把项目徽章当成 demo。
- 抓取时间写入每条记录的 `checked_at`；信号保存在 `signals` 字段，供逐条审计。
- 已知局限：文档完整度靠章节结构推断，不看内容质量；页面抓取对 JS 渲染的站点可能漏检媒体；"下载方式"不含纯源码构建说明（这正是 Class 2 "不确定能不能 build" 的含义）。
- 人工修订：[`data/evidence-class-overrides.json`](../data/evidence-class-overrides.json) 中的条目覆盖自动结果，`basis` 字段标记 `override`。自动判定明显不对时优先补 override，而不是改启发式。

## 3. 重新生成

```bash
python3 scripts/classify_evidence_classes.py            # 带本地缓存（.cache/evidence-scan/）
python3 scripts/classify_evidence_classes.py --fresh    # 忽略缓存全部重抓
```

脚本输出条目数与各档位分布。`scripts/build_site.py` 把 `evidence_class` 合并进 `catalog.json` / `catalog-index.json`，并在条目缺失档位时直接报错，保证目录与档位数据不脱节。
