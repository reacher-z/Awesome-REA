# 提交第一个资源：完整示例

[English](first-resource.md) · [中文贡献指南](../CONTRIBUTING.zh-CN.md) · [目录格式（英文）](../data/README.md)

本页以 [tool-resources.json](../data/tool-resources.json) 中已有的 `r2frida` 记录为例，逐一说明新增一条精选资源会涉及的每个文件，供提交自己的资源时参照。r2frida 已经收录，请不要重复添加：你的记录需要自己的 ID 和自己的证据。

需要公开仓库的克隆、Python 3.10 或更新版本以及 Node.js。下面的命令不需要授权图标文件、部署权限、令牌或网络访问。

## 1. 先确认没有重复条目

动笔之前，先检索精选目录和独立的自动仓库索引：

```sh
python3 scripts/catalog.py r2frida
python3 scripts/catalog.py --source-index nowsecure/r2frida
```

第一条命令找到精选记录。如果你的资源已经收录，请对那条记录提出修正，而不是再加一条。第二条命令在自动索引中找到该仓库；索引记录只是 README 扫描，不是复核，收录为精选仍需完成下面的步骤。

## 2. 复核并固定一手来源

阅读项目自己的文档，记录其中写明的内容。r2frida 的 `evidence_url` 是复核时那次提交的 README：`https://github.com/nowsecure/r2frida/blob/4f1f8d7b1096ed0ca29778688d0f164461d56f05/README.md`，因此链接始终显示当时复核的文本；`url` 仍是会随项目变化的项目链接。GitHub 证据是仓库根地址或未固定修订的 Wiki 页面时，`python3 scripts/validate.py` 会给出不阻断的警告。`verified_at` 是你复核的日期。

`verification: source-reviewed`（来源已复核）只表示已对照这些文档核对说明，不表示有人安装、审计或运行过该项目；目录记录也不收录运行结果。如果你实际运行过，可以在 pull request 中说明，帮助审核者核实，但这些内容不会作为验证结果发布。

## 3. 编写记录

证据表明与 REA 有关联的记录（官方、社区和维护者配套合集等关系）保存在 [rea-resources.json](../data/rea-resources.json)。像 r2frida 这样的独立记录，新增时放在 [tool-resources.json](../data/tool-resources.json) 末尾。两个文件会合并展示，ID 在两个文件中都必须唯一。记录内容如下：

```json
{
  "id": "r2frida",
  "name": "r2frida",
  "url": "https://github.com/nowsecure/r2frida",
  "category": "dynamic-analysis",
  "relationship": "foundation",
  "kind": "tool",
  "targets": ["app", "binary"],
  "description_en": "Use radare2 commands and Frida instrumentation together to inspect local or remote process memory, symbols, classes, and runtime calls on desktop and mobile targets.",
  "description_zh": "结合 radare2 命令与 Frida 插桩，检查桌面和移动目标中本地或远程进程的内存、符号、类及运行时调用。",
  "evidence_url": "https://github.com/nowsecure/r2frida/blob/4f1f8d7b1096ed0ca29778688d0f164461d56f05/README.md",
  "verified_at": "2026-10-16",
  "verification": "source-reviewed",
  "requirements": [
    "Install with r2pm or use a plugin build matching the radare2 major/minor ABI; the reviewed README reports CI against radare2 6.2.2 and git master.",
    "Mobile or remote operation needs a reachable Frida target, such as frida-server over USB or TCP. The plugin bundles the host Frida library; separate host frida-tools are not required."
  ]
}
```

| 字段 | 示例中的选择 |
| --- | --- |
| `id` | 小写短名，同时是详情页路径 `/resources/r2frida/`。 |
| `category` | 工具族 `dynamic-analysis`；`python3 scripts/catalog.py --list-categories` 列出当前使用的值。 |
| `relationship` | `foundation`（基础工具）：独立于 REA 工作的成熟工具。其文档没有确立与 REA 的关联，因此不暗示任何关联。 |
| `kind` | `tool`，与 category 和 relationship 分别独立选择。 |
| `targets` | `app` 和 `binary`，因为 README 涵盖桌面与移动进程。 |
| `description_en` / `description_zh` | 用自己的话写出读者能用它做什么，不照搬宣传文字。 |
| `requirements` | 复核文档中写明的安装与平台条件，必要时注明复核时的版本。 |

如何选择 `kind`、`relationship`、`category` 和 `targets`，见[中文贡献指南](../CONTRIBUTING.zh-CN.md#kindrelationshipcategory-与-targets)；全部字段和取值见[目录格式（英文）](../data/README.md)。

## 4. 添加中文名称与使用条件

网站的中文名称和使用条件保存在 [translations.zh-CN.json](../site/translations.zh-CN.json)，以记录 ID 为键。英文 `requirements` 的每一项都对应一项中文，顺序相同。`name` 可以省略：r2frida 保留上游名称；不提供 `name` 时，网站显示英文名称。译法请沿用[术语对照](../CONTRIBUTING.zh-CN.md#术语对照)。

```json
"r2frida": {
  "requirements": [
    "通过 r2pm 安装，或使用与 radare2 主版本和次版本 ABI 匹配的插件构建；复核时 README 说明 CI 测试覆盖 radare2 6.2.2 和主分支。",
    "移动或远程操作需要可连接的 Frida 目标，例如通过 USB 或 TCP 连接的 frida-server。插件包含主机端 Frida 库，无需单独安装主机端 frida-tools。"
  ],
  "name": "r2frida"
}
```

## 5. 重新生成并检查

在仓库根目录运行：

```sh
python3 scripts/build_readme.py
python3 scripts/build_repository_index.py
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/build_site.py
node --check site/app.js
```

两个被编辑的源文件与生成结果的对应关系：

| 编辑的源文件 | 生成命令 | 输出 | r2frida 带来的变化 |
| --- | --- | --- | --- |
| `data/tool-resources.json`、`site/translations.zh-CN.json` | `build_readme.py` | `README.md`、`README.zh-CN.md` | 条目出现在“原生二进制”分区并标注“也适用：应用”，资源计数随之更新。分区由 category 决定；中文 README 使用中文名称。 |
| `data/tool-resources.json` | `build_repository_index.py` | `docs/repositories/` 各页及两个 README 中的仓库计数 | `dynamic-analysis.md` 及其中文页的 nowsecure/r2frida 一行加上“精选”链接，因为 `url` 正是一个已扫描仓库的根地址。其他资源不会改动这些文件。 |
| 两者 | `build_site.py` | `dist/`（Git 忽略） | 首页目录、`/resources/r2frida/`、`/zh/resources/r2frida/` 和站点地图。 |

提交两个源文件，以及生成命令在 `README.md`、`README.zh-CN.md` 和 `docs/repositories/` 下改动的文件；不要提交 `dist/`。如果案例还对应[案例合集覆盖记录](case-coverage.zh-CN.md)，还需修改 `data/case-coverage.json`，并运行 `python3 scripts/build_case_coverage.py` 重新生成摘要。

查看页面时，用 `python3 -m http.server 8000 --bind 127.0.0.1 --directory dist` 启动预览，打开 `http://127.0.0.1:8000/resources/r2frida/` 和 `/zh/resources/r2frida/`。CI 还会运行生产构建和浏览器冒烟测试，完整步骤见英文指南的[目录更新部分](../CONTRIBUTING.md#update-the-catalog)；本地缺少 Chrome 时冒烟测试会跳过。

## 6. 提交 pull request

把分支推送到你的 fork，向 `main` 提交 pull request，并按模板填写：原始链接、类型、目标领域、简短说明、固定版本的证据与复核日期、尚未核实的内容，以及运行过的命令。基础分支可信代码执行的[规则审核（英文）](automation.md#pull-request-review)会检查结构、重复项、来源字段和常见隐私问题，`Catalog checks` 运行校验。之后由维护者审核资源是否相关、说法是否属实；检查通过不代表批准或合并。

如果资源有需要维护者判断的问题，例如包含源自专有软件的内容，请以草稿（draft）形式提交 pull request，并在开头说明顾虑。Pull request 是公开的：粘贴任何内容前，请删除令牌、Cookie、账户标识、本地路径和私人抓包数据。
