# Fidelity document evidence

[简体中文](fidelity-evidence.zh-CN.md) · [Evidence classes](evidence-classes.md) · [Artifact evidence](artifact-evidence.md)

Status: review aid, collected from public text at the reviewed commit. It does not install, run or reproduce an application.

`scripts/fidelity_scan.py` reads a curated entry's pinned `evidence_url` README and up to five README-linked Markdown/RST/TXT documents, plus up to two second-hop documents whose path names an explicit comparison, coverage or limits record. It prints line-addressed excerpts for five signal families and never writes into `data/`.

## Signal families

| Key | What the line suggests |
| --- | --- |
| `coverage` | A feature matrix, compatibility table, supported/unsupported formats or coverage statement |
| `workflow` | A save/reopen, import/edit/export, end-to-end or playthrough path |
| `comparison` | Differential, oracle, byte-match or original/reference comparison |
| `limits` | Known issues, missing features, incomplete workflows or stated exclusions |
| `route` | Clean-room, reimplementation, decompilation, static recompilation or compatibility-layer wording |

A matching line is a pointer to read, not a conclusion. The excerpt includes one line before and up to two after; the URL opens the same line at the pinned commit.

## Run

```sh
python3 scripts/fidelity_scan.py --ids storytold/lightcraft-case --pretty
python3 scripts/fidelity_scan.py --ids a,b,c > /tmp/fidelity.json
python3 scripts/fidelity_scan.py --repo owner/name --commit <40-char sha> --path README.md
```

`--ids` reads `data/rea-resources.json` and `data/tool-resources.json`. `--repo` and `--commit` accept an id outside the catalog. The script uses `GITHUB_TOKEN`, or the token from `gh auth token`; it sends it only to `api.github.com`.

## Output

One object per id, or an array when `--ids` names several:

```json
{
  "schema_version": 1,
  "id": "storytold/lightcraft-case",
  "repo": "owner/name",
  "commit": "…",
  "readme_path": "README.md",
  "readme_url": "https://github.com/…/blob/<commit>/README.md",
  "documents": [{"path": "docs/parity.md", "readable": true, "bytes": 1200}],
  "signals": {"coverage": [], "workflow": [], "comparison": [], "limits": [], "route": []},
  "signal_counts": {"coverage": 0, "workflow": 0, "comparison": 0, "limits": 0, "route": 0},
  "scope": "README + up to 5 linked documents + up to 2 targeted second-hop documents; not an exhaustive repository crawl",
  "runtime_verified": false,
  "generated_at": "…"
}
```

A README that cannot be read at the pinned commit is reported as an error for that id and sets a non-zero exit code; other ids still run when several are requested.

## Limits

- The scan reads text, not behavior. A matched sentence can be outdated, aspirational or marketing copy.
- The link selection is heuristic and capped; it does not crawl the repository, wiki, issues, tests or videos.
- The output is not an evidence class and does not change `data/evidence-classes.json`. Class assignments and Class 0 reviews remain separate reviewed records.
- Human review stays separate: record which excerpts were checked, what they support and what remains unknown. A signal is not a runtime reproduction.
