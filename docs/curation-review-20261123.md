# Backlog curation review — 2026-11-23

This batch digests the followed-source lead backlog and adds six tool records: four Binary Ninja or IDA analysis plugins and two x64dbg automation tools. It is the first batch curated from the stored lead queue rather than from fresh scans; the followed-source workflow keeps completing without writing new batches because its sources have published nothing new since 2026-11-20.

## Selection scope

The stored queue holds 8,930 pending identities. Tool-kind leads whose descriptions mention Ghidra, IDA, Binary Ninja, x64dbg, radare, decompilation or disassembly numbered 462; nine were shortlisted for activity and license, six passed manual review. Records that only exist in a dead or superseded form (bad64 points at its replacement exarmo, rust_diff at binja_diff_view) were replaced by their living successors.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `ida-arsenal` | `native-analysis` | [khalilammarr/ida-arsenal](https://github.com/khalilammarr/ida-arsenal/blob/c36a4abc8473c5b393db5fef91f346ca64b3c96e/README.md) | `68c06aa2328c7eda6658d9ff7a6b125da6e01c9c5e20a3c50cad10ca3d725d16` |
| `binja-agent-mcp` | `agent-mcp` | [y637F9QQ2x/binja-agent-mcp](https://github.com/y637F9QQ2x/binja-agent-mcp/blob/1b954eba368897760844c6308de433ffc563a567/README.md) | `8b22e5bc70f17af0df58f03296d7599c8815253f06989a2ec24f8875a9c798f3` |
| `binja-diff-view` | `native-analysis` | [meerkatone/binja_diff_view](https://github.com/meerkatone/binja_diff_view/blob/551f3f687fdf1217a3e8153c60aaa8565f611706/README.md) | `bb1bf26a3ca10a58272d810fd241d7a0811b6181b75eda1a53940ba9b8238b21` |
| `threatray-binja` | `native-analysis` | [cod3nym/threatray-binja](https://github.com/cod3nym/threatray-binja/blob/0b0780547b97b155dd807e0e0d93f837a14a8ce7/README.md) | `4bfbe3926216aea1b51318d080b42e3aa999a5499ace4cb0c106894ecd46637e` |
| `x64dbg-automate` | `dynamic-analysis` | [dariushoule/x64dbg-automate](https://github.com/dariushoule/x64dbg-automate/blob/76421a901499fb22846127b0cba6b7c4de0ab850/README.md) | `86cc7b971a57cbeb6e71cfa770e32149148f95d4212b32bf430fc9d20a370e62` |
| `x64dbg-skills` | `agent-workflows` | [dariushoule/x64dbg-skills](https://github.com/dariushoule/x64dbg-skills/blob/0409f535af6f29389676f1d7f60f25cc83801cb8/README.md) | `a13b9902f1fe60cea4279e8b06aac397f586c57f9c5dc688eddb962468df66ab` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| yrp604/bad64 | The crate declares itself dead in favor of Vector35 exarmo; the living successor belongs upstream, not in this catalog. |
| meerkatone/rust_diff | Superseded by the same author\u0027s binja_diff_view, which is recorded instead. |
| BenMcAvoy/IDA-Plugins, overkazaf/VulnHunter4Ghidra, icsharpcode/AvaloniaILSpy | No license file recorded by the GitHub API. |

## Validation notes

All six records are `kind: tool` with `relationship: foundation`, carry Chinese requirement items in site/translations.zh-CN.json parallel to their requirement_facets, and received evidence-class entries. The evidence previews, READMEs, case indexes and site were regenerated after the catalog change.

---

# Backlog curation review, second batch — 2026-11-23

This round adds seven more tools from the stored lead queue: unidbg (Android native-library emulation), microsoft DebugMCP (a debugger MCP server for AI agents), the x64dbg DataExplorer (ImHex pattern language in the debugger), binja_wasm (a WebAssembly architecture for Binary Ninja), bninja-ps3 (a Cell PPU ELF loader), binja-blocks (Apple libclosure annotations) and GhidrAI (an AI-assisted malware pipeline for Ghidra).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `unidbg` | `android` | [zhkl0228/unidbg](https://github.com/zhkl0228/unidbg/blob/30911d7ecf44ee8aeed2ae5e6c91bb683c8afdd4/README.md) | `d34feb56407b7ab43868f15a01880aaf520fe9a367da7665b91aa112c92878eb` |
| `debugmcp` | `agent-mcp` | [microsoft/DebugMCP](https://github.com/microsoft/DebugMCP/blob/d0b4a334a6a3d8d600c5aa75ec60d9de272af3c4/README.md) | `89275f3226e7ec2795c560db41e7fb78be30ae4042c7605f62c82d2941728ff0` |
| `dataexplorer` | `dynamic-analysis` | [x64dbg/DataExplorer](https://github.com/x64dbg/DataExplorer/blob/904b75dc41d8b5c40d89594599e11c81bc008ef5/README.md) | `bdbacb575714b478ddbfe2d4d24070189f13e971ca43bea045e20469c10df1b6` |
| `binja-wasm` | `native-analysis` | [SecondNewtonLaw/binja_wasm](https://github.com/SecondNewtonLaw/binja_wasm/blob/ab4ac166dcbf0078158470e6382bf7e579bfbf4a/README.md) | `569f853be9c94fbdee8b597aa634388df5cd26a9e48b26b33e8c53e75f7add19` |
| `bninja-ps3` | `native-analysis` | [valters-tomsons/bninja-ps3](https://github.com/valters-tomsons/bninja-ps3/blob/5e53df569359b0132f949e018d2aef74df75f71e/README.md) | `d91de03d775d5e7c9e0dde2671d86b641b39bc25657f772ec494a870a0b7e66b` |
| `binja-blocks` | `native-analysis` | [droe/binja-blocks](https://github.com/droe/binja-blocks/blob/75c8c29fcec719274ebf59cc1e29b2a759730805/README.md) | `a5730bdb4b51d4d23326095b361946fd4048bf27c0adc7486c40e67a9fccf427` |
| `ghidrai` | `agent-workflows` | [John-A0/GhidrAI](https://github.com/John-A0/GhidrAI/blob/274474a47e7db1aeb18c3bc0085d674444a5dc6f/README.md) | `f3e448c1684263700b04ece55618a7c251a32d871a7e4d719612770eb206a04a` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| idalib-rs/idalib | Rust bindings for the IDA SDK with 355 stars, but the repository records no license file. |
| psifertex/BinAssistMCP, symgraph BinAssistMCP family | Overlaps with binja-agent-mcp recorded in the first backlog batch; recorded one Binary Ninja MCP server. |
| bochs-emu/Bochs, Ircama/ELM327-emulator | General-purpose emulators outside the catalog\u0027s reverse-engineering tool scope. |

---

# Backlog curation review, third batch — 2026-11-23

This round adds eight more records from the stored lead queue: two PlayStation emulators (RPCS3 and shadPS4) and the v86 PC emulator, the MemProcFS memory-forensics file system, the XIV Animation Toolkit, the OpenJK source port of the two Jedi Knight games, and the librespot and SatDump protocol tools.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `rpcs3` | `game-analysis` | [RPCS3/rpcs3](https://github.com/RPCS3/rpcs3/blob/3bfac607760d39dcdbe77eb137ab6dbb723b3b36/README.md) | `a074616f81441f36d6a06d4ce30239bd8a6d01123eec9ebe74e8f7e2a9b7e526` |
| `shadps4` | `game-analysis` | [shadPS4-emu/shadPS4](https://github.com/shadPS4-emu/shadPS4/blob/bbc020e5d0fcc959a4fe5bd9cdaa0205b0edf405/README.md) | `6b1150aeb8744fbac86a06ab5fd1658e0af6cf601a6bacdfb3a7d4d85d999ec6` |
| `v86` | `firmware` | [copy/v86](https://github.com/copy/v86/blob/9457e7a2f6890f3133bb6ac0f749e588f63c4c36/README.md) | `3b580d883b88ad6c22e00dd74bafed216aa44eed134690541770ab5a183b6c16` |
| `memprocfs` | `dynamic-analysis` | [ufrisk/MemProcFS](https://github.com/ufrisk/MemProcFS/blob/6d30b27bcf3295088b36e289aa111aff176e993e/README.md) | `fc3e3e8597a58c824d6b6f1573d3b03d00ae3e008eb60216a0cdc75005e9f721` |
| `xat` | `game-analysis` | [Etheirys/XAT](https://github.com/Etheirys/XAT/blob/3955622dba651456efbd8ecfdaf045cb0f2423c4/README.md) | `68a20449699407e21cb86cd042a1480da4774db310123aaceb87628642a8a8c8` |
| `openjk` | `reconstruction-cases` | [JACoders/OpenJK](https://github.com/JACoders/OpenJK/blob/260c59c2907187af555a676fe0cc798893bf7757/README.md) | `617c291db3e826a630ee986c02320fd5041dc6bdba635aa204c7898005182451` |
| `librespot` | `protocol-analysis` | [librespot-org/librespot](https://github.com/librespot-org/librespot/blob/15e02e86c72d96dd39d548e3749f00abe39ffdde/README.md) | `78f78f9266aba8daeea81256e8f475b4bdaed10c3bb3d13023ab01b0bfd81bde` |
| `satdump` | `protocol-analysis` | [SatDump/SatDump](https://github.com/SatDump/SatDump/blob/9fee0793c7d42bea2d401d330422e18c33c126fa/README.md) | `704f997118da74ad48557e2a274b0ea8d86cdabf41b45b72fed581237e98ec15` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| renezander030/capcut-cli, LibreDWG/libredwg | Already curated under existing ids; the lead queue still listed them as pending. |
| openvideodev/react-video-editor | Source-available OpenVideo License restricts larger for-profit companies; no standard open-source license. |
| godotengine/godot, assimp/assimp, luanti-org/luanti | General-purpose engines and asset libraries, not reconstructions or analysis tools. |
| Etheirys/XAT sibling animation utilities | Superseded by XAT, which combines them. |

## Validation notes

All eight records carry pinned README evidence, Chinese requirements parallel to their facets where facets are present, and evidence-class entries. The batch also fixes the `WASM` spell-check finding in the previous batch by writing `WebAssembly` in the binja_wasm description, then regenerates previews, READMEs, case indexes and the site.

---

# Backlog curation review, fourth batch — 2026-11-23

This round adds eight more records from the stored lead queue: three console emulators (Azahar, PCSX2 and mGBA), Tasmota alternative ESP firmware, the dump1090 Mode S decoder, the whatsmeow WhatsApp protocol library, the easyeda2kicad CAD conversion tool, and FreeRDP. No qualified 3D, animation, video or analysis-class reconstruction surfaced in this slice of the queue.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `azahar` | `game-analysis` | [azahar-emu/azahar](https://github.com/azahar-emu/azahar/blob/6f293a24daa292bd02b4ffee1a2adb5435e1ae00/README.md) | `9d325b7e75be361b51968a69da02b1f1f11d23eac6875a969d61e1afab045d7f` |
| `pcsx2` | `game-analysis` | [PCSX2/pcsx2](https://github.com/PCSX2/pcsx2/blob/61d75c21bf007bd7214521a794f39051b301d699/README.md) | `739358ce872c24806fbd74445a3ad633894495e05677c86aed753760a0a4a80c` |
| `mgba` | `game-analysis` | [mgba-emu/mgba](https://github.com/mgba-emu/mgba/blob/feeea8f5c2f53f3fc10e534b54c1b4f7366a42f2/README.md) | `0becd59a16337833fdf57f8d346662624e561b1356ad53f87db7d7914091f18e` |
| `tasmota` | `firmware` | [arendst/Tasmota](https://github.com/arendst/Tasmota/blob/016be6317eb963777ae1879b9f59a76cca9e83e9/README.md) | `18f13cdd4f10bf93c41db9f37d5f79f1ef82cc49ef177be5f7671c547c4ad64f` |
| `dump1090` | `protocol-analysis` | [antirez/dump1090](https://github.com/antirez/dump1090/blob/efe64db3c6ba1520291331628a33c1e208e851a6/README.md) | `6255f70a10b18112bfe3c45a38d1f8b7cab22b7aa0f7d3b05955efb7f21d8ec2` |
| `whatsmeow` | `protocol-analysis` | [tulir/whatsmeow](https://github.com/tulir/whatsmeow/blob/19d61352436f3aeb21ad2cf93c2e3599ac409415/README.md) | `027b3da3b6d4d914ace426715b3cda7cf3365c27b704b400fb58a34e74864d99` |
| `easyeda2kicad` | `native-analysis` | [uPesy/easyeda2kicad.py](https://github.com/uPesy/easyeda2kicad.py/blob/fff10a38619963d7cb1c57d779655a9ea4572e95/README.md) | `508c1917927f382837d9fb80e818391dbd2e99de3fd5556b421c0620312693ae` |
| `freerdp` | `protocol-analysis` | [FreeRDP/FreeRDP](https://github.com/FreeRDP/FreeRDP/blob/5379388d4fc4bc3554a61343407be3cf5c9ee3ca/README.md) | `bff17fb39c0bb72fc286e9c799d3be11631bbd609cd65fba6a9002e6829af7c6` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| ferrumc-rs/ferrumc | The README states the Minecraft server rewrite is not actively maintained and its rework is on hold. |
| valentderah/totk-pc-recomp, deadinside28/bloodborne_pc, scarsty/kys-cpp, yairm210/Unciv | Already curated under existing case ids; the lead queue still listed them as pending. |
| openvideodev/react-video-editor, itsjwill/vanta | Custom or missing license terms; not a standard open-source license. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements, and evidence-class entries; the two Class 1 records (Tasmota and easyeda2kicad) received previews. Previews, READMEs, case indexes and the site were regenerated.

---

# Backlog curation review, fifth batch — 2026-11-23

This round adds eight records from the stored lead queue: Atmosphère and Luma3DS custom firmware, esptool and the Proxmark3 Iceman client, IronRDP and Geyser protocol tools, the REA Investigation Prompts collection and REFramework. The batch shifts away from console emulators toward firmware, protocol and agent-workflow material.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `atmosphere` | `firmware` | [Atmosphere-NX/Atmosphere](https://github.com/Atmosphere-NX/Atmosphere/blob/3e8915011e1de89f595462d929c1cc3294470896/README.md) | `368ea957dbf80cc2f3982199f4d67e797240071f497fc219910111ad5032bc12` |
| `luma3ds` | `firmware` | [LumaTeam/Luma3DS](https://github.com/LumaTeam/Luma3DS/blob/c7790ee1d79574471f948e1078bb6f2c5c620e9b/README.md) | `0c1e1512218f0ea62fc7c8d98655d90fc94d32efcf2539cb4937c40d378a256f` |
| `esptool` | `firmware` | [espressif/esptool](https://github.com/espressif/esptool/blob/6ec584a39e046c63f507d8022cb0b7df25e2d4de/README.md) | `fcff74336b1463a7da838cae3b21b31bd4f4af87e46d07474973ca603b1b6ab3` |
| `proxmark3` | `firmware` | [RfidResearchGroup/proxmark3](https://github.com/RfidResearchGroup/proxmark3/blob/da929f9c52500abecef6a33258e0bcc08f16931f/README.md) | `798bd799564eec8c3feaf00a268b906b3b4593954a646bc2ff4a3c7f08f988d4` |
| `ironrdp` | `protocol-analysis` | [Devolutions/IronRDP](https://github.com/Devolutions/IronRDP/blob/79e763a04dc9b22962559d33bdce074d08cf4c84/README.md) | `d86bedceeb85cbb12dde46e7ff7536b92630cd64a7644108f26c82c7ad8def12` |
| `geyser` | `protocol-analysis` | [GeyserMC/Geyser](https://github.com/GeyserMC/Geyser/blob/2a2f5afd3cc092a86b622bb1429d3b5750a02293/README.md) | `0c1ec96051059059dbcbb8f940f99233b33f670451cf002fb6e1e1f483aea6a0` |
| `rea-prompts` | `learning` | [JoasASantos/REA-Prompts](https://github.com/JoasASantos/REA-Prompts/blob/9756618f25af1920c8965f8969820eed22247936/README.md) | `926cf21e5b21b4ab8776f187159cfbacf4e37d4288d2d4ec18dac3c9f3b6a308` |
| `reframework` | `game-analysis` | [praydog/REFramework](https://github.com/praydog/REFramework/blob/22c713cef9372b918c08d3c0550fcec0ea6714e4/README.md) | `6bdb249061ecd17c154f48390a814a33f2d7d317b54017dbc6211cd890642902` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| Cemu, melonDS, Vita3K, flycast, desmume, project64 | More console emulators; deferred to keep this batch focused on firmware and protocol material. |
| godotengine/godot, assimp/assimp, luanti-org/luanti | General-purpose engines and asset libraries, not reconstructions or analysis tools. |
| openvideodev/react-video-editor, itsjwill/vanta | Custom or missing license terms; not a standard open-source license. |
| valentderah/totk-pc-recomp, deadinside28/bloodborne_pc, scarsty/kys-cpp, yairm210/Unciv | Already curated under existing case ids. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; the two Class 1 records (Atmosphère and Luma3DS) received previews. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, sixth batch — 2026-11-23

This round adds eight records from the stored lead queue: MiSTer main binary (FPGA hardware reimplementation platform), edl (Qualcomm Sahara/Firehose client), nexmon (Wi-Fi firmware patching), PortEx (PE analysis library), Assemblyline 4 (malware analysis framework), RuneLite (OldSchool RuneScape client), WidescreenFixesPack and DeepZero.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `mister-main` | `firmware` | [MiSTer-devel/Main_MiSTer](https://github.com/MiSTer-devel/Main_MiSTer/blob/ac2e102990fd4e3df83809565873db2d25037ecf/README.md) | `848b447ea7cf8c1b87f69ada695b76285ebf94b4b886f7cda8aabd65d9d1c6d0` |
| `edl` | `firmware` | [bkerler/edl](https://github.com/bkerler/edl/blob/1cda1a616748d608667b2d13b73a28d3197ceb45/README.md) | `58f122811cefc2030a20fd2a526d631165d08f2e6e5398698742e40e3014f13b` |
| `nexmon` | `firmware` | [seemoo-lab/nexmon](https://github.com/seemoo-lab/nexmon/blob/68720406f54ff16cad28fd3c51f2392aefad9fb7/README.md) | `f0014cecdb05ed8c9a02c8fcedd71b94195f1b1188f0c665698731f234e49b27` |
| `portex` | `binary-libraries` | [struppigel/PortEx](https://github.com/struppigel/PortEx/blob/bbcb1e452ae54dd7e211ca701dcaee5abb7bc28f/README.md) | `4b118fdb297d07cf58051fac9de04c01e1009723573edc645f05b3af6daea514` |
| `assemblyline` | `dynamic-analysis` | [CybercentreCanada/assemblyline](https://github.com/CybercentreCanada/assemblyline/blob/9ddae776f91f9767cacd81fd9478a904121cd096/README.md) | `faa85ba22ebffa93a59cec5700a4f37a5e1c670ecba2f3efd0803acb1c6278a6` |
| `runelite` | `game-analysis` | [runelite/runelite](https://github.com/runelite/runelite/blob/0fa3b8489e929a47410c7214ffcb710e67c7bb46/README.md) | `2764d23f1f83bb1a0d2ef700300e5b03240fab66059560709d1f6c0e928dfbc8` |
| `widescreen-fixes-pack` | `game-analysis` | [ThirteenAG/WidescreenFixesPack](https://github.com/ThirteenAG/WidescreenFixesPack/blob/f26357ecb727e6e8e8856a74ce7f2b20d0d28097/README.md) | `2859518259cda36e5a65d6a1cc8ea6afefbcfed397f466b55f2c4108ed386181` |
| `deepzero` | `dynamic-analysis` | [416rehman/DeepZero](https://github.com/416rehman/DeepZero/blob/b26865ba5eed25a6eceabb930f04f86bf8243ae3/README.md) | `5a2213892f056b9384d4a01f490210f94c0b6fc61b3c6caf6bee4cc060d08f99` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| Cemu, melonDS, Vita3K, flycast, jsnes, 86Box | More console emulators; coverage already grew in the previous batches. |
| al-khaser, malwoverview, pyWhat, assemblyline-lab variants | Malware-hunting tools whose catalog overlap needs a separate review pass. |
| openvideodev/react-video-editor, itsjwill/vanta | Custom or missing license terms. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. nexmon and PortEx received Class 1 previews; WidescreenFixesPack is Class 1 without usable media. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, seventh batch — 2026-11-23

This round adds eight records from the stored lead queue: AnyPS5 (PS5 executable relinking), touchHLE (early iOS app emulator), Impostor and vkQuake as reconstruction cases, PortaPack Mayhem firmware, openfortivpn and boofuzz as protocol tools, and al-khaser as a defensive technique test harness.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `anyps5` | `game-analysis` | [boykopovar/AnyPS5](https://github.com/boykopovar/AnyPS5/blob/7482424113477a71f7a259b2b4b75607858e25c5/README.md) | `619a53aac824a31f7995222e490a8b37c41c5ecffafc63780aae1f84c6f4e4c7` |
| `touchhle` | `game-analysis` | [touchHLE/touchHLE](https://github.com/touchHLE/touchHLE/blob/ca1de89c578e79746f33c1332e28efd106c334ba/README.md) | `d9aad10f305e47440680ad4768f27d04bed362c2ffaa58c5f068708a3aa330df` |
| `impostor` | `reconstruction-cases` | [Impostor/Impostor](https://github.com/Impostor/Impostor/blob/7686635e6653f6e90a1b11061991117bdd0639c3/README.md) | `560104cfdd29540e31054e689dd98d5b7c2b266917999ef21a4894183e5f47e2` |
| `vkquake` | `reconstruction-cases` | [Novum/vkQuake](https://github.com/Novum/vkQuake/blob/1e573d7490147fef33fb1aaccc1425df186869e7/README.md) | `2b4c0674a11b6600322f15d4931222a2765f1befa2f2856f8c9d6ddaf83c0cba` |
| `mayhem-firmware` | `firmware` | [portapack-mayhem/mayhem-firmware](https://github.com/portapack-mayhem/mayhem-firmware/blob/4e204cd5d4f042a78de3eef04004001cb31992ac/README.md) | `03c44f5dd1e962d75fc5c2641cfaeaf6866d2f9d33d119100f9c3a42ccb8f093` |
| `openfortivpn` | `protocol-analysis` | [adrienverge/openfortivpn](https://github.com/adrienverge/openfortivpn/blob/866c0eab271cc84f6b743b6fef037e95dd8c9013/README.md) | `a67014eb66b89facc8e59bd72f9099f81f2d1b5340db4ebe6cb42d92b1555465` |
| `boofuzz` | `dynamic-analysis` | [jtpereyda/boofuzz](https://github.com/jtpereyda/boofuzz/blob/41a808ef6bdb19ba64d811dc5d882b66a1033316/README.md) | `a669aa4adbfeceaba8960e68cd2494385a640247bfbb95a6e488710024153a24` |
| `al-khaser` | `dynamic-analysis` | [ayoubfaouzi/al-khaser](https://github.com/ayoubfaouzi/al-khaser/blob/a14ba9f014ecba3659e5f939109259ca8c3a04fa/README.md) | `e1784832094efb23223eba26353254983866ccea80f21a5cbd70e00fbca3a648` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| Cemu, melonDS, Vita3K, flycast, desmume, project64, jsnes, 86Box, visualboyadvance-m | More console and computer emulators; this batch instead covers iOS apps and reconstruction cases. |
| ferrumc-rs/ferrumc | README states the Minecraft server rewrite is not actively maintained. |
| openvideodev/react-video-editor, itsjwill/vanta | Custom or missing license terms. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; AnyPS5 and PortaPack Mayhem received Class 1 previews. The two new case studies update the game case indexes and README case sections.

---

# Backlog curation review, eighth batch — 2026-11-23

This round adds eight records from the stored lead queue: Cemu (Wii U emulator), coreboot and HackRF as hardware projects, fwupd as a firmware update daemon, pyWhat and nvim-dap as analysis tools, and GlobalProtect-openconnect and Greenlight as protocol clients.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `cemu` | `game-analysis` | [cemu-project/Cemu](https://github.com/cemu-project/Cemu/blob/2f49c079da1d50b85cea0ed99aedda58846b3523/README.md) | `ba008e510be40b711822b6aab1c161c96b080fa1921f38fa5fc26493f41bae70` |
| `coreboot` | `firmware` | [coreboot/coreboot](https://github.com/coreboot/coreboot/blob/41084423cd688dcd57e7ac59b71e41bf38a26b92/README.md) | `e623ebfad2fef138c471c5712bbbf6c9243e8b6bab72136c0f148789b6899f3a` |
| `hackrf` | `firmware` | [greatscottgadgets/hackrf](https://github.com/greatscottgadgets/hackrf/blob/8540a765590bf67cade4139f6fc9513c238c7235/README.md) | `dd72fde6951b106f4db029707a84bd317e9a417fb8d3ac93738952f8b996558d` |
| `fwupd` | `firmware` | [fwupd/fwupd](https://github.com/fwupd/fwupd/blob/cab5cd33cbd101bb500f2145557fe787d7d553aa/README.md) | `6e0685b5d16c879d1942b16ac57dec7b847a863cebea43c4f1281cd907f61682` |
| `pywhat` | `native-analysis` | [bee-san/pyWhat](https://github.com/bee-san/pyWhat/blob/eeca660fac35f32ffe975ddc49fb6a38046d6d9a/README.md) | `4403a9c4b0264e9b2068fb830c4a07bd944b990cda4a3faab795fb80c64e1ba1` |
| `nvim-dap` | `dynamic-analysis` | [mfussenegger/nvim-dap](https://github.com/mfussenegger/nvim-dap/blob/cfa2d58f4537aca6ca83e2de1a0d9f1491121264/README.md) | `d66b0182b783c961b3d3bb961daf2aead11ff8557fc86b287ce28ac93d235568` |
| `globalprotect-openconnect` | `protocol-analysis` | [yuezk/GlobalProtect-openconnect](https://github.com/yuezk/GlobalProtect-openconnect/blob/2160bd82f8432eb0f9b567f07e1e642a50c301e9/README.md) | `49ff9d9b9f42726bdfe4f25ded464be9fd9105afb75592e533e29ace399cec07` |
| `greenlight` | `protocol-analysis` | [unknownskl/greenlight](https://github.com/unknownskl/greenlight/blob/baa4072cbe1583e76b6271a82e8eda7d46fcf9b9/README.md) | `eb7ce65fc24b3f944cba6f31d86940d78b846dca4ca6a95fa7c2c21cdb1e3910` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| systemsecuritystorm/awesome-binary-similarity | No license file recorded by the GitHub API. |
| melonDS, Vita3K, flycast, desmume, project64, jsnes, 86Box, visualboyadvance-m | More console emulators; deferred to keep this batch on firmware and analysis tooling. |
| Playnite, unpoller, wolfssl | General software or infrastructure rather than reverse-engineering tools. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; four Class 1 records received previews. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, ninth batch — 2026-11-23

This round returns to reconstruction cases and emulators: Augustus (Caesar III), OpenLoco (Locomotion), OpenMoHAA (Medal of Honor: Allied Assault) and idTech4A++ (id Tech 4 games) as case studies, plus melonDS, Vita3K, 86Box and psd-tools.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `augustus` | `reconstruction-cases` | [Keriew/augustus](https://github.com/Keriew/augustus/blob/4ec115e75651ded84fb56b43abbf118bcda34f72/README.md) | `0afdbee507bf115ac9a4f08332349e84692a0762f86c92d9fb4400dd4e2b23e0` |
| `openloco` | `reconstruction-cases` | [OpenLoco/OpenLoco](https://github.com/OpenLoco/OpenLoco/blob/da1a3459725157eb26380bebee894ce18d2ba354/README.md) | `7a230ca1cb0ced72bc55ac54975a9095e6869ff1a6d90c3f6f4d5875033d511d` |
| `openmohaa` | `reconstruction-cases` | [openmoh/openmohaa](https://github.com/openmoh/openmohaa/blob/a2f340195975f4f042e28a60b62561dd9a0b2700/README.md) | `e90afc893e6cb54715cd905ece00e71eaa88de60a303cfaa2168fd14bb9c1244` |
| `idtech4a` | `reconstruction-cases` | [glKarin/com.n0n3m4.diii4a](https://github.com/glKarin/com.n0n3m4.diii4a/blob/4a14e1ab186160394ed37dc8c204104bc725b218/README.md) | `1613fd1b5744175ec0417f308abd971d83106a147bd7efca9435511cd7b8ab5f` |
| `melonds` | `game-analysis` | [melonDS-emu/melonDS](https://github.com/melonDS-emu/melonDS/blob/ff972523f8a70e877dd054439876c3c8c6b79197/README.md) | `6deb041b19a7dbfdc24963a97df94e5ab39cc4e6958d5f868620249f74697390` |
| `vita3k` | `game-analysis` | [Vita3K/Vita3K](https://github.com/Vita3K/Vita3K/blob/a631dd35d46747fdb27d7715a0524ea67b0b1a89/README.md) | `83448ab0be9dbe292d2211081753afc8036c9213a88f7095a9483ff292f978de` |
| `86box` | `firmware` | [86Box/86Box](https://github.com/86Box/86Box/blob/bd6ccce8a035fab9cf0d6d7c33ee9acb146286a1/README.md) | `c9d3ae5c0ba608a6d0086e8f5a790b9c04654619a49b04a4e83295009a5fa039` |
| `psd-tools` | `native-analysis` | [psd-tools/psd-tools](https://github.com/psd-tools/psd-tools/blob/6a827c19543106cd83a50fd830b07312df950531/README.md) | `6b22e011eb0689a21f521b6a554701b919c6f070b6bc33ed23c9625011d6e90b` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| ZDoom/Raze, dxx-rebirth, ECWolf, OpenBVE, OpenLieroX | No license file recorded by the GitHub API. |
| chrissotraidis/caesarpad, chrissotraidis/deviltouch | Derivatives of Augustus and DevilutionX already in the catalog. |
| OpenRA/ra2, cookgreen/Yuris-Revenge, Inq8/CAmod | OpenRA game mods rather than standalone reconstructions. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; seven Class 1 records received previews. The four new case studies update the game case indexes and README case sections.

---

# Backlog curation review, tenth batch — 2026-11-23

This round adds eight records from the stored lead queue: Project64, Visual Boy Advance - M, Flycast, JSNES and Lemuroid as emulator projects, wolfSSL as a protocol library, and Chameleon Ultra and ESPurna as firmware projects.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `project64` | `game-analysis` | [project64/project64](https://github.com/project64/project64/blob/c2c0dcbff292416457ec9151ee779e6556128c7f/README.md) | `4044e711cea590417eba9aefd79c072420d06081740c845a9de7eeb1dc4ae678` |
| `visualboyadvance-m` | `game-analysis` | [visualboyadvance-m/visualboyadvance-m](https://github.com/visualboyadvance-m/visualboyadvance-m/blob/e4456a8d5e1f7d6d18aa147de950c5dbca4bfc0a/README.md) | `9143adae0bec3a175ce13ec5226c9bf61c5743decf131671a77f037b734e9d2c` |
| `flycast` | `game-analysis` | [flyinghead/flycast](https://github.com/flyinghead/flycast/blob/105342d53fc181493cd372c8f1ebf5c49621ed1a/README.md) | `956b43a35c6f095dd046a0fe4bb6fb737eada2c331e78926fe8b321fb4f838ce` |
| `jsnes` | `game-analysis` | [bfirsh/jsnes](https://github.com/bfirsh/jsnes/blob/1ead3bebca6c8eb6edb270a5b01561b1827814ee/README.md) | `1665012657c00dd79902eb283c6546dda1f100010386456984c46f51150ad5b8` |
| `lemuroid` | `game-analysis` | [Swordfish90/Lemuroid](https://github.com/Swordfish90/Lemuroid/blob/3625bc121d5d79fd4b80ce930fb0f3236c9334e8/README.md) | `d877174fa604829fab43dc8a7b7ff1f2d408271877305f7cc043195524bad6f5` |
| `wolfssl` | `protocol-analysis` | [wolfSSL/wolfssl](https://github.com/wolfSSL/wolfssl/blob/e92099e116662db6f8c2aa66ad6f75911e43717e/README.md) | `9a28dd418b12944e1c5528d63c3dc75b0ef0940fcf756af221b4ee1bcddba27c` |
| `chameleon-ultra` | `firmware` | [RfidResearchGroup/ChameleonUltra](https://github.com/RfidResearchGroup/ChameleonUltra/blob/6009a5fb8adbb92d3efb548eaac9e501bd179801/README.md) | `2c20405a6f5f6edf85710f7eb9e41f02ef0580e0d04e196e62edddd422bbf270` |
| `espurna` | `firmware` | [xoseperez/espurna](https://github.com/xoseperez/espurna/blob/bbadc15c8a520841c505333adb29ea33275dfc4a/README.md) | `909ec75e6acbdf1f1b95e7dbaeb0b7a606ee796917771f4bbad571263746492a` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| TASEmulators/desmume | The repository README is a 225-byte stub, below the documentation threshold for a catalog entry. |
| Cemu, melonDS, Vita3K, 86Box, Azahar, PCSX2, mGBA, RPCS3, shadPS4 | Already added in earlier batches. |
| BizHawk, dxx-rebirth, ECWolf, OpenBVE, OpenLieroX | No license file recorded by the GitHub API. |

## Validation notes

All eight records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; four Class 1 records received previews. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, eleventh batch — 2026-11-23

This round adds six records from the stored lead queue, weighted toward reconstruction cases: SDLPoP (Prince of Persia), FreeSO (The Sims Online) and The Forgotten Server (Tibia server), plus EKA2L1 (Symbian/N-Gage emulator), Gearboy and RT64. A smaller batch keeps the bilingual README growth in check.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `sdlpop` | `reconstruction-cases` | [NagyD/SDLPoP](https://github.com/NagyD/SDLPoP/blob/f7be2e939375d369d26e1d10bcdd5ca74d3002a2/README.md) | `c08a42a7c6afd1bea84e7729697cf846ef0e5b95027914636bb2f95ec689a3b8` |
| `freso` | `reconstruction-cases` | [riperiperi/FreeSO](https://github.com/riperiperi/FreeSO/blob/4c6b3e8f5835b228723caea3c9f683c62f244f73/README.md) | `347febfa03e066e2001d218ff58ff70e77fd33a2007ce795dd924446a5bf57e8` |
| `forgottenserver` | `reconstruction-cases` | [otland/forgottenserver](https://github.com/otland/forgottenserver/blob/1561fa91d0a0a879dd90792a87f82ea31083de03/README.md) | `c6542cbaf3d00fd59282219488ddd25167aefcbe778fc341c77f5a5027003c1a` |
| `eka2l1` | `game-analysis` | [EKA2L1/EKA2L1](https://github.com/EKA2L1/EKA2L1/blob/e6d454d1caa826affef1784a6097a178a841e598/README.md) | `c9e76a45090cb11e6637ced0bb468a29060c4316fefe51201e245842c3935a8b` |
| `gearboy` | `game-analysis` | [drhelius/Gearboy](https://github.com/drhelius/Gearboy/blob/340964cb57a63432fb56d9ca2a2965457d9275d5/README.md) | `6ea5de9913a11f9032c5a2ffd82d624524006cd9afa6940c3b81f536a6e13dc3` |
| `rt64` | `game-analysis` | [rt64/rt64](https://github.com/rt64/rt64/blob/d9817c68ffd7328cd0af383af124971489366e18/README.md) | `63d619fe018adcc0971a74b03eff4575fea4edbd793e7bfb925e607ab58e3a11` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| amhndu/SimpleNES | README declares the project archived and no longer maintained. |
| TASEmulators/desmume | README is a 225-byte stub below the documentation threshold. |
| dxx-rebirth, ECWolf, OpenBVE, OpenLieroX, BizHawk | No license file recorded by the GitHub API. |
| OpenRA/ra2, OpenKrush, Yuris-Revenge, CAmod | OpenRA game mods rather than standalone reconstructions. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; FreeSO, EKA2L1 and Gearboy received Class 1 previews. The three new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twelfth batch — 2026-11-23

This round adds six records from the stored lead queue: Eglantine, NooDS, SkyEmu, Clock Signal and Ymir as emulator projects, and Malwoverview as a threat-hunting CLI. The batch stays at six records to keep the bilingual README under its rendering budget.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `eglantine` | `game-analysis` | [Eglantine-Community/Eglantine](https://github.com/Eglantine-Community/Eglantine/blob/835019fec5548748034a1449575cc7d37a4cfa16/README.md) | `69fc9c69a74c145e3546b9be36ad8414cf7ac86abcec38421d041321e962db31` |
| `noods` | `game-analysis` | [Hydr8gon/NooDS](https://github.com/Hydr8gon/NooDS/blob/4cb1439c330248b26cdf5f8dbcfa4e5ac53dcda0/README.md) | `52efb9b893036761f80cfba09ae8a40c3d091b5968ac5d059c8d9f23d8260232` |
| `skyemu` | `game-analysis` | [skylersaleh/SkyEmu](https://github.com/skylersaleh/SkyEmu/blob/b64903f0fde8104d0796546b96859e9f682311b7/README.md) | `9ae0f6e7aae16e7f635eba53308598a18259cd13b95a4cd62368597982ec331d` |
| `clk` | `firmware` | [TomHarte/CLK](https://github.com/TomHarte/CLK/blob/922ad314ce88b576306cb0a914f2c4bf223ab67f/README.md) | `3b46b96b441cf901ad35b9ad75a3a636c74f864ded11a55334c21193a60ad4d7` |
| `ymir` | `game-analysis` | [ymir-emu/Ymir](https://github.com/ymir-emu/Ymir/blob/0fdabbdd41f17fd7fda58195130c3b43f7fd00e5/README.md) | `1e2d4aa5766313f8f15058a886f68573da5495fe8af47babf75b92324c574095` |
| `malwoverview` | `dynamic-analysis` | [alexandreborges/malwoverview](https://github.com/alexandreborges/malwoverview/blob/439f3b79e1e8e95a26e2e196d68c5c81d74e682b/README.md) | `692befb09e7919af3de5beabe386e8fcf384231f5402e498abddbfba962a9b81` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| amhndu/SimpleNES | README declares the project archived and no longer maintained. |
| TASEmulators/desmume | README is a 225-byte stub below the documentation threshold. |
| GPCS4, mooneye-gb, OpenRakis | Last activity is 2022-2023 and the projects are not actively maintained. |
| dxx-rebirth, ECWolf, OpenBVE, OpenLieroX, BizHawk | No license file recorded by the GitHub API. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Eglantine, SkyEmu, Clock Signal and Ymir received Class 1 previews. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, thirteenth batch — 2026-11-23

This round adds six records from the stored lead queue: Bochs and Heads as hardware/firmware projects, gopher64 and ProjectPSX as emulator projects, libewf as a forensic image library, and The Oracles Project as a reconstruction case.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `bochs` | `firmware` | [bochs-emu/Bochs](https://github.com/bochs-emu/Bochs/blob/d214bbf542c8b1f7e0fa3dab37eba2250e551f70/README.md) | `a022a14b6ccaecde4b70b9bd06e998346cf0a6892353a7d459d59c52899e0e03` |
| `gopher64` | `game-analysis` | [gopher64/gopher64](https://github.com/gopher64/gopher64/blob/8159147d65ba17767fd5ed77a3d1898d637bb151/README.md) | `5e3207fe2d7ad242f93d54776184d238a9e1e72c146fa339e9ae2ef14d898725` |
| `projectpsx` | `game-analysis` | [BluestormDNA/ProjectPSX](https://github.com/BluestormDNA/ProjectPSX/blob/f4dc13aea42d2b5bc096e2315ba2a6b7542cf744/README.md) | `c32d55400add7e65e1f0f64d4376c42502380b46d38d3ddc9bb8e72cf47761c1` |
| `heads` | `firmware` | [linuxboot/heads](https://github.com/linuxboot/heads/blob/5f835ca4bcf34b91ec284a181ab389e8eb2a9075/README.md) | `23c50d915913da6ed04d73ba369a344ed440fa23888f63910df512bd2b0058c3` |
| `libewf` | `binary-libraries` | [libyal/libewf](https://github.com/libyal/libewf/blob/c709254af2634f20d27f5f2c3af18bd67067e0e0/README.md) | `7334b2ba64accd892006e97f17faf08a0fee190fb57ee6ab0c45e4b1d2084cf9` |
| `oracles-project` | `reconstruction-cases` | [thibautbus/top](https://github.com/thibautbus/top/blob/9f7475cefc0a38f86ea760743994c16373c17e48/README.md) | `4f54090b2f914b647b416cb62daa577693a0e74612730ce69323d9e745db86dc` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| dolphin-emu/dolphin, stenzek/duckstation, LIJI32/SameBoy | No license file recorded by the GitHub API. |
| TASEmulators/freej2me-plus, libretro/REminiscence | No license file recorded by the GitHub API. |
| dwc_network_server_emulator | Last activity is 2024 and the project is not actively maintained. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Heads and The Oracles Project received Class 1 previews. The new case study updates the game case indexes and README case sections.

---

# Backlog curation review, fourteenth batch — 2026-11-23

This round adds four libyal format libraries from the stored lead queue: libesedb (ESE databases), libpff (Outlook mail stores), libbde (BitLocker volumes) and libfsntfs (NTFS). The batch stays small because all four are Class 2 without previews and the bilingual README is close to its rendering budget.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `libesedb` | `binary-libraries` | [libyal/libesedb](https://github.com/libyal/libesedb/blob/bd12fbe75d31005a4180688f0b49400445b321fb/README.md) | `1892f529d6a96cac014c929abaa84ee70063974030965127d54d41be2e489164` |
| `libpff` | `binary-libraries` | [libyal/libpff](https://github.com/libyal/libpff/blob/d233208f12ebbaeef0b0a9196e010d0ccca93caa/README.md) | `a014a522f956c1fb503137e6726bb4c42e12af4dee6601b1abac34f6a4c650cf` |
| `libbde` | `binary-libraries` | [libyal/libbde](https://github.com/libyal/libbde/blob/4343f149fd37dbae30a832fac5571a97f471d579/README.md) | `3cb7b8a17bc292555296bb794898fb7e4281557181dcf8c41378e36258b20afe` |
| `libfsntfs` | `binary-libraries` | [libyal/libfsntfs](https://github.com/libyal/libfsntfs/blob/2d22e7fe338bf7cc1718e1c94a8b44769dbb1aaa/README.md) | `b47adc507213ee4ec0b3feb9159664dfefe047e166073bee396f17895858cd02` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| libyal/libevtx, libyal/libregf | READMEs are below the 400-byte documentation threshold used by the evidence rubric. |
| libyal/libvshadow, libyal/libolecf | Lower-star siblings deferred to keep the batch focused on the highest-use formats. |

## Validation notes

All four records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. All are Class 2, so no previews were added; READMEs and the site were regenerated.

---

# Backlog curation review, fifteenth batch — 2026-11-23

This round adds six records from the stored lead queue: the official Flipper Zero firmware and the Unleashed community firmware, Gearsystem and Ludo for emulation, and two more libyal format libraries (VSS and OLE 2).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `flipperzero-firmware` | `firmware` | [flipperdevices/flipperzero-firmware](https://github.com/flipperdevices/flipperzero-firmware/blob/e459e2d939db7f292d7dcfe6935b8fb2641409e3/README.md) | `424edcdfed69e00beb9ee514e78c945f14c996e490d65bcf8cc163fc288a3e67` |
| `unleashed-firmware` | `firmware` | [DarkFlippers/unleashed-firmware](https://github.com/DarkFlippers/unleashed-firmware/blob/a96dd64d3520d7643b58e633ab7a99758938c371/README.md) | `e09fab52d7beee2ab0132e7717b4564bcefcf8ec7a69e32cdfba858aeeb3c4fc` |
| `gearsystem` | `game-analysis` | [drhelius/Gearsystem](https://github.com/drhelius/Gearsystem/blob/2fdd8f7c8ff3ae9523dafb7f1d8125776e96aae6/README.md) | `88e98dab415b3ebbd5d6290fcac5780eb0187dd924b292f832fe3dfbd3b3fb60` |
| `ludo` | `game-analysis` | [libretro/ludo](https://github.com/libretro/ludo/blob/7a2dc452c72e43dc06b5ecc711c3d03c8aeeb261/README.md) | `7db79884aee333032ba5397160ee2da8ada192f5624b391081fabb13a01c8699` |
| `libvshadow` | `binary-libraries` | [libyal/libvshadow](https://github.com/libyal/libvshadow/blob/0551f11ed32502063de7cd80767d52d4a070a516/README.md) | `681e0789488d85895863232c4d3dcfc8bfb88855f3569eccf101f5c9394edca3` |
| `libolecf` | `binary-libraries` | [libyal/libolecf](https://github.com/libyal/libolecf/blob/148cef77c93f5597a05ed3d9ed0f6b8ca9247d24/README.md) | `2e10a77c6de4100c76f8b165542510beed88a42902f34e21b7b64b6284cdaafd` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| schellingb/dosbox-pure, libyal/libscca, libyal/libfwsi | READMEs are below the 400-byte documentation threshold. |
| Next-Flip/Momentum-Firmware | Another Flipper Zero firmware; the official and Unleashed projects cover the base and community variants. |
| dwc_network_server_emulator, mooneye-gb, GPCS4 | Last activity is 2022-2024 and the projects are not actively maintained. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Unleashed, Gearsystem and Ludo received Class 1 previews. Previews, READMEs and the site were regenerated.

---

# Backlog curation review, sixteenth batch — 2026-11-23

This round returns to the core of the catalog with six reconstruction cases from the stored lead queue: Shockolate (System Shock), DOOM Retro, Open Fodder (Cannon Fodder), OpenTyrian, the Banjo-Kazooie matching decompilation and ServUO (Ultima Online server).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `shockolate` | `reconstruction-cases` | [Interrupt/systemshock](https://github.com/Interrupt/systemshock/blob/f622c304f844d988782fb6029928ea97e5ef580f/README.md) | `e1fa41d227f34b06357bc285ff8102e1bae457b5a2753c123d0199e73dd20c8f` |
| `doomretro` | `reconstruction-cases` | [bradharding/doomretro](https://github.com/bradharding/doomretro/blob/865bf0b874ee2e5f44147fe573a82b5bae95055c/README.md) | `e3dd77dbdbef21c8edf770df36698665e4801e89ad851886cf6f3b6fd17af172` |
| `openfodder` | `reconstruction-cases` | [OpenFodder/openfodder](https://github.com/OpenFodder/openfodder/blob/ad15d39fafd9c65d7c9a02ecd7c48939cff3a4ce/README.md) | `e3c285d6bbd00d8f8639733cd99fedbf4b548ca5c5e283ad96d8dacb5b0f1071` |
| `opentyrian` | `reconstruction-cases` | [opentyrian/opentyrian](https://github.com/opentyrian/opentyrian/blob/26e40a2012903812f16aae5dd6af2be50b96b5cb/README.md) | `28455843e37ffbc219a53dd4a1448e881defd382751e76f03b07bc810c217b20` |
| `banjo-kazooie` | `reconstruction-cases` | [n64decomp/banjo-kazooie](https://github.com/n64decomp/banjo-kazooie/blob/7b6a4c44a1a5bf80977adcf48d822ea9d6bdf899/README.md) | `ffbd7d5ed79bb5306a9e2f3bf81acc796c762c62f90a2ae0739c211f4167a727` |
| `servuo` | `reconstruction-cases` | [ServUO/ServUO](https://github.com/ServUO/ServUO/blob/d76bf4443cf76d081ddaf8f57c87ff33749256af/README.md) | `af199759316c2fb10f226d419b20bca1a9b0490c5765dce95f23dcb9122f3758` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| TASEmulators/desmume | README is a 225-byte stub below the documentation threshold. |
| ferrumc-rs/ferrumc | README declares the project is not actively maintained. |
| zortos293/Lichii, Eglantine | Very experimental Switch 2 emulators; Eglantine is already curated. |
| n64js, boytacean, binjgb | More emulators deferred to keep this batch focused on reconstruction cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Shockolate, DOOM Retro and Open Fodder received Class 1 previews. All six are case studies, so the game case indexes and README case sections were regenerated.

---

# Backlog curation review, seventeenth batch — 2026-11-23

This round adds six more reconstruction cases from the stored lead queue: Space Station 14, Marathon Recompiled (Sonic 2006), NocturneRecomp (Symphony of the Night), Omnispeak (Commander Keen), Heretic2R and OpenRealm (Warcraft III data).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `space-station-14` | `reconstruction-cases` | [space-wizards/space-station-14](https://github.com/space-wizards/space-station-14/blob/6726d80a26a5e83bacc24b67561d16a2f5d7e000/README.md) | `bef20443fcf421b4a3179a9cb23afb3175e47a36f8b1b445cd5cad6528f0341a` |
| `marathon-recomp` | `reconstruction-cases` | [sonicnext-dev/MarathonRecomp](https://github.com/sonicnext-dev/MarathonRecomp/blob/42831cdc572efe04fe30f8d86585fc9a61b7171f/README.md) | `8390b7bf1696853e5c2f872e1ae1a55339385b2652d6bde44477f2148f69c76a` |
| `nocturne-recomp` | `reconstruction-cases` | [birabittoh/NocturneRecomp](https://github.com/birabittoh/NocturneRecomp/blob/d409a67c6be29592e96524de038a03593c199e4b/README.md) | `d4cd48fe34890b917df2aa6254801a2593ab96e1f53a11a53d39d3c4e9c99b75` |
| `omnispeak` | `reconstruction-cases` | [sulix/omnispeak](https://github.com/sulix/omnispeak/blob/46cefb33b5f604448da9b81d67368aed82b4c3da/README.md) | `1b72590a42ef5990fe33eb6ca96dd4b73adf00c9e352ba6723b71952401aea45` |
| `heretic2r` | `reconstruction-cases` | [m-x-d/Heretic2R](https://github.com/m-x-d/Heretic2R/blob/4d677156a458cfe03a5d5ddceb2e9a445bc39744/README.md) | `cd9ffd7ce75fdb15d16d2dc1c95da3a52f4db7c3bbfd153f5bbdbd266a3de535` |
| `open-realm` | `reconstruction-cases` | [corepunch/open-realm](https://github.com/corepunch/open-realm/blob/e357d117c949da41a7e81b664b23b4172f16bff9/README.md) | `d943945aad3bd608b16e5c6c49150004dbcd21f0aaeb6a9470de27d769b86f0c` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| akarnokd/open-ig, AshfordFamily/recvx-decomp | Already covered by main-branch PRs #4253 and #4265; not duplicated in the stacked branch. |
| ferrumc-rs/ferrumc | README declares the project is not actively maintained. |
| zortos293/Lichii, sacrapy/HeyListen | Very experimental Switch 2 emulators/recomps; deferred. |
| n64js, boytacean, binjgb, nestopia, stella, punes | More emulators deferred to keep this batch on reconstruction cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Marathon Recompiled and OpenRealm received Class 1 previews. All six are case studies, so the game case indexes and README case sections were regenerated.

---

# Backlog curation review, eighteenth batch — 2026-11-23

This round adds five more reconstruction cases and one forensics parser: Type PAL, bo2-mac, Mercenaries Recompiled, CatacombGL, Project ReLink and ccl_chromium_reader.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `type-pal` | `reconstruction-cases` | [IllegalCreed/type-pal](https://github.com/IllegalCreed/type-pal/blob/0443a023ce59e8c18910244c54ed34e5d392870d/README.md) | `a05b65fd98d1f880578144c5f4aedb4ed7f2f7ee554c6b21b997417a4ce36af2` |
| `bo2-mac` | `reconstruction-cases` | [adrbn/bo2-mac](https://github.com/adrbn/bo2-mac/blob/e360a0f447957f5b579bd63d9140c9496ede3cfb/README.md) | `078c982f693cacc478282bec34fc07c0047a0c79f7affc9a6af51286310fd2cb` |
| `mercenaries-recompiled` | `reconstruction-cases` | [KraftMacAndChee/Mercenaries-Recompiled](https://github.com/KraftMacAndChee/Mercenaries-Recompiled/blob/f513ae4e041401b7b032410016940971488d523b/README.md) | `a440b163a42d4814384cbde2db736c90ca3b49a6b7dbd4e0c0ee5dc32d02c201` |
| `catacombgl` | `reconstruction-cases` | [ArnoAnsems/CatacombGL](https://github.com/ArnoAnsems/CatacombGL/blob/d00d480f65edaaf75f087e6bcf55b0e0737f24c6/README.md) | `84c8784365fe67681bfb163f9babdf49143b956a3636d67a07a1d3eb490a4110` |
| `project-relink` | `reconstruction-cases` | [pixl27/ProjectReLink](https://github.com/pixl27/ProjectReLink/blob/54af18cda249233a9a9aafcddf5dc317cb3fad42/README.md) | `68cf175a554476be104f359df12b6522d20ed6ec3d4e6cae2a87527e20dc166d` |
| `ccl-chromium-reader` | `native-analysis` | [cclgroupltd/ccl_chromium_reader](https://github.com/cclgroupltd/ccl_chromium_reader/blob/7a01b07dc5205a9c12004f2c9eabce0bb4697860/README.md) | `3318cb254ad5de43ade6ac08e8f09907f99f3f71e76ea46203928dd7b9e2ecef` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| SwagSoftware/KisakCOD | GitHub returned HTTP 451 for the repository during review. |
| ferrumc-rs/ferrumc | README declares the project is not actively maintained. |
| Awis13/liberty-pro-max, Sacrappy/HeyListen | More Ocarina of Time / GTA recompilation variants deferred to avoid near-duplicate cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Type PAL, bo2-mac and Project ReLink received Class 1 previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, nineteenth batch — 2026-11-23

This round adds four reconstruction cases and two analysis tools from the stored lead queue: Civ2-clone, SpaceAnimalsRecomp (Star Fox), ssx3-recomp, Oxide (Minecraft server), HlslDecompiler and spimdisasm.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `civ2-clone` | `reconstruction-cases` | [axx0/Civ2-clone](https://github.com/axx0/Civ2-clone/blob/d3677ab6c586c87cfba73b3c5e69ad7c9f13259e/README.md) | `7bd50a5863eb24158163edb782f83b59b33e76d02195530333b2fdc3070d2064` |
| `spaceanimalsrecomp` | `reconstruction-cases` | [SerenityG4K/SpaceAnimalsRecomp](https://github.com/SerenityG4K/SpaceAnimalsRecomp/blob/6c34c495975986875b2dffb3710408752c0c3f87/README.md) | `772d36e4d81d3a7cc8f67ad0858107d7ef63380c9f3eb74bff38ef1b0dc080d2` |
| `ssx3-recomp` | `reconstruction-cases` | [koenhendriks/SSX3-recomp](https://github.com/koenhendriks/SSX3-recomp/blob/bdb5110ec1cb3ac73c84de7aded73852f7656fa8/README.md) | `d34c0b49f6476516b7b592e7feab9732b629eaf720f99954e672c00ef0a12e45` |
| `oxide` | `reconstruction-cases` | [T-x-T/oxide](https://github.com/T-x-T/oxide/blob/8e0770ea9fb13f585134a7aa376682e514cd2ff6/README.md) | `2ade32b94fcf36f002bf5e9ce1c96344ddd6fdc6c19dbad76a65d1ffe75809cc` |
| `hlsldecompiler` | `native-analysis` | [AndresTraks/HlslDecompiler](https://github.com/AndresTraks/HlslDecompiler/blob/1ea80d55173d024a209cc33c7569b1663e8cc99e/README.md) | `0ed44a80708c1bc684ddaa229e411ae7ad681a9840feddc2ca63dc107eca0950` |
| `spimdisasm` | `native-analysis` | [Decompollaborate/spimdisasm](https://github.com/Decompollaborate/spimdisasm/blob/4b5d4c68eeb9f9eae14b3bb713971433ae2c3c43/README.md) | `c659b932d9e98e0b3acf04555ca0d0f7934207d0c8269cad5d6932a0578222cd` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| ZeusAFK/LibreKO | GitHub returned HTTP 404 for the repository during review. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| SwagSoftware/KisakCOD | GitHub returned HTTP 451 for the repository during review. |
| fuddlesworth/pokebw2, OpenCrystalCaves, jaenster/redivivus | Near-duplicates of records already carried by other open PRs or pending library coverage. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; ssx3-recomp received a Class 1 preview. The four new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twentieth batch — 2026-11-23

This round adds four reconstruction cases and two decompilation toolkits from the stored lead queue: Pokémon Black 2/White 2, Redivivus (Diablo II), femto8 (PICO-8) and Shadows of the Empire: Recompiled, plus ds-decomp and ps2-native-recomp.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `ds-decomp` | `native-analysis` | [AetiasHax/ds-decomp](https://github.com/AetiasHax/ds-decomp/blob/3b2df91c530ad144cbda0031abb7ce0eec3b1d83/README.md) | `b2c182a8fc1f5e731c216ca0f2015f9889bed80ff180f524b488aa87f7accd5e` |
| `ps2-native-recomp` | `game-analysis` | [exoteric33/ps2-native-recomp](https://github.com/exoteric33/ps2-native-recomp/blob/66528c8a7f5457caaeec76566d9e43d57e5bbb92/README.md) | `71643bf145e385b15316184f9baeeba2c2884133f5870b8589d58a850bb44686` |
| `pokebw2` | `reconstruction-cases` | [fuddlesworth/pokebw2](https://github.com/fuddlesworth/pokebw2/blob/345b790e6000869b481b79838bb5727309f832fb/README.md) | `d0a6eaa0398225433b8dd2cb3533fb4aec743c843d25841dc484c23c4b1bb5a2` |
| `redivivus` | `reconstruction-cases` | [jaenster/redivivus](https://github.com/jaenster/redivivus/blob/17c86009cc63656842f5315bb32b3bf5838efe5c/README.md) | `b7474e76245da12abe46e17f9a70203e1fdba854061ba94e44955e9078a88dd6` |
| `femto8` | `reconstruction-cases` | [benbaker76/femto8](https://github.com/benbaker76/femto8/blob/d83bab199a8dafb6c00aa8ecd16d2b50e7d5c562/README.md) | `029fa62d63ff7605e7a002906036ef8daa364b10c22399e0317ae6616061f135` |
| `sote-recomp` | `reconstruction-cases` | [GTTeancum/SotE-Recomp](https://github.com/GTTeancum/SotE-Recomp/blob/457832809a4bed9bf82f0b4b4431e23422be3392/README.md) | `ab815f05c0df95350100ede3bc6caccd77f38644e5305443ba20be74e664b938` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| ZeusAFK/LibreKO | GitHub returned HTTP 404 for the repository during review. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| fuddlesworth/pokebw2 siblings, OpenCrystalCaves | Deferred where another open PR already carries the same game or list. |
| Russian-Doom, EDGE-classic, chocolate-quake, woof | More Doom/Quake source ports deferred to avoid near-duplicate cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; femto8 and Shadows of the Empire: Recompiled received Class 1 previews. The four new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-first batch — 2026-11-23

This round adds five reconstruction cases and one decompilation tool: Ace Combat X, OpenTower (Pizza Tower), Naruto: The Broken Bond, Haunting Ground, Time Crisis VR and Porytiles.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `ace-combat-x-recomp` | `reconstruction-cases` | [sal063/Ace-Combat-X-Recompilation](https://github.com/sal063/Ace-Combat-X-Recompilation/blob/f6268e959cac75481989077a94305b22e55ec8ad/README.md) | `16b98300ccb84f9fb2585e2ea07d2195db4f07852ad0625f73b7268f1ca52737` |
| `open-tower` | `reconstruction-cases` | [femloy/OpenTower](https://github.com/femloy/OpenTower/blob/51060bc52e98c26ea5f857b6a0f6028e7a21b96b/README.md) | `990eb77c21f3ac87035ebfbd774d1c6d2ae5b670be83593b6a9db47897acccb6` |
| `naruto-broken-bond-port` | `reconstruction-cases` | [Auremana666/Naruto-The-Broken-Bond-PC-Port](https://github.com/Auremana666/Naruto-The-Broken-Bond-PC-Port/blob/570142f98b7f852fce944776bee2dd3369d1cd10/README.md) | `cff61e061e6f8f33a4c769a08399014fe5599f4add728490d19707cac922dbde` |
| `haunting-ground-recomp` | `reconstruction-cases` | [N900x4/HauntingGround-Recomp-Project](https://github.com/N900x4/HauntingGround-Recomp-Project/blob/1db0f0ce71850e15b86faa16b7532212aedf0a02/README.md) | `fa721ab7d82cc2011efaca965c2cdf78ef63fca26c51357037d6c6c09fa051af` |
| `porytiles` | `native-analysis` | [grunt-lucas/porytiles](https://github.com/grunt-lucas/porytiles/blob/4c244d587c3daf16447366d0d8398b84a28370fe/README.md) | `db86ad678ec0f7308465ede2d7086b42a0abe3b97149c66e5bb9456cbcc3e41b` |
| `time-crisis-vr` | `reconstruction-cases` | [DR-89/time-crisis-vr](https://github.com/DR-89/time-crisis-vr/blob/a92faadc4e8c2042b1f6baccc77d4785863ceb7c/README.md) | `4fea267877998ef4937c5dfa6b2e9cc48364d0ba14aa20250faee0340926617d` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| CMUSTRUDEL/DIRE | README is a 46-byte stub below the documentation threshold. |
| fuddlesworth/pokebw2 siblings, OpenCrystalCaves | Deferred where another open PR already carries the same game or list. |
| Russian-Doom, EDGE-classic, chocolate-quake, woof | More Doom/Quake source ports deferred to avoid near-duplicate cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; OpenTower, Naruto, Porytiles and Time Crisis VR received Class 1 previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-second batch — 2026-11-23

This round adds five reconstruction cases and one packer-analysis tool: Resident Evil Outbreak Recompiled, WWE 2K14, Animal Crossing: City Folk, The Sims 2: Castaway, Silent Hill 4 for PS Vita and Magicmida-RS.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `re-outbreak-recomp` | `reconstruction-cases` | [RaccoonRecomp/ResidentEvilOutbreakRecompiled](https://github.com/RaccoonRecomp/ResidentEvilOutbreakRecompiled/blob/e0fcc5fb6e7e1011a6876824fa772ec5354a4534/README.md) | `fa7965021a5dcaa147d96483998b18280b5d4cdf2d8b8e6fc54d6e8427fcd4e9` |
| `wwe2k14-recomp` | `reconstruction-cases` | [Jarrodfeng/wwe2k14-recomp](https://github.com/Jarrodfeng/wwe2k14-recomp/blob/de26df28d477c73ee58a258163f01dd666daba3d/README.md) | `95ff8874603b729f04cdfe7c2ee9407c310abfe06e19116ac9621ad9899436a4` |
| `cf-decomp` | `reconstruction-cases` | [ACreTeam/cf-decomp](https://github.com/ACreTeam/cf-decomp/blob/ecef279ab1d55d74c40b0ad86c0964951495a9ca/README.md) | `591f200ac4c448155ee18b562f3a2e2de5bfc8990f13bca5762708aed9f5dea6` |
| `sims2-castaway-decomp` | `reconstruction-cases` | [HaydnTrigg/Castaway](https://github.com/HaydnTrigg/Castaway/blob/f5c5dbcf2b4a20eb797b1aa6eb03f6cf09a4dbbe/README.md) | `13e10bb9ca631fce9e039dec0f3d9eb1c3ba7cd783c1e50bd95f14aecad7ceca` |
| `magicmida-rs` | `native-analysis` | [guoxing2024/magicmida-rs](https://github.com/guoxing2024/magicmida-rs/blob/cc10f642e0d29ce68763f7b0e292ff751453df0b/README.md) | `d2b03c89585bcc76fa0ea46d3a4d7e7d7d4234da679d1967239ce03fab876de9` |
| `sh4vita` | `reconstruction-cases` | [vallfrr/sh4vita](https://github.com/vallfrr/sh4vita/blob/386541b726538a50f2e3cdf48d5ac24b553d6239/README.md) | `0eabce9e2aa48aaaa4fd64513b46b3efab3392efccf53a21201e034e6dc6ef38` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| sp00nznet/snesrecomp | Record id already used by the stacked catalog; a new id would be needed before adding it. |
| Vidanox/BanjoTooieRecompiled, hamishakl/LibertyRecomp | Near-duplicates of records already carried by other open PRs. |
| Russian-Doom, EDGE-classic, chocolate-quake, woof | More Doom/Quake source ports deferred to avoid near-duplicate cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Resident Evil Outbreak Recompiled and Magicmida-RS received Class 1 previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-third batch — 2026-11-23

This round adds five reconstruction cases and one recompilation toolkit: SPR Recomp (Splatoon Raiders), Klonoa: Empire of Dreams, Sonic Advance, Wild 9, The Simpsons Game for Switch and neogeorecomp.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `spr-recomp` | `reconstruction-cases` | [Elie-0066/SPR-Recomp-Project](https://github.com/Elie-0066/SPR-Recomp-Project/blob/a4bc49a85bfba986def112114e40b1da458adfa5/README.md) | `35d30e1bd4a51d3fb28d80d4ead81e9f64fd9f1531ab2470c5f294f9c3693e4e` |
| `kleod` | `reconstruction-cases` | [testyourmine/kleod](https://github.com/testyourmine/kleod/blob/18e6e1d8017da139ff0f712793aa6fdca75268bb/README.md) | `00dcc3b23b158937a2d0de993c78027c620dde17758ca816a59fd339510e3a43` |
| `sonic-advance-recomp` | `reconstruction-cases` | [smiluredev/SonicAdvanceRecomp](https://github.com/smiluredev/SonicAdvanceRecomp/blob/e637fc89861b66b291ce3a1b02cdb151ca53bc22/README.md) | `99b1dd1c3c0317c05835b51e42d147e4cae2754874549fd9c359cd4bff47e019` |
| `wild9-recomp` | `reconstruction-cases` | [plinkr/Wild9Recomp](https://github.com/plinkr/Wild9Recomp/blob/6bff4d1acfd44e8fe34349fe2dd4965b7526c679/README.md) | `e4c4efad6bbfffdf0ba14e56717d5baf11c2a8ec22f539d309fb5e10d4e8367a` |
| `simpsons-game-nx` | `reconstruction-cases` | [R-drg/the-simpsons-game-nx](https://github.com/R-drg/the-simpsons-game-nx/blob/3cb2cdf7fa1665a1f2d653aa7502fe4baa03680f/README.md) | `f93a493c7c9cef0b04657ac70109db7fddb74892bc33d95178984026e47a8d50` |
| `neogeorecomp` | `game-analysis` | [sp00nznet/neogeorecomp](https://github.com/sp00nznet/neogeorecomp/blob/af96b2b4b39b42b392b17bcaa6a74a5f27088202/README.md) | `2f38dbe88c2a883845fceacead22db868c7c2972669567c73175a2225842da11` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| sp00nznet/snesrecomp | Record id already used by the stacked catalog; a new id would be needed before adding it. |
| Vidanox/BanjoTooieRecompiled, hamishakl/LibertyRecomp | Near-duplicates of records already carried by other open PRs. |
| Russian-Doom, EDGE-classic, chocolate-quake, woof | More Doom/Quake source ports deferred to avoid near-duplicate cases. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Wild 9 Recompiled and neogeorecomp received Class 1 previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-fourth batch — 2026-11-23

This round focuses on recompilation and agent tooling: IDA MCP Server, C64RE, Exhume, dcrecomp, nxrecomp, plus the Scarface matching decompilation.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `ida-mcp-server` | `agent-mcp` | [coleleavitt/ida-mcp-server](https://github.com/coleleavitt/ida-mcp-server/blob/893675eae72c6a04bda095b24ada67f56fbaf3ab/README.md) | `166bd8e1e86c178897d5aff5fa1ca1dd5d8015a393fb03b46bf7a58fdae29f79` |
| `c64-re-mcp` | `agent-mcp` | [Jondalar/C64ReverseEngineeringMCP](https://github.com/Jondalar/C64ReverseEngineeringMCP/blob/c26d09a5dffcd847a0791a3ec55be9f2c216bdb6/README.md) | `bf0e0932bd882aa50db7555e7a74be0ed340fc2b11a1e52094d773c7feaa0f32` |
| `exhume` | `native-analysis` | [abedegno/Exhume](https://github.com/abedegno/Exhume/blob/ff95127148f753b87f45d47b7b0dbd76d8fbe81f/README.md) | `3e4d45b01485e2c5dfea50e5510ed31b1351ce07fb4e96eac4ca1c19277bd998` |
| `dcrecomp` | `game-analysis` | [sp00nznet/dcrecomp](https://github.com/sp00nznet/dcrecomp/blob/3c60e6f03cbbaaabeaa1f3165247ed3120f23c3e/README.md) | `faab99a16eddd7eca19bbc04c50c3e26e8f6b4b326578c81c3dc6d59b5f8e4f4` |
| `nxrecomp` | `game-analysis` | [drakolordx7/nxrecomp](https://github.com/drakolordx7/nxrecomp/blob/0a9fe4653648cab485864524a30997b75589df9d/README.md) | `43eab373485e6a41871685e37308a4d8580ed903275b868dbbcfc5ab8e3826af` |
| `scarface-decomp` | `reconstruction-cases` | [scarface-decomp/scarface_decomp](https://github.com/scarface-decomp/scarface_decomp/blob/dd4e326dd376302886660a6f8c96e2127fe32e6b/README.md) | `6bd6589c850646c7a4f2854c8527698e6eb840f89d26ad50b7aeee1c367e4979` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| sp00nznet/snesrecomp, sp00nznet/gbarecomp | Sibling recompilation toolkits deferred; the Neo Geo and Dreamcast toolkits are already represented. |
| batinium/gta-stories-recompiled, Vidanox/BanjoTooieRecompiled | Near-duplicates of records already carried by other open PRs. |
| R-drg siblings, YesterMester/TheSimpsonsGameRecomp | Upstream projects behind the already-curated Switch port. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. All are Class 2, so no previews were added; READMEs and the site were regenerated.

---

# Backlog curation review, twenty-fifth batch — 2026-11-23

This round adds two recompilation toolkits and four reconstruction cases: gbarecomp and XRecomp, plus OpenGP, slingshot-animals-recomp, LEGO Star Wars and Sengoku Basara 2 Heroes.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `sp00nznet-gbarecomp` | `game-analysis` | [sp00nznet/gbarecomp](https://github.com/sp00nznet/gbarecomp/blob/ac1176f467cbb708f58785e65f36b4f091a8ab20/README.md) | `58be8aff6deaf59f5dcf144564bd09c774bc6ca5609362abfc4e435ecdc4c50d` |
| `xrecomp` | `game-analysis` | [MisterAlex95/Xrecomp](https://github.com/MisterAlex95/Xrecomp/blob/6bb0ebabf20d28a8240a8902fedf9a5f6f0ad6f7/README.md) | `58f4cfc872a6806552a1abaf7392043f6e164812eb965fce10f2fd6ec679d1af` |
| `open-gp` | `reconstruction-cases` | [OpenGP-dev/OpenGP](https://github.com/OpenGP-dev/OpenGP/blob/cad7929717fc65f7f338c1f3997d1e413b491ffa/README.md) | `537a2bd93075b73ad34678e52d07e680c994393f20abad37af3915daedadcf62` |
| `slingshot-animals-recomp` | `reconstruction-cases` | [Berny23/slingshot-animals-recomp](https://github.com/Berny23/slingshot-animals-recomp/blob/1c29eb1bd33e41fc83dc5140b3346bdb7a0f636b/README.md) | `fc5dc556051913cbe5531ed0ce5f6e31795d91810a589bff562a30c62f391cf7` |
| `lsw1-decomp` | `reconstruction-cases` | [ellierocks/lsw1-decomp](https://github.com/ellierocks/lsw1-decomp/blob/e61bfd5345e5499be0d88a70573dc0a3665321ee/README.md) | `6e9ce7713b94ba1b3b44f41b171d6e96bc18db8b939212cea56852937fda2d06` |
| `b2h-wii-android` | `reconstruction-cases` | [PotatoRecomp/B2HWii-Android](https://github.com/PotatoRecomp/B2HWii-Android/blob/0e531a2257e5dae28d063c80e455a1f6ea36ff59/README.md) | `ccb6a47cdadbfe43a7ec57d156de38afc2379b7a2db476c4e6bc4a686f71f6e4` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| dreamsailing59-ops/SuperRecomp | README declares the project abandoned and no longer updated. |
| sp00nznet/snesrecomp | Record id already used by the stacked catalog; a new id would be needed before adding it. |
| batinium/gta-stories-recompiled, Vidanox/BanjoTooieRecompiled | Near-duplicates of records already carried by other open PRs. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; XRecomp received a Class 1 preview. The four new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-sixth batch — 2026-11-24

This round adds two recompilation tools, one arcade launcher and three reconstruction cases: genrecomp, psprism, HIRAKU, Crystal Cut (TimeSplitters 2), Team Buddies and MechWarrior 2.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `genrecomp` | `game-analysis` | [sp00nznet/genrecomp](https://github.com/sp00nznet/genrecomp/blob/b3900079c4ebb9d7f383bef3cd6d05e496667599/README.md) | `5338365c94a0301cfd9194d7844bb452394cb5508640d461878805588ae53607` |
| `psprism` | `game-analysis` | [anthonyhfm/psprism](https://github.com/anthonyhfm/psprism/blob/8764f39bb6ee0d10a9c07d8ca2934ce38a5ecb83/README.md) | `f42e4f6b54f508ebc278d39d67399363faf69348c3ceca6c595da091378eb5d2` |
| `hiraku` | `game-analysis` | [Roganis/HIRAKU](https://github.com/Roganis/HIRAKU/blob/a43eee67ecb68de78b02aa0760013359b1c1c869/README.md) | `f63ca04f3102072ac1ab5ded92433ecc795f7eee4f80ece44ccc434c5f956ef7` |
| `crystal-cut` | `reconstruction-cases` | [Destinity13/TimeSplitters-2-Native-Linux-Recomp](https://github.com/Destinity13/TimeSplitters-2-Native-Linux-Recomp/blob/e1d714b43b04c7209d2671fd97492b857cb32dd5/README.md) | `6688f70918adadc8f2b8c72c8caeac33bea0b999f817e8cd5eca3f9e949a048a` |
| `tbuddies-decomp` | `reconstruction-cases` | [hcbt/tbuddies-decomp](https://github.com/hcbt/tbuddies-decomp/blob/d2ca1dce934263d553cfd8f835c81438c0df906f/README.md) | `c80266ab3415f18dac275d87abcabc9e6a2f3ab5dec3d7c176e473ea5d39dbcc` |
| `demech2` | `reconstruction-cases` | [anpage/demech2](https://github.com/anpage/demech2/blob/07c629aecaf694ea803c8ebc45333ba7c9bd428a/README.md) | `6efe5613281d457d8fdcaca68efbadf204c9f0785d8940b87fac9e607114abe2` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| sp00nznet/snesrecomp | Record id already used by the stacked catalog; a new id would be needed before adding it. |
| SuperRecomp, abandoned projects | READMEs declare the projects abandoned or no longer maintained. |
| batinium/gta-stories-recompiled, Vidanox/BanjoTooieRecompiled | Near-duplicates of records already carried by other open PRs. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Crystal Cut received a Class 1 preview. The three new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-seventh batch — 2026-11-24

This round adds one toolchain decompilation and five reconstruction cases: mweppc (Metrowerks CodeWarrior), Stunt Race FX, New Play Control! Pikmin, Lionheart Remake, Time Crisis II VR and GTA Stories Recompiled.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `mweppc` | `native-analysis` | [doldecomp/mweppc](https://github.com/doldecomp/mweppc/blob/919828d97d33d236da675824d43c5d57332afe74/README.md) | `48de95ae2a66fc7dffbfe99da5f3e587ffe05141de35ad6b9b15380a4109dc7f` |
| `stuntracefx` | `reconstruction-cases` | [jeff-strutb/stuntracefx](https://github.com/jeff-strutb/stuntracefx/blob/61b46e8065c49650e03ce7a1bc2532e56192907a/README.md) | `9f1a56dd71d4b80db294e86bbb6ffaa04f264ac492c855a46ce2c4d25b3f721e` |
| `pik1wii` | `reconstruction-cases` | [projectPiki/pik1wii](https://github.com/projectPiki/pik1wii/blob/0450613e9e29a5ff63ef3bf677f62078cbe66f86/README.md) | `9942ef7d21676814c011abc8bc265df42591ad77339960f952c00a32582c7b50` |
| `lionheart-remake` | `reconstruction-cases` | [b3dgs/lionheart-remake](https://github.com/b3dgs/lionheart-remake/blob/46c2eeb75421c33903a24bff993c856ef9c85a8f/README.md) | `026a1258034cd09294223ac81d1dbae90abb3a84ea73d28531d721dbb9b395a4` |
| `time-crisis-2-vr` | `reconstruction-cases` | [DR-89/time-crisis-2-vr](https://github.com/DR-89/time-crisis-2-vr/blob/41c057a4c6943f466fb64062e91b9fa5e987bdd0/README.md) | `79708cd2aa37b43bab859ed8538c34a11b19b798a0836cbd94acd15f9fd2108f` |
| `gta-stories-recompiled` | `reconstruction-cases` | [batinium/gta-stories-recompiled](https://github.com/batinium/gta-stories-recompiled/blob/8a895d2e3c71cc9aeab83c6a27049c4ee75111e5/README.md) | `c068b7f43108dbf6d732718b8a88ebdeb87eaa3c59ebdadbddb6a498da61d636` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| sp00nznet/snesrecomp | Record id already used by the stacked catalog; a new id would be needed before adding it. |
| SuperRecomp, abandoned projects | READMEs declare the projects abandoned or no longer maintained. |
| Vidanox/BanjoTooieRecompiled, hamishakl/LibertyRecomp | Near-duplicates of records already carried by other open PRs. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; Stunt Race FX, Time Crisis II VR and GTA Stories Recompiled received Class 1 previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-eighth batch — 2026-11-24

This round adds two recompilation libraries and four reconstruction cases: pcrecomp, snesrecomp, Castlevania: Legacy of Darkness, Link’s Awakening (Switch), Skylanders: Spyro’s Adventure and Sonic Unleashed (Wii).

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `pcrecomp` | `native-analysis` | [sp00nznet/pcrecomp](https://github.com/sp00nznet/pcrecomp/blob/7c07a0b42059b6dc4313d9b4ebded6f7a72db8f3/README.md) | `b2e0a6c91db082fe6246358f5d368d34798bbada0b5b4702cc60b3aea8824b8c` |
| `sp00nznet-snesrecomp` | `game-analysis` | [sp00nznet/snesrecomp](https://github.com/sp00nznet/snesrecomp/blob/03bf6178ed0569d76fe7cd1e456bc3b3974b2533/README.md) | `73b425f9195bd9ce550a31e3d5df19b78434e4b261d121ac11ed11b0f5ae5eb2` |
| `cvlod-recomp` | `reconstruction-cases` | [fliperama86/cvlod_recomp](https://github.com/fliperama86/cvlod_recomp/blob/60b40b5561c73389d4e5c317749deab601f32644/README.md) | `adc5ad49e6b6fe9dc55452a5f01265a1b4712fac3f87c26edc654b65413ac531` |
| `las-decomp` | `reconstruction-cases` | [Owen-Splat/las-decomp](https://github.com/Owen-Splat/las-decomp/blob/72cbe70e1319a369a5a5cb06fc864913e44fe069/README.md) | `f165d30e49bf2c6180e0f424bcb0696ae02b7cb18d4dc48f154595bb600d3eb6` |
| `ssa-recomp` | `reconstruction-cases` | [tsapZ/SSARecomp](https://github.com/tsapZ/SSARecomp/blob/35dfceb782b5e7716ff99530ff77b5be953b0f59/README.md) | `fceb2b4c9ed1c7969701bdb81f3b7c23b8a67525bd1cf8593ca2ed971a58926c` |
| `unwiished-recomp` | `reconstruction-cases` | [K-r0zen/Unwiished-Recomp](https://github.com/K-r0zen/Unwiished-Recomp/blob/1cb8f9531f0c4e60b5a4221081198cabb21a74af/README.md) | `61496aea6fd7af67d657908a096e8fac7473f86b42c4118ccb18baf467992ba4` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| codepdbh/nfsu2-recompiled, soyjxck/dod3-recomp, rigaz29/Ascension-R | No license file recorded by the GitHub API. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; SSARecomp received a Class 1 preview. The four new case studies update the game case indexes and README case sections.

---

# Backlog curation review, twenty-ninth batch — 2026-11-24

This round adds one recompilation list and five reconstruction cases: awesome-recompilations, Shadow of Rome Recompiled, Qwark’s Awakening, strikers-recomp, spm-nx and GalaxyFrame.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `awesome-recompilations` | `related-lists` | [BlueInterlude/awesome-recompilations](https://github.com/BlueInterlude/awesome-recompilations/blob/c75b7006dceae9ec492742476a9c61a1dcb35530/README.md) | `46ec2a29b49d83a67a567d30fc507b085142b239c33f9ff612391742c4fd2c61` |
| `shadow-of-rome-recompiled` | `reconstruction-cases` | [Korvonordico/shadow-of-rome-recompiled](https://github.com/Korvonordico/shadow-of-rome-recompiled/blob/18eb0226a3d7f2531860f0a64147e9074af1cb0d/README.md) | `6d7ca7aa559df3b8b6cb97c02588ed1fc3dbd1a2994da13423888c965df444bb` |
| `qwarks-awakening` | `reconstruction-cases` | [undecuple/qwarks-awakening](https://github.com/undecuple/qwarks-awakening/blob/e52809e64307b27134d83cc3893dccc38ca77538/README.md) | `a4220aa551f637515757407bf3d0eb9159e7a8dd8e1b1cc637b1a0425548ce66` |
| `strikers-recomp` | `reconstruction-cases` | [MTG9T4/strikers-recomp](https://github.com/MTG9T4/strikers-recomp/blob/54aa14f8646ae38c9d9b2c326fdc51556057ada8/README.md) | `225f486ccdce71804128f845365cef614cdd4d7068ebaba564340b7adb9f61b1` |
| `spm-nx` | `reconstruction-cases` | [Eladerino/spm-nx](https://github.com/Eladerino/spm-nx/blob/64405352c35b433e932fe11cec206f55eadd5040/README.md) | `c6bc9728e2a32749aee59fb16aee44a9201531b10d1369f80294cca8f79e00f9` |
| `galaxy-frame` | `reconstruction-cases` | [PodeCaradox/GalaxyFrame](https://github.com/PodeCaradox/GalaxyFrame/blob/fa5766398b7dec88ecffa80302bd016e667a9d22/README.md) | `7d29e739619e59243a1813d57e814a5ff7ca0ea105cdecc776a4bd6b397071a8` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| codepdbh/nfsu2-recompiled, soyjxck/dod3-recomp, rigaz29/Ascension-R | No license file recorded by the GitHub API. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; four Class 1 records received previews. The five new case studies update the game case indexes and README case sections.

---

# Backlog curation review, thirtieth batch — 2026-11-24

This round adds one port catalog, two port cases and three emulators: Native Ports, JSRF Unleashed NX, King’s Field Enhanced, Nestopia, Stella and WinUAE.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `native-ports-list` | `related-lists` | [matheusbrauna/native-ports](https://github.com/matheusbrauna/native-ports/blob/e182e7b07ef048c282dee9fb53b71263c07ad6ff/README.md) | `4d1f0c572a16d8a12ce53a3bb43464361c24b3001bba0fd4c2cb98318a79b79b` |
| `jsrf-unleashed-nx` | `reconstruction-cases` | [Eladerino/JetSetRadioFuture-Unleashed-NX](https://github.com/Eladerino/JetSetRadioFuture-Unleashed-NX/blob/bdda28e1702d476c32b29d76bf3e34628575f9f4/README.md) | `6004246a5b759b9be6d1618715d591892d31342c7aaa5de1cb9e98fd71796543` |
| `kf1-enhanced` | `reconstruction-cases` | [Acranon/kf1-enhanced](https://github.com/Acranon/kf1-enhanced/blob/ac147450249c95b8d7683300292a2761796cb611/README.md) | `23232b97d59834c0c80d0eb1a79d060330a80d5847edaef9a2654b9f9269885f` |
| `nestopia` | `game-analysis` | [0ldsk00l/nestopia](https://github.com/0ldsk00l/nestopia/blob/7b5c87d8dc3c817211545449683d1fcd897324ca/README.md) | `9091f47998564306d3bb69c8c8e098fee3cb29f9baaacb814b00a19662f80efe` |
| `stella` | `game-analysis` | [stella-emu/stella](https://github.com/stella-emu/stella/blob/8dd560091d22f9867cd9192880aa28570ed4d6db/README.md) | `26a62ea7113e3cc6d4c55d238c7c70107160db3a80bac6c0aedb4b4fa3032aca` |
| `winuae` | `firmware` | [tonioni/WinUAE](https://github.com/tonioni/WinUAE/blob/ee784914c8d61bb503d137e358b22fcc4758a294/README.md) | `a41a464952e30bf0bfb359deb766617605c6408d8b2490b2b206184478d25ff1` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| codepdbh/nfsu2-recompiled, soyjxck/dod3-recomp, rigaz29/Ascension-R | No license file recorded by the GitHub API. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; JSRF Unleashed NX received a Class 1 preview. The two new case studies update the game case indexes and README case sections.

---

# Backlog curation review, thirty-first batch — 2026-11-24

This round adds three emulators and three reconstruction cases: Firebird Emu, puNES, Boytacean, F-Zero Forever, GT5 Recomp and the Silent Hill Origins/GTA Vice City Stories recompiler fork.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `firebird` | `firmware` | [nspire-emus/firebird](https://github.com/nspire-emus/firebird/blob/f75e590fd43365654ea2bbe6683f15b54e57abfb/README.md) | `1905a848a73e0083c4e5a46e480e6b2b9d74874672cbc6f6064eb7ee2f75402b` |
| `punes` | `game-analysis` | [punesemu/puNES](https://github.com/punesemu/puNES/blob/b1758ec26a3d6da10abf50dc184fa837236c5f61/README.md) | `54b845b9d80b5d085df1812b70d0340904ad38096cd25848f1bab9a21b84c6f0` |
| `boytacean` | `game-analysis` | [joamag/boytacean](https://github.com/joamag/boytacean/blob/29b98dec9248d0ee2b9a155a625fa45467c038d8/README.md) | `702bcfda339026fd8041d4a7354be2fd88411cbe6791a830099714e9d375fce1` |
| `fzero-forever` | `reconstruction-cases` | [RetroPortingToolKit/FZeroSNESRecomp](https://github.com/RetroPortingToolKit/FZeroSNESRecomp/blob/de360149ff0758dafe4eda346e4bfa2179ff9ad1/README.md) | `dd6bc5a729663aaa00edbe6fa48cf57e17280f3573c062e93cc8ea6f671aa4d4` |
| `gt5-recomp` | `reconstruction-cases` | [MormonFTP-hub/gt5-recomp](https://github.com/MormonFTP-hub/gt5-recomp/blob/656133a97052a29abfaee8730d80f2fe73e688a6/README.md) | `606b7fd86710592325e70504d5d28d7e8c066787354493bf50eeaaf6af4a4ed2` |
| `sho-gta-vcs-recomp` | `reconstruction-cases` | [BlackLineInteractive/SHO-GTA-VCS-PS2Recomp](https://github.com/BlackLineInteractive/SHO-GTA-VCS-PS2Recomp/blob/659a2b0db11a14e818001f57331e216f5c604000/README.md) | `02a1f0063892d91217fea51adba9ccab767d28e9a27a94b9d4fc60db18ca8d56` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| codepdbh/nfsu2-recompiled, soyjxck/dod3-recomp, rigaz29/Ascension-R | No license file recorded by the GitHub API. |
| hulkholden/n64js, binji/binjgb, DaedalusX64 | More emulators deferred to keep this batch balanced. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; five Class 1 records received previews. The three new case studies update the game case indexes and README case sections.

---

# Backlog curation review, thirty-second batch — 2026-11-24

This round adds four emulators and two reconstruction cases: DaedalusX64, n64js, binjgb, Lichii, PGR4:ReGPU and Bomberman 64: The Second Attack! Recompiled.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `daedalusx64` | `game-analysis` | [DaedalusX64/daedalus](https://github.com/DaedalusX64/daedalus/blob/580c0c409358db332149fc2903c610449434f8fc/README.md) | `ef793f65fb4151c5fbb7afea96cbccc0f06c1af47bafc2c5127d8f6e9c270825` |
| `n64js` | `game-analysis` | [hulkholden/n64js](https://github.com/hulkholden/n64js/blob/3240cfd322460a7097080cba7a4e3d4eeb8bd56b/README.md) | `5a41efc1f772d89e64ac9016d794d68c6a4770a65f2e11235cf8e98d8ad0ae4a` |
| `binjgb` | `game-analysis` | [binji/binjgb](https://github.com/binji/binjgb/blob/6c04827f63d272f32afd86138a8e7262b3800344/README.md) | `0748ae75beac9018b69275702f04388edd2a43c285a785462c27303b2f733b73` |
| `lichii` | `game-analysis` | [zortos293/Lichii](https://github.com/zortos293/Lichii/blob/11021b0604c1c6462eff14147930481556014998/README.md) | `905a992363f5b8b06080713e5d8110f4cc30c91850e7f1e33a40e80920625165` |
| `pgr4-regpu` | `reconstruction-cases` | [zer0ducksgiven/PGR4-ReGPU](https://github.com/zer0ducksgiven/PGR4-ReGPU/blob/591e5730d0d95221b30d33586640a99e59ee3ec5/README.md) | `c1a132cc3213d851cf3ca3cccb6f8d427807b58dd46929182fbe67520fc9f283` |
| `pommy-recomp` | `reconstruction-cases` | [bdragoncore/pommy-recomp](https://github.com/bdragoncore/pommy-recomp/blob/0ba26ac1658130f750c2ed3a04ab632df1e2a79e/README.md) | `1533aa40e4c691a8c6aca3b9d9e2a49bb9b4b50b5f9bddd077316c3bbd1784cb` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| mstan/*Recomp (PSX/NES), TechnicallyComputers/*Recomp | No license file recorded by the GitHub API. |
| SamiEnazi/infamous2-port, rigaz29/Ascension-R | No license file recorded by the GitHub API. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; binjgb received a Class 1 preview. The two new case studies update the game case indexes and README case sections.

---

# Backlog curation review, thirty-third batch — 2026-11-24

This round adds four toolchain/workbench tools and two reconstruction cases: PatchELF, CE C/C++ Toolchain, PSX Modding Toolchain, decomp.anything, Rich4 reverse engineering and Star Fox Adventures decompilation.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `patchelf` | `native-analysis` | [NixOS/patchelf](https://github.com/NixOS/patchelf/blob/2b4b49d36b62690860414dd127f567be4f1f3208/README.md) | `65ea71d8063cba43f1a5e90bea028be91ed701fe0a4c8ede1d0f9aadbbc5ef4a` |
| `ce-toolchain` | `firmware` | [CE-Programming/toolchain](https://github.com/CE-Programming/toolchain/blob/7643f1a71e0d669f67dda22e8a4c38041812ce8a/README.md) | `f38aefbb152fa87b366236e1b0eed0b1fbe63255854d24931ae30b0835686e28` |
| `psx-modding-toolchain` | `game-analysis` | [mateusfavarin/psx-modding-toolchain](https://github.com/mateusfavarin/psx-modding-toolchain/blob/9332a8d43943c513502e92a7b8b03d9950fff5bb/README.md) | `561da067e1cd56a5ccc8291a1900b636c47453ad69daa46e42d55d7fc8788368` |
| `decomp-anything` | `native-analysis` | [giveen/decomp.anything](https://github.com/giveen/decomp.anything/blob/a37f31b9d77cfa800963e4fcdb66f4201a2adc37/README.md) | `98eb637f5290743676640cc25f4be5b4a5cc250b588362a6d451c5c14248304e` |
| `rich4` | `reconstruction-cases` | [mytbk/rich4](https://github.com/mytbk/rich4/blob/f4a1e13b7507f649c467802c7501ea214957a85c/README.md) | `bfc65f5f6df2b6bc69237e2ad494d59b4181d3a89a285866416d261c60581d47` |
| `sfa-decomp` | `reconstruction-cases` | [zcanann/SFA-Decomp](https://github.com/zcanann/SFA-Decomp/blob/ccd4d9aa413fbb4d715aaf5715764012cb4d93c1/README.md) | `da8f0c4783cdc6741f85b6ba310d543651060d4677f5eb2baccbb498d6c9880d` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| mstan/*Recomp, TechnicallyComputers/*Recomp | No license file recorded by the GitHub API. |
| MegaMan64Recomp/MegaMan64Recompiled | README is a 52-byte stub below the documentation threshold. |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. All are Class 2, so no previews were added; READMEs, case indexes and the site were regenerated.

---

# Backlog curation review, thirty-fourth batch — 2026-11-24

This round adds four reconstruction cases and two tools: BT4decomp, Halo 64, Carmageddon 2 rec2, Spyro the Dragon, Fulton and Levo.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| `bt4-decomp` | `reconstruction-cases` | [NauTaro/DBZ-BT4-Tag-Team-Decomp](https://github.com/NauTaro/DBZ-BT4-Tag-Team-Decomp/blob/a822ed987b41fb60ea53cfc211fa977c8d0d3be5/README.md) | `1047a556cff33943fdf28287fa574b1584fb92234f3254a67a967343f4eb5cd5` |
| `halo-64` | `reconstruction-cases` | [JackTulli/halo-64](https://github.com/JackTulli/halo-64/blob/0cabf11440d9bb63ee0fdce32b92e81774365865/README.md) | `e7d85d852d31bc0081f09852c6fda9182dc0aaeb2b0eb55536de8bf6ca409ee1` |
| `carmageddon2-rec2` | `reconstruction-cases` | [dethrace-labs/rec2](https://github.com/dethrace-labs/rec2/blob/73a125e85b6ff961b42070c1640e9a1ea6b6c72e/README.md) | `00286da22c55450f7c75319d95da617a00201b1e6433183411d6f4b35db9f772` |
| `fulton` | `game-analysis` | [TriwindBryan/fulton](https://github.com/TriwindBryan/fulton/blob/0d569b3a151018cf290560cfba34696595ebb078/README.md) | `5ffebf26f856a705919440b1670eb676ad62cf9d881b052a8a404cec337ba4b1` |
| `levo` | `native-analysis` | [momo5502/levo](https://github.com/momo5502/levo/blob/a6ff30cecb560feefd4f25add55831c7750239a3/README.md) | `7c18216bc6f14e3b9d15e123b688fbcc2b1f309701b5cc16ce6d0afe689621e2` |
| `spyro-1-decomp` | `reconstruction-cases` | [TheMobyCollective/spyro-1](https://github.com/TheMobyCollective/spyro-1/blob/8e1eabc1c8cf171ed4e4349ad70e7451b7ca0da7/README.md) | `1886b9ca11a9bd692f051bd759ae15186fe59011c3ec8fe39fa1e5a6d5792bda` |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| ruslan831/PlantsVsZombies-decompilation | README is 327 bytes below the documentation threshold. |
| mstan/*Recomp, TechnicallyComputers/*Recomp | No license file recorded by the GitHub API. |
| mstan/PokemonStadiumRecomp | README declares the project no longer maintained as of August 2026. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; BT4decomp and Halo 64 received Class 1 previews. The four new case studies update the game case indexes and README case sections.

## Batch 35 — 2026-11-24

Five reconstruction cases and a browser disassembler: Play Stunts, arcade-js, Daytona USA Web, Lambda1VR, the Street Fighter III 3rd Strike CPS3 decompilation and binkeep.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| play-stunts-web | reconstruction-cases | [ACatWithEbola/playstunts](https://github.com/ACatWithEbola/playstunts/blob/4d59314c41ba834a96050101492de97c043a0c85/README.md) | cdfebec5d41ba39b75b882de28ed956bf58fa02d829acae44027b10a8d14412f |
| arcade-js | reconstruction-cases | [qarl/arcade-js](https://github.com/qarl/arcade-js/blob/174d526f2e66301e5e466ce5d68230ebbe6b6f95/README.md) | b12350d73bf85609ae251c932d9553d8ca1e89fc846c121ade9fa121d038e1fc |
| daytona-usa-web | reconstruction-cases | [johannruiz/Daytona-USA-Web](https://github.com/johannruiz/Daytona-USA-Web/blob/1c05247ab0ae08821629ca1f751dbc38851200ba/README.md) | 06e2a4782dce0147aa6a26ac36e72cea5102798523c7f82f85081489a92f7b55 |
| lambda1vr | reconstruction-cases | [Team-Beef-Studios/Lambda1VR](https://github.com/Team-Beef-Studios/Lambda1VR/blob/99a0d62ebb051151929c9655a2fdab3977ee8a33/README.md) | 087ca9ae7fb9aaf5b251a1fbd9d5245d7337e6af54cb8fb58a127c83432efffd |
| sfiii3-arcade-decomp | reconstruction-cases | [gibletto/sfIII3-cps3-decomp](https://github.com/gibletto/sfIII3-cps3-decomp/blob/d440837003292a6521f85f0c57752c7b5f30255b/README.md) | 1f259af293c7214ce90790ea1ea33a934b71321c33b389c631e60cee07350861 |
| binkeep | native-analysis | [kano92-dir/binkeep](https://github.com/kano92-dir/binkeep/blob/a0084a8f146672a2ee0b219a3a5dd695f9b7ac96/README.md) | 5cb848f5a2469d5973e518e4ccd7bc14990964ef630dc227aeb34dc3e50b1344 |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| deathkiller/jazz2 | The Jazz Jackrabbit 2 reimplementation source moved to jazz2-native, which the catalog already carries. |
| benstone/3DMMEx, foone/3DMMForever | Modernised ports of Microsoft released 3D Movie Maker source, not reverse-engineering work. |
| headshot2017/3dpinball-dc | Last pushed 2024-07-19, too stale for an active entry. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; all six classify as Class 2 (code and docs, no demo or download). The three browser ports record game as their only target so the game method sections render.

## Batch 36 — 2026-11-25

Six reconstruction cases: ReStreet, MKW-THWOMP, MP4 Recomp, Liberty Pro Max, OpenCrystalCaves and Kart PS5.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| restreet-fifa-street-case | reconstruction-cases | [samuelit0davila/fifa-street-pc-port](https://github.com/samuelit0davila/fifa-street-pc-port/blob/0b554e377ef565a23641e5fe98dad4b569836ca4/README.md) | a8f03a63f82231b70c0375279ba90fe2eed588603f17931e0fb92e17e59ebb56 |
| mkw-thwomp-case | reconstruction-cases | [STS78721/MKW-THWOMP](https://github.com/STS78721/MKW-THWOMP/blob/d456e6b613b3f689b2655fc39e0971a030ce352d/README.md) | 68f3c66f6e34a475a0c85483615220eeafd906f5085ef06f0d30b8398633d635 |
| mp4-recomp-case | reconstruction-cases | [linuxopt/mp4-recomp](https://github.com/linuxopt/mp4-recomp/blob/74c0832150b7bb2731069744e0b400d3dba13fd2/README.md) | 4f80b84fccb048fd41bacbdb8f589d535fdbd45f79b422ca9938aa7366193aa0 |
| liberty-pro-max-case | reconstruction-cases | [Awis13/liberty-pro-max](https://github.com/Awis13/liberty-pro-max/blob/d825c4a40e096f8b327702ae6950c49b7320bd47/README.md) | 99a3e252ea928dc18a91cb42fdd528232abb913ffd36c8d5b845c080b7109ece |
| open-crystal-caves-case | reconstruction-cases | [OpenCrystalCaves/OpenCrystalCaves](https://github.com/OpenCrystalCaves/OpenCrystalCaves/blob/bb049b80d8abc9e032fb204eb4e29667a8f61240/README.md) | 73e4b84415c5cc0b0bb6b51fe70dc4f59c79684a3d106d8aa91247c131e159b1 |
| kart-ps5-mkwii-case | reconstruction-cases | [Phi1ow/mkwii-ps5](https://github.com/Phi1ow/mkwii-ps5/blob/5715a133f253f42dc2a0b43c45aaa0a4aeabcacc/README.md) | ae0a4c30b42d82078936190029baa6b4ed3f87ce80e62f58be17586e3a87ec45 |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| AshfordFamily/recvx-decomp | Code: Veronica X GameCube and Dreamcast decompilations are already curated. |
| Mabec-games/Conker-Recomped-and-Reloaded | The catalog already carries the Conker Live and Reloaded Xbox recompilation. |
| FoxWorkshop/ShadowRecomp | Three Shadow the Hedgehog decompilation and recompilation records already exist. |
| whovian64/pocket-native | A fork of the curated Zakuro project without a distinct reconstruction scope. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries; OpenCrystalCaves is Class 1 with a README demo image and the other five are Class 2.

## Batch 37 — 2026-11-25

Six mobile and multi-platform reconstruction cases: MBHaxe, melonDS for Android, the TMNT arcade port, HommaRe, Elite Force Single Player on Android and Super Mario Odyssey on Android.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| mbhaxe-case | reconstruction-cases | [RandomityGuy/MBHaxe](https://github.com/RandomityGuy/MBHaxe/blob/6cdb43386b550da5b155543f24db473ebec566f5/README.md) | 219746053eb9840b462a132b519629a4cd6fb08416bebc36ebf29de9feca061b |
| melonds-android | game-analysis | [rafaelvcaetano/melonDS-android](https://github.com/rafaelvcaetano/melonDS-android/blob/909647ba95ce903797e0112fedae570732bfd9cc/README.md) | ac25535dfd91a24cc0d3cc1b5a0d180a64fd6cabeab720a74cae2c5b02f69759 |
| tmnt-arcade-port-case | reconstruction-cases | [cheviman/tmnt-port](https://github.com/cheviman/tmnt-port/blob/aba58859fbc82f214bf3e82c928cd20d12902bc4/README.md) | 7ee39db04b959dd46e8b108518bfea179566bd11b91e7a9940dd7e01734f89b1 |
| hommare-case | reconstruction-cases | [livmaster-dev/HommaRe-public](https://github.com/livmaster-dev/HommaRe-public/blob/c398121ffcb994a10b883a0ff9f102cbe7b2d279/README.md) | 348fb84fe600c3cf01fa24ecae3aeae546fa5d304532f101b5bb788e1d77d942 |
| voyager-sp-android-case | reconstruction-cases | [imjustadudegamer/VoyagerSP-Android](https://github.com/imjustadudegamer/VoyagerSP-Android/blob/c73750361cfc22c1afb3a2c160fa9c5df57214db/README.md) | 61ca4fb14d58593e44e14c338bd92fa9d08bdb02caa3971b3d92b7a5f68701c8 |
| smo-android-case | reconstruction-cases | [Deez-coder/SMO-android-port](https://github.com/Deez-coder/SMO-android-port/blob/1b2f502de940e9f0261ca112db2a5cae6faea7ad/README.md) | a49cc1c8cba8ab63fc8fd115df13d7ef9c7dc5c2ff4bf42591839d45ccd3770c |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| daniele-rapagnani/alephone-android | Last pushed 2024-07-18, too stale for an active entry. |
| EXL/Gish | Last pushed 2022-08-12, too stale for an active entry. |
| JayElDragon/Paper-Boat-Android-Port | The catalog already carries PaperBoat, the native Paper Mario port built on the decompilation. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. MBHaxe, melonDS for Android, the TMNT arcade port and Elite Force Single Player are Class 1 with merged previews; HommaRe and the Super Mario Odyssey Android port are Class 2.

## Batch 38 — 2026-11-25

Six records: the LBA2 classic source port, OpenAdhoc, the Spyro 3 decompilation, Transformers Armada recompiled, CafeRecomp and Vice City Stories on Android.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| lba2-classic-community | reconstruction-cases | [LBALab/lba2-classic-community](https://github.com/LBALab/lba2-classic-community/blob/36076270ba608747f865e081c33d425ea5d68e93/README.md) | 14956e396b4f62c311cda81454cf9a6b1c2411843d12386e511fd539de135d4f |
| openadhoc | game-analysis | [Nenkai/OpenAdhoc](https://github.com/Nenkai/OpenAdhoc/blob/66e749b382702732908ac62e15e699ed62f95827/README.md) | 9b2b53e24a7ff00c473afa15807b2796e351280c74673a0addfc2a8db27240a2 |
| spyro-3-decomp | reconstruction-cases | [TheMobyCollective/spyro-3](https://github.com/TheMobyCollective/spyro-3/blob/0b03dad822902ca54c8e6298e9b37ad0b9eaf722/README.md) | cadb07e720a562507fe942e4246911148107dcaa454163c92338162af4bb146c |
| transformers-armada-recomp | reconstruction-cases | [kayliox/transformers-armada-recomp](https://github.com/kayliox/transformers-armada-recomp/blob/97bb7cf6de562238f82417227b0e2ed66dea30cf/README.md) | 7ef26d6fb82f2a336695db6ddd0cdc152768079e49f0aa7b671f50302a9cad4d |
| cafe-recomp-case | reconstruction-cases | [hardkiller2565123123/CafeRecomp](https://github.com/hardkiller2565123123/CafeRecomp/blob/6285e85423283b39f4acbe744b2cca69a863ccb5/README.md) | b4c887ae94e6beff71b5b9d5ed5a9964abaef4f038a2d54b11ca9283070f8387 |
| psprecomp-vcs-android-case | reconstruction-cases | [codepdbh/PSPRecomp-VCS-Android](https://github.com/codepdbh/PSPRecomp-VCS-Android/blob/9fd696f8d85f11ba36292c0c0fbe5403e8067359/README.md) | 95a61e199fcfdba24f034793b3a5b89386ad31f65ba0bb269859c8d965608659 |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| tclamb/mhp2g-decomp | Repository has no README, below the documentation threshold. |
| Brandon04Gonzalez/nier-android | README declares maintenance stopped. |
| YesterMester/TheSimpsonsGameRecomp, noahbaxter/GHClassic | The catalog already carries a Simpsons Game recompilation and two Guitar Hero II projects. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. Transformers Armada is Class 1 with a merged preview; the other five are Class 2.

## Batch 39 — 2026-11-25

Six records: HeyListen, Mario Party Recompiled, EDGE-Classic, Belfast, Sonic Riders Recomp and the 3D Home Architect print fix.

| Record | Category | Primary evidence | README SHA-256 |
| --- | --- | --- | --- |
| hey-listen-case | reconstruction-cases | [Sacrappy/HeyListen](https://github.com/Sacrappy/HeyListen/blob/752e305b8050f3882c12999dd509638f1271a644/README.md) | 5e0e6f9c3ce10f6f3a0c51c619e32794d623830f1c86bc579abc5052d9a2d841 |
| mario-party-recomp-case | reconstruction-cases | [n64hub/mario-party-recomp](https://github.com/n64hub/mario-party-recomp/blob/6e330af2ba306d3e6fc207a1158c586cb6cf510d/README.md) | 1fceade918ad6f1cff85a05ea829e9a5ab75cd9455e4d102e9b719044dfbf1f6 |
| edge-classic-case | reconstruction-cases | [edge-classic/EDGE-classic](https://github.com/edge-classic/EDGE-classic/blob/d4fe222e18453c5bce84845ae4cd93c0a99ff831/README.md) | 772ef8f2770207b1046a8d30c20bb8e87f5ad56ec5f4540b5c3726253dd28737 |
| belfast-case | reconstruction-cases | [catgirl-systems/belfast](https://github.com/catgirl-systems/belfast/blob/8eaa50b841b5996bd7c87016338bbd631e6b2639/README.md) | 4b0d8398422c7b13b72dfea668a1f830b1dd772884f1ee3247155f6b83b85285 |
| sonic-riders-recomp-case | reconstruction-cases | [teclilla18/sonic-riders-recomp](https://github.com/teclilla18/sonic-riders-recomp/blob/2f1d028d187361e9994d3b94676a4f3af2fbe1fe/README.md) | c105257014528b0f002744165124a37a3d2110cb2ffc19192134f3bcfc83fb47 |
| 3dhad3-print-image-case | reconstruction-cases | [jake-378/3dhad3-print-image-fix](https://github.com/jake-378/3dhad3-print-image-fix/blob/147c0b06bf151739658007ee43a854c1c2fae8ce/README.md) | 8e1f8ad59335bbce664a606c34ab318038a92fe84a4d9dad657736eb8920600a |

## Candidates set aside

| Candidate | Review result |
| --- | --- |
| shad0w77-code/MC_LA_Recompiled | A Midnight Club L.A. recompilation fork with PT-BR and FSR extras; four MCLA recompilation records already exist. |
| Glitxhhh/XenobladeChroniclesRecompiled | Series-wide work in development without releases, overlapping the curated Xenoblade recompilations. |
| dougchansan/pkmn-colosseum | The catalog already carries the continued Pokemon Colosseum matching decompilation. |

## Validation notes

All six records carry pinned README evidence, parallel Chinese requirements and evidence-class entries. HeyListen, EDGE-Classic and Sonic Riders Recomp are Class 1 with merged previews; the other three are Class 2. The 3D Home Architect record is the first 3d-design case in several batches.
