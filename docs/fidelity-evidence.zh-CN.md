# 文档保真度证据

[English](fidelity-evidence.md) · [证据档位](evidence-classes.zh-CN.md) · [研究产物与许可证据](artifact-evidence.zh-CN.md)

状态：复核辅助工具，只读取复核提交上的公开文本；不安装、不运行、不重建任何应用。

`scripts/fidelity_scan.py` 读取精选条目 `evidence_url` 所固定的 README，以及最多 5 份 README 链接的 Markdown/RST/TXT 文档，再从这些文档跟进最多 2 份路径明确写着对照、覆盖或局限的第二跳文档。它输出五类信号的带行号摘录，且从不写入 `data/`。

## 信号类别

| 键 | 该行可能意味着 |
| --- | --- |
| `coverage` | 功能矩阵、兼容性表、支持／不支持的格式或覆盖说明 |
| `workflow` | 保存后重开、导入／编辑／导出、端到端或通关路径 |
| `comparison` | 差分、oracle、逐字节匹配或与原版／参考实现的对照 |
| `limits` | 已知问题、缺失功能、未完成工作流或明确排除项 |
| `route` | 净室、重新实现、反编译、静态重编译或兼容层措辞 |

命中一行只表示「需要去读」，不是结论。摘录包含该行前一行与后两行；链接指向固定提交的同一行。

## 运行

```sh
python3 scripts/fidelity_scan.py --ids storytold/lightcraft-case --pretty
python3 scripts/fidelity_scan.py --ids a,b,c > /tmp/fidelity.json
python3 scripts/fidelity_scan.py --repo owner/name --commit <40 位 sha> --path README.md
```

`--ids` 读取 `data/rea-resources.json` 与 `data/tool-resources.json`；`--repo` 与 `--commit` 可处理目录外条目。脚本使用 `GITHUB_TOKEN` 或 `gh auth token`，且只把令牌发给 `api.github.com`。

## 输出

单个 id 输出一个对象；`--ids` 指定多个时输出数组，字段与英文文档相同。无法在固定提交读取 README 时，该 id 记为错误并返回非零退出码；其他 id 仍会继续运行。

## 局限

- 只读文本，不读行为。命中的句子可能过时、只是计划或营销措辞。
- 链接选择是启发式且有上限；不爬仓库、wiki、issue、测试或视频。
- 输出不是证据档位，也不修改 `data/evidence-classes.json`；档位与 Class 0 复核仍是独立的人工记录。
- 人工判断仍须单独记录：哪些摘录被核对、支持什么、仍不知道什么。信号不等于运行复现。
