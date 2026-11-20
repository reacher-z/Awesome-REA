# FrontierCUA task-domain pilot

[简体中文](frontier-taxonomy.zh-CN.md) · [Proposal issue](https://github.com/reacher-z/Awesome-REA/issues/4516) · [Data classes](../data/README.md#data-records)

Status: pilot data, reviewed 2026-11-19. It is not a replacement for `targets` or `evidence_class`, and it is not shown on the website yet.

The pilot maps the **15 Class 0 records** in `data/evidence-classes.json` to one FrontierCUA v1.1 task field each. The taxonomy itself is copied from the `ruoxining/rea-tracker` audit snapshot at a pinned commit: 15 realms and 120 fields, kept in `data/frontier-taxonomy.json`.

## Data files

- [`data/frontier-taxonomy.json`](../data/frontier-taxonomy.json): the 15 realms, 120 fields, their definitions, example applications, and the taxonomy metadata and source URL.
- [`data/frontier-taxonomy-map.json`](../data/frontier-taxonomy-map.json): one entry per Class 0 record with `id`, `field`, `field_name`, a short reason and the rea-tracker evidence URL.

A record is mapped only when its reviewed software has a clear primary user task; unmapped records are left out rather than guessed. The pilot uses one field per record, even where a project supports several tasks.

## What it is for

The catalog's existing facets answer **what is reconstructed** (`targets`, `class`) and **how well the public evidence supports it** (`evidence_class`). The task field answers a different question: **what kind of computer-use work does the reconstruction support?** Examples:

| Record | Field | Realm |
| --- | --- | --- |
| `photocraft-case` | `R06.02` image editing and photo retouching | R06 media and creative work |
| `gridcraft-case` | `R04.03` spreadsheets | R04 office and documents |
| `cadcraft-case` | `R07.01` computer-aided design | R07 engineering and CAD |
| `openrct2-engine-case` | `R13.01` games | R13 games and interactive media |

## Limits

- The mapping is editorial. The rea-tracker rules are keyword-based, and a record can fit more than one task field.
- The pilot covers Class 0 only. It does not claim that other records have no task, and it does not assign task difficulty, reproduction scope or workload.
- The taxonomy is a research artifact, not a runtime test or a statement of feature parity.

## Next step

The [proposal issue](https://github.com/reacher-z/Awesome-REA/issues/4516) asks whether the facet belongs in the collection and which population should follow the pilot. If accepted, the next step is a reviewed mapping for a wider population, then a browse/filter surface; the pilot data is not wired into the site yet.
