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
