# Case collection coverage

[简体中文](case-coverage.zh-CN.md) · [Machine-readable ledger](../data/case-coverage.json)

Reviewed 2026-10-18 (UTC). **591 collection occurrences** become **589 inventory units** after 2 documented duplicate merges. These are reports, tools, papers, discussions and ideas—not a count of unique verified projects.

Project identity resolution is incomplete, so the unique-project count is `null`, not zero. English/Chinese copies of one upstream entry are counted once. Separate reports about one project remain separate units unless an explicit alias decision joins them.

## Frozen sources

| Collection snapshot | Occurrences | Linked GitHub repositories | Catalog record |
| --- | ---: | ---: | --- |
| [songshikang0111/awesome-REA-cases · 3a1c5cdfaa3f](https://github.com/songshikang0111/awesome-REA-cases/tree/3a1c5cdfaa3f2db0dd4f587208f8870eb633de23) | 423 | 50 | [awesome-rea-cases](https://awesomerea.org/resources/awesome-rea-cases/) |
| [yibie/awesome-rea · 6df1bc922ac6](https://github.com/yibie/awesome-rea/tree/6df1bc922ac6b92dcd1b2f905c94d8cc4f3b5a3e) | 28 | 11 | [yibie-awesome-rea](https://awesomerea.org/resources/yibie-awesome-rea/) |
| [HaozheH3/awesome-rea-games · 4316a4ce86fd](https://github.com/HaozheH3/awesome-rea-games/tree/4316a4ce86fdd851f0180ffee87dc336851bf5b6) | 140 | 137 | [haozhe-awesome-rea-games](https://awesomerea.org/resources/haozhe-awesome-rea-games/) |

The ledger retains pinned file URLs, Git blob IDs, SHA-256 digests and byte counts. It describes only these enumerated snapshots, not later upstream changes or the whole field. Full upstream descriptions and README bodies are not republished.

Repository counts use normalized GitHub repository, tree and file links within each collection. They do not merge inventory units or establish unique projects. For a game-organized table, each project row is an occurrence; a game heading or a shared repository does not make two rows the same report.

## Counts and states

| State | Occurrences | Inventory units | Meaning |
| --- | ---: | ---: | --- |
| Already curated (`already-curated`) | 72 | 71 | Full-scope identity mapping to a catalog resource or paper; not independent runtime reproduction. |
| Pending (`pending`) | 448 | 447 | Primary review or complete catalog coverage remains pending; partial matches stay here. |
| Insufficient evidence (`insufficient-evidence`) | 71 | 71 | An idea, request or unsupported reconstruction claim is retained as a lead. |

78 occurrences have catalog links. They reference 70 distinct resource IDs and 1 paper ID. Match scope is recorded separately; do not add these populations as unique projects.

This ledger records a new primary-source review for 87 inventory units. Other catalog-linked entries inherit the catalog’s separate source-review record; a link does not mean the entire collection report was reviewed again. No runtime experiment was independently reproduced for this ledger.

Repository README scan IDs and counts are deliberately absent. A successful README fetch, an upstream list entry and a source-reviewed case are different facts.

## Primary-reviewed cases

| Case | State | Primary evidence |
| --- | --- | --- |
| Universal Modder | Already curated | [Source](https://github.com/rehan-remade/universal-modder/blob/6a8865ae171b406f50892c7f46fc5f45655269eb/README.md) |
| PlxNative: reconstructing a native webOS media-client interface | Already curated | [Source](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| Agent decompilation: a byte-matching retrospective | Already curated | [Source](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote: Siri Remote protocol reconstruction | Already curated | [Source](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| BaoCut Slides: adapting an interactive web editor | Already curated | [Source](https://github.com/JimLiu/baocut/blob/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/docs/design/slides/slides-design.md) |
| Urban Terror in the browser | Insufficient evidence | [Source](https://x.com/levelsio/status/2106150888289009666) |
| Flutter build identification | Already curated | [Source](https://github.com/morluto/rea/pull/1582) |
| MIPS ELF analysis through Ghidra | Already curated | [Source](https://github.com/morluto/rea/issues/1620) |
| PSP static ELF analysis through Ghidra | Already curated | [Source](https://github.com/morluto/rea/issues/1330) |
| Touhou reconstructions: an agent-driven method across three games | Already curated | [Source](https://github.com/morluto/rea/blob/c12d9eda87aa5a022ee7e18ea96d8d03bfd12e96/website/evidence/touhou-reconstruction-method.md) |
| Dinosaur runner: recovering one acceleration rule | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| ArtCraft: not proven Adobe or Office reverse engineering | Insufficient evidence | [Source](https://getartcraft.com/apps) |
| Obsidian ASAR: large-package analysis | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/746) |
| Unity/Valheim assemblies | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/1801) |
| Large multidex Android APK | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/893) |
| .NET NativeAOT recovery request | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/744) |
| Windows Calculator: reconstructing percentage rules | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Android ApiDemos: tracing Java methods from an APK | Insufficient evidence | [Source](https://github.com/morluto/rea/pull/738) |
| Static HarmonyOS package inventory | Already curated | [Source](https://github.com/morluto/rea/pull/1447) |
| Firmware analysis | Already curated | [Source](https://github.com/morluto/rea/pull/741) |
| Codex browser annotations: finding the interaction bridge | Insufficient evidence | [Source](https://x.com/dotey/status/2109417222724600172) |
| Browserbase plugin: re-hosting Claude in Chrome’s browser bridge | Already curated | [Source](https://github.com/browserbase/claude-code-plugin/blob/b399af34a1b1cc365d1e1c0089823c4fa5e10ea5/forwarding-server.js) |
| pi-computer-use: desktop interaction for other models | Insufficient evidence | [Source](https://github.com/injaneity/pi-computer-use/blob/67e9e2f77643f84605b738a3198048a88e92190e/README.md) |
| Background Computer Use in Swift | Insufficient evidence | [Source](https://github.com/actuallyepic/background-computer-use/blob/52116acfe0f2f57174f5e0166881abe944cb6eeb/README.md) |
| GameCube/Wii PowerPC support request | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/1741) |
| Super Mario Sunshine: a native PC port from an AI-assisted decompilation | Already curated | [Source](https://github.com/chasem-dev/sms-pc-port/blob/a2ff4eef099b22b2af487d1b5e3ac09ffe667d31/README.md) |
| Apple Preview: adding AI directly to a compiled app | Insufficient evidence | [Source](https://github.com/Pasta-Lab/edit-my-app/blob/7f469c1f179e2552cd3c5b46ab29b21aeadc838f/README.md) |
| wine-uwp: running packaged Windows Store apps on a patched Wine | Already curated | [Source](https://github.com/designgears/wine-uwp/blob/1cf79d025e0c18167de803820345a1c5f82fd17d/README.md) |
| CF632BLE: a local client from scale-protocol research | Already curated | [Source](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| Netflix/Prime: a reported unified streaming interface | Insufficient evidence | [Source](https://x.com/HigbeyMyrta/status/2109596534350524664) |
| fowlbrowser: an existing-session browser bridge for agents | Insufficient evidence | [Source](https://github.com/argofowl/FowlBrowser/blob/18f7519fa27289885c95b67eff714401ffff51f0/README.md) |
| OpenSetter: rebuilding comment-to-DM flows with an AI setter | Insufficient evidence | [Source](https://github.com/xbirimensah/opensetter/blob/40dc5ae2fde0b3930e6b59132eaf061edb0da0a8/README.md) |
| zee-rp: reconstructing supported Axure RP 11 document operations | Already curated | [Source](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| Classic shooters: reported AI-assisted browser ports | Insufficient evidence | [Source](https://x.com/i/status/2109639780577190171) |
| Nanolathe: a documented Total Annihilation engine reimplementation | Already curated | [Source](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| cooler-lcd: a Thermalright display protocol implementation | Already curated | [Source](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Helm Chart API v2: an AI-assisted specification draft | Pending | [Source](https://github.com/mattfarina/specs/blob/7d0395726d712e654a9aaf167603e82007811517/charts/v2.md) |
| AYN Odin 2 Portal: Codex-assisted native Omarchy bring-up | Pending | [Source](https://github.com/TechLuddite/omarchy-mobile-odin2/blob/00d11efc018971f6bab711e7952ff184cad333c2/README.md) |
| Virtual Desktop Streamer: rehosting the platform layer on Linux | Already curated | [Source](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| Open Claude UI: REA-informed interface reference components | Already curated | [Source](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| Eleven | Already curated | [Source](https://github.com/Zfinix/eleven/blob/94760718dfd741ba93fcc9b591eb39a96c034103/README.md) |
| GTM tool: a reported REA-assisted lead and email workflow | Insufficient evidence | [Source](https://github.com/tashfeenahmed/kinetic/blob/6ccbff87d190aea8e11be993e25783f099b55a93/README.md) |
| TCLimate: reconstructing selected TCL Home cloud controls | Already curated | [Source](https://github.com/umarz317/TCLimate/blob/2a33c2013dbf3f297238131ca9eb6e287b2beb67/Docs/Investigation.md) |
| Tea-export website: reported REA-assisted rebuild | Insufficient evidence | [Source](https://x.com/i/status/2110010062597230838) |
| Ledger Reborn: an independent accounting app informed by QuickBooks study | Already curated | [Source](https://github.com/lxistired/ledger-reborn/blob/d7f6b8a1f4ad6c4ae8b10100d1c93cf15940c21d/docs/CASE_STUDY.md) |
| Visor: an independent Ray-Ban Meta glasses client | Already curated | [Source](https://github.com/macedonga/visor/blob/8caaa12df919c014c249efb71fdfa32b263f6c3e/README.md) |
| Profound: a reported REA-assisted SaaS reconstruction | Insufficient evidence | [Source](https://github.com/yaojingang/profound-clone/blob/93e87c901b9c51f444b243110dd643e066aa6e22/README.md) |
| GAMEKB-K17: reconstructing a macropad configuration protocol | Already curated | [Source](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| IsaacRecomp: translating Flash game bytecode to native C++ | Already curated | [Source](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| Feishu: an author-reported isolated second app instance | Already curated | [Source](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Mi Health: timestamp repair and a cloud-data exporter | Insufficient evidence | [Source](https://github.com/LilZeeCN/mi-health-exporter/blob/1dc9274a90ccc83f02cbb3706aae2a4d55c8e90a/README.md) |
| Plustek 8200i / ThinkPad MIPI: improve Linux drivers using Windows reference behavior | Pending | [Source](https://github.com/cschalle/hw-harness/blob/093afc5c576c200f29b771d01624a327d0ff1806/examples/plustek-film-scanner/README.md) |
| UU Remote on Linux: an unofficial protocol implementation | Already curated | [Source](https://github.com/VallierDev/uu-remote-linux/blob/696cf10e334b2e7fe1afcb698b354c09ee328447/README.en.md) |
| REA Reconstruction Companion: connect evidence to specifications, implementation and acceptance | Pending | [Source](https://github.com/ShadowSwaps/REA-Reconstruction-Companion/blob/590e65dd99596c7fb66598eaa5d6c051c2ec9a5f/evals/reference/reconstruction/README.md) |
| NJFE: a Soulear camera protocol bridge for desktop inspection | Already curated | [Source](https://github.com/WildweaselMS/NJFE/blob/992866c6609f8c813f459ff79840cf04d5883f8e/README.md) |
| LeanREA | Already curated | [Source](https://github.com/aicodeking/leanrea/blob/09ba4aa0217f82cd880f855a60b877f59f39b22b/README.md) |
| Super Mario 64 DS: matching decompilation with relocation checks | Already curated | [Source](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| GoldenEye 007: an agent-assisted native port from a decompilation | Already curated | [Source](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip: an AI-assisted Super Smash Bros. native port | Already curated | [Source](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp: static recompilation with explicit mode limits | Already curated | [Source](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| KartPad: platform integration for a Mario Kart Wii recompilation | Already curated | [Source](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |
| Super Mario 64: ROM reconstruction with explicit comparison gates | Already curated | [Source](https://github.com/n64decomp/sm64/blob/9921382a68bb0c865e5e45eb594d9c64db59b1af/README.md) |
| 🗡️ The Legend of Zelda: Breath of the Wild — zeldaret/botw | Pending | [Source](https://github.com/zeldaret/botw/blob/e78c02499d0f108ae9c00158198289764c5980fe/README.md) |
| 🗡️ The Legend of Zelda: Ocarina of Time — zeldaret/oot | Pending | [Source](https://github.com/zeldaret/oot/blob/8a3634ca774a9b58d822cbc2cc09309f31eac6a4/README.md) |
| Zelda 64: Recompiled — a native Majora’s Mask port without a full source decompilation | Already curated | [Source](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/b65c482ed672258eb684ab94a4e8c8aa662615ee/README.md) |
| Majora’s Mask: matching US N64 decompilation | Already curated | [Source](https://github.com/zeldaret/mm/blob/bf6bd9d0d3a90fe2f8960e034fbfd328e8bdef22/README.md) |
| 🗡️ The Legend of Zelda: The Minish Cap — zeldaret/tmc | Pending | [Source](https://github.com/zeldaret/tmc/blob/6fb6dfb4a7efbe24d0fd1dda5097af6131faacde/README.md) |
| 🚀 Metroid Prime — AxioDL/metaforce | Pending | [Source](https://github.com/AxioDL/metaforce/blob/de8fc69bd7f345d6cf5f0c8fc2798295e22522d3/README.md) |
| 🦔 Sonic Mania — RSDKModding/Sonic-Mania-Decompilation | Pending | [Source](https://github.com/RSDKModding/Sonic-Mania-Decompilation/blob/9dc699428420d752af9767bdb13f585ee0881bc0/README.md) |
| Unleashed Recompiled: translating Xbox 360 game code and shaders | Already curated | [Source](https://github.com/hedge-dev/UnleashedRecomp/blob/cf829a9eca8fb680fba4b0409ddeb6ca92f22e3c/README.md) |
| OpenGOAL: recovering GOAL code and rebuilding the Jak games | Already curated | [Source](https://github.com/open-goal/jak-project/blob/32c3cf73970f885c0a588623208232db72a74a58/README.md) |
| LEGO Island: source reconstruction with separately reported exact rebuilds | Already curated | [Source](https://github.com/isledecomp/isle/blob/8119bd013645972c72480e4de21529f1e91ce5c7/README.md) |
| ⚡ Pokémon FireRed — pret/pokefirered | Pending | [Source](https://github.com/pret/pokefirered/blob/037335f4c725d7c9aecdac87066f2002b4bd7e14/README.md) |
| DevilutionX: porting Diablo’s reconstructed engine | Already curated | [Source](https://github.com/diasurgical/DevilutionX/blob/94433061f847d22863e5d705c398f7c13d7bab85/README.md) |
| OpenMW: replacing Morrowind’s engine while reusing original content | Already curated | [Source](https://github.com/OpenMW/openmw/blob/5fdc0f1c4d1d07575f9b360b8cf1d6562232bf8e/README.md) |
| 🧙 Ultima Underworld: The Stygian Abyss — abedegno/underworld-exhumed | Pending | [Source](https://github.com/abedegno/underworld-exhumed/blob/e5deadd6945b492636aadccc14f52caa908b4186/README.md) |
| 🧙 Paper Mario — pmret/papermario | Pending | [Source](https://github.com/pmret/papermario/blob/1104f1f71b824042a5fa1f958f2d861b603320fd/README.md) |
| 🥊 Super Smash Bros. Melee — doldecomp/melee | Pending | [Source](https://github.com/doldecomp/melee/blob/f0cdbb0a7046aea44c7177fd72abf33c3d2af4d4/.github/README.md) |
| ⚔️ Perfect Dark — perfect-dark-pc-port/perfect_dark | Pending | [Source](https://github.com/perfect-dark-pc-port/perfect_dark/blob/32a1cb9f268dd3ac73016801025c6bbbfa20130f/README.md) |
| Perfect Dark: matching Nintendo 64 decompilation | Already curated | [Source](https://github.com/n64decomp/perfect_dark/blob/169ed48bdcbfb3b568b028bd5bebb27680073514/README.md) |
| REDRIVER2: reconstructing Driver 2 through a PlayStation compatibility layer | Already curated | [Source](https://github.com/OpenDriver2/REDRIVER2/blob/b2d8857426f815007486def9bd23f9a6007a2c64/README.md) |
| Snowball War: a bounded REA-assisted minigame reconstruction | Already curated | [Source](https://github.com/tuunanet/rea-ski-or-die-reconstruction/blob/0eac0671c90e21a16e663da7772b60710101ef7f/README.md) |
| SpaceCadetPinball: decompiled game logic adapted to SDL2 | Already curated | [Source](https://github.com/k4zmu2a/SpaceCadetPinball/blob/cb9b7b886244a27773f66b0b19fdc2998392565e/README.md) |
| Open Scrantic: reconstructing the Johnny Castaway screensaver engine | Already curated | [Source](https://github.com/glauberlima/open-scrantic/blob/2db75008931eb744f79d0c3fb12e0d89950466ff/README.md) |

## Partial coverage and aliases

Partial or related catalog mappings:

- `song:touhou-reconstruction` — The REA-published essay, its pinned evidence notes and merged REA PR #1475 cover this combined report: TH08, TH095 and TH04 milestones, ledger counts under separate definitions, and the TH08 floating-literal oracle gap. The full mapping is to that method case; the TH08 project record remains a partial match. Results stay author-reported, the TH095 and TH04 repositories were not separately reviewed, and no build or runtime reproduction is claimed.
- `song:artcraft-boundary` — The ArtCraft apps page says every Crafting App is written from scratch in Rust and makes no reverse-engineering claim; the four reviewed READMEs describe clean-room implementations from public specifications and observed behavior, with no proprietary code. No primary source documents decompilation or recovery of Adobe or Microsoft software, and none establishes the third-party REA attribution. PhotoCraft, WordCraft, GridCraft and DeckCraft keep partial mappings to their implementation records; other listed apps such as FilmCraft, LightCraft and CADCraft have public repositories not reviewed here. Retain the lead without a full mapping; this is not a judgment of the apps’ quality.
- `song:schaller-opticfilm-thinkpad-linux` — The existing scanner investigation and the separate ThinkPad IMX471 tuning/driver case cover two bounded components of this report. Their mappings remain partial: neither asserts complete scanner/camera behavior, all-device compatibility or independent runtime reproduction.
- `song:rea-reconstruction-companion` — The Pocket Tasks mapping covers one maintainer-informed command-line reconstruction with published candidate and bounded comparison evidence. It does not cover the broader Companion workflow, other examples or model/host effectiveness. Prior source exposure, pending human review and the historical instruction-packet hash remain explicit; no independent runtime reproduction is established.
- `hao-games:row-020` — Pinned README, build rules, checksum and CI configuration support this US N64 Majora’s Mask decompilation report. The full mapping covers this repository, not the post’s linked archive; a related mapping records that Zelda 64: Recompiled credits it for headers and functions but is a separate static recompilation. WIP status, the original-ROM dependency, the absent license and project-reported matching remain explicit.
- `hao-games:row-134` — The TH08 reconstruction is curated, but this separate WebAssembly companion repository is not covered as the same artifact. Its own implementation and deployment claims remain pending.
- `hao-games:row-136` — Only the official TH04 bullet-ring helper showcase is covered. This collection row identifies a broader reconstruction repository, so full repository/game coverage remains pending.
- `hao-games:row-137` — Only the official DX-Ball sound-pan function showcase is covered. That does not establish curation or completion of this broader game-reconstruction repository.

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
