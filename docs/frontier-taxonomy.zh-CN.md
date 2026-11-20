# FrontierCUA 任务领域 pilot

[English](frontier-taxonomy.md) · [提议 issue](https://github.com/reacher-z/Awesome-REA/issues/4516) · [数据类别](../data/README.md#data-records)

状态：pilot 数据，2026-11-19 复核。它不替代 `targets` 或 `evidence_class`，目前也还没有接入网站。

本 pilot 把 `data/evidence-classes.json` 中的 **15 条 Class 0 记录**各自映射到一个 FrontierCUA v1.1 任务领域字段。分类本体以固定提交来自 `ruoxining/rea-tracker` 的审计快照：15 个领域圈、120 个字段，保存在 `data/frontier-taxonomy.json`。

## 数据文件

- [`data/frontier-taxonomy.json`](../data/frontier-taxonomy.json)：15 个领域圈、120 个字段及其定义、示例应用，以及分类元数据和来源 URL。
- [`data/frontier-taxonomy-map.json`](../data/frontier-taxonomy-map.json)：每条 Class 0 记录的 `id`、`field`、`field_name`、简短理由和 rea-tracker 证据 URL。

只有当被复核软件有明确的主要用户任务时才映射；未映射的记录不会被猜测填入。pilot 每条记录只指定一个字段，即使项目支持多个任务。

## 用途

目录现有的 facet 回答的是**重建了什么**（`targets`、`class`）和**公开证据支持到什么程度**（`evidence_class`）。任务字段回答另一个问题：**这项重建支持哪一类 computer-use 工作？** 例如：

| 记录 | 字段 | 领域圈 |
| --- | --- | --- |
| `photocraft-case` | `R06.02` 图像编辑与照片修饰 | R06 媒体与创意 |
| `gridcraft-case` | `R04.03` 电子表格 | R04 办公与文档 |
| `cadcraft-case` | `R07.01` 计算机辅助设计 | R07 工程与 CAD |
| `openrct2-engine-case` | `R13.01` 游戏 | R13 游戏与互动媒体 |

## 局限

- 映射是编辑判断。rea-tracker 的规则基于关键词，一条记录也可能同时符合多个任务领域。
- pilot 只覆盖 Class 0；它不主张其他记录没有任务，也不标注任务难度、复现范围或工作量。
- 该分类是研究产物，不是运行测试，也不代表功能等价。

## 下一步

[提议 issue](https://github.com/reacher-z/Awesome-REA/issues/4516) 用来确认该 facet 是否属于本合集，以及 pilot 之后覆盖哪些记录。若接受，下一步是为更大范围做人工复核映射，然后增加浏览／筛选界面；pilot 数据暂不接入站点。
