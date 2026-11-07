# Platform release packages

[简体中文](platform-packages.zh-CN.md) · [Documentation](README.md)

Status: Beta, collected from public release metadata and READMEs. Spec version: `platform-packages-v1`. Collector: [`scripts/collect_platform_packages.py`](../scripts/collect_platform_packages.py). Data: [`data/platform-packages.json`](../data/platform-packages.json).

This snapshot records **where each curated software entry publishes packages**, by operating system. It covers all curated software kinds (`case-study`, `project`, `tool`, `integration`). The homepage shows a **Release packages** filter and a package line on each card; entry pages list the collected assets under **Release packages**.

## 1. Platform keys

| Key | Meaning |
| --- | --- |
| `windows` | `.exe`, `.msi`, `.msix`, `.appx`, `.appinstaller`, or a Windows-labelled archive |
| `macos` | `.dmg`, `.pkg`, or a macOS/Darwin-labelled archive |
| `linux` | `.AppImage`, `.deb`, `.rpm`, `.flatpak`, `.snap`, `.pkg.tar.*`, or a Linux-labelled archive |
| `android` | `.apk`, `.aab`, `.xapk`, `.apks`, or an Android-labelled archive; Alpine `.apk` stays Linux |
| `ios` | `.ipa` or an iOS-labelled archive |
| `web` | WebAssembly/Emscripten assets or a web-labelled archive |
| `freebsd` | FreeBSD-labelled assets |
| `source` | Source archives and cross-platform package-manager commands (`cargo`, `pip`, `npm`, …) |
| `other` | A release asset whose OS cannot be established from its name |

## 2. Collection method

- GitHub REST: the newest stable release, plus the newest prerelease only when it is newer than that stable release.
- Release assets are filtered for checksums, signatures, symbols, SBOMs, `.zsync` metadata, tiny files and generated source archives.
- README links count only when they name the target software; install commands are matched to the target package too.
- Non-GitHub entries are kept with `source: "not-collected"`; a missing source is visible rather than treated as “no packages”.
- The automated scan index is not collected in this snapshot: it retains README section signals, not release assets.

## 3. Data shape

Each entry has `id`, `repo`, `source`, `checked_at`, `release_scope`, `platforms`, `platform_keys` and `reason`. Each platform bucket is a list of descriptors:

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

Install commands have `kind: "install-command"` and no URL. README links use `kind: "readme-link"`.

Read current counts from the data rather than copying them into this guide:

```bash
python3 - <<'PY'
import json
d = json.load(open('data/platform-packages.json', encoding='utf-8'))
print(d['meta']['platform_entry_counts'])
print(d['meta']['platform_package_counts'])
PY
```

## 4. Limits

- A package filename or install command does not prove that it installs, runs or matches the target software.
- Asset names can be ambiguous. A generic `.zip`/`.7z` without an OS hint is `other`, not a guessed platform.
- Only the newest stable release (and a newer prerelease) is used; an older release with assets is not treated as current.
- Non-GitHub pages and the automated scan index are not collected here.
- This is metadata evidence, not runtime testing. The catalog does not install or run the packages.

## 5. Regeneration

```bash
python3 scripts/collect_platform_packages.py          # use the local package cache
python3 scripts/collect_platform_packages.py --fresh  # refetch every repository
python3 scripts/build_site.py
```

`build_site.py` merges `platforms`, `platform_counts` and `platform_packages` into the generated catalog. It fails when a curated software entry is missing from the snapshot.
