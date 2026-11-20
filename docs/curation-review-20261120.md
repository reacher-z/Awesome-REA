# Sparse-class curation review — 2026-11-20

This batch adds 12 source-reviewed reconstructions to the curated catalog: 2 CAD, 2 animation, 2 video, 3 mobile-app and 3 website records. It also corrects the first ten records in this branch.

## Discovery and review scope

The existing `scan_sources.py` ran five bounded scans with public, non-fork and non-archived gates. The runs executed 12 search queries and read and hashed 25 READMEs per scan, for 125 successful reads. Manual review covered 17 shortlisted candidates and the ten earlier additions. Twelve candidates were selected. The scanner snapshots remain separate from curated records.

| Domain | Executed queries | Successful README reads | Scan snapshot SHA-256 |
| --- | ---: | ---: | --- |
| 3d-design | 5 | 25 | `0443cb6513706d6a10ccd1a233ed178d06cd5f91a76454c032cd4feca1eec6bf` |
| animation | 3 | 25 | `00b57add2a990df793339dcea1cd97bd5da22e42b525c853b54055ecc0674e54` |
| mobile-app-dev | 1 | 25 | `93bc4e9f43f12172634688990225ece671be930fd546d4ce8bcea277819c5c53` |
| video | 2 | 25 | `a389101a3c4c61c0194024a82c20c75b88626f463efae8f62212018eb13a3191` |
| website | 1 | 25 | `7613ab6649aded9a3c323f72809b70938021d21bad3225153cd7c8d256ac3498` |

## Promoted records

Each row links the immutable README reviewed for the record. The digest matches the README bytes captured by the scanner. Code trees and relevant build or license files were checked separately.

| Record | Data class | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `cnccraft-vectric-spark-case` | `3d-design` | [freegroup/CncCraft](https://github.com/freegroup/CncCraft/blob/4b9debd4aff7b81f33a230e25dbe336c675de40e/README.md) | `3bdcd5fc9538080f0d0d61a69de2187c1c78df3e18afd80e242b49ac6297255a` |
| `autocaded-autocad-14-case` | `3d-design` | [dmytro-yemelianov/autocaded](https://github.com/dmytro-yemelianov/autocaded/blob/544fdb6b57d573aa72358bad623f8e5c6ceaf059/README.md) | `9e8beb1cf54308dd2dd62695ea4c5c0acf646986ec488d51324b574a1a047eba` |
| `minnamate-adobe-animate-case` | `animation` | [mirvoxtm/minnamate](https://github.com/mirvoxtm/minnamate/blob/cd2afd95b5b235ec9b1b7b70b0c5b9503d6068c1/README.md) | `4656ddb28e4d91af33e2f664f1da6bbf36fcb9095dd5d0fb24ea1966f2683afd` |
| `fla-viewer-animate-playback-case` | `animation` | [lifeart/fla-viewer](https://github.com/lifeart/fla-viewer/blob/b14fa1d1e3e2d2b035e174bde472a7941d385b17/README.md) | `db2bb223a6ff601041ed91e0e8543fcf53cba9bbc350b28ec63c43e988d466c9` |
| `clonepremiere-editor-case` | `video` | [thecloners21/adobe-Premiere-Pro-clone](https://github.com/thecloners21/adobe-Premiere-Pro-clone/blob/8995ed14947197b48863f00d0b205f37870aebb4/README.md) | `4a154c0f79b37f5005f1eb13357a83c68ec8a7f7f3128281c348f9f80a1a2366` |
| `clipforge-capcut-editor-case` | `video` | [YibinLong/ClipForge](https://github.com/YibinLong/ClipForge/blob/96c902f90c02bc7e4eb62d021752aaa474c0aa28/README.md) | `89e4c795e7939921ebc22547b62873ab4ca67945b7f7e2416d9d539e57da50c9` |
| `tsf-reborn-launcher-case` | `mobile-app-dev` | [GlerschNersch/TSFReborn](https://github.com/GlerschNersch/TSFReborn/blob/647f622373999031c05ebd737785c184e07c2a96/README.md) | `d9b619ca3ee425a2fd34976175a7330e74f21ced874cdb0ccd5e35ab6485352b` |
| `translater-yandex-android-case` | `mobile-app-dev` | [sgrekov/Translater](https://github.com/sgrekov/Translater/blob/24a1a1955ca901d4bf5ff08ff2f8e3eb2719c825/README.md) | `02bf79e8d2b2a1fd36299828d11a77cad608fb9023bd7191bb0b726d7c1c1c69` |
| `aare-android-auto-phone-case` | `mobile-app-dev` | [prototux/AARE](https://github.com/prototux/AARE/blob/37f8236b031e42e17220b347a203a3c2882490da/README.md) | `093b4561bbf1bfe9bc85c29d332ceb6bd49860d64ff7a8176072626998196bf4` |
| `jsoneditoronline-site-case` | `website` | [djmattyg007/jsoneditoronline](https://github.com/djmattyg007/jsoneditoronline/blob/2090d3d71756cd00ef75b857e2b6fb46ab628f10/README.md) | `824d752bc69a4171f8c908c111c17c54bb605eb88ec22b644ff996c573b420dc` |
| `awwwards-zentry-site-case` | `website` | [BlockLune/awwwards-zentry](https://github.com/BlockLune/awwwards-zentry/blob/9780238a13ed050ff113a2abe6f09625d87e3e44/README.md) | `40fa5d14b09c3f4daa2e2584c88112b310b9c92f4c10f4f1e0f6746d8d201359` |
| `javascript-on-the-brain-site-case` | `website` | [Eggbertx/JavaScriptOnTheBrain](https://github.com/Eggbertx/JavaScriptOnTheBrain/blob/37a981dc363d20f383f13f14728a4c9e328b576f/README.md) | `5ceb076615ee273744935d264c4b36a001997aad04075c406ae29368398e9f27` |

## Corrections to the first batch

- Anm2Ed moves from Animation to Game Dev: it replaces the game-specific animation editor for The Binding of Isaac. Its targets now include Game and App. The pinned GPLv3 license is linked.
- The SketchUp workspace moves from 3D Design to Analysis. Its own README describes reading model structure and measuring a wardrobe through the official Trimble SDK; its targets now contain App. The SDK dumpers are recorded as scope rather than testing evidence.
- The CapCut REA report moves to the community REA case collection with its author-reported REA workflow relationship.
- SurfaceCraft records its MIT/Apache-2.0 choice. ZapCut records MIT source, GPLv3 bundled FFmpeg and OFL fonts. The Papers with Code entry records the CC BY-SA template and describes its preserved data and task viewer.
- Translation and preview JSON retain the base branch key order, removing unrelated whole-file reformatting from the pull request.

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| DenisJCS/SketchUp-Clone | The pinned root contains README, HTML and build configuration but no application source directory, despite the README describing one. |
| DwayneCrous/Kerfwright | The README describes a general CAD/CAM/CAE application and independent techniques; this batch prioritizes reconstructions of identified products. |
| openvideodev/react-video-editor | The reviewed README describes the OpenVideo engine showcase and SaaS starter. The search description still calls it a CapCut/Canva clone. |
| kruumy/QuickSearch | An After Effects preset-search script that depends on the original host application. |
| achur/MobileDesigner | The short README identifies an iPhone planning tool; its SketchUp reconstruction scope is documented only in repository metadata. |

## Search observations

The 125 reads are a bounded discovery batch. Query execution stopped when each scan reached 25 successful README reads. The following are the queries actually executed:

- `"SketchUp" clone in:description is:public fork:false archived:false` — total 4, returned 4.
- `"AutoCAD" reimplementation in:description is:public fork:false archived:false` — total 1, returned 1.
- `"SolidWorks" clone in:description is:public fork:false archived:false` — total 5, returned 5.
- `"Tinkercad" clone in:description is:public fork:false archived:false` — total 3, returned 3.
- `"3D" "clean-room" in:description is:public fork:false archived:false` — total 46, returned 46.
- `"After Effects" clone in:description is:public fork:false archived:false` — total 4, returned 4.
- `"Flash Player" reimplementation in:description is:public fork:false archived:false` — total 0, returned 0.
- `"Adobe Animate" in:description is:public fork:false archived:false` — total 514, returned 100.
- `"Android" reimplementation in:description is:public fork:false archived:false` — total 80, returned 80.
- `"Premiere" clone in:description is:public fork:false archived:false` — total 16, returned 16.
- `"CapCut" clone in:description is:public fork:false archived:false` — total 29, returned 29.
- `"website" "reimplementation" in:description is:public fork:false archived:false` — total 31, returned 31.
