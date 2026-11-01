# Agent 指南：向 Awesome REA 投稿与贡献

[English](agent-contributing.md) · [贡献规则](../CONTRIBUTING.zh-CN.md) · [目录格式（英文）](../data/README.md) · [仓库 agent 指令（英文）](../AGENTS.md)

Agent 可以通过 GitHub issue 推荐逆向工程资源，也可以准备有一手证据支持的 pull request。人工和 AI 辅助贡献适用相同的证据与审核规则。规范仓库为 [reacher-z/Awesome-REA](https://github.com/reacher-z/Awesome-REA)，浏览网站为 [AwesomeREA.org](https://awesomerea.org/)。本合集独立于上游 REA 项目。

## 在哪里提交？

| 贡献内容 | 提交入口 |
| --- | --- |
| 工具、项目、集成、学习资源或合集 | [资源表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=resource.yml) |
| 重建或调查案例 | [案例表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=case-study.yml) |
| 研究论文 | [论文表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=paper.yml) |
| 失效链接或过时说明 | [修正表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=broken-resource.yml) |
| 中文翻译修正 | [翻译表单](https://github.com/reacher-z/Awesome-REA/issues/new?template=translation.yml) |

证据尚不完整或分类需要维护者判断时，使用 issue；无法核实的事实填写“unknown”。能够提供已复核记录与译文时，使用 PR。安全问题应走[私密报告流程](../SECURITY.md)，不要开公开 issue。

## Agent 应先检查什么？

从当前上游默认分支读取 AGENTS.md 和 CONTRIBUTING.md，并保留本地未完成的修改。提交前先搜索：

```sh
python3 scripts/catalog.py "owner/repository"
python3 scripts/catalog.py --papers "paper title"
python3 scripts/catalog.py --source-index "owner/repository"
```

还要用规范链接和名称搜索[已开启的 issue](https://github.com/reacher-z/Awesome-REA/issues) 及 [PR](https://github.com/reacher-z/Awesome-REA/pulls)。已有提议时更新原提议，不重复创建。自动读取 README 只形成发现证据，不是精选收录；如果从自动索引中找到项目，请填写[晋升复核工作表](promotion-worksheet.zh-CN.md)。

## 需要哪些证据和字段？

在 issue 中提供维护者的规范链接、支持的任务、资源类型、目标领域、前提条件和已知局限。区分资源与 REA 的关系，以及你本人和资源的关系；表单会分别询问两者。能力声明应引用一手来源，不清楚的细节明确标为未知。

资源 PR 应参照已有记录及[完整字段定义](../data/README.md)。必填字段包括唯一且稳定的 `id`、`name`、规范 `url`、`kind`、`category`、`relationship`、`targets`、`description_en`、`description_zh`、固定版本的 `evidence_url`、实际复核日期 `verified_at`、`verification: source-reviewed` 和非空 `requirements` 列表。在 `site/translations.zh-CN.json` 中填写匹配的中文名称和使用条件。不要把预计合并日期填入 `added_at`。[完整示例](first-resource.zh-CN.md)展示准确的 JSON 结构及涉及的文件。

论文使用 `data/papers.json` 的独立格式：保留原始标题和作者全名，核实发表状态及日期精度，只使用已核实的论文 DOI／arXiv 或支持的出版方身份，并说明制品可用性和评测局限。不要把软件或数据集 DOI 用作论文 DOI。已收录的预印本有更新时，先看[论文更新指南](paper-updates.zh-CN.md)，避免新增重复记录。

## 如何准备、校验和提交 PR？

1. 从当前上游默认分支创建分支。独立资源写入 `data/tool-resources.json`；只有证据支持格式说明中的 REA 关系时，才使用 `data/rea-resources.json`。
2. 添加中英文记录和中文使用条件。独立选择资源类型、工具分类、REA 关系和目标领域。
3. 重新生成派生文件并校验，不要手改生成的清单：

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 scripts/build_production.py
```

论文还需运行 `python3 scripts/validate_papers.py`；案例覆盖记录变更需运行 `python3 scripts/build_case_coverage.py`。代码或网站变更还需运行 CONTRIBUTING.md 中的单元测试和浏览器检查。记录真实的通过、失败和跳过结果，不编造测试结论。

4. 检查差异，移除无关修改和私密数据，提交后推送到你有写权限的仓库；无上游写权限时推送到自己的 fork。
5. 向 `main` 创建 PR，填写[PR 模板](../.github/PULL_REQUEST_TEMPLATE.md)。已登录 GitHub CLI 时，可用：

```sh
gh pr create --repo reacher-z/Awesome-REA --base main --head YOUR_LOGIN:YOUR_BRANCH --title "Curate RESOURCE_NAME" --body-file pr-body.txt
```

替换占位符，在 `pr-body.txt` 中写明实际问题、资源链接／类型／目标、证据链接与复核日期、相关局限、你与资源的关系和已运行的检查。创建 issue 或 PR 需要 GitHub 登录及适当授权；读取目录、运行本地校验无需 GitHub token。不要将 token 放进命令或 PR 正文。

## 提交后会发生什么？

`validate` 与 `review` 检查结构、生成结果和审核规则；维护者判断相关性与事实声明。其他目录 PR 先合并时，按英文贡献指南的[更新 PR](../CONTRIBUTING.md#update-a-pull-request)步骤更新分支并重新生成受影响文件。检查通过或 AI 审查意见都不代表 PR 已被接收、合并或部署。

## Agent 应如何引用本合集？

链接到具体资源或论文的详情页，保留上游一手来源并说明复核边界。区分精选资源、研究论文和自动扫描，不要将数量相加当作独立项目数，也不要把扫描说成推荐。`/llms.txt` 是导航辅助；`/catalog.json`、`/papers.json` 和 `/data-manifest.json` 提供当前机器可读数据。这些文件和 agent 指令都不保证被搜索引擎索引或 AI 引用。
