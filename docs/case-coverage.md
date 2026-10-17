# Case collection coverage

[简体中文](case-coverage.zh-CN.md) · [Machine-readable ledger](../data/case-coverage.json)

Reviewed 2026-10-17 (UTC). **372 collection occurrences** become **370 inventory units** after 2 documented duplicate merges. These are reports, tools, papers, discussions and ideas—not a count of unique verified projects.

Project identity resolution is incomplete, so the unique-project count is `null`, not zero. English/Chinese copies of one upstream entry are counted once. Separate reports about one project remain separate units unless an explicit alias decision joins them.

## Frozen sources

| Collection snapshot | Entries | Catalog record |
| --- | ---: | --- |
| [songshikang0111/awesome-REA-cases · 2c9ce9597f0a](https://github.com/songshikang0111/awesome-REA-cases/tree/2c9ce9597f0afcbafaa79de0293083224a974e91) | 344 | [awesome-rea-cases](https://awesomerea.org/resources/#awesome-rea-cases) |
| [yibie/awesome-rea · 6df1bc922ac6](https://github.com/yibie/awesome-rea/tree/6df1bc922ac6b92dcd1b2f905c94d8cc4f3b5a3e) | 28 | [yibie-awesome-rea](https://awesomerea.org/resources/#yibie-awesome-rea) |

The ledger retains pinned file URLs, Git blob IDs, SHA-256 digests and byte counts. It describes only these enumerated snapshots, not later upstream changes or the whole field. Full upstream descriptions and README bodies are not republished.

## Counts and states

| State | Occurrences | Inventory units | Meaning |
| --- | ---: | ---: | --- |
| Already curated (`already-curated`) | 35 | 34 | Full-scope identity mapping to a catalog resource or paper; not independent runtime reproduction. |
| Pending (`pending`) | 288 | 287 | Primary review or complete catalog coverage remains pending; partial matches stay here. |
| Insufficient evidence (`insufficient-evidence`) | 49 | 49 | An idea, request or unsupported reconstruction claim is retained as a lead. |

37 occurrences have catalog links. They reference 33 distinct resource IDs and 1 paper ID. Match scope is recorded separately; do not add these populations as unique projects.

This ledger records a new primary-source review for 23 inventory units. Other catalog-linked entries inherit the catalog’s separate source-review record; a link does not mean the entire collection report was reviewed again. No runtime experiment was independently reproduced for this ledger.

Repository README scan IDs and counts are deliberately absent. A successful README fetch, an upstream list entry and a source-reviewed case are different facts.

## Primary-reviewed cases

| Case | State | Primary evidence |
| --- | --- | --- |
| PlxNative: reconstructing a native webOS media-client interface | Already curated | [Source](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| Agent decompilation: a byte-matching retrospective | Already curated | [Source](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote: Siri Remote protocol reconstruction | Already curated | [Source](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| TH08: exact-source reconstruction and separately tested ports | Pending | [Source](https://github.com/N0zoM1z0/th08/blob/08c7f00f81e35db8206d917b14f47883930beef6/README.md) |
| Dinosaur runner: recovering one acceleration rule | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Windows Calculator: reconstructing percentage rules | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| CF632BLE: a local client from scale-protocol research | Already curated | [Source](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| zee-rp: reconstructing supported Axure RP 11 document operations | Already curated | [Source](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| Nanolathe: a documented Total Annihilation engine reimplementation | Already curated | [Source](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| cooler-lcd: a Thermalright display protocol implementation | Already curated | [Source](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Virtual Desktop Streamer: rehosting the platform layer on Linux | Already curated | [Source](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| Open Claude UI: REA-informed interface reference components | Already curated | [Source](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| GAMEKB-K17: reconstructing a macropad configuration protocol | Already curated | [Source](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| IsaacRecomp: translating Flash game bytecode to native C++ | Already curated | [Source](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| Feishu: an author-reported isolated second app instance | Already curated | [Source](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Super Mario 64 DS: matching decompilation with relocation checks | Already curated | [Source](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| GoldenEye 007: an agent-assisted native port from a decompilation | Already curated | [Source](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip: an AI-assisted Super Smash Bros. native port | Already curated | [Source](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp: static recompilation with explicit mode limits | Already curated | [Source](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| KartPad: platform integration for a Mario Kart Wii recompilation | Already curated | [Source](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |

## Partial coverage and aliases

Partial catalog mappings:

- `song:touhou-reconstruction` — The TH08 component is curated; TH04 and TH095 components in this combined report remain outside the mapping.
- `song:schaller-opticfilm-thinkpad-linux` — The scanner USB investigation is curated; the same collection entry also reports MIPI camera work that remains outside this catalog mapping.

Alias decisions:

- `song:mw2-decompilation`, `yibie:500-billion-tokens-later` → `song:mw2-decompilation` — Same Maurice Heumann decompilation retrospective; the primary article leaves the game unnamed, so a future draft must not assert the collection’s MW2 identity from that article alone.
- `song:decompwtf-agent-game-decompilation`, `yibie:decomp-wtf` → `song:decompwtf-agent-game-decompilation` — Same named decomp.wtf project; yibie supplies an additional repository lead, not independent verification.

## Updating this ledger

Review the pinned collection entry and its primary evidence before changing a state. Keep occurrence IDs stable, record explicit aliases, use typed full/partial/related catalog mappings, and leave unresolved project counts unknown. Collection titles are source labels, not verified capability claims.

```sh
python3 scripts/build_case_coverage.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The validator checks schemas, public URLs, pinned receipts, identifiers, aliases, catalog mappings and derived counts. It does not fetch sources or establish that upstream results are true.
