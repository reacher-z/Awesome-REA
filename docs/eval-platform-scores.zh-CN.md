# rea-tracker 条目证据强度分（v1）

状态：第一版基线。日期：2026-10-29。口径版本：`evidence-strength-v1`。生成脚本：[`scripts/build_tracker_evidence_scores.py`](../scripts/build_tracker_evidence_scores.py)。

本文件定义并记录对 [rea-tracker](https://github.com/ruoxining/rea-tracker) `taxonomy.html` 全部条目的**证据强度分**。它衡量"公开证据能支撑多强的结论"，不衡量"复现做到了什么程度"。tracker 页面自己的边界在这里原样适用：全部条目只是公开证据初筛，未安装、启动或验证核心工作流；Class 0 是较完整复现候选，不是逐工作流验收认证。

## 1. 输入与快照

| 项 | 值 |
| --- | --- |
| tracker 本地快照 | `rea-tracker` 仓库提交 `f1908a5`（2026-10-23 构建 `taxonomy.html`） |
| 上游摄入点 | Awesome-REA `169fd43c`，awesome-REA-cases `9d3820c8` |
| 审计时间 | 主体 2026-10-21，macOS 包补查 2026-10-23 |
| 条目总数 | 4,398 个去重实体：主体 1,270（Class 0:17 / Class 1:101 / 第二类:441 / 第三类:711）+ 资源附录 3,128 |
| 关联键 | tracker 记录 ID（如 `repo:owner/name`），与页面导出的项目 CSV 一致 |

打分只读取 tracker 已核验的结构化证据（`data/taxonomy_page.json` 与 `data/audit/`），不重新抓取上游，全部离线可复现。

## 2. 计分定义

类别（Class）仍是主档位；分数只在**同一类别内部**细化排序，任何加减分都不会跨档（每档有上下限，超出即截断）。资源附录单独一档，不与实体比较。

档位基准：

| 类别 | 基准分 | 档位区间 |
| --- | --- | --- |
| Class 0 · 较完整复现候选 | 8.0 | 8.0–10.0 |
| Class 1 · 通过初筛 | 6.0 | 6.0–7.9 |
| 第二类 · 仓库证据不足 | 3.0 | 3.0–5.9 |
| 第三类 · 笔记或局部实现 | 0.5 | 0.5–2.9 |
| 资源附录 | 0.1 | 0.0–0.4 |

加减项（全部来自 tracker 记录字段）：

| 项 | 分值 | 依据字段 |
| --- | --- | --- |
| Release 附带产物文件 | +1.0 | `acquisition[].assets` 非空 |
| 仅有下载/发布入口或源码安装说明 | +0.5 | `acquisition[].kind` ∈ release/download/source-install |
| 有公开 macOS 发行包 / 仅 CI 包 | +0.5 / +0.25 | `macos.status` ∈ available/ci |
| 经过逐项人工复核 | +0.5 | `manual_review` |
| 记录到实际 demo 媒体 | +0.25 | `media` 非空 |
| 文档二筛正向信号（原版对照／互通记录、内部一致性检查） | 各 +0.25 | `fidelity/document_review.csv`（仅历史 108 项快照） |
| 核验警告 | 每条 −0.25，至多 −0.5 | `warnings` |
| 仓库已归档 / 不可读取 | −0.5 / −1.0 | `archived` / `available` |

## 3. 结果概览

| 类别 | 条目 | 分数区间 |
| --- | --- | --- |
| Class 0 | 17 | 9.25–10.00 |
| Class 1 | 101 | 6.75–7.90 |
| 第二类 | 441 | 3.00–4.75 |
| 第三类 | 711 | 0.50–2.25 |
| 资源附录 | 3,128 | 0.00–0.10 |

主体 1,270 项中：237 项有带产物的发布包，149 项仅有源码安装说明；macOS 包状态仅对 Class 0/1 的 118 项做过补查（64 有包、1 仅 CI、53 未确认），其余类别该字段为空；167 项经过人工逐项复核；6 项有文档二筛正向信号。

数据文件：[CSV 明细](scores/tracker-evidence-scores.csv)（含逐项加分构成）、[JSON](scores/tracker-evidence-scores.json)、[可视化看板](scores/tracker-scores.html)（各类别分布、macOS 包状态、获取入口构成三组图 + 可筛选排序的数据表，明暗双主题，`#light`/`#dark` 可固定主题）。

## 4. 与完成度实测的衔接（提案，未执行）

证据强度分之后，计划对能获取的软件做实跑，补"复现完成度"维度。该工作会另开 PR；此节只固定口径，防止实跑结果与证据分混排。

- **Class 1（可运行性）**：按 README 下载、安装并尝试启动；只要下载、安装、能启动三者都成功，记"可运行"，记录环境（OS/架构/安装来源）与失败步骤。不比较功能。
- **Class 0（对原版一致性）**：先由人写出该软件核心工作流的少量任务（新建→编辑→保存→重开→导出一类），复现版与原版在相同初始状态下各跑一遍，逐任务比对导出产物语义与关键界面状态；"差不多"指逐任务断言通过，不汇总成单一总分。
- **工具选择**：第一版不建议从 GraphWalker 起步。它适合纯逻辑状态机（协议、解析器、CLI 参数流），macOS GUI 应用用它要先维护一套 UI 驱动模型，覆盖率指标也不回答"跟原版像不像"。更直接的路径是 Accessibility（AX）驱动的成对任务脚本＋必过断言＋导出文件语义对比，截图差异作辅助；GraphWalker 留给确实无 GUI 的纯逻辑组件。

## 5. 复现方式

```bash
python3 scripts/build_tracker_evidence_scores.py --tracker /path/to/rea-tracker
```

需要本地有一份 rea-tracker 检出（含 `data/` 快照）；脚本只用 Python 标准库，不访问网络。重新生成会覆盖 `docs/scores/` 下三个文件，人工编辑会被覆盖。

## 6. 局限

- 分数完全继承 tracker 快照的证据与局限：未运行任何项目，demo 与获取入口是 README/Release 层面的核对。
- 加减项权重是为同类内排序设的工程约定，不是测量结果；跨类别的分差只反映档位，不构成可比性。
- macOS 字段、文档二筛标签只覆盖 tracker 补查过的子集，空值表示"未查"，不是"没有"。
- 实跑后（安装成功、任务通过）不回写本分数；完成度结果将使用独立字段与独立 PR。
