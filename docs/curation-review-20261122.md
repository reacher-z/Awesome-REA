# Class-scoped curation review — 2026-11-22

This batch adds seven source-reviewed records to the curated catalog: two mobile-app, two website, one video, one animation and one game-dev record. It continues the promotion worksheet of 2026-11-20.

## Discovery and review scope

Bounded scans ran scripts/scan_sources.py with the public, non-fork and non-archived gates over six query groups (CapCut, Premiere and After Effects clones; SketchUp, AutoCAD, SolidWorks and Tinkercad; Flash Player, Animate and Shockwave; website reconstruction and pixel-perfect clones; Android reimplementations; Blender, Figma and WhatsApp clones), discovering 553 candidate repositories and reading 52 READMEs at pinned commits. The followed-source lead queue (67 batches, 12,807 identities, 8,932 still unreviewed) was screened for the sparse Data classes first. Manual review checked each shortlisted repository for a license file in the pinned tree, recent push dates and README scope claims; template copies sharing one description and paper project websites were set aside.

| Domain | Executed queries | Successful README reads | Scan snapshot SHA-256 |
| --- | ---: | ---: | --- |
| video | 3 | 9 | `740c6b29c2d6e5cedf762d3a6d1f390e855b19d3c3c692257eaf836e80bc9a2a` |
| 3d-design | 4 | 12 | `d5a381a159b01170b4a40f46d467cee096a831c210050e6ffb031853b56d8e92` |
| animation | 3 | 5 | `77af848f8f1bfd6be5e2dafb59721f691aec1903766a99f885eafd1175704d4e` |
| website | 2 | 9 | `de38e6be61e5ebb002543d184b7a55683405284f1fd20a4b72b4b646a1972340` |
| mobile-app-dev | 2 | 9 | `ef73107e22e894e9158c105c6338098856eba2b0b2e28295964965c1f5bb2737` |
| follow-up (Blender/Figma/WhatsApp) | 3 | 8 | `8ad30ac274ff5b1c48d654943e63712d2485082891bf30338dc7c24b101dd27d` |

## Promoted records

Each row links the immutable README reviewed for the record. The digest matches the README bytes at the reviewed commit. License files were checked separately in the pinned trees.

| Record | Data class | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `persona-im-messaging-case` | `mobile-app-dev` | [chris-horner/Persona-IM](https://github.com/chris-horner/Persona-IM/blob/c486c9d972b5197bf72d1f78b24d2838352f1424/README.md) | `10b83ccaff82a503d0ddbfcc2901624691a25900a14dad7b98862ebb6cca24ba` |
| `termuxam-am-command-case` | `mobile-app-dev` | [termux/TermuxAm](https://github.com/termux/TermuxAm/blob/fdc83ef1f3c70b04a19c04e5acd159609a7e5a1d/README.md) | `7d8c1ba5230ed5d270707dbf86d7786f8baedadd8279c043c5db8ca26df9527f` |
| `capcut-cli-projects-case` | `video` | [renezander030/capcut-cli](https://github.com/renezander030/capcut-cli/blob/1c88efc54ba6532070228cbb09baad55156eecbb/README.md) | `edfa70369e88fd62380199246d122610bcdc77c7f6c8edf23086427d9b789e45` |
| `tidewater-warcraft2-case` | `game-dev` | [nlwstein/tidewater](https://github.com/nlwstein/tidewater/blob/c64437ab376b992d545a0562e56510eba5181437/README.md) | `11dfc2b189a0fff85f13a293603e9db6b525b2e248cfe521e30fca41b7793c4e` |
| `siteforge-site-exporter-case` | `website` | [bahaeddinmselmi/siteforge-chrome-extension](https://github.com/bahaeddinmselmi/siteforge-chrome-extension/blob/814d3611ed56ea357e24ea5a40a0d7aef1327b77/README.md) | `09655c6a8ca654e344b7be442539475d2860789721088dfdc4d7dbe23605145d` |
| `figma-clone-canvas-case` | `website` | [sanidhyy/figma-clone](https://github.com/sanidhyy/figma-clone/blob/387a533e87ffdeb5063b9e8101f997f9b505f10c/README.md) | `395f1b0c8a4b9ae704bb0ef1ee081ffebda6e9f89ab883a34937fcd1b754e0cf` |
| `lightspark-flash-player-case` | `animation` | [lightspark/lightspark](https://github.com/lightspark/lightspark/blob/670eaebeffd5436c08b0c4e693ab7f36fb4befed/README.md) | `40da14d913fcfe768c808111b74767524184515a02666dd49313eeaac26928df` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| caramelcupcakes842/On-The-Run-2-Decomp | No license file, a two-line README and a last push in 2024-06; a genuine Shockwave decompilation that waits for documentation and licensing. |
| datagutten/ShockwaveParser | GPL-3.0 parser package with a real module layout, but the README is a 101-byte stub and the evidence classification returns notes-only; revisit when documentation lands. |
| 47thtechcorner/RayCodes_Rea-AI-Agent-Setup | No license file; a tutorial companion repository rather than a reconstruction or an REA report. |
| adrianhajdin/figma_clone | Tutorial starter without a license file; sanidhyy/figma-clone is recorded instead. |
| Mahdi-Cheraghi/flappy-bird-as3 | An Animate-authored game clone; the Anm2Ed precedent puts game-specific works under Game Dev, which this batch does not grow. |
| Bi7Wis3/Jarvis_Studio, markrkendall-dot/Sketchup, dhokaleraj-cpu/STAWN-CAD-Pro | Zero-star SolidWorks or SketchUp clones without license files or verifiable scope. |
| luis-ar/editor-video, aquacommander/ReactVideoEditor, asheshmagar/react-video-editor, designcombo/react-design-editor | Copies of one remotion starter sharing the same description; openvideodev/react-video-editor remains set aside as reviewed on 2026-11-20. |
| DenisJCS/SketchUp-Clone, achur/MobileDesigner | Remain set aside as reviewed on 2026-11-20. |

## Validation notes

Each promoted record carries a bilingual title, Chinese requirement items in site/translations.zh-CN.json parallel to its requirement_facets, and an evidence-class entry; tidewater-warcraft2-case is grouped under `engine-reimplementation`. README.zh-CN.md already exceeded the 420,000-byte advisory budget at HEAD (436,202 bytes); this batch adds about 0.7 KB and the warning stays advisory with 75,075 bytes of headroom below the GitHub render limit.

The two scan snapshots from 2026-11-20 remain the earlier discovery baseline; the snapshots above are bounded single-run scans kept in .cache and not committed.
