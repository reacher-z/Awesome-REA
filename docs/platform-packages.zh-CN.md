# 各平台发行包

[English](platform-packages.md) · [文档索引](README.zh-CN.md)

状态：Beta，依据公开 Release 元数据与 README 收集。口径版本：`platform-packages-v1`。采集脚本：[`scripts/collect_platform_packages.py`](../scripts/collect_platform_packages.py)。数据：[`data/platform-packages.json`](../data/platform-packages.json)。

本快照记录每条**精选软件**在哪些操作系统发布安装包，覆盖 `case-study`、`project`、`tool`、`integration` 四类软件条目。主页增加“发行包”筛选和卡片上的一行平台信息；详情页在“发行包”下列出收集到的产物。

## 1. 平台键

| 键 | 含义 |
| --- | --- |
| `windows` | `.exe`、`.msi`、`.msix`、`.appx`、`.appinstaller`，或文件名带 Windows 标识的归档 |
| `macos` | `.dmg`、`.pkg`，或文件名带 macOS/Darwin 标识的归档 |
| `linux` | `.AppImage`、`.deb`、`.rpm`、`.flatpak`、`.snap`、`.pkg.tar.*`，或文件名带 Linux 标识的归档 |
| `android` | `.apk`、`.aab`、`.xapk`、`.apks`，或文件名带 Android 标识的归档；Alpine 的 `.apk` 记为 Linux |
| `ios` | `.ipa`，或文件名带 iOS 标识的归档 |
| `web` | WebAssembly/Emscripten 产物，或文件名带 web 标识的归档 |
| `freebsd` | 文件名带 FreeBSD 标识的产物 |
| `source` | 源码归档，以及跨平台包管理器命令（`cargo`、`pip`、`npm` 等） |
| `other` | 无法从文件名判断操作系统的 Release 产物 |

## 2. 收集方法

- 使用 GitHub REST：最新稳定版 Release；仅当最新预发布版比稳定版更新时，再纳入该预发布版。
- Release 产物会过滤校验和、签名、符号、SBOM、`.zsync` 元数据、过小文件和自动生成的源码归档。
- README 链接只在指向目标软件时计入；安装命令也必须匹配目标包名。
- 非 GitHub 条目保留为 `source: "not-collected"`，让“未采集”和“没有包”保持可见的区别。
- 本快照不采集自动扫描索引：扫描只保留 README 章节信号，没有 Release 产物。

## 3. 数据结构

每条记录包含 `id`、`repo`、`source`、`checked_at`、`release_scope`、`platforms`、`platform_keys`、`reason`。每个平台桶是描述对象列表：

```json
{
  "platform": "windows",
  "name": "tool-1.2.3-x64.msi",
  "url": "https://github.com/owner/tool/releases/download/v1.2.3/tool-1.2.3-x64.msi",
  "kind": "release-asset",
  "tag": "v1.2.3",
  "published_at": "2026-10-01T12:00:00Z"
}
```

安装命令的 `kind` 为 `install-command`，没有 URL；README 链接为 `readme-link`。

当前数量从数据文件读取，不在本文维护副本：

```bash
python3 - <<'PY'
import json
d = json.load(open('data/platform-packages.json', encoding='utf-8'))
print(d['meta']['platform_entry_counts'])
print(d['meta']['platform_package_counts'])
PY
```

## 4. 局限

- 包文件名或安装命令不证明它能安装、能运行或与目标软件兼容。
- 产物命名可能含糊；没有平台标识的通用 `.zip`/`.7z` 记为 `other`，不猜测平台。
- 只使用最新稳定版（以及更新的预发布版）；较旧 Release 里有产物也不算当前可用。
- 非 GitHub 页面和自动扫描索引不在此次采集范围。
- 这是元数据证据，不是运行验证；本目录不安装或运行这些包。

## 5. 重新生成

```bash
python3 scripts/collect_platform_packages.py          # 使用本地包缓存
python3 scripts/collect_platform_packages.py --fresh  # 忽略缓存全部重抓
python3 scripts/build_site.py
```

`build_site.py` 把 `platforms`、`platform_counts` 和 `platform_packages` 合并进生成的目录数据；精选软件条目缺少快照时直接报错。
