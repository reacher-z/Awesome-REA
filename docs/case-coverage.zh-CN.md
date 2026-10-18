# 案例合集覆盖记录

[English](case-coverage.md) · [机器可读记录](../data/case-coverage.json)

核查日期：2026-10-18（UTC）。**591 个合集出现项**经 2 次有记录的重复合并后，对应 **589 个清单单元**。其中包括报告、工具、论文、讨论和想法，不能当作独立且已核验的项目数量。

项目身份归并尚未完成，因此独立项目数为 `null`，并非零。同一上游条目的中英文版本只计一次。同一项目的不同报告仍分别计为清单单元，除非已有明确的别名合并决定。

## 固定来源

| 合集快照 | 出现项 | 链接的 GitHub 仓库 | 目录记录 |
| --- | ---: | ---: | --- |
| [songshikang0111/awesome-REA-cases · 3a1c5cdfaa3f](https://github.com/songshikang0111/awesome-REA-cases/tree/3a1c5cdfaa3f2db0dd4f587208f8870eb633de23) | 423 | 50 | [awesome-rea-cases](https://awesomerea.org/zh/resources/awesome-rea-cases/) |
| [yibie/awesome-rea · 6df1bc922ac6](https://github.com/yibie/awesome-rea/tree/6df1bc922ac6b92dcd1b2f905c94d8cc4f3b5a3e) | 28 | 11 | [yibie-awesome-rea](https://awesomerea.org/zh/resources/yibie-awesome-rea/) |
| [HaozheH3/awesome-rea-games · 4316a4ce86fd](https://github.com/HaozheH3/awesome-rea-games/tree/4316a4ce86fdd851f0180ffee87dc336851bf5b6) | 140 | 137 | [haozhe-awesome-rea-games](https://awesomerea.org/zh/resources/haozhe-awesome-rea-games/) |

记录保留固定版本文件 URL、Git blob 标识、SHA-256 和字节数，仅描述这些已清点快照，不代表上游后续版本或整个领域。这里不再发布完整的上游简介或 README 正文。

仓库数按每个合集中的 GitHub 仓库、目录及文件链接规范化后计数，不会据此合并清单单元，也不代表独立项目数。对于按游戏组织的表格，每个项目行是一个出现项；同一游戏标题或共享仓库不能证明两个项目行是同一报告。

## 数量与状态

| 状态 | 出现项 | 清单单元 | 含义 |
| --- | ---: | ---: | --- |
| 已收录 (`already-curated`) | 73 | 72 | 完整范围已对应目录资源或论文；不代表独立运行复现。 |
| 待核查 (`pending`) | 447 | 446 | 一手核查或完整目录覆盖尚待完成；部分映射也保留在此状态。 |
| 证据不足 (`insufficient-evidence`) | 71 | 71 | 将想法、请求或尚缺支持的重建说法保留为线索。 |

80 个出现项含目录链接；共关联 72 个不同资源 ID 和 1 个论文 ID。映射范围单独记录，不能将这些群体相加当作独立项目数。

此记录为 88 个清单单元记载了新的一手来源核查。其他已有目录链接的条目对应目录中独立的来源核查记录；链接本身不代表重新核查了整篇合集报告。此记录没有独立复现运行实验。

此记录刻意不包含仓库 README 扫描 ID 或扫描数量。成功读取 README、被上游合集列出和案例经过来源核查，是不同事实。

## 本轮一手核查案例

| 案例 | 状态 | 一手证据 |
| --- | --- | --- |
| Universal Modder 游戏模组智能体工具包 | 已收录 | [来源](https://github.com/rehan-remade/universal-modder/blob/6a8865ae171b406f50892c7f46fc5f45655269eb/README.md) |
| PlxNative：重建原生 webOS 媒体客户端接口 | 已收录 | [来源](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| 智能体反编译：字节匹配验收复盘 | 已收录 | [来源](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote：Siri Remote 协议重建 | 已收录 | [来源](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| BaoCut Slides：交互式网页编辑器改编 | 已收录 | [来源](https://github.com/JimLiu/baocut/blob/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/docs/design/slides/slides-design.md) |
| Urban Terror in the browser | 证据不足 | [来源](https://x.com/levelsio/status/2106150888289009666) |
| Flutter 构建识别 | 已收录 | [来源](https://github.com/morluto/rea/pull/1582) |
| 通过 Ghidra 分析 MIPS ELF | 已收录 | [来源](https://github.com/morluto/rea/issues/1620) |
| 通过 Ghidra 静态分析 PSP ELF | 已收录 | [来源](https://github.com/morluto/rea/issues/1330) |
| 东方 Project 重建：贯穿三款游戏的智能体驱动方法 | 已收录 | [来源](https://github.com/morluto/rea/blob/c12d9eda87aa5a022ee7e18ea96d8d03bfd12e96/website/evidence/touhou-reconstruction-method.md) |
| 恐龙跑酷：恢复一条加速规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| ArtCraft: not proven Adobe or Office reverse engineering | 证据不足 | [来源](https://getartcraft.com/apps) |
| Obsidian ASAR: large-package analysis | 证据不足 | [来源](https://github.com/morluto/rea/issues/746) |
| Unity/Valheim assemblies | 证据不足 | [来源](https://github.com/morluto/rea/issues/1801) |
| Large multidex Android APK | 证据不足 | [来源](https://github.com/morluto/rea/issues/893) |
| .NET NativeAOT recovery request | 证据不足 | [来源](https://github.com/morluto/rea/issues/744) |
| Windows Calculator：重建百分比规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Android ApiDemos: tracing Java methods from an APK | 证据不足 | [来源](https://github.com/morluto/rea/pull/738) |
| HarmonyOS 应用包静态清点 | 已收录 | [来源](https://github.com/morluto/rea/pull/1447) |
| 固件分析 | 已收录 | [来源](https://github.com/morluto/rea/pull/741) |
| Codex browser annotations: finding the interaction bridge | 证据不足 | [来源](https://x.com/dotey/status/2109417222724600172) |
| Browserbase 插件：将 Claude in Chrome 浏览器桥接转接到云端 | 已收录 | [来源](https://github.com/browserbase/claude-code-plugin/blob/b399af34a1b1cc365d1e1c0089823c4fa5e10ea5/forwarding-server.js) |
| pi-computer-use: desktop interaction for other models | 证据不足 | [来源](https://github.com/injaneity/pi-computer-use/blob/67e9e2f77643f84605b738a3198048a88e92190e/README.md) |
| Background Computer Use in Swift | 证据不足 | [来源](https://github.com/actuallyepic/background-computer-use/blob/52116acfe0f2f57174f5e0166881abe944cb6eeb/README.md) |
| GameCube/Wii PowerPC support request | 证据不足 | [来源](https://github.com/morluto/rea/issues/1741) |
| Super Mario Sunshine：基于 AI 辅助反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/chasem-dev/sms-pc-port/blob/a2ff4eef099b22b2af487d1b5e3ac09ffe667d31/README.md) |
| Apple Preview: adding AI directly to a compiled app | 证据不足 | [来源](https://github.com/Pasta-Lab/edit-my-app/blob/7f469c1f179e2552cd3c5b46ab29b21aeadc838f/README.md) |
| wine-uwp：在修改版 Wine 上运行打包的 Windows 商店应用 | 已收录 | [来源](https://github.com/designgears/wine-uwp/blob/1cf79d025e0c18167de803820345a1c5f82fd17d/README.md) |
| CF632BLE：基于体脂秤协议研究的本地客户端 | 已收录 | [来源](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| DLSS on AMD: reported AI-assisted compute-shader reconstruction | 待核查 | [来源](https://github.com/mochizuki0323/DLSSNR-AMD/blob/ab00d2b23584de0f42ac91eca4d7d2d2fad11465/README.md) |
| Netflix/Prime: a reported unified streaming interface | 证据不足 | [来源](https://x.com/HigbeyMyrta/status/2109596534350524664) |
| fowlbrowser: an existing-session browser bridge for agents | 证据不足 | [来源](https://github.com/argofowl/FowlBrowser/blob/18f7519fa27289885c95b67eff714401ffff51f0/README.md) |
| OpenSetter: rebuilding comment-to-DM flows with an AI setter | 证据不足 | [来源](https://github.com/xbirimensah/opensetter/blob/40dc5ae2fde0b3930e6b59132eaf061edb0da0a8/README.md) |
| zee-rp：重建 Axure RP 11 的受支持文档操作 | 已收录 | [来源](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| Classic shooters: reported AI-assisted browser ports | 证据不足 | [来源](https://x.com/i/status/2109639780577190171) |
| Nanolathe：附研究文档的 Total Annihilation 引擎重实现 | 已收录 | [来源](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| cooler-lcd：Thermalright 显示屏协议实现 | 已收录 | [来源](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Helm Chart API v2: an AI-assisted specification draft | 待核查 | [来源](https://github.com/mattfarina/specs/blob/7d0395726d712e654a9aaf167603e82007811517/charts/v2.md) |
| AYN Odin 2 Portal: Codex-assisted native Omarchy bring-up | 待核查 | [来源](https://github.com/TechLuddite/omarchy-mobile-odin2/blob/00d11efc018971f6bab711e7952ff184cad333c2/README.md) |
| Virtual Desktop Streamer：在 Linux 上重建平台适配层 | 已收录 | [来源](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| Open Claude UI：基于 REA 调查的界面参考组件 | 已收录 | [来源](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| Eleven | 已收录 | [来源](https://github.com/Zfinix/eleven/blob/94760718dfd741ba93fcc9b591eb39a96c034103/README.md) |
| GTM tool: a reported REA-assisted lead and email workflow | 证据不足 | [来源](https://github.com/tashfeenahmed/kinetic/blob/6ccbff87d190aea8e11be993e25783f099b55a93/README.md) |
| TCLimate：重建选定的 TCL Home 云端控制 | 已收录 | [来源](https://github.com/umarz317/TCLimate/blob/2a33c2013dbf3f297238131ca9eb6e287b2beb67/Docs/Investigation.md) |
| Tea-export website: reported REA-assisted rebuild | 证据不足 | [来源](https://x.com/i/status/2110010062597230838) |
| Ledger Reborn：基于 QuickBooks 研究的独立记账实现 | 已收录 | [来源](https://github.com/lxistired/ledger-reborn/blob/d7f6b8a1f4ad6c4ae8b10100d1c93cf15940c21d/docs/CASE_STUDY.md) |
| Visor：独立的 Ray-Ban Meta 眼镜客户端 | 已收录 | [来源](https://github.com/macedonga/visor/blob/8caaa12df919c014c249efb71fdfa32b263f6c3e/README.md) |
| Profound: a reported REA-assisted SaaS reconstruction | 证据不足 | [来源](https://github.com/yaojingang/profound-clone/blob/93e87c901b9c51f444b243110dd643e066aa6e22/README.md) |
| GAMEKB-K17：重建宏键盘配置协议 | 已收录 | [来源](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| IsaacRecomp：将 Flash 游戏字节码转换为原生 C++ | 已收录 | [来源](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| 飞书：作者报告的隔离第二应用实例 | 已收录 | [来源](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Mi Health: timestamp repair and a cloud-data exporter | 证据不足 | [来源](https://github.com/LilZeeCN/mi-health-exporter/blob/1dc9274a90ccc83f02cbb3706aae2a4d55c8e90a/README.md) |
| Plustek 8200i / ThinkPad MIPI: improve Linux drivers using Windows reference behavior | 待核查 | [来源](https://github.com/cschalle/hw-harness/blob/093afc5c576c200f29b771d01624a327d0ff1806/examples/plustek-film-scanner/README.md) |
| Linux 上的 UU 远程：非官方协议实现 | 已收录 | [来源](https://github.com/VallierDev/uu-remote-linux/blob/696cf10e334b2e7fe1afcb698b354c09ee328447/README.en.md) |
| REA Reconstruction Companion: connect evidence to specifications, implementation and acceptance | 待核查 | [来源](https://github.com/ShadowSwaps/REA-Reconstruction-Companion/blob/590e65dd99596c7fb66598eaa5d6c051c2ec9a5f/evals/reference/reconstruction/README.md) |
| NJFE：用于电脑检查的 Soulear 相机协议桥接 | 已收录 | [来源](https://github.com/WildweaselMS/NJFE/blob/992866c6609f8c813f459ff79840cf04d5883f8e/README.md) |
| LeanREA 命令行逆向分析技能 | 已收录 | [来源](https://github.com/aicodeking/leanrea/blob/09ba4aa0217f82cd880f855a60b877f59f39b22b/README.md) |
| Super Mario 64 DS：带重定位核对的匹配反编译 | 已收录 | [来源](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| GoldenEye 007：基于反编译成果的智能体辅助原生移植 | 已收录 | [来源](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip：AI 辅助的 Super Smash Bros. 原生移植 | 已收录 | [来源](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp：明确玩法边界的静态重编译 | 已收录 | [来源](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| KartPad：Mario Kart Wii 重编译的平台集成 | 已收录 | [来源](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |
| Super Mario 64：带明确比较开关的 ROM 重建 | 已收录 | [来源](https://github.com/n64decomp/sm64/blob/9921382a68bb0c865e5e45eb594d9c64db59b1af/README.md) |
| 《旷野之息》：Switch 主程序的逐函数一致性反编译 | 已收录 | [来源](https://github.com/zeldaret/botw/blob/e78c02499d0f108ae9c00158198289764c5980fe/README.md) |
| 🗡️ The Legend of Zelda: Ocarina of Time — zeldaret/oot | 待核查 | [来源](https://github.com/zeldaret/oot/blob/8a3634ca774a9b58d822cbc2cc09309f31eac6a4/README.md) |
| Zelda 64: Recompiled：无需完整源码反编译的《姆吉拉的假面》原生移植 | 已收录 | [来源](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/b65c482ed672258eb684ab94a4e8c8aa662615ee/README.md) |
| 《姆吉拉的假面》：生成一致美版 N64 ROM 的反编译重建 | 已收录 | [来源](https://github.com/zeldaret/mm/blob/bf6bd9d0d3a90fe2f8960e034fbfd328e8bdef22/README.md) |
| 🗡️ The Legend of Zelda: The Minish Cap — zeldaret/tmc | 待核查 | [来源](https://github.com/zeldaret/tmc/blob/6fb6dfb4a7efbe24d0fd1dda5097af6131faacde/README.md) |
| 🚀 Metroid Prime — AxioDL/metaforce | 待核查 | [来源](https://github.com/AxioDL/metaforce/blob/de8fc69bd7f345d6cf5f0c8fc2798295e22522d3/README.md) |
| 🦔 Sonic Mania — RSDKModding/Sonic-Mania-Decompilation | 待核查 | [来源](https://github.com/RSDKModding/Sonic-Mania-Decompilation/blob/9dc699428420d752af9767bdb13f585ee0881bc0/README.md) |
| Unleashed Recompiled：转换 Xbox 360 游戏代码与着色器 | 已收录 | [来源](https://github.com/hedge-dev/UnleashedRecomp/blob/cf829a9eca8fb680fba4b0409ddeb6ca92f22e3c/README.md) |
| OpenGOAL：恢复 GOAL 代码并重建 Jak 系列游戏 | 已收录 | [来源](https://github.com/open-goal/jak-project/blob/32c3cf73970f885c0a588623208232db72a74a58/README.md) |
| LEGO Island：源码重建与单独记录的精确重构建 | 已收录 | [来源](https://github.com/isledecomp/isle/blob/8119bd013645972c72480e4de21529f1e91ce5c7/README.md) |
| ⚡ Pokémon FireRed — pret/pokefirered | 待核查 | [来源](https://github.com/pret/pokefirered/blob/037335f4c725d7c9aecdac87066f2002b4bd7e14/README.md) |
| DevilutionX：移植重建后的 Diablo 引擎 | 已收录 | [来源](https://github.com/diasurgical/DevilutionX/blob/94433061f847d22863e5d705c398f7c13d7bab85/README.md) |
| OpenMW：复用原内容并替代 Morrowind 引擎 | 已收录 | [来源](https://github.com/OpenMW/openmw/blob/5fdc0f1c4d1d07575f9b360b8cf1d6562232bf8e/README.md) |
| 🧙 Ultima Underworld: The Stygian Abyss — abedegno/underworld-exhumed | 待核查 | [来源](https://github.com/abedegno/underworld-exhumed/blob/e5deadd6945b492636aadccc14f52caa908b4186/README.md) |
| 🧙 Paper Mario — pmret/papermario | 待核查 | [来源](https://github.com/pmret/papermario/blob/1104f1f71b824042a5fa1f958f2d861b603320fd/README.md) |
| 🥊 Super Smash Bros. Melee — doldecomp/melee | 待核查 | [来源](https://github.com/doldecomp/melee/blob/f0cdbb0a7046aea44c7177fd72abf33c3d2af4d4/.github/README.md) |
| ⚔️ Perfect Dark — perfect-dark-pc-port/perfect_dark | 待核查 | [来源](https://github.com/perfect-dark-pc-port/perfect_dark/blob/32a1cb9f268dd3ac73016801025c6bbbfa20130f/README.md) |
| Perfect Dark：生成一致 ROM 的 Nintendo 64 反编译重建 | 已收录 | [来源](https://github.com/n64decomp/perfect_dark/blob/169ed48bdcbfb3b568b028bd5bebb27680073514/README.md) |
| REDRIVER2：借助 PlayStation 兼容层重建 Driver 2 | 已收录 | [来源](https://github.com/OpenDriver2/REDRIVER2/blob/b2d8857426f815007486def9bd23f9a6007a2c64/README.md) |
| Snowball War：范围明确的 REA 辅助小游戏重建 | 已收录 | [来源](https://github.com/tuunanet/rea-ski-or-die-reconstruction/blob/0eac0671c90e21a16e663da7772b60710101ef7f/README.md) |
| SpaceCadetPinball：将反编译游戏逻辑适配到 SDL2 | 已收录 | [来源](https://github.com/k4zmu2a/SpaceCadetPinball/blob/cb9b7b886244a27773f66b0b19fdc2998392565e/README.md) |
| Open Scrantic：重建 Johnny Castaway 屏幕保护程序引擎 | 已收录 | [来源](https://github.com/glauberlima/open-scrantic/blob/2db75008931eb744f79d0c3fb12e0d89950466ff/README.md) |

## 部分覆盖与别名

部分或相关目录映射：

- `song:touhou-reconstruction` — REA 发表的文章、其固定版本的证据说明及已合并的 REA PR #1475 覆盖了这份组合报告：TH08、TH095 与 TH04 的里程碑、各自定义下的进度计数，以及 TH08 浮点字面量判定依据的漏洞。完整映射指向该方法案例；TH08 项目条目仍为部分匹配。结果仍为作者报告，未单独审阅 TH095 与 TH04 仓库，也未主张构建或运行复现。
- `song:artcraft-boundary` — ArtCraft 应用页面称每个 Crafting App 都用 Rust 从零编写，并未声称进行了逆向工程；所审阅的四份 README 描述的是依据公开规范与观察到的行为完成的净室实现，不含专有代码。没有一手来源记录对 Adobe 或 Microsoft 软件的反编译或代码恢复，也没有来源确立第三方帖子所称的 REA 使用。PhotoCraft、WordCraft、GridCraft 与 DeckCraft 保留指向各自实现条目的部分映射；页面列出的 FilmCraft、LightCraft、CADCraft 等其他应用另有公开仓库，本次未审阅。保留此线索而不建立完整映射；这并非对这些应用质量的评价。
- `song:dlss-amd-compute-report` — 所链接的 DLSSNR-AMD 仓库经固定版本审阅，记录了 DLSS 5 神经渲染网络的 Vulkan 重新实现，权重由使用者自行提取，并与 NVIDIA DLL 的输出对比；该项目已另行收录，此处仅作为相关映射。被回复的帖子串引用的是另一个项目 HelixSR 的发布消息（在 AMD 上运行 DLSS 3.7 网络），因此不能确定该评论指的是 DLSSNR-AMD。DLSSNR-AMD 的文档和 HelixSR 的 README 都未描述 AI 辅助的逆向工程。完整映射需先审阅该帖子串所指项目；AI 主张仍未确立。
- `song:schaller-opticfilm-thinkpad-linux` — 既有扫描仪调查和独立的 ThinkPad IMX471 调校／驱动案例，覆盖此报告中的两个有限范围组成部分。映射仍为部分覆盖：均不确立完整扫描仪／相机行为、全设备兼容性或独立运行复现。
- `song:rea-reconstruction-companion` — Pocket Tasks 映射只覆盖一个作者已接触源码、公开候选及有限比较证据的命令行重建案例；不覆盖更广的 Companion 工作流、其他示例或模型／宿主效果。既有源码接触、人工复核待完成及历史指令包哈希均明确保留；不确立独立运行复现。
- `hao-games:row-020` — 固定版本的 README、构建规则、校验文件和 CI 配置支持这份美版 N64《姆吉拉的假面》反编译报告。完整映射只覆盖此仓库，不涵盖帖子所链接的存档；相关映射记录 Zelda 64: Recompiled 注明借用其头文件和函数，但它是独立的静态重编译。进行中状态、原 ROM 依赖、许可证缺失和项目报告的一致性均明确保留。
- `hao-games:row-134` — TH08 重建已收录，但此独立 WebAssembly 配套仓库不能作为同一制品视为已覆盖；其自身实现与部署说法仍待核查。
- `hao-games:row-136` — 目前只覆盖官方 TH04 弹幕角度辅助函数展示；此合集行指向更广的重建仓库，因此完整仓库／游戏覆盖仍待核查。
- `hao-games:row-137` — 目前只覆盖官方 DX-Ball 声像函数展示，不能据此认定此更广的游戏重建仓库已被精选收录或已完成。

别名决定：

- `song:mw2-decompilation`, `yibie:500-billion-tokens-later` → `song:mw2-decompilation` — 两条线索指向同一篇匿名游戏反编译复盘；不能采用二手合集推断的游戏名称。
- `song:decompwtf-agent-game-decompilation`, `yibie:decomp-wtf` → `song:decompwtf-agent-game-decompilation` — 两条线索指向同一个已命名的 decomp.wtf 项目；附加仓库线索不构成独立验证。

## 更新此记录

改变状态前应核查固定版本合集条目及其一手证据。保持出现项 ID 稳定，明确记录别名，使用带类型的完整／部分／相关目录映射，并将尚未解决的项目数量保持为未知。合集标题只是来源标识，不是已经核验的能力声明。

```sh
python3 scripts/build_case_coverage.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

校验器检查结构、公开 URL、固定版本收据、标识、别名、目录映射和派生数量；它不会访问上游来源，也不能证明上游结果为真。
