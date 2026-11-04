# 软件证据评分

[English](quality-scoring.md) · [数据格式](../data/README.md#quality-evidence-and-scores) · [评分目录](https://awesomerea.org/zh/quality/)

目录为每个软件条目提供一个可比较的**证据评分**。它只回答一个问题：该软件在软测指南的九个评测维度上，有多少公开、可复现的证据？它不是实测结果、完成度百分比或产品质量估计。

## 评分范围

`kind` 为 `tool`、`case-study`、`integration` 或 `project` 的目录记录都会评分。文档、合集、学习资料和研究记录不参与。评分只来自目录与提交的证据快照，不存在逐条手工改分。

九个维度来自评测指南，权重相同：

| 维度 | 检查的证据 |
| --- | --- |
| 功能覆盖 | 功能文档、用法示例、文档深度、演示图/视频、范围与限制声明 |
| 正确性 | 测试路径、CI 中的测试、测试说明、fuzz/性质测试、fixture 或 golden 数据 |
| 性能与容量 | benchmark 代码、实测数字、profiling、数值预算 |
| 用户隔离与秘密保护 | 安全策略、授权或租户证据、秘密与依赖处理、扫描器 |
| UI 一致性 | 截图或演示媒体、UI/视觉测试、可访问性证据、界面说明 |
| 持久化与故障恢复 | 持久化或恢复证据、存储/迁移层、失败处理、恢复文档 |
| 并发与状态一致性 | 并发证据、一致性模型、负载或压力证据 |
| 文件格式与外部兼容 | 导入/导出证据、格式校验器、格式 fixture、往返或消费端检查 |
| 可复现性与可靠性 | 许可证、构建清单、锁文件、CI、安装说明、版本化发布、可分发包、维护状态 |

不适用的维度会被排除，不按零分计入。例如，命令行二进制解析器没有 UI 分，单用户桌面编辑器没有多用户隔离分。

## 分数计算

每个检查分为 `pass`（1）、`partial`（0.5）或 `missing`（0）。维度分是检查均值，总分是适用维度的等权均值：

```
score = 100 × mean(适用维度分)
```

输出同时报告：

- `coverage`：有证据（pass 或 partial）的适用检查比例。
- `dimension_coverage`：达到 50 分及以上的适用维度比例。
- `confidence`：观察到完整 README 与仓库树时为 `high`，只有部分来源或页面时为更低级别。
- `band`：`strong-evidence`、`moderate-evidence`、`limited-evidence`、`minimal-evidence` 或 `ungraded`。

无法观察来源的条目为 `ungraded`，分数是 `null`，不是零分。README 声明或测试目录只能证明证据存在，不能证明功能可用或测试通过。

## 数据文件

- [`data/quality-evidence.json`](../data/quality-evidence.json)：带日期的公开证据快照。
- [`data/quality-evaluations.json`](../data/quality-evaluations.json)：由快照生成，禁止手改。
- [`scripts/collect_quality_evidence.py`](../scripts/collect_quality_evidence.py)：刷新快照。
- [`scripts/quality_scoring.py`](../scripts/quality_scoring.py)：离线重算全部分数。
- [`scripts/validate_quality_scoring.py`](../scripts/validate_quality_scoring.py)：重算并拒绝手改。
- [`scripts/build_quality_pages.py`](../scripts/build_quality_pages.py)：生成双语 `/quality/` 页面。

## 重新生成

```sh
python3 scripts/collect_quality_evidence.py --all
python3 scripts/quality_scoring.py --all
python3 scripts/validate_quality_scoring.py
python3 scripts/build_site.py
```

采集器读取公开的 GitHub 元数据、README 文本、仓库树、Release 产物和最多两个 CI 工作流文件；非 GitHub 条目读取公开页面。令牌只发送给 `api.github.com`，不下载或运行可执行文件，限制响应大小，原始响应缓存在被忽略的 `.cache/quality-evidence/` 目录。

快照记录审阅 ref、README 字节数与 SHA-256、仓库树 SHA、Release 资产名和观察时间。被截断的树会标明；缺失路径按“没有观察到证据”处理，而不是断言该实践不存在。

## 限制

- 公开证据可能不完整、过时或属于宣传文本。
- 评分器无法观察功能、与参考实现比对、测量性能或测试授权。
- README 完善的项目可能高于文档较少但实际更好用的项目。
- 分数衡量证据覆盖程度，不是软件质量排名。

后续阶段会增加独立的实测分：下载产物、在规则包和沙箱中运行。实测分单独报告，不会回填修改证据分。
