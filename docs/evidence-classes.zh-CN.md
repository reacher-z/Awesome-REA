# 证据档位（C0–C3 + Unknown，v4）

[English](evidence-classes.md) · [文档索引](README.zh-CN.md)

状态：v4 Beta，自动生成 + 人工复核。口径版本：`evidence-class-v4`。精选分类脚本：[`scripts/classify_evidence_classes.py`](../scripts/classify_evidence_classes.py)。数据：[`data/evidence-classes.json`](../data/evidence-classes.json)。Class 0 复核：[`data/evidence-class-zero-reviews.json`](../data/evidence-class-zero-reviews.json)。

本文件定义主页精选目录和自动扫描仓库索引中显示的**证据档位**与**复现范围**。这是公开证据口径。**Class 0 只授予人工确认的完整软件复现**；自动规则最高只到 Class 1。

档位、复现范围和运行状态分开记录：

- `evidence_class`：0–3；来源不可读时为空
- `scope`：`full` / `partial` / `analysis` / `unknown` / `notes`
- `runtime_status`：固定 `not-run`
- `evidence_status`：`observed` / `unknown`

主页精选卡片显示 `C0`–`C3` / `?` 徽章，筛选栏下方有图例，并可通过“证据档位”下拉筛选。Class 0/1 且文档中有 demo 的条目显示预览图；只有视频或链接、没有可提取图片时显示「有 demo · 暂无截图」。

仓库视图显示单独的**扫描证据档位**。扫描档位只使用 C1–C3：`data/source-index.json` 记录 README 大小和章节信号，但没有采集 Release 产物、demo 媒体或运行行为，Class 0 不会由扫描元数据授予。

## 1. 精选档位

| 档位 | 定义 | 徽章 |
| --- | --- | --- |
| Class 0 | **人工确认的完整软件复现**（`kind: case-study`）：范围、目标版本和一手证据逐条复核，记录在 `data/evidence-class-zero-reviews.json` | C0 |
| Class 1 | **自动判定上限**：有下载方式和非品牌 demo，但范围是部分/补丁/移植，或本身不是软件复现（工具、集成、指南、binary 分析条目） | C1 |
| Class 2 | 缺 demo 或下载方式，但有代码和文档；不确定能不能构建 | C2 |
| Class 3 | 无代码或无文档，只有笔记、进度记录或局部片段 | C3 |
| Unknown | 复核时来源不可达或不可读 | ? |

## 2. 精选判定信号

只使用条目 URL 的公开内容（GitHub REST、GitLab REST 或页面抓取）：

| 信号 | 含义 |
| --- | --- |
| `code` | URL 是代码仓库，或页面链接到代码仓库 |
| `docs` / `docs_full` | README 或页面正文 ≥ 400 字节；章节结构覆盖安装/构建与使用 |
| `download` | Release **附产物**、可执行产物直链，或**安装目标软件本身**的包命令（包名与仓库名匹配） |
| `download_links` | 从 README、README 链接的文档（如 `docs/INSTALL.md`）和 README 指向的分发页面解析到的具体下载链接与安装命令；纯项目主页不算 |
| `demo` | 非品牌的位图截图、视频平台链接或 demo/playable 链接 |

不算下载：只有 Release tag、没有产物；构建依赖（如仓库是 `foo` 时 `pip install ninja`）。
不算 demo：logo、徽章、二维码、群聊邀请、进度图、CI/Release 徽章。

判定顺序：

1. 无 code 或 docs → **Class 3**
2. 有 code + docs，但缺 demo 或缺 download → **Class 2**
3. download + demo 都有 → 自动最高 **Class 1**
4. **Class 0 只能由人工复核授予**：复核文件里 `scope: full`，且至少具备 code、docs、download、demo、`kind: case-study`、非 binary 目标

## 3. 扫描档位

扫描映射由 [`scripts/classify_scan_evidence.py`](../scripts/classify_scan_evidence.py) 生成到 [`data/scan-evidence-classes.json`](../data/scan-evidence-classes.json)。它只读已提交的扫描快照和公开补充批次，不发起网络请求。

| 扫描档位 | 定义 |
| --- | --- |
| Class 1 | README 同时记录安装与用法。Release 产物、demo 媒体和可构建性仍未观察。 |
| Class 2 | 有 README 文档，但未找到安装或用法说明。 |
| Class 3 | 未找到可用的 README 文档。 |
| Class 0 | 不会由扫描元数据授予。 |

扫描档位描述 README 文档。

## 4. 方法与局限

- 分布数字从数据文件读取，不在本文维护副本：

  ```bash
  python3 - <<'PY'
  import collections, json
  curated = json.load(open('data/evidence-classes.json', encoding='utf-8'))
  scan = json.load(open('data/scan-evidence-classes.json', encoding='utf-8'))
  print('curated', curated['meta']['class_counts'], 'unknown', curated['meta']['unknown_count'])
  print('basis', collections.Counter(entry['basis'] for entry in curated['entries']))
  print('scan', scan['meta']['class_counts'], 'unknown', scan['meta']['unknown_count'])
  PY
  ```

- Class 0 是 `evidence_class == 0` 与 `data/evidence-class-zero-reviews.json` 中 `scope: full` 的交集。除 Class 0 外没有逐条 class override。
- GitHub token 只发送到 `api.github.com`；跨域重定向会剥离认证头。普通页面抓取不携带 token。
- 图片过滤掉 logo、徽章、二维码、群聊和赞助链接，避免把品牌图当成 demo。
- 主页预览由 [`scripts/build_evidence_previews.py`](../scripts/build_evidence_previews.py) 选取并写入 [`data/evidence-previews.json`](../data/evidence-previews.json)；[`scripts/fetch_previews.py`](../scripts/fetch_previews.py) 在构建前下载到 `.cache/previews/`，构建复制到站点的 `previews/` 目录，页面不外链第三方图片。
- 单条复核使用 [`scripts/verify_evidence_entry.py`](../scripts/verify_evidence_entry.py)。

## 5. 重新生成

```bash
python3 scripts/classify_evidence_classes.py            # 带本地缓存
python3 scripts/classify_evidence_classes.py --fresh    # 忽略缓存全部重抓
python3 scripts/classify_evidence_classes.py --ids <id,...> --merge  # 只复核新增记录
python3 scripts/classify_scan_evidence.py               # 对扫描快照确定性生成
python3 scripts/build_evidence_previews.py                  # 本次未找到媒体时保留已有预览
python3 scripts/build_evidence_previews.py --drop-missing   # 删除本次未找到的预览
python3 scripts/fetch_previews.py
python3 scripts/build_site.py
python3 scripts/verify_evidence_entry.py <entry-url>
```

`build_site.py` 把 `evidence_class`、`evidence_status`、`scope`、`runtime_status`、`evidence_review` 与预览字段合并进 `catalog.json` / `catalog-index.json`，为仓库视图写出紧凑的 `scan-classes.json`，并在精选条目缺少档位时直接报错。
