# 复刻质量评分 v2（rule-based evaluation）

状态：第一版工程骨架。代码：[`scripts/quality_scoring.py`](../scripts/quality_scoring.py)。规则包：[`quality-rules/`](../quality-rules/)。输出：`data/quality-evaluations.json`（由 scorer 生成，与候选数据一起在后续 PR 提交）。

v1 证据档位（C0–C3）只读公开文档、Release 元数据和 README。v2 不替代 v1，而是在 v1 的初步信号之上做路由：只有信号表明某类工具可用时，才下载、检查或运行软件，并把观察结果交给版本化规则判分。**文档不是质量结论，只是决定下一步问什么的输入。**

## 1. 处理流程

```
catalog record + evidence signals
        │
        ▼
profile：源码、文档、产物、平台、架构、界面类型
        │
        ▼
router：L0 证据 / L1 源码静态 / L2 产物静态 / L3 运行时冒烟 / L4 功能规则
        │
        ├── artifact download → hash → archive/package inspect
        ├── source inspection（后续）
        └── Docker sandbox → rule pack（本版仅 Woxi）
        │
        ▼
score：维度覆盖率、规则通过率、证据深度权重、限制
```

路由器是确定性的，规则写在代码里，不写逐条 override。规则包只包含测试和期望，不包含分数；同一套聚合逻辑跑所有条目。

## 2. 评分输入

scorer 读 653 条精选记录，以及 `data/evaluation-candidates.json` 中显式列出的候选。候选不是精选条目：不渲染网站、不改变 v1 证据档位、不进入 README；它只让评分器能评估一个已经点名、但还没有走完目录收录流程的项目。

首个候选是 Picture Man。它在 rea-tracker 里是 Class 0，但 #2549 的收录标准是 README demo + acquisition evidence；Picture Man 的 README 明说没有预编译二进制、只能源码构建，所以当时没有进精选目录。v2 把它放进评分候选，路由到 L1 源码静态检查，而不是假装它有可下载产物。

## 3. 档位与可用工具

| 档位 | 触发条件 | 本版实际动作 | 分数上限 |
| --- | --- | --- | --- |
| L0 证据 | 非软件条目、无 code/download、来源不可读 | 只记录 catalog 元数据 | 无分数 |
| L1 源码静态 | 有源码，无可用产物 | `--inspect-source` 读取 GitHub 默认分支树，检查 license、tests、构建清单和 CI；不构建、不运行 | 20 |
| L2 产物静态 | 有可下载产物，但平台无 sandbox 或没有规则包 | 下载、SHA-256、归档/包检查、`.appinstaller` 解析 | 40 |
| L3 运行时冒烟 | Linux CLI/服务产物，无规则包 | 预留 Docker 冒烟；本版尚无条目走到这里 | 60 |
| L4 功能规则 | 有产物 + 规则包 + 本地 Docker 镜像 | 解包、静态检查、在容器内运行固定命令并比对期望 | 100 |
| L5 全量质量 | 规则包覆盖性能、权限、持久化、并发、格式、UI 等 | 尚未实现 | 100 |

`LEVEL_WEIGHT` 是全局常数，不按条目调整。

## 4. 初步信号如何决定路由

- `kind` 不是 `case-study` / `project` / `tool` / `integration`：L0，不运行任何东西。
- 证据状态是 `unknown`：L0，避免把抓取失败当成“仅笔记”。
- 有源码、没有任何可下载产物：L1。
- 有产物，但平台是 macOS/Windows：L2；本机没有对应 VM，运行时明确标 blocked。
- 有 Linux 产物且界面是 CLI/服务：没有规则包时 L3，有规则包和本地镜像时 L4。
- 产物只来自 README 直链、Release asset 或目标安装命令；纯项目主页不算产物。
- README 直链使用比 v1 更宽的扩展名集合（含 `.appinstaller`、`.msix`、`.pkg`），因为 v2 需要实际文件，而不只是“有下载”这一强信号。

## 5. 维度与工具

维度沿用用户提供的评测工具指南（`软件复刻质量评测工具.md`）中的九类，另加 `artifact_integrity`（可下载产物的最低证据）。

| 维度 | 本版工具 | 后续工具 |
| --- | --- | --- |
| `artifact_integrity` | HTTPS 下载、大小上限、SHA-256、归档清单、`.appinstaller` XML | 上游校验和、签名、包元数据 |
| `correctness` | 规则包中的固定命令 + 精确/包含期望（Woxi） | pytest + Hypothesis、参考实现差分 |
| `functional_coverage` | 预留 | Crawljax / Katana / Schemathesis / Playwright |
| `performance` | 预留 | k6 / Locust / Chrome DevTools |
| `security_isolation` | 容器默认 `--network none`、cap-drop、只读挂载 | 权限矩阵、ZAP、Gitleaks |
| `ui_consistency` | 预留 | Playwright 截图 + pixelmatch |
| `persistence_recovery` | 预留 | Testcontainers / Toxiproxy |
| `concurrency` | 预留 | HTTPX + asyncio、Playwright 多 context |
| `file_formats` | 预留 | qpdf、glTF-Validator、真实消费端 |
| `reproducibility` | 产物 SHA-256、固定镜像 ID、固定命令、许可证/README 文件检查 | pytest-repeat、trace、版本清单 |

## 6. 安全边界

- 每个下载物放在 `.cache/quality-scan/work/<entry-id>/` 自己的目录里，不进入 Git。
- 只接受 HTTPS；有下载大小上限；不携带认证头。
- 归档先只读清单；解包前拒绝绝对路径、`..`、符号链接，并限制条目数和解压后大小。
- `.appinstaller` 拒绝 DTD，避免外部实体。
- 规则只在 Docker 内运行：`--network none`、`--cap-drop ALL`、`no-new-privileges`、`--read-only`、`/tmp` tmpfs、CPU/内存/PID 限制、超时。
- 只使用本地已有镜像，不隐式 `docker pull`；镜像 ID 记入证据。
- macOS/Windows 产物不在主机执行；没有对应 VM 时标记 blocked。**本版没有在主机上运行任何下载的二进制。**
- 规则命令来自版本化规则包，不从被测软件的文档或文件里读取命令。

## 7. 规则包

示例：[`quality-rules/woxi-case.json`](../quality-rules/woxi-case.json)。

```json
{
  "schema_version": 1,
  "entry_id": "woxi-case",
  "sut": {
    "kind": "release-artifact",
    "artifact": {"name_pattern": "woxi-v*-aarch64-unknown-linux-gnu.tar.gz",
                  "platform": "linux", "arch": "arm64"},
    "sandbox": {"image": "rea-rollout/woxi:0.3.0-arm64", "network": false,
                 "timeout_seconds": 60, "interfaces": ["cli"]}
  },
  "rules": [
    {"id": "arithmetic", "dimension": "correctness",
     "command": ["/sut/woxi", "eval", "1 + 2"],
     "expect": {"exit_code": 0, "stdout_equals": "3"}}
  ],
  "static": [
    {"id": "license-file", "dimension": "reproducibility",
     "check": "file-in-artifact", "path": "license.txt"}
  ]
}
```

约束：

- `entry_id` 必须在 catalog 中；规则包不新增条目。
- `command` 是固定参数列表，在容器内用 `sh -lc` 执行；不拼接被测软件提供的文本。
- 每个规则必须有 `id`、已知 `dimension` 和至少一个期望。
- 规则包可以指定 `interfaces`，覆盖从描述推断的界面类型。
- 规则包是测试资产，不是评分资产；新增规则后重跑全量，而不是给某条目录记录改分。

## 8. 评分

每个维度先按规则状态聚合：

- 任一规则失败 → 维度 `fail`，维度得分 0。
- 全部通过 → `pass`，维度得分 1。
- 有阻塞/错误 → `blocked`，维度得分 0。
- 其余 → `partial`，维度得分按通过的规则比例（partial 计 0.5）。
- 没有规则 → `not-tested`，维度得分 0。

然后：

```
quality_fraction = mean(所有 applicable 维度的得分)
score = 100 × quality_fraction × level_weight
coverage = 已评估维度 / applicable 维度
```

- 没有任何 pass/fail 规则时 `score = null`，避免把“没跑”当成 0 分。
- `pass_rate` 仍单独报告（passes / (passes + fails)），阻塞不计入分母。
- `verdict`：`failed` > `verified`（L4/L5 且所有 applicable 维度 pass）> `artifact-verified`（L2 同理）> `source-inspected`（L1）> `partially-verified` > `blocked` > `ungraded`。
- 分数是"已验证质量"，不是产品质量估计；覆盖率低时分数低，不能反推软件差。

## 9. 第一轮结果（2026-11-03）

| 条目 | 路由 | 实际动作 | 分数 | 结论 |
| --- | --- | --- | ---: | --- |
| Woxi | L4 | 下载 `woxi-v0.3.0-aarch64-unknown-linux-gnu.tar.gz`；SHA-256 `e33497ac…`；容器内 `--version`、`1 + 2`、`StringJoin` 全部通过；源码树有 license/tests/Cargo.toml/CI | 42.9 | partially-verified；7 个 applicable 维度只测了 3 个 |
| Wino Mail | L2 | README 的 `WinoMail.appinstaller` 被识别并下载（551 B）；XML 解析通过；源码树无 tests、无 CI | 36.7 | partially-verified；Windows 运行时 blocked |
| Ledger Reborn | L2 | 下载 macOS arm64 DMG（13.9 MB）；SHA-256 `ae04762a…`；DMG 无可用检查器；源码有 tests 和 requirements | 35.0 | partially-verified；macOS 运行时 blocked |
| Picture Man | L1 | 评分候选；README 明说没有预编译产物；源码树 159 个路径，license/tests/Cargo.toml/CI 齐全 | 20.0 | source-inspected；没有 download，运行时未尝试 |

Wino Mail 的 `.appinstaller` 在 v1 中漏检（扩展名不在 `DOWNLOAD_EXTENSIONS`，且 `## Download` 标题不算 install）；v2 从同一份缓存 README 的 markdown/HTML 链接中直接提取产物 URL，这是评分规则的修正，不是对该条目的手工改分。

离线 `--plan --all` 的 654 条路由分布（653 条精选 + 1 个候选）：L0 74、L1 214、L2 363、L3 2、L4 1。L2 占多数，说明“有产物但平台无 sandbox 或没有规则包”是下一阶段的主要工作；当前只有 Woxi 有规则包，因此不能把这一分布当作全量质量结论。

## 10. 已知限制与下一步

1. 只有 Woxi 有规则包；其余条目的 L3/L4 能力还没有内容。
2. L1 只读取 GitHub tree 的路径，不读取文件内容，也不判断测试质量；`--inspect-source` 还没有接入全量计划。
3. L5 的九维工具尚未接入；Playwright/HTTPX/Hypothesis 需要作为可选依赖和独立 sandbox 计划引入。
4. macOS/Windows 产物只做静态检查；需要 VM adapter 才能运行。
5. 预览/截图、性能、权限、持久化、并发、格式校验都还没有规则。
6. `data/quality-evaluations.json` 目前是四个试点条目（三个精选 + 一个候选），不是全量结果。全量运行需要先为更多条目补规则包，并按预算分批执行。

下一步顺序：更多 CLI/服务规则包 → L3 冒烟 → HTTPX/Playwright 功能规则 → 性能/权限/持久化/并发/格式 → 全量分批运行。
