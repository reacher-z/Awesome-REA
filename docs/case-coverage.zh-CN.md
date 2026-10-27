# 案例合集覆盖记录

[English](case-coverage.md) · [机器可读记录](../data/case-coverage.json)

核查日期：2026-10-20（UTC）。**591 个合集出现项**经 2 次有记录的重复合并后，对应 **589 个清单单元**。其中包括报告、工具、论文、讨论和想法，不能当作独立且已核验的项目数量。

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
| 已收录 (`already-curated`) | 214 | 212 | 完整范围已对应目录资源或论文；不代表独立运行复现。 |
| 待核查 (`pending`) | 34 | 34 | 一手核查或完整目录覆盖尚待完成；部分映射也保留在此状态。 |
| 证据不足 (`insufficient-evidence`) | 343 | 343 | 将想法、请求或尚缺支持的重建说法保留为线索。 |

232 个出现项含目录链接；共关联 220 个不同资源 ID 和 2 个论文 ID。映射范围单独记录，不能将这些群体相加当作独立项目数。

此记录为 498 个清单单元记载了新的一手来源核查。其他已有目录链接的条目对应目录中独立的来源核查记录；链接本身不代表重新核查了整篇合集报告。此记录没有独立复现运行实验。

此记录刻意不包含仓库 README 扫描 ID 或扫描数量。成功读取 README、被上游合集列出和案例经过来源核查，是不同事实。

## 本轮一手核查案例

| 案例 | 状态 | 一手证据 |
| --- | --- | --- |
| Universal Modder 游戏模组智能体工具包 | 已收录 | [来源](https://github.com/rehan-remade/universal-modder/blob/6a8865ae171b406f50892c7f46fc5f45655269eb/README.md) |
| Firefighter：将反编译的 DOS 游戏移植为 Rust | 已收录 | [来源](https://gitlab.com/esr/firefighter/-/blob/84861db110928202571af2042cb9762720dc2c3e/history.adoc) |
| PlxNative：重建原生 webOS 媒体客户端接口 | 已收录 | [来源](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| 智能体反编译：字节匹配验收复盘 | 已收录 | [来源](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote：Siri Remote 协议重建 | 已收录 | [来源](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| Tuya RGB lights from a Mac | 证据不足 | [来源](https://x.com/luchoalfonso_/status/2108200739495362718) |
| BaoCut Slides：交互式网页编辑器改编 | 已收录 | [来源](https://github.com/JimLiu/baocut/blob/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/docs/design/slides/slides-design.md) |
| Claude Code: inspecting a compressed codebase | 证据不足 | [来源](https://x.com/servasyy_ai/status/2108846931183378537) |
| Urban Terror in the browser | 证据不足 | [来源](https://x.com/levelsio/status/2106150888289009666) |
| Binary-library rewrite | 证据不足 | [来源](https://x.com/leeoxiang/status/2109159806183538768) |
| Flutter 构建识别 | 已收录 | [来源](https://github.com/morluto/rea/pull/1582) |
| 通过 Ghidra 分析 MIPS ELF | 已收录 | [来源](https://github.com/morluto/rea/issues/1620) |
| 通过 Ghidra 静态分析 PSP ELF | 已收录 | [来源](https://github.com/morluto/rea/issues/1330) |
| 东方 Project 重建：贯穿三款游戏的智能体驱动方法 | 已收录 | [来源](https://github.com/morluto/rea/blob/c12d9eda87aa5a022ee7e18ea96d8d03bfd12e96/website/evidence/touhou-reconstruction-method.md) |
| 恐龙跑酷：恢复一条加速规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Smart toilet from the desktop | 证据不足 | [来源](https://x.com/thinkszyg/status/2109309251533570509) |
| flipper-telink：Tuya Zigbee 遥控器的替换固件 | 已收录 | [来源](https://github.com/ngxson/flipper-telink/blob/d58aef2e65b30f33f560474ce460127c6f18ca30/custom_fw/ss6400zb/README.md) |
| Website rebuild: delivery report | 证据不足 | [来源](https://x.com/goan999999/status/2109080288823562734) |
| TradingView: reconstruction workflow claim | 证据不足 | [来源](https://x.com/RohOnChain/status/2109347169316839434) |
| WHOOP Android app investigation | 证据不足 | [来源](https://x.com/uwwgo/status/2109217632758976755) |
| ArtCraft: not proven Adobe or Office reverse engineering | 证据不足 | [来源](https://getartcraft.com/apps) |
| Obsidian ASAR: large-package analysis | 证据不足 | [来源](https://github.com/morluto/rea/issues/746) |
| Unity/Valheim assemblies | 证据不足 | [来源](https://github.com/morluto/rea/issues/1801) |
| Large multidex Android APK | 证据不足 | [来源](https://github.com/morluto/rea/issues/893) |
| 借助 Ghidra 恢复 NativeAOT 元数据 | 已收录 | [来源](https://github.com/morluto/rea/issues/744) |
| Windows Calculator：重建百分比规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Android ApiDemos: tracing Java methods from an APK | 证据不足 | [来源](https://github.com/morluto/rea/pull/738) |
| HarmonyOS 应用包静态清点 | 已收录 | [来源](https://github.com/morluto/rea/pull/1447) |
| 固件分析 | 已收录 | [来源](https://github.com/morluto/rea/pull/741) |
| macOS Preview: rebuilds with and without REA and the limits of self-tests | 证据不足 | [来源](https://x.com/maheshboda006/status/2109154423712977359) |
| Codex browser annotations: finding the interaction bridge | 证据不足 | [来源](https://x.com/dotey/status/2109417222724600172) |
| BaoCut Design：移植重建的设计稿与设计系统编辑器 | 已收录 | [来源](https://github.com/JimLiu/baocut/blob/7aa049e82e1367da013b7aba80f0b79033fa04ad/packages/design-runtime/README.md) |
| Bluetooth gamepad on Windows | 证据不足 | [来源](https://x.com/fexisnpc/status/2103865671608307838) |
| Browserbase 插件：将 Claude in Chrome 浏览器桥接转接到云端 | 已收录 | [来源](https://github.com/browserbase/claude-code-plugin/blob/b399af34a1b1cc365d1e1c0089823c4fa5e10ea5/forwarding-server.js) |
| pi-computer-use: desktop interaction for other models | 证据不足 | [来源](https://github.com/injaneity/pi-computer-use/blob/67e9e2f77643f84605b738a3198048a88e92190e/README.md) |
| Background Computer Use in Swift | 证据不足 | [来源](https://github.com/actuallyepic/background-computer-use/blob/52116acfe0f2f57174f5e0166881abe944cb6eeb/README.md) |
| GarageBand format for automated composition | 证据不足 | [来源](https://x.com/anshuc/status/2106131543752122774) |
| Boba Fett in Red Dead Redemption 2 | 证据不足 | [来源](https://x.com/ChrisGPT/status/2106925689190354989) |
| Apple Notes migration to Grape | 证据不足 | [来源](https://x.com/ozgrozer/status/2035124755854979272) |
| GameCube/Wii PowerPC support request | 证据不足 | [来源](https://github.com/morluto/rea/issues/1741) |
| Gamepad settings after Bluetooth analysis | 证据不足 | [来源](https://x.com/corndogjpn2/status/2109289076243525916) |
| ASUS ACPI and Linux GPU support | 证据不足 | [来源](https://x.com/200Tabs1Brain/status/2108983700776186112) |
| Poker table organizer | 证据不足 | [来源](https://x.com/lipinhobeats/status/2109435654962655526) |
| Aerobiz 2: REA and Kimi decompilation | 证据不足 | [来源](https://x.com/TSFisher24nrex/status/2109452544913326086) |
| Codex computer-use interoperability research | 证据不足 | [来源](https://x.com/thisishars/status/2109461719789735948) |
| Pump.fun reconstruction report | 证据不足 | [来源](https://x.com/0rdlibrary/status/2109464346103263523) |
| Super Mario Sunshine：基于 AI 辅助反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/chasem-dev/sms-pc-port/blob/a2ff4eef099b22b2af487d1b5e3ac09ffe667d31/README.md) |
| Gaoding-inspired cover workbench | 证据不足 | [来源](https://x.com/Astronaut_1216/status/2109487167726903560) |
| Gaming mouse settings on macOS | 证据不足 | [来源](https://x.com/MovingCharts11/status/2109491501013377526) |
| Hermes Agent: Hark-assisted harness reconstruction | 证据不足 | [来源](https://x.com/pablothethinker/status/2109509759044854087) |
| Apple Preview: adding AI directly to a compiled app | 证据不足 | [来源](https://github.com/Pasta-Lab/edit-my-app/blob/7f469c1f179e2552cd3c5b46ab29b21aeadc838f/README.md) |
| PS5 security: reported AI-assisted investigation | 证据不足 | [来源](https://x.com/0x0SojalSec/status/2109517461921902780) |
| Air-conditioner protocol for AR gesture control | 证据不足 | [来源](https://x.com/justhalfbit/status/2109524402765488499) |
| wine-uwp：在修改版 Wine 上运行打包的 Windows 商店应用 | 已收录 | [来源](https://github.com/designgears/wine-uwp/blob/1cf79d025e0c18167de803820345a1c5f82fd17d/README.md) |
| Redmi TV: browser inspection for a dashboard | 证据不足 | [来源](https://x.com/zxlie_fehelper/status/2109533072370917846) |
| CleanMyMac: reported native-app prototype | 证据不足 | [来源](https://x.com/xiaoshan0413/status/2109540598633877515) |
| Nexalytics: testing REA on the author's own app | 证据不足 | [来源](https://x.com/wikwanat/status/2109542201927647588) |
| MetaTrader: a reported signal-analysis use case | 证据不足 | [来源](https://x.com/TheKing_Rapture/status/2109547879199056181) |
| Red Alert 2: an engine rewrite for reinforcement learning | 证据不足 | [来源](https://x.com/Chen1090874226/status/2109548112281055674) |
| Business software: an ongoing agent-assisted rebuild | 证据不足 | [来源](https://x.com/iamsupersocks/status/2109553690595979371) |
| CapCut transitions: a module-reconstruction lead | 证据不足 | [来源](https://x.com/fireandstart/status/2109554617004466397) |
| CF632BLE：基于体脂秤协议研究的本地客户端 | 已收录 | [来源](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| Android app: inspecting root checks and certificate pinning | 证据不足 | [来源](https://x.com/IanJKerins/status/2109559519584088093) |
| Kindle: Android firmware for WeRead | 证据不足 | [来源](https://x.com/hbyxabc/status/2109583911483519202) |
| Proxy client: restoring a Clash subscription bridge | 证据不足 | [来源](https://x.com/web3_fising/status/2109601382273880327) |
| Controlled JS/.NET samples: Codex with and without REA | 证据不足 | [来源](https://x.com/0xlangeai/status/2109603485914206498) |
| The Incredible Machine: a Claude-assisted browser rebuild | 证据不足 | [来源](https://x.com/staskulesh/status/2109605915175596275) |
| DLSS on AMD: reported AI-assisted compute-shader reconstruction | 待核查 | [来源](https://github.com/mochizuki0323/DLSSNR-AMD/blob/ab00d2b23584de0f42ac91eca4d7d2d2fad11465/README.md) |
| Netflix/Prime: a reported unified streaming interface | 证据不足 | [来源](https://x.com/HigbeyMyrta/status/2109596534350524664) |
| fowlbrowser: an existing-session browser bridge for agents | 证据不足 | [来源](https://github.com/argofowl/FowlBrowser/blob/18f7519fa27289885c95b67eff714401ffff51f0/README.md) |
| OpenSetter: rebuilding comment-to-DM flows with an AI setter | 证据不足 | [来源](https://github.com/xbirimensah/opensetter/blob/40dc5ae2fde0b3930e6b59132eaf061edb0da0a8/README.md) |
| Street Fighter III: AI refactoring of decompiled C | 证据不足 | [来源](https://x.com/renmu2017/status/2109581250424123651) |
| zee-rp：重建 Axure RP 11 的受支持文档操作 | 已收录 | [来源](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| CapCut: a REA/Claude video-editor rebuild | 证据不足 | [来源](https://x.com/Mehal_Kay/status/2109665456735076494) |
| ClearSpace: a CleanMyMac-inspired native cleanup app | 证据不足 | [来源](https://x.com/iceman_shen/status/2109665812017746132) |
| Home devices: a reported desktop controller | 证据不足 | [来源](https://x.com/Jumpan1111/status/2109664718499762606) |
| Discontinued accounting app: blocked by encryption | 证据不足 | [来源](https://x.com/liguozzz/status/2109671680977367085) |
| REA analysis: a binary prompt-injection test idea | 证据不足 | [来源](https://x.com/riyoway/status/2109670989319868863) |
| Classic shooters: reported AI-assisted browser ports | 证据不足 | [来源](https://x.com/i/status/2109639780577190171) |
| Obsidian: a GPT-selected reconstruction attempt | 证据不足 | [来源](https://x.com/tokyo10086/status/2109676911500951649) |
| Web Flow: a REA-assisted REST specification report | 证据不足 | [来源](https://x.com/GeekCatX/status/2109689282336346575) |
| Nanolathe：附研究文档的 Total Annihilation 引擎重实现 | 已收录 | [来源](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| Android priv-app: GPT-assisted permission inspection | 证据不足 | [来源](https://x.com/sisiisthinking/status/2109711257779765741) |
| cooler-lcd：Thermalright 显示屏协议实现 | 已收录 | [来源](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Camera firmware: a Codex-driven VM boot investigation | 证据不足 | [来源](https://x.com/elliehuxtable/status/2109715839117316150) |
| Helm Chart API v2: an AI-assisted specification draft | 待核查 | [来源](https://github.com/mattfarina/specs/blob/7d0395726d712e654a9aaf167603e82007811517/charts/v2.md) |
| Mobile game interactions: Codex and REA evidence mapping | 证据不足 | [来源](https://x.com/Steven_Soto/status/2109721540245782843) |
| Homatics ATV14: a reported Dolby Vision firmware fix | 证据不足 | [来源](https://x.com/qwerty__cs/status/2109722857207115879) |
| Personal website: a REA-assisted design reconstruction | 证据不足 | [来源](https://x.com/khaled_cli/status/2109733299115475393) |
| SaaS feature subsets: Codex observation and Replit rebuilding | 证据不足 | [来源](https://x.com/Andrew_Blumson/status/2109733493202981247) |
| Star Fox and Sonic CD: reported AI-assisted native ports | 待核查 | [来源](https://github.com/carlosrmz009/arwing/blob/d8fe7aaf67e0f4ba77c9814852d2ffaccd7d63c7/README.md) |
| AYN Odin 2 Portal: Codex-assisted native Omarchy bring-up | 证据不足 | [来源](https://github.com/TechLuddite/omarchy-mobile-odin2/blob/00d11efc018971f6bab711e7952ff184cad333c2/README.md) |
| Virtual Desktop Streamer：在 Linux 上重建平台适配层 | 已收录 | [来源](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| LG TV: a reported native Claude Code terminal | 证据不足 | [来源](https://x.com/ceoico/status/2109774258738176000) |
| WeChat local chats: a reported Codex-assisted decryption task | 证据不足 | [来源](https://x.com/trendtranslate1/status/2109779123778490858) |
| Sixteen note files: a reported REA/no-REA decoder comparison | 证据不足 | [来源](https://x.com/operatranscend/status/2109783203892597103) |
| Android touchscreen photo frame: Codex-assisted device research | 证据不足 | [来源](https://x.com/LeonardVolner/status/2109785163475591510) |
| LightBurn: a reported personal laser-control rebuild | 证据不足 | [来源](https://x.com/LIQUID8RPF/status/2109789864891940904) |
| Echo Show 5 Gen 2: a reported Hermes intercom and camera system | 证据不足 | [来源](https://x.com/Kurcide/status/2109791974014496983) |
| Elgato HDR：为 Elgato 4K X 的 10 位模式提供用户态采集通路 | 已收录 | [来源](https://x.com/talkaboutdesign/status/2109795113807630735) |
| Gardena mower: reported Codex motor control and firmware work | 证据不足 | [来源](https://x.com/BderKhan/status/2109840164004737341) |
| MarkText: a REA-assisted HTML export rebuild | 证据不足 | [来源](https://x.com/KKetemepi/status/2109839329933824026) |
| LGwebOS-menubar：LG webOS 电视的原生 macOS 遥控器 | 已收录 | [来源](https://x.com/greco_dev/status/2109842197654692349) |
| Screen Studio：作者报告的 REA 自动缩放规则研究 | 已收录 | [来源](https://x.com/HanZhang415188/status/2109843188341207283) |
| Armed and Dangerous: exploring remastering approaches with Ghidra and AI | 证据不足 | [来源](https://x.com/NikhilVerma/status/2109911827203358998) |
| Open Claude UI：基于 REA 调查的界面参考组件 | 已收录 | [来源](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| Fort Apocalypse: a reported Codex/Ghidra Android port | 证据不足 | [来源](https://x.com/JesperAdolf/status/2109865837477716324) |
| Minecraft × Plants vs. Zombies: a reported playable REA-assisted mashup | 证据不足 | [来源](https://x.com/Relph35432/status/2109912103813599539) |
| Three Kingdoms XIV: a reported trainer-to-MCP project | 证据不足 | [来源](https://x.com/0xMcDonald/status/2109913567428592046) |
| Virtua Fighter 2.1 / 3 TB: AI-assisted decompilation in progress | 待核查 | [来源](https://github.com/celsowm/vf2-decomp/blob/9a9f7270f090cfa0f38b0ec6a22c3e53dae4bd18/README.md) |
| Typeless: a reported local voice-input alternative built with REA | 证据不足 | [来源](https://x.com/TuyetloanP81840/status/2109971905336037671) |
| Supermodel：Real3D Pro-1000 图像生成器的初步模拟 | 已收录 | [来源](https://x.com/BartronPolygon/status/2110028302215999825) |
| Eleven | 已收录 | [来源](https://github.com/Zfinix/eleven/blob/94760718dfd741ba93fcc9b591eb39a96c034103/README.md) |
| 48-million-row database: a second-hand REA query-optimization report | 证据不足 | [来源](https://x.com/mika_systems/status/2110037357164441796) |
| GTM tool: a reported REA-assisted lead and email workflow | 证据不足 | [来源](https://github.com/tashfeenahmed/kinetic/blob/6ccbff87d190aea8e11be993e25783f099b55a93/README.md) |
| TCLimate：重建选定的 TCL Home 云端控制 | 已收录 | [来源](https://github.com/umarz317/TCLimate/blob/2a33c2013dbf3f297238131ca9eb6e287b2beb67/Docs/Investigation.md) |
| Tea-export website: reported REA-assisted rebuild | 证据不足 | [来源](https://x.com/i/status/2110010062597230838) |
| iTerm: Arabic text rendering informed by REA | 证据不足 | [来源](https://x.com/khaled_cli/status/2110091122517410164) |
| Bloomberg-style research terminal: a reported REA/Claude build | 证据不足 | [来源](https://x.com/ludoonchart/status/2110082824371908790) |
| Projector IR remote: inferring and testing a missing focus command | 证据不足 | [来源](https://x.com/notyroon/status/2110090047579926826) |
| Closed-source coding agent: reverse-engineered collaboration logic and a pi plugin | 证据不足 | [来源](https://x.com/aloosekite/status/2110151664846139425) |
| Smart pen: Codex-assisted decompilation and integration | 证据不足 | [来源](https://x.com/xhfloz/status/2110108201043775589) |
| ChatGPT app: a reported REA-assisted gradient-background modification | 证据不足 | [来源](https://x.com/LinearUncle/status/2110207568090198474) |
| Dragon Ball Budokai: an unverified AI-assisted browser-port report | 证据不足 | [来源](https://x.com/0x0SojalSec/status/2110230860717060262) |
| Ledger Reborn：基于 QuickBooks 研究的独立记账实现 | 已收录 | [来源](https://github.com/lxistired/ledger-reborn/blob/d7f6b8a1f4ad6c4ae8b10100d1c93cf15940c21d/docs/CASE_STUDY.md) |
| Visor：独立的 Ray-Ban Meta 眼镜客户端 | 已收录 | [来源](https://github.com/macedonga/visor/blob/8caaa12df919c014c249efb71fdfa32b263f6c3e/README.md) |
| Hongguo Short Drama: REA-assisted reverse engineering to remove ads and overlays | 证据不足 | [来源](https://x.com/web3_goto/status/2110320554049941661) |
| Profound: a reported REA-assisted SaaS reconstruction | 证据不足 | [来源](https://github.com/yaojingang/profound-clone/blob/93e87c901b9c51f444b243110dd643e066aa6e22/README.md) |
| Codex Desktop: author reports trying REA to study its differences from CLI | 证据不足 | [来源](https://x.com/ZhenHan261538/status/2110377021402661320) |
| Mac desktop app: REA-assisted analysis and reference materials | 证据不足 | [来源](https://x.com/fantexi997/status/2110382256829386935) |
| Apple Weather: reported REA-assisted rebuild | 证据不足 | [来源](https://x.com/jasonjias/status/2110459951365980334) |
| Friday Night Funkin’: a Claude-assisted gameplay variant | 证据不足 | [来源](https://x.com/i/status/2110407024731439392) |
| Linux cal: tracing the 1752 calendar switch | 证据不足 | [来源](https://x.com/fahdmirza/status/2110453427209916612) |
| TicTacToe-AI：REA 分叉对单个游戏方法的有限重建 | 已收录 | [来源](https://github.com/heaven-hm/re-agent/blob/a84c61e8baa65d445485722420a57ff4132b90d3/benchmarks/native-windows-ports/reports/targets/tictactoe.md) |
| Home-device protocols connected to a local LLM | 证据不足 | [来源](https://x.com/bitfish/status/2110539823572463953) |
| GAMEKB-K17：重建宏键盘配置协议 | 已收录 | [来源](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| Kirby: a reported REA investigation in progress | 证据不足 | [来源](https://x.com/oh_Roach/status/2110553648787013950) |
| Claude Code 中的 REA：隔离配置下的静态分析 A/B 试验 | 已收录 | [来源](https://zenn.dev/keigoly/articles/8738d8d241b5a1) |
| REA 6.4.0: Windows .NET and Electron sample tests | 证据不足 | [来源](https://x.com/i/status/2110563764886266167) |
| CPU kernels: Claude Code orchestrates Astra with REA | 证据不足 | [来源](https://x.com/nkeilar/status/2110566660113625486) |
| A saved website investigated with WorkBuddy International | 证据不足 | [来源](https://x.com/Muma102kMichael/status/2110593537872175256) |
| apk-reverse: an Android analysis skill for coding agents | 证据不足 | [来源](https://github.com/zzusec/apk-reverse/blob/1b94651b1e3c4479336406b8b5c06d4c1fd7082e/README.md) |
| Hailo: a planned agent-assisted reverse-engineering run | 证据不足 | [来源](https://x.com/TheCogArchitect/status/2110600631144919232) |
| Wyze scale: weight data in a custom iOS app | 证据不足 | [来源](https://x.com/Boards86/status/2110604057287217339) |
| A license-compliance comparison during reverse engineering | 证据不足 | [来源](https://x.com/i/status/2110614074941927618) |
| Codex: a personal library following REA research | 证据不足 | [来源](https://x.com/LinearUncle/status/2110616441611542781) |
| Richman 4: REA research to a Flutter iPhone rebuild | 证据不足 | [来源](https://x.com/iam678/status/2110618564608880843) |
| Tuya AC: local Mac controls exposed to Claude over MCP | 证据不足 | [来源](https://x.com/sarequl_basar/status/2110620776915411243) |
| A HyperOS monitor: exploring exposed control services | 证据不足 | [来源](https://x.com/binaryify/status/2110622119419838752) |
| Notes example: tracing a CSV export button | 证据不足 | [来源](https://x.com/0xCortexq/status/2110623921611432090) |
| IsaacRecomp：将 Flash 游戏字节码转换为原生 C++ | 已收录 | [来源](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| A legacy binary: an agent invents nonexistent APIs | 证据不足 | [来源](https://x.com/harden_369741/status/2110630792049115198) |
| Codex next-input prediction recreated for Pi | 证据不足 | [来源](https://x.com/a1chzt/status/2110631522403512760) |
| DOOM and Terraria: reported no-source mod experiments | 证据不足 | [来源](https://x.com/i/status/2110641024389271883) |
| 飞书：作者报告的隔离第二应用实例 | 已收录 | [来源](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Roko Input: Apple on-device dictation after Typeless research | 证据不足 | [来源](https://github.com/bassnova42/rokoinput/blob/3cd2da84ae83905b961a2de9f06bdf6bac888294/README.en.md) |
| Mi Health: timestamp repair and a cloud-data exporter | 证据不足 | [来源](https://github.com/LilZeeCN/mi-health-exporter/blob/1dc9274a90ccc83f02cbb3706aae2a4d55c8e90a/README.md) |
| REA and archify: interactive architecture diagrams | 证据不足 | [来源](https://x.com/i/status/2110570919169286424) |
| A colony-simulation engine: a decompilation research plan | 证据不足 | [来源](https://x.com/Promptmethus/status/2110642225361371219) |
| iX500 Scan：基于逆向 ScanSnap Wi-Fi 协议的 macOS 客户端 | 已收录 | [来源](https://x.com/jonaswagnr/status/2110647905027604700) |
| Sonic physics in Elden Ring: an unverified REA mod report | 证据不足 | [来源](https://x.com/Capslock404/status/2110648710606557644) |
| iriver E30: personalizing an unsupported player's main screen | 证据不足 | [来源](https://x.com/MikeS190477/status/2110651009181851731) |
| A radiator-control app bridged to Home Assistant with AI | 证据不足 | [来源](https://x.com/Madsoulswe/status/2110651982323310818) |
| D2R Mobile：在 Apple 设备上重新托管 Diablo II: Resurrected 的 Switch 程序 | 已收录 | [来源](https://x.com/OLD9Gaming/status/2110658894360097141) |
| WHOOP and Zhoop: an iPhone data path for a health agent | 证据不足 | [来源](https://x.com/0xLogicrw/status/2110659108076769728) |
| macOS Notes: a reported REA-assisted SwiftUI rebuild | 证据不足 | [来源](https://x.com/xiyue0803/status/2110670751087137197) |
| reverse-skill: investigation workflows for coding agents | 待核查 | [来源](https://x.com/i/status/2110680583634366777) |
| A thermofluid equation solver: ongoing REA/Opus work | 证据不足 | [来源](https://x.com/iamsupersocks/status/2110684985900355622) |
| A booking funnel investigated and rebuilt as a personal calendar | 证据不足 | [来源](https://x.com/JulianGoldieSEO/status/2110686215846699236) |
| Watch5 Pro: a reported Claude/REA health-sensor app | 证据不足 | [来源](https://x.com/Sp00kyD00kyXRS/status/2110693137773392155) |
| REA with local Qwen and pi: multi-target commercial-software tests | 证据不足 | [来源](https://x.com/deluxebear/status/2110696564335214807) |
| QUICKSURFACE AI: announced scan-to-parametric-CAD automation | 证据不足 | [来源](https://x.com/ManMetrologyLTD/status/2110699093333000322) |
| Spider-Man swinging in GTA V: an internally inconsistent REA claim | 证据不足 | [来源](https://x.com/vmrmax/status/2110699414792642732) |
| Humidity readings through an agent-built Bluetooth app | 证据不足 | [来源](https://x.com/real_kai42/status/2110700189912912155) |
| Grok Bot: a worker-network reverse-engineering idea not pursued | 证据不足 | [来源](https://x.com/leaf_sanren/status/2110702662270460232) |
| From a Little Prince game to Dragon Ball-themed HTML 3D | 证据不足 | [来源](https://x.com/i/status/2110713533193453572) |
| SentinelOne and Daybreak: a reported malware-analysis time reduction | 证据不足 | [来源](https://x.com/i/status/2110726263392387158) |
| A construction firm's SaaS workflows, observed and rebuilt | 证据不足 | [来源](https://x.com/andywalters/status/2110726879665660172) |
| Reversed with AI：AI 辅助逆向项目目录 | 已收录 | [来源](https://reversedwithai.com/about) |
| Mario Odyssey on macOS: a secondary Claude-assisted report | 证据不足 | [来源](https://x.com/swordBluesy/status/2110735780842999962) |
| Hermes Agent 的 REA 插件 | 已收录 | [来源](https://github.com/NousResearch/hermes-official-plugins/blob/6dacaaddbfd8e98dfc524096c44f712f743246b8/rea/README.md) |
| Mario's jump in Halo: an unverified six-parameter REA claim | 证据不足 | [来源](https://x.com/Capslock404/status/2110741739732435179) |
| Roborock Local Server：自托管替代 Roborock 扫地机云端 | 已收录 | [来源](https://x.com/whyamas/status/2110741945874350429) |
| Arkham: a Grok Bot/REA research-workbench rebuild | 证据不足 | [来源](https://x.com/monokern/status/2110743454959509801) |
| A plate reader's filter-wheel fault: a Claude-assisted repair report | 证据不足 | [来源](https://x.com/r_gross_/status/2110745676875227179) |
| Grok Build: exploratory code study with REA and Claude Code | 证据不足 | [来源](https://x.com/omerfrkdemiral/status/2110749141710028914) |
| Codex CLI: inspecting model-identity prompts and routing fields | 证据不足 | [来源](https://x.com/jiangkoumo_/status/2110751118343164066) |
| Rust Duty: reconstructing gameplay from video, not decompilation | 证据不足 | [来源](https://x.com/reidhslaughter/status/2110752844328419587) |
| 2010 Rust Rewrite Mashup: Skate 3 in MW2 maps | 待核查 | [来源](https://x.com/thenuntheia/status/2110757135009112576) |
| A wireless CarPlay adapter: a reported REA/Grok firmware change | 证据不足 | [来源](https://x.com/omercoskun_tech/status/2110759012266332509) |
| A daily voice-input app: quick client inspection, hours of rebuilding | 证据不足 | [来源](https://x.com/pirrer/status/2110759506003304641) |
| Linux EAC: an AI devirtualization claim via IDA Assist MCP | 证据不足 | [来源](https://x.com/i/status/2110759663822352852) |
| Browser Counter-Strike: a colleague's AI-build claim | 证据不足 | [来源](https://x.com/FuSheng_0306/status/2110760621113548854) |
| REA JavaScript demo: a stale-price check at 400 ms | 证据不足 | [来源](https://x.com/0xAlhimik/status/2110761684411572247) |
| Galaxy-Android: a reported AI-assisted native Super Mario Galaxy port | 待核查 | [来源](https://x.com/ToniCipriani007/status/2110763621768716353) |
| An old phone: an author reports running OEM firmware in Wasm with Claude | 证据不足 | [来源](https://x.com/ShishirTandale/status/2110765881768747173) |
| BINNY 逆向分析智能体框架 | 已收录 | [来源](https://github.com/openbin-ai/binny/blob/000b6aca8c9d266b38252470102ac16c98575cd8/README.md) |
| An illustrative game.exe demo: two rooms and three reconstruction oracles | 证据不足 | [来源](https://x.com/i/status/2110783611800522897) |
| H1Z1: research followed by an MMO built with Opus, Astra and Tripo | 证据不足 | [来源](https://x.com/i/status/2110784230687125852) |
| 《神秘海域：内森·德雷克合集》原生 Windows 移植 | 已收录 | [来源](https://github.com/bc160201983/Uncharted-The-Nathan-Drake-Collection-PC-port/blob/dfc9fb6e70794bc81ae62836e3e5fb993ff50b3e/README.md) |
| Slipstream 5000: an author reports a two-day Codex decompilation | 证据不足 | [来源](https://x.com/i/status/2110786958649684035) |
| A Chrome dark-mode extension: REA research for improvements | 证据不足 | [来源](https://x.com/i/status/2110797282308153562) |
| A construction-bid decryptor: reported Claude Code research into a password error | 证据不足 | [来源](https://x.com/i/status/2110802464786264210) |
| Pokémon HeartGold/SoulSilver: a secondhand multi-agent decompilation and cost report | 证据不足 | [来源](https://x.com/i/status/2110816115718824296) |
| A Resend alternative: reported email APIs and inboxes for agents | 证据不足 | [来源](https://x.com/i/status/2110817677778489400) |
| Two games' RNG: a Codex/ILSpy prediction-tracking report | 证据不足 | [来源](https://x.com/i/status/2110817897706582486) |
| Destiny 2 build 86657：Sunrise／Dawn 重建研究报告 | 已收录 | [来源](https://github.com/isinternets/d2-research/blob/9a5b58f1f8408ed48b01705e0138ee25050669f2/README.md) |
| Self-owned Android/Windows 95 apps: an Opus reverse-engineering test without REA | 证据不足 | [来源](https://x.com/i/status/2110820518983000118) |
| RINGFALL: a reported browser boss fight built from TH04 bullet-ring notes | 证据不足 | [来源](https://x.com/i/status/2110844188178952423) |
| Apple Watch Ultra 2: an unverified AI-reverse-engineering report of Android connectivity | 证据不足 | [来源](https://x.com/i/status/2110844478239945061) |
| Plustek 8200i / ThinkPad MIPI: improve Linux drivers using Windows reference behavior | 待核查 | [来源](https://github.com/cschalle/hw-harness/blob/093afc5c576c200f29b771d01624a327d0ff1806/examples/plustek-film-scanner/README.md) |
| Open-BFME: a report of AI-assisted Battle for Middle Earth decompilation and byte matching | 证据不足 | [来源](https://x.com/i/status/2110857508470604174) |
| Greenlight video API: query fields with AI, then probe actual validation with invalid values | 证据不足 | [来源](https://x.com/i/status/2110868326528303367) |
| Electron Notes sample: an REA static IPC test with an answer key | 证据不足 | [来源](https://x.com/i/status/2110869440762196138) |
| A character on a video homepage: a report of Fu Sheng's REA mashup demonstration | 证据不足 | [来源](https://x.com/i/status/2110873715810660594) |
| A personal YouTube version: an REA-assisted niche-video and AI-topic dashboard report | 证据不足 | [来源](https://x.com/i/status/2110878456611319835) |
| decomp.wtf 智能体反编译工具 | 已收录 | [来源](https://github.com/i12bp8/decomp.wtf/blob/575b4a30ed481ff5497dfb9ce4f599368a95a04a/README.md) |
| A local REA workbench: combine investigation and personal office workflows | 证据不足 | [来源](https://x.com/i/status/2110904597900673267) |
| Ledger Opus: an unverified finance-agent promotion referencing Claude for Finance | 证据不足 | [来源](https://x.com/i/status/2110916629244641548) |
| Immersive Portals: an AI-assisted Minecraft JE 26.2 compatibility report | 证据不足 | [来源](https://x.com/i/status/2110918344886927696) |
| TV firmware: an AI ad-removal idea and two implementation accounts | 证据不足 | [来源](https://x.com/i/status/2110919403961192504) |
| Excel reconciliation workbooks: infer a procedure from an accepted artifact for agents | 证据不足 | [来源](https://x.com/i/status/2110919658748719318) |
| OpenCodex / Antigravity: REA investigation of missing multi-turn tool-call signatures | 证据不足 | [来源](https://x.com/i/status/2110921946418602001) |
| Minesweeper and Bilibili: a secondary roundup of REA demonstration titles | 证据不足 | [来源](https://x.com/i/status/2110936629221450214) |
| MoonBit: Claude investigates name mangling to improve VSCode debugging | 证据不足 | [来源](https://x.com/i/status/2110938121080631767) |
| Obfuscated old games: a report of Claude guessing structure sizes incorrectly | 证据不足 | [来源](https://x.com/i/status/2110942707074183405) |
| Saturn Sonic 3D Blast: byte-matching decompilation and a native PC port | 证据不足 | [来源](https://x.com/i/status/2110939629516186067) |
| Linux 上的 UU 远程：非官方协议实现 | 已收录 | [来源](https://github.com/VallierDev/uu-remote-linux/blob/696cf10e334b2e7fe1afcb698b354c09ee328447/README.en.md) |
| Notes CSV 导出：作者报告的 REA 重建验收器检查 | 已收录 | [来源](https://x.com/i/status/2110963427791487391) |
| Obfuscated JavaScript request signatures: an author reports restoring data retrieval with REA | 证据不足 | [来源](https://x.com/i/status/2110968095850561701) |
| Immersive-translation-style extensions: investigating a bring-your-own-token alternative with Codex | 证据不足 | [来源](https://x.com/i/status/2110976193671709123) |
| ChatGPT Intelligent UI: asking Codex to investigate the implementation | 证据不足 | [来源](https://x.com/i/status/2110983483271286909) |
| Claude Code 背景动画实验室：基于 REA 调查的桌面动画重新实现 | 已收录 | [来源](https://github.com/Henry-fan88/claude-code-background/blob/3dbd1065835508be6027137927deeddb8c30fe55/README.md) |
| ChatGPT Work Cloud: probing a cloud agent's tools through introspection | 证据不足 | [来源](https://x.com/i/status/2111009945865097386) |
| Indian Kanoon: a reported Claude Code legal-search integration | 证据不足 | [来源](https://x.com/i/status/2111027056234627119) |
| Amap anti-bot controls: a secondhand Tencent sandbox-agent incident report | 证据不足 | [来源](https://x.com/i/status/2111034426066956783) |
| JPCERT/CC：攻击服务器上的 APK 解析与 API 探测 | 已收录 | [来源](https://blogs.jpcert.or.jp/ja/2026/10/web_api_attacks.html) |
| Polymarket Up/Down bot: a promotional REA strategy-analysis and replay report | 证据不足 | [来源](https://x.com/i/status/2111049696630194596) |
| crashlens 崩溃分诊工具 | 已收录 | [来源](https://github.com/mingleiw/crashlens/blob/7188611a506e058a8f4937acf3dfd3035545f2d1/README.md) |
| Halo 3 Reforged: a reader's AI-decompilation and 128-player claim | 证据不足 | [来源](https://x.com/i/status/2111052865410375683) |
| Samsung AC: local-network control with reported partial Claude assistance | 证据不足 | [来源](https://x.com/i/status/2111055239378018407) |
| A 2000 stress.exe: a reported Opus/REA revival for Mac and the web | 证据不足 | [来源](https://x.com/i/status/2111061027211395485) |
| RKD Telemetry Extractor：解读 Race-Keeper 赛道日录制数据 | 已收录 | [来源](https://github.com/sam-dumont/rkd-telemetry-extractor/blob/8db9f373e1a7162d3f2efa297986bdfa86d9400f/RESEARCH_NOTES.md) |
| QQPet: a cross-platform pet rebuilt from Arctic Penguin T800 | 证据不足 | [来源](https://x.com/aigeeknews/status/2111095142790857087) |
| Website to Next.js: a reported Claude Code template with parallel DOM-based rebuilding | 证据不足 | [来源](https://x.com/0xPascual/status/2111096590387601489) |
| Black Bot / Blacksidian: reported REA rebuilds with AI-provider choice | 证据不足 | [来源](https://x.com/i/status/2111100877083947405) |
| iOS on Android hardware: a porting idea and unverified HACKIOS/Redmi claims | 证据不足 | [来源](https://x.com/i/status/2111100973238329497) |
| VMP-protected sample: a reported failed DeepSeek challenge | 证据不足 | [来源](https://x.com/i/status/2111101746001113381) |
| Mega Man Battle Network: a secondhand AI decompilation and modding lead | 证据不足 | [来源](https://x.com/i/status/2111103450448572730) |
| A twelve-year-old Kindle: reported Claude safety refusal during a jailbreak attempt | 证据不足 | [来源](https://x.com/i/status/2111106257431961740) |
| 1997 audio software: investigating Windows 11 compatibility to continue old work | 证据不足 | [来源](https://x.com/i/status/2111115615628824723) |
| OpenRiseOfNations：原生 macOS 引擎重新实现 | 已收录 | [来源](https://github.com/ben-wright-1/OpenRiseOfNations/blob/2a0dfde8acdb7185c6087b10ef89b4f66731e5a0/README.md) |
| Computer integrates REA: five app-feature rebuilding demos including Figma | 证据不足 | [来源](https://x.com/AskPerplexity/status/2111120664543596957) |
| Claude Intercept 流量捕获分析工具 | 已收录 | [来源](https://github.com/whaesemeyer/claude-intercept/blob/c2b7d01911e11e063533dbd61a22b404b503b48d/README.md) |
| Claude client: inspecting environment telemetry with REA | 证据不足 | [来源](https://x.com/i/status/2111134289970765964) |
| Codex cursor: recovering drawing geometry for a Windows pointer | 证据不足 | [来源](https://x.com/i/status/2111142820207837308) |
| Gears of War 3: AI-assisted static recompilation and graphics work | 证据不足 | [来源](https://x.com/i/status/2111146922522402943) |
| WristBeam：为 Mac 配套应用重建佳明手表协议 | 已收录 | [来源](https://x.com/i/status/2111155441077977138) |
| Three open tools to personal apps: an REA recording, markup and dictation report | 证据不足 | [来源](https://x.com/i/status/2111156533002227870) |
| LmDrum firmware: Claude reportedly stops after decompilation progress | 证据不足 | [来源](https://x.com/i/status/2111169026160480290) |
| 1977 DES test vectors: Claude reportedly traces their random-generation environment | 证据不足 | [来源](https://x.com/i/status/2111170587792208361) |
| jq and Fossify Calculator: REA function identification and early inspection | 证据不足 | [来源](https://x.com/i/status/2111171612149985567) |
| Notion app.asar: a Claude read-only file and domain-string inspection | 证据不足 | [来源](https://x.com/0xKurogamii/status/2111182893313613877) |
| Grok Bot + REA: a reported software-investigation chat template | 证据不足 | [来源](https://x.com/ChaiWithAi/status/2111184500093026340) |
| Owned hardware for voice agents: an REA attempt inspired by earbuds and a smart ring | 证据不足 | [来源](https://x.com/i/status/2111158379896877249) |
| Patrick's AI reverse-engineered games directory: an ongoing resource project | 待核查 | [来源](https://x.com/i/status/2111185397782880475) |
| Doom: a claimed clean-room reimplementation with 19 Claude agents | 证据不足 | [来源](https://x.com/i/status/2111187899479658673) |
| NIST ECDSA curves: Claude traces the generation of public parameters | 待核查 | [来源](https://www.anthropic.com/research/ecdsa-curve-origins) |
| Niuniu AI / MT5: an REA rebuild report after a reseller relationship ended | 证据不足 | [来源](https://x.com/sera00111/status/2111206851606159655) |
| Mac video export: studying DaVinci and CapCut to improve a personal editor | 证据不足 | [来源](https://x.com/i/status/2111214346428686478) |
| Wiki Lab: a claimed REA-based Wikipedia for agents | 证据不足 | [来源](https://x.com/BrianDevoor/status/2111215569047314589) |
| Set-top-box APK: a short WorkBuddy extraction and analysis report | 证据不足 | [来源](https://x.com/i/status/2111216713245364424) |
| Base arbitrage contract: an unverified REA/Opus bytecode report | 证据不足 | [来源](https://x.com/i/status/2111220274226217276) |
| System UI from video: Claude measures frames and infers animation parameters | 证据不足 | [来源](https://x.com/i/status/2111222217849946308) |
| Linux mouse driver: reverse engineering among a week's AI projects | 证据不足 | [来源](https://x.com/i/status/2111224894297870413) |
| Roadster video: a Claude-assisted three.js visual teardown experiment | 证据不足 | [来源](https://x.com/i/status/2111225325531074716) |
| ENS v2 phishing email: a Claude-assisted investigation of dangerous agent repositories | 证据不足 | [来源](https://x.com/i/status/2111234225022067029) |
| Game-function matcher: an audit account of wrong constants passing checks | 待核查 | [来源](https://x.com/i/status/2111241506006700380) |
| Google Home: a blocked attempt to revive an old speaker without replacing hardware | 证据不足 | [来源](https://x.com/i/status/2111215951857246251) |
| A 3D home model: a reported REA-assisted Mac menu-bar controller | 证据不足 | [来源](https://x.com/0xProbabillity/status/2109978137794883621) |
| AMABOO Frameo: Claude Code adapts an existing Home HQ frame setup | 证据不足 | [来源](https://x.com/InvestingVault/status/2111250941886226471) |
| Grok Bot real-time features: a Hermes investigation with audio unresolved | 证据不足 | [来源](https://x.com/i/status/2111251559275487538) |
| Jiuchuan Xiaozhi AI speaker: give Muse stock firmware and hardware specifications | 证据不足 | [来源](https://x.com/i/status/2111251131665940519) |
| Fallout 4: a brief claim of fixes after Claude reverse engineering | 证据不足 | [来源](https://x.com/i/status/2111262935293038623) |
| A Windows keyboard utility: Claude builds a Linux version and checks it with a camera | 证据不足 | [来源](https://x.com/i/status/2111269740249489643) |
| REA Reconstruction Companion 重建配套技能 | 已收录 | [来源](https://x.com/xiyue0803/status/2111273763799191896) |
| Claude Desktop app.asar: Opus reportedly opens the package during feature research | 证据不足 | [来源](https://x.com/i/status/2111275332989059193) |
| CLO3D DLLs: an idea to rebuild a garment-design tool with Claude/Codex | 证据不足 | [来源](https://x.com/i/status/2111281354910704058) |
| NJFE：用于电脑检查的 Soulear 相机协议桥接 | 已收录 | [来源](https://github.com/WildweaselMS/NJFE/blob/992866c6609f8c813f459ff79840cf04d5883f8e/README.md) |
| LeanREA 命令行逆向分析技能 | 已收录 | [来源](https://github.com/aicodeking/leanrea/blob/09ba4aa0217f82cd880f855a60b877f59f39b22b/README.md) |
| MISE.exe: Claude proposes Ghidra-derived rules instead of screenshot guesses | 证据不足 | [来源](https://x.com/i/status/2111312368840126836) |
| Guitar effects: emulate the original firmware, then compare a standalone C++ library | 证据不足 | [来源](https://news.ycombinator.com/item?id=50104955) |
| RetroScope: a local-LLM assistant for ROM instruction references | 证据不足 | [来源](https://x.com/i/status/2111332462811087061) |
| China Mobile app: AI investigates number-selection pages and protocols for local filtering | 证据不足 | [来源](https://x.com/i/status/2111337934406484446) |
| Roku TV: a firmware-modification inquiry blocked by Claude's bootloader assessment | 证据不足 | [来源](https://x.com/i/status/2111349282745757858) |
| Serein's nine-bot workflow: pass REA behavior specifications to an isolated builder | 证据不足 | [来源](https://x.com/i/status/2111365135143219711) |
| Chrome LINE: AI reads JavaScript to build a TUI and messaging API | 证据不足 | [来源](https://x.com/i/status/2111366415639064608) |
| Reverse Engineering Assistant: a framework advertised for offline file-analysis reports | 待核查 | [来源](https://x.com/i/status/2111230457568227404) |
| 731 functions: an REA reconstruction account using specification isolation and four negative controls | 证据不足 | [来源](https://x.com/i/status/2111165651599663599) |
| Zenith collaborative editing: a reader asks about investigating it with REA | 证据不足 | [来源](https://x.com/i/status/2111358914520600998) |
| Hue screen-synced lighting: Claude investigates a macOS Bluetooth mode | 证据不足 | [来源](https://x.com/i/status/2111385823270625370) |
| JavaScript divergence: formatting switches the game, an AI reversing-decoy idea | 证据不足 | [来源](https://x.com/i/status/2111386823763411016) |
| Three-model binary research: function maps, competing hypotheses and an original-binary oracle | 证据不足 | [来源](https://x.com/i/status/2111389348339827041) |
| re2ds：Resident Evil 2 的原生 Nintendo DS 引擎 | 已收录 | [来源](https://www.reddit.com/r/ReverseEngineering/comments/1x85dp5/a_port_of_resident_evil_2_for_the_nintendo_ds/) |
| Starshield signals: a reader's idea to investigate frequencies with REA | 证据不足 | [来源](https://x.com/i/status/2111395824991097074) |
| Windows kernel: an REA collaboration idea for a free operating system | 证据不足 | [来源](https://x.com/i/status/2111405429486211272) |
| Amazon Prime tvOS: investigating IPA Universal Links to open shows from a personal app | 证据不足 | [来源](https://x.com/i/status/2111424789827228006) |
| Claude and Codex limits: an REA-assisted top-bar display report | 证据不足 | [来源](https://x.com/i/status/2111426952162947310) |
| LLVM ABI: gingerBill's account of using LLMs to investigate undocumented internals | 证据不足 | [来源](https://x.com/i/status/2111396413066363009) |
| Super Mario 64 DS：带重定位核对的匹配反编译 | 已收录 | [来源](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Define correctness as PASS/FAIL, then let agents iterate | 证据不足 | [来源](https://x.com/arpit_bhayani/status/2109505311904309621) |
| Where "software is solved" is overstated | 证据不足 | [来源](https://x.com/wangdou/status/2109404200513708307) |
| Reverse Engineer Anything, tried on a live game | 证据不足 | [来源](https://x.com/AIWarper/status/2109060856466264566) |
| Snowboard Kids：智能体辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/decompiling-a-nintendo-64-game-in-84-days/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| All games are open source now | 证据不足 | [来源](https://x.com/rehan_shei/status/2106548006350942533) |
| Sonic Advance 3：AI 辅助匹配单个敌人模块 | 已收录 | [来源](https://gambiconf.substack.com/p/development-journey-on-game-decompilation) |
| Claims that genAI speeds up PC ports of classic games are either "false" or missing the point | 证据不足 | [来源](https://www.reddit.com/r/SBCGaming/comments/1wyhd5s/claims_that_genai_speeds_up_pc_ports_of_classic/) |
| AI-generated decompilations are garbage | 证据不足 | [来源](https://www.reddit.com/r/decomps/comments/1v6b9gw/aigenerated_decompilations_are_garbage/) |
| Why isn't decompilation a solved problem in the AI era? | 证据不足 | [来源](https://news.ycombinator.com/item?id=49646640) |
| How are y'all using ai to make recompilations? | 证据不足 | [来源](https://www.reddit.com/r/recomps/comments/1wyle7y/how_are_yall_using_ai_to_make_recompilations/) |
| Zelda and Banjo Recompiled dev slams the slew of poor-quality "slopcomps" | 证据不足 | [来源](https://www.reddit.com/r/technology/comments/1ww1twg/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| 寻找 Jingle Town：在没有调试符号时调试 N64 游戏 | 已收录 | [来源](https://blog.chrislewis.au/finding-jingle-town-debugging-an-n64-game-without-symbols/) |
| Awesome Decomp Games：附评分、每日刷新的游戏重建项目目录 | 已收录 | [来源](https://github.com/SubmitGame/awesome-decomp-games/blob/02727e90fe10c7b55fad3fdd4bd671c55e1fe587/README.md) |
| GoldenEye 007：基于反编译成果的智能体辅助原生移植 | 已收录 | [来源](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip：AI 辅助的 Super Smash Bros. 原生移植 | 已收录 | [来源](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp：明确玩法边界的静态重编译 | 已收录 | [来源](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| Vandal Hearts：基于一致性反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/HalmyLyseas/VandalHearts-decomp-SLPM-86007/blob/75017596cc439a7141e405943afdb469b717787c/README.md) |
| KartPad：Mario Kart Wii 重编译的平台集成 | 已收录 | [来源](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |
| Xenosaga I 反编译兼容性工具包 | 已收录 | [来源](https://github.com/LinuxJessi/decomp-compat-kit/blob/d9bb53dac364ecfaff4f8b00ea44baec60a27abf/README.md) |
| sm64ex：基于反编译成果的 Super Mario 64 增强版 PC 移植 | 已收录 | [来源](https://github.com/sm64pc/sm64ex/blob/d7ca2c04364a6dd0dac58b47151e04e26887e6f0/README.md) |
| Super Mario 64：带明确比较开关的 ROM 重建 | 已收录 | [来源](https://github.com/n64decomp/sm64/blob/9921382a68bb0c865e5e45eb594d9c64db59b1af/README.md) |
| Ghostship：基于 libultraship 的 Super Mario 64 原生移植 | 已收录 | [来源](https://github.com/HarbourMasters/Ghostship/blob/40eef13823a954a466574dc78e73187a17a2dd42/README.md) |
| 🍄 Super Mario 64 — coop-deluxe/sm64coopdx | 证据不足 | [来源](https://github.com/coop-deluxe/sm64coopdx/blob/8cd6e5977d9f920d51ca71f2c61801d019ed79c6/README.md) |
| Super Mario Sunshine：仍在推进的 GameCube 一致性反编译重建 | 已收录 | [来源](https://github.com/doldecomp/sms/blob/b2350a119b0e113e6cebc389fda9af00328ee85e/README.md) |
| Super Mario Sunshine（美版）：AI 辅助的一致性反编译分支 | 已收录 | [来源](https://github.com/chasem-dev/sms-english/blob/d5f4eb3eb54ac49638b5513efb1fc368068805da/README.md) |
| 🍄 Super Mario Sunshine — chasem-dev/sms-launcher | 证据不足 | [来源](https://github.com/chasem-dev/sms-launcher/blob/c04b5a40788050ce15deb7955d215cbeea4fa125/README.md) |
| Petari：Super Mario Galaxy 一致性反编译重建 | 已收录 | [来源](https://github.com/SMGCommunity/Petari/blob/86ae7a3d3241adf07d5d3f9949e0462cccc583c1/README.md) |
| 《旷野之息》：Switch 主程序的逐函数一致性反编译 | 已收录 | [来源](https://github.com/zeldaret/botw/blob/e78c02499d0f108ae9c00158198289764c5980fe/README.md) |
| 《天空之剑》：以哈希校验重新链接的 Wii 版反编译 | 已收录 | [来源](https://github.com/zeldaret/ss/blob/d3d8e3cbf3d353b2231f06690965cac5366e28a1/README.md) |
| Ship of Harkinian：基于反编译源码的《时之笛》原生移植 | 已收录 | [来源](https://github.com/HarbourMasters/Shipwright/blob/dd702b0679f2240209763d00277e7343ee1424b9/README.md) |
| 《时之笛》：16 个版本均以 MD5 校验 ROM 构建的反编译 | 已收录 | [来源](https://github.com/zeldaret/oot/blob/8a3634ca774a9b58d822cbc2cc09309f31eac6a4/README.md) |
| Dusklight：基于反编译的《黄昏公主》原生移植 | 已收录 | [来源](https://github.com/TwilitRealm/dusklight/blob/34a144a493b7f57adeb4034d382317c826eb5c8d/README.md) |
| 《黄昏公主》：GameCube 版代码完全一致的反编译 | 已收录 | [来源](https://github.com/zeldaret/tp/blob/c8fa8c9e2aab72cf4e5db0e5d1c84a9ea6ee6eb0/README.md) |
| 《风之杖》：以哈希校验重新链接的 GameCube 版反编译 | 已收录 | [来源](https://github.com/zeldaret/tww/blob/8b93b372dc8e841f12ddfb7e0215626f62b05417/README.md) |
| Wind Waker HD Recomp：通过静态重编译实现的 Wii U 游戏原生移植 | 已收录 | [来源](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp/blob/f10b56621ed13e0053e7cf8190e740834377e45a/README.md) |
| Zelda 64: Recompiled：无需完整源码反编译的《姆吉拉的假面》原生移植 | 已收录 | [来源](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/b65c482ed672258eb684ab94a4e8c8aa662615ee/README.md) |
| 《姆吉拉的假面》：生成一致美版 N64 ROM 的反编译重建 | 已收录 | [来源](https://github.com/zeldaret/mm/blob/bf6bd9d0d3a90fe2f8960e034fbfd328e8bdef22/README.md) |
| 2 Ship 2 Harkinian：基于反编译的《姆吉拉的假面》原生移植 | 已收录 | [来源](https://github.com/2ship2harkinian/2ship2harkinian/blob/f1dda4c28cb9ed7cc80d8c78337ee31a8d2c7d0e/README.md) |
| 《缩小帽》：面向五个 ROM 的 GBA 反编译重建 | 已收录 | [来源](https://github.com/zeldaret/tmc/blob/6fb6dfb4a7efbe24d0fd1dda5097af6131faacde/README.md) |
| z2rs：以模拟器对照逐步重建《塞尔达传说 II》的 Rust 项目 | 已收录 | [来源](https://github.com/troyedwardsjr/z2rs/blob/4fe7a35f8ccfdccdf32421badf97b48b02d0127f/README.md) |
| Metaforce：在反编译之上重建的《密特罗德 Prime》引擎重实现 | 已收录 | [来源](https://github.com/AxioDL/metaforce/blob/de8fc69bd7f345d6cf5f0c8fc2798295e22522d3/README.md) |
| Metroid Prime Port：AI 辅助完成的 PrimeDecomp 反编译原生移植 | 已收录 | [来源](https://github.com/Odrannnn/MetroidPrimePort/blob/26febe4e09685ab68e7e0a9822934c0daa306a22/README.md) |
| Sonic Mania：面向 RSDKv5 引擎的游戏代码反编译重建 | 已收录 | [来源](https://github.com/RSDKModding/Sonic-Mania-Decompilation/blob/9dc699428420d752af9767bdb13f585ee0881bc0/README.md) |
| RSDKv5 Decompilation：重建 Retro Engine v5 与 v5U | 已收录 | [来源](https://github.com/RSDKModding/RSDKv5-Decompilation/blob/191d7aea6c262d891244172a8609ac69fbfd7571/README.md) |
| Unleashed Recompiled：转换 Xbox 360 游戏代码与着色器 | 已收录 | [来源](https://github.com/hedge-dev/UnleashedRecomp/blob/cf829a9eca8fb680fba4b0409ddeb6ca92f22e3c/README.md) |
| Donkey Kong 64: Recompiled：基于 N64Recomp 的原生移植 | 已收录 | [来源](https://github.com/Rainchus/Donkey-Kong-64-Recompiled/blob/3b0c36d3fbfeb0b5d2c47923f35cf84b31edcbf7/README.md) |
| c1：PlayStation 版《古惑狼》的 C 语言移植 | 已收录 | [来源](https://github.com/wurlyfox/c1/blob/256fdcef59f15a190290cc19db3fa9a707843b69/README.md) |
| Crash Bandicoot 2 Recompiled：基于 PSXRecomp 的原生构建 | 已收录 | [来源](https://github.com/Zumbo06/Crash2Recomp/blob/48036cf3b49dfe4343e5c093d1df8a7b12617f81/README.md) |
| C2C：《古惑狼 2》的混合重编译与手工反编译 | 已收录 | [来源](https://github.com/ughman/c2c/blob/2e9535fb0c59e37bf42316cb768be80c5e8073d4/README.md) |
| Conker's Bad Fur Day: Recompiled：基于 N64Recomp 的原生移植 | 已收录 | [来源](https://github.com/sciaschi/CBFD-Recompiled/blob/ed1b8bb7f3f036334124ec27eb28efa64e400178/README.md) |
| Banjo: Recompiled：基于 N64Recomp 的《Banjo-Kazooie》原生移植 | 已收录 | [来源](https://github.com/BanjoRecomp/BanjoRecomp/blob/dbd52154bc1e00e56867b1fac94a8f907052f41b/README.md) |
| Lighthouse：基于反编译项目的《Banjo-Kazooie》PC 移植 | 已收录 | [来源](https://github.com/HarbourMasters/Lighthouse/blob/4e8dfd23c64b143eb93ae9ee9fbae832cae2a2ef/README.md) |
| SymphonyRecomp：用 RecompOne 静态重编译《恶魔城：月下夜想曲》 | 已收录 | [来源](https://github.com/BlackLabelHQ/SymphonyRecomp/blob/c94a9096bab25bf513cceea50d6838a4c8d7bf5b/README.md) |
| Castlevania: Symphony of the Night：覆盖 PlayStation、PSP 与 Saturn 版本的一致性反编译 | 已收录 | [来源](https://github.com/Xeeynamo/sotn-decomp/blob/eddaf22fe86f5189b85fd34915afe6564f19df20/README.md) |
| Castlevania 64: Recompiled：测试版静态重编译移植 | 已收录 | [来源](https://github.com/RevoSucks/CV64Recomp/blob/141b35d8902a6c74e247988df26d394822f8026c/flatpak/io.github.cv64recomp.cv64recomp.metainfo.xml) |
| 🏰 Castlevania 64 — spacefarergames/CV64-Recomp | 证据不足 | [来源](https://github.com/HaozheH3/awesome-rea-games/blob/4316a4ce86fdd851f0180ffee87dc336851bf5b6/README.md) |
| ProjectCane：《Sly Cooper and the Thievius Raccoonus》原生 PC 移植 | 已收录 | [来源](https://github.com/theclub654/ProjectCane/blob/d8e34caf5edd2a0e2d4ec292b69145425ec6201c/README.md) |
| Sly Cooper and the Thievius Raccoonus：PlayStation 2 一致性反编译 | 已收录 | [来源](https://github.com/TheOnlyZac/sly1/blob/ea5e2d77ac2a083df1efeafcee178f895943b13d/README.md) |
| Ratchet & Clank：记录了代理流程的 PS2 一致性反编译 | 已收录 | [来源](https://github.com/OpenRAC/rac1-decomp/blob/7f5d3ff56701b611ac0e2c2589ef1f49cf8ac8fe/README.md) |
| OpenGOAL：恢复 GOAL 代码并重建 Jak 系列游戏 | 已收录 | [来源](https://github.com/open-goal/jak-project/blob/32c3cf73970f885c0a588623208232db72a74a58/README.md) |
| The Two Towers Recompiled：初代 Xbox 静态重编译移植 | 已收录 | [来源](https://github.com/Gumpolas/TooTawersRecomp/blob/6fce430797ec0573634fa6be18a08f73957efa63/README.md) |
| LEGO Island：源码重建与单独记录的精确重构建 | 已收录 | [来源](https://github.com/isledecomp/isle/blob/8119bd013645972c72480e4de21529f1e91ce5c7/README.md) |
| LEGO Island 可移植版：反编译源码的多平台移植 | 已收录 | [来源](https://github.com/isledecomp/isle-portable/blob/d0bf04fe605d7ec2a291e65df08bf26712452379/README.md) |
| MediEvil Recomp：PlayStation 游戏静态重编译为 C# | 已收录 | [来源](https://github.com/BlackLabelHQ/MediEvilRecomp/blob/b9e46db34db40d6e5c8e19b538e4d517299a4012/README.md) |
| MediEvil 反编译：早期阶段、以校验值把关的 PlayStation 项目 | 已收录 | [来源](https://github.com/MediEvilDecompilation/medievil-decomp/blob/6afe6fe35d5ddf0ce1bebdb2e72f8215b5b5b407/README.md) |
| ico-pc：由 PS2 反编译源码编译而成的《ICO》原生移植 | 已收录 | [来源](https://github.com/nathanialf/ico-pc/blob/4c29ac4c121a357092dea6ee12f6d715ce6cf1f9/README.md) |
| King Kong Recompiled：由 AI 开发的 Xbox 360 静态重编译 | 已收录 | [来源](https://github.com/TekRantGaming/king-kong-recompiled/blob/c852d9f467201e9a02c1aaf099b65522535b3473/README.md) |
| pokered：一致构建的《精灵宝可梦 红／蓝》反汇编 | 已收录 | [来源](https://github.com/pret/pokered/blob/af519899719f0754965776faac0e836a3b906e6d/README.md) |
| pokecrystal：一致构建的《精灵宝可梦 水晶》反汇编 | 已收录 | [来源](https://github.com/pret/pokecrystal/blob/3bc8daa4173e96a7f4011dad3922eb6fa5dad5c6/README.md) |
| pokeruby：一致构建的《精灵宝可梦 红宝石／蓝宝石》反编译 | 已收录 | [来源](https://github.com/pret/pokeruby/blob/5784633ce4ef7ade1a7f2d2d0c288e3d5e6cdd7f/README.md) |
| 《宝可梦 绿宝石》：生成一致 ROM 的 Game Boy Advance 反编译重建 | 已收录 | [来源](https://github.com/pret/pokeemerald/blob/731ad5bfd6e6f265508d0efcca0ba42f9dcf5881/README.md) |
| 《宝可梦 火红／叶绿》：生成一致 ROM 的 Game Boy Advance 反编译重建 | 已收录 | [来源](https://github.com/pret/pokefirered/blob/037335f4c725d7c9aecdac87066f2002b4bd7e14/README.md) |
| 《宝可梦 心金／魂银》：校验一致的进行中 DS 反汇编项目 | 已收录 | [来源](https://github.com/pret/pokeheartgold/blob/5bb4b3b4961cbf0f8a42360c58a3c045d8535069/README.md) |
| 《宝可梦 白金》：校验一致的 Nintendo DS 反编译重建 | 已收录 | [来源](https://github.com/pret/pokeplatinum/blob/1dc13dcea40c04ab53f1f607de46023dc409ef20/README.md) |
| Pokémon Platinum PC Port：基于 pret 反编译的原生移植 | 已收录 | [来源](https://github.com/cybervisi0n/pokeplatinum/blob/35067868f64f23d25d17ac3e536cfdd9a7f40523/README.md) |
| UltraSunnyMoon：以 REA 主导的部分《宝可梦 究极之日》重建 | 已收录 | [来源](https://github.com/tylergraydev/UltraSunnyMoon/blob/913eed4969163ea15e354dacb8e2bfe0a2439de5/README.md) |
| 《王国之心 358/2 Days》：逐字节一致的 Nintendo DS 反编译重建 | 已收录 | [来源](https://github.com/Yokimitsuro/khdays-decomp/blob/261a89eaa8f65dd566ae0828b0b57c85c847a6ee/README.md) |
| Kingdom Hearts 358/2 Days：基于一致性反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/Yokimitsuro/khdays-port/blob/8e0ad0b04d97d869c53f301bc40987f0ab929799/README.md) |
| D2R Mobile：在 Apple 设备上重新托管 Diablo II: Resurrected 的 Switch 程序 | 已收录 | [来源](https://github.com/jhaizhou-ops/d2r-mobile/blob/9393b00ea9aca52d9254214da93738f26582562f/README.md) |
| DevilutionX：移植重建后的 Diablo 引擎 | 已收录 | [来源](https://github.com/diasurgical/DevilutionX/blob/94433061f847d22863e5d705c398f7c13d7bab85/README.md) |
| DiabloWeb：基于 Devilution 的 WebAssembly 浏览器移植 | 已收录 | [来源](https://github.com/d07RiV/diabloweb/blob/c61ef19c54ea646aed328bd8cc82c8a5f1ebd81d/README.md) |
| OpenMW：复用原内容并替代 Morrowind 引擎 | 已收录 | [来源](https://github.com/OpenMW/openmw/blob/5fdc0f1c4d1d07575f9b360b8cf1d6562232bf8e/README.md) |
| FFTARecomp：Final Fantasy Tactics Advance 的静态重编译 | 已收录 | [来源](https://github.com/Jorge262007/FFTARecomp/blob/7af625665d40ef3d39b3730a3c591ff66f7b2929/README.md) |
| Underworld Exhumed：重建 Ultima Underworld I 与 II | 已收录 | [来源](https://github.com/abedegno/underworld-exhumed/blob/e5deadd6945b492636aadccc14f52caa908b4186/README.md) |
| Vandal Hearts：基于一致性反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/HalmyLyseas/VandalHearts-PcPort/blob/14552fffa0e0b47e02b57592e274fc6e7a649923/README.md) |
| 🧙 Paper Mario — lucyawrey/Paper_Mario_64_Recomp | 证据不足 | [来源](https://github.com/lucyawrey/Paper_Mario_64_Recomp/blob/09dcb129ab4c3ab5ae4d1838841f05decb6e7b26/README.md) |
| Paper Mario：覆盖四个版本的一致性 Nintendo 64 反编译 | 已收录 | [来源](https://github.com/pmret/papermario/blob/1104f1f71b824042a5fa1f958f2d861b603320fd/README.md) |
| PaperBoat：基于反编译成果的 Paper Mario 原生移植 | 已收录 | [来源](https://github.com/HarbourMasters/PaperBoat/blob/d98b4b630f0674548067f59019fffef6885766e8/README.md) |
| Lost Odyssey Recomp：将 Xbox 360 角色扮演游戏静态重编译为原生移植 | 已收录 | [来源](https://github.com/freefrank/LostOdysseyRecomp/blob/32fb6f73efef0e34ac05913b8521bad026b4ff65/README.md) |
| GoldenEye 007：覆盖三个版本的一致性 Nintendo 64 反编译 | 已收录 | [来源](https://github.com/n64decomp/007/blob/c4356466796c697dfd298010b9bed261f9ed8c6a/readme.md) |
| Budokai Tenkaichi 3：基于一致性反编译的原生 PC 移植 | 已收录 | [来源](https://github.com/z3xox/Tenkaichi3Decomp/blob/ec3c85a98cffd9cd22c22ac14cd62fb584d23664/README.md) |
| Halo 2：智能体辅助的 LTCG Xbox 版一致性反编译 | 已收录 | [来源](https://github.com/kirklandsig/halo2-decompiled/blob/e25e96f9236a74b15ab0f0acaa7af53918ca1233/README.md) |
| Super Smash Bros. Melee：可移位构建的 GameCube 一致性反编译 | 已收录 | [来源](https://github.com/doldecomp/melee/blob/f0cdbb0a7046aea44c7177fd72abf33c3d2af4d4/.github/README.md) |
| Melee Unlocked：Melee 的 Windows 源码移植与静态重编译 | 已收录 | [来源](https://github.com/Hero88go/melee-unlocked/blob/589415b70123e699226f1925ad7a59ef8203a71c/README.md) |
| Saints Reborn：基于 ReXGlue 的 Saints Row 静态重编译 | 已收录 | [来源](https://github.com/whompay/SaintsReborn/blob/cb09c54cf9ff5c19a9c1cb8e080f465a322bd0eb/README.md) |
| Starfox 64: Recompiled：基于 N64Recomp 的静态重编译移植 | 已收录 | [来源](https://github.com/sonicdcer/Starfox64Recomp/blob/f2996555d73ca480f3dc3639f375c50818847bfc/README.md) |
| Starship：基于反编译的 Star Fox 64 PC 移植 | 已收录 | [来源](https://github.com/HarbourMasters/Starship/blob/3322643f0bbf80d2f8f7e1c0d2c4c578515f6c90/README.md) |
| ⚔️ Perfect Dark — perfect-dark-pc-port/perfect_dark | 待核查 | [来源](https://github.com/perfect-dark-pc-port/perfect_dark/blob/32a1cb9f268dd3ac73016801025c6bbbfa20130f/README.md) |
| Perfect Dark：生成一致 ROM 的 Nintendo 64 反编译重建 | 已收录 | [来源](https://github.com/n64decomp/perfect_dark/blob/169ed48bdcbfb3b568b028bd5bebb27680073514/README.md) |
| 🕵️ Syphon Filter — Madxbio97/SF-pc-port | 证据不足 | [来源](https://github.com/HaozheH3/awesome-rea-games/blob/4316a4ce86fdd851f0180ffee87dc336851bf5b6/README.md) |
| Syphon Filter: The Omega Strain：可逐字节重建 PS2 可执行文件的一致性反编译 | 已收录 | [来源](https://github.com/zm2283145/syphon-filter-omega-strain-decomp/blob/d41eacc6dd89befed75fec21a02faaa2b5a4750c/README.md) |
| The Darkness Recomp：配有原生 D3D11 渲染器的 Xbox 360 静态重编译 | 已收录 | [来源](https://github.com/portingpete/The-Darkness-Recomp/blob/98f0bcd49dfee90dfee968a3b75fd40e892c91e7/README.md) |
| P.T. PC 版：基于行为重新实现、读取 PS4 数据的引擎 | 已收录 | [来源](https://github.com/LoreanXavier/pt-pc/blob/d0a9b8f8969588a9ab2b1db03a35854d3af63f2e/README.md) |
| Dead Rising 2: Case Zero：Xbox 360 XBLA 游戏的静态重编译移植 | 已收录 | [来源](https://github.com/wivi514/Dead_Rising_2_Case_Zero_Xenon_Recomp/blob/a1feb9dd7a61e23b4bcbb1afab8edf3439ee86ac/README.md) |
| Dead Rising 2: Case West：同系列的 Xbox 360 XBLA 静态重编译移植 | 已收录 | [来源](https://github.com/wivi514/Dead_Rising_2_Case_West_Xenon_Recomp/blob/cb7dc0f46cfc71961e37f8a20b07ad143a3e161a/README.md) |
| Himuro：Fatal Frame（《零》）PS2 一致性反编译 | 已收录 | [来源](https://github.com/Mikompilation/Himuro/blob/595b082aef19c329a25dc6926e4ac638d13ed75d/README.md) |
| MikuPan：基于 Himuro 反编译的 Fatal Frame 原生 PC 移植 | 已收录 | [来源](https://github.com/Mikompilation/MikuPan/blob/ec204d75441e98d8bd43ddd95cae744eb683f00c/README.md) |
| 🏎️ Mario Kart 64 — n64decomp/mk64 | 证据不足 | [来源](https://github.com/HaozheH3/awesome-rea-games/blob/4316a4ce86fdd851f0180ffee87dc336851bf5b6/README.md) |
| MarioKart 64: Recompiled：通过 N64Recomp 静态重编译实现的原生移植 | 已收录 | [来源](https://github.com/sonicdcer/MarioKart64Recomp/blob/3f72d2385cc995fea79e8fca81d886cb2bdce1de/README.md) |
| SpaghettiKart：基于反编译源码的《马力欧卡丁车 64》原生移植 | 已收录 | [来源](https://github.com/HarbourMasters/SpaghettiKart/blob/5073d2e3636cdb2794f4c845ee3bdec5ac4718c4/README.md) |
| SpeedBreaker：对 Xbox 360 版《极品飞车：最高通缉》的静态重编译 | 已收录 | [来源](https://github.com/SpeedBreakerProject/speedbreaker/blob/31849f5f1d275bf21987440cdc27d94071013656/README.md) |
| Skate 3 Recomp：通过 ReXGlue 实现的 Xbox 360 原生重编译 | 已收录 | [来源](https://github.com/mchughalex/skate3recomp/blob/f6e0ae87fdfecbadb5c1e36c55d66a744187a3cd/README.md) |
| DOAXVB Native PC Port：对《Dead or Alive Xtreme Beach Volleyball》的静态重编译 | 已收录 | [来源](https://github.com/NoRain211/doaxvb-re/blob/e282a3fc15c793e621098fc0a5d9e70aa6a6e9c2/README.md) |
| CTR Turbocharged：基于 Crash Team Racing 反编译成果的 PC 移植 | 已收录 | [来源](https://github.com/CameronRedmore/Crash-Team-Racing-Turbocharged/blob/07d0c49f01d62dcb9887b455be27ce65728ee893/README.md) |
| TonyWasAProSkater：派生自一致性反编译的 THPS1 原生移植 | 已收录 | [来源](https://github.com/LANCommander/TonyWasAProSkater/blob/23968e91391ccdeb35f45e1fe987a8a40085aa5f/README.md) |
| SVR2011-Recomp：借助 ReXGlue 重编译 WWE SmackDown vs. Raw 2011 | 已收录 | [来源](https://github.com/shaneomac1337/SVR2011-Recomp/blob/6a12d52d0e32adfca092b6474d584b97d459b148/README.md) |
| 🏁 WWE SmackDown vs. Raw 2011 — KaikoClanworth1/wwe-svr2011-pc | 证据不足 | [来源](https://github.com/HaozheH3/awesome-rea-games/blob/4316a4ce86fdd851f0180ffee87dc336851bf5b6/README.md) |
| The Simpsons Wrestling Recompiled：基于 psxrecomp 的 PlayStation 静态重编译 | 已收录 | [来源](https://github.com/TekRantGaming/simpsons-wrestling-recompiled/blob/1aaee1a999f4dcc60dbf965a9ed9944373528469/README.md) |
| Driver Recompiled：在本地构建游戏的 psxrecomp 安装宿主 | 已收录 | [来源](https://github.com/alexbeavs-ps1-ports/driver-recomp/blob/11e9a4a8c8fcf931e4ef70121d231a5a3cb5c42b/README.md) |
| REDRIVER2：借助 PlayStation 兼容层重建 Driver 2 | 已收录 | [来源](https://github.com/OpenDriver2/REDRIVER2/blob/b2d8857426f815007486def9bd23f9a6007a2c64/README.md) |
| Snowball War：范围明确的 REA 辅助小游戏重建 | 已收录 | [来源](https://github.com/tuunanet/rea-ski-or-die-reconstruction/blob/0eac0671c90e21a16e663da7772b60710101ef7f/README.md) |
| 🏡 Animal Crossing — ACreTeam/forest | 证据不足 | [来源](https://github.com/HaozheH3/awesome-rea-games/blob/4316a4ce86fdd851f0180ffee87dc336851bf5b6/README.md) |
| Animal Crossing：基于 GameCube 反编译成果的原生 PC 移植 | 已收录 | [来源](https://github.com/flyngmt/ACGC-PC-Port/blob/4099d246c927e75b4fd342ca13f4ac4395c55af5/README.md) |
| Animal Crossing：生成一致产物的 GameCube 反编译重建 | 已收录 | [来源](https://github.com/ACreTeam/ac-decomp/blob/09ca8e8b5b24e6ab44047ee980cf0088ad7ecb4c/README.md) |
| Animal Crossing: Wild World：附差分运行检查的韩版 DS 一致性反编译重建 | 已收录 | [来源](https://github.com/banatic/acww-decomp/blob/c7e3256743367fe04ed1a47f9a0f57e2ab57a24f/README.md) |
| The Sims: Bustin' Out：AI 驱动的部分 GBA 一致性反编译重建 | 已收录 | [来源](https://github.com/DaBrown95/tsbodp/blob/0beb04fdc3142a9860059600d1037725f1bc6c77/README.md) |
| OpenRA：重新诠释早期 Westwood 即时战略游戏的引擎重新实现 | 已收录 | [来源](https://github.com/OpenRA/OpenRA/blob/e180e3225f3930272dd451917467631618f8976f/README.md) |
| OpenRCT2：RollerCoaster Tycoon 2 的开源重新实现 | 已收录 | [来源](https://github.com/OpenRCT2/OpenRCT2/blob/53bbc400e28be44d3c2e56fa514d5f65b61a64d4/readme.md) |
| OpenXcom：X-COM: UFO Defense 与 Terror from the Deep 的开源克隆 | 已收录 | [来源](https://github.com/OpenXcom/OpenXcom/blob/4a4bae5fa2e5a09282928e84943fc84b093e34ff/README.md) |
| CorsixTH：Theme Hospital 的开源重新实现 | 已收录 | [来源](https://github.com/CorsixTH/CorsixTH/blob/e5138ed8de906ccbf6692299b4375f9312df147e/README.md) |
| Mario Party 4：美版 GameCube 一致性反编译重建 | 已收录 | [来源](https://github.com/mariopartyrd/marioparty4/blob/5b01c79b4910525e3fc5aa312eddd6d014e7f337/README.md) |
| Snap64 Recomp：Pokémon Snap 的静态重编译移植 | 已收录 | [来源](https://github.com/JackandBeans/Snap64Recomp/blob/cf53b89272b9db19059dd97eed2690ea1dd94844/README.md) |
| 恐龙跑酷：经 REA 检查、由 Codex 重建的速度规则 | 已收录 | [来源](https://github.com/zhxunzh84/rea-dino-reverse-engineering/blob/1fa0ae9faae97d65754f2abf89d3e8326aea9525/README.md) |
| SpaceCadetPinball：将反编译游戏逻辑适配到 SDL2 | 已收录 | [来源](https://github.com/k4zmu2a/SpaceCadetPinball/blob/cb9b7b886244a27773f66b0b19fdc2998392565e/README.md) |
| Touhou 6：重建东方红魔乡 1.02h 版源码 | 已收录 | [来源](https://github.com/GensokyoClub/th06/blob/e840ab447f38579c2ea877e16a5d91a49adf016e/README.md) |
| TH08 Web：基于重建源码的 WebAssembly 移植 | 已收录 | [来源](https://github.com/N0zoM1z0/th08-web/blob/e3485ab9a9af3b5a90ce51841667bbdf5a867e5c/README.md) |
| TH095：东方文花帖 1.02a 的函数级重建 | 已收录 | [来源](https://github.com/N0zoM1z0/th095/blob/6084b36cfa90ac1720f0cba36caec3ee56fc5e1f/README.md) |
| TH04：从源码重建东方幻想乡的四个 PC-98 程序 | 已收录 | [来源](https://github.com/N0zoM1z0/th04/blob/11577b35392c706f3bd39ff1ea932c003e1eaa6b/README.md) |
| DX-Ball：借助 REA 并由 Codex 完成的函数级重建 | 已收录 | [来源](https://github.com/N0zoM1z0/dx-ball/blob/d1251ea4bd000c7204c895c029194cae1d269731/README.md) |
| Pre-CU Star Wars Galaxies: an idea to accelerate emulator reverse engineering with AI | 证据不足 | [来源](https://x.com/i/status/2111615624678088837) |
| Animal Jam / Burrow: an unconfirmed account of Claude-assisted decompilation | 证据不足 | [来源](https://x.com/i/status/2111623879487795255) |
| Kernel anticheat privacy: using REA to investigate machine information sent to a vendor | 证据不足 | [来源](https://x.com/i/status/2111627155449004086) |
| LittleBigPlanet: an AI-decompilation idea for a moddable native PC port | 证据不足 | [来源](https://x.com/i/status/2111639768270594300) |
| REDOC: a claimed on-chain platform for agent reverse engineering and capability reconstruction | 证据不足 | [来源](https://x.com/i/status/2111668130489549026) |
| A 231-function reversing studio: a REA and Opus multi-tool workflow demonstration | 证据不足 | [来源](https://x.com/i/status/2111563711005745602) |
| Codex ad-free app reconstruction: a 20-minute report includes wireless ADB troubleshooting | 证据不足 | [来源](https://x.com/i/status/2111479225890865430) |
| A pro-software licensing algorithm: an unverified report of a REA keygen in hours | 证据不足 | [来源](https://x.com/i/status/2111423397095723483) |
| Show Your Work：对 REA 证据架构的实测剖析 | 已收录 | [来源](https://no-flag.com/2026/10/18/REA-paper/) |
| Game ad behavior: a reported Claude inspection of obfuscated JavaScript | 证据不足 | [来源](https://x.com/i/status/2111582817251738031) |
| LG OLED pause ads: an idea to modify firmware with Codex | 证据不足 | [来源](https://x.com/i/status/2111556091712581745) |
| Dhaedalida: an AI reverse-engineering comparison on a self-made licensing sample | 证据不足 | [来源](https://x.com/i/status/2111560797855916293) |
| FormEasy: an agent-native forms project reportedly based on studying Google Forms | 证据不足 | [来源](https://x.com/i/status/2111562194660016471) |
| Coding harnesses into skills: a plan to study agent orchestration implementations | 证据不足 | [来源](https://x.com/YashasGunderia/status/2111579690532278697) |
| Gemini Web To API: an agent installation test against stand-in services only | 证据不足 | [来源](https://x.com/argusiccom/status/2111585716195004425) |
| DeepSeek V4.1: a reported V8 n-day to Electron IPC investigation | 证据不足 | [来源](https://x.com/i/status/2111587595750637954) |
| An offline Linux reverse-engineering workspace: separating Codex from private files | 证据不足 | [来源](https://x.com/i/status/2111588450969231812) |
| CM 01-02 to FM26: an idea to study football-manager data migration with REA | 证据不足 | [来源](https://x.com/i/status/2111591082119106953) |
| Six-app two-room reconstruction: a report of 299 claims and a negative-control judge rule | 证据不足 | [来源](https://x.com/i/status/2111591362449592514) |
| Windows 加载器：借助 REA 与 Codex 的静态恶意软件分析 | 已收录 | [来源](https://codegeeksai.github.io/en/blog/static-malware-analysis-rea-codex/) |
| T3 Code: an unverified claim of reconstruction and open-source release with 100 Claude agents | 证据不足 | [来源](https://x.com/axmed_bl/status/2111544615669014664) |
| An 1,842-file AI desktop shell: an animated demonstration of local/server boundaries | 证据不足 | [来源](https://x.com/i/status/2111446154713964643) |
| Mario Kart 8 Deluxe: 0xsvsv's Claude/REA PC-port account | 证据不足 | [来源](https://x.com/i/status/2111431983691862272) |
| Kerbal Space Program 2: an AI-decompilation idea for community maintenance | 证据不足 | [来源](https://x.com/i/status/2111434708575805636) |
| Cursor: an account of custom relays and personal Codex/Claude Code quotas | 证据不足 | [来源](https://x.com/FoxSnowing/status/2111465121126207605) |
| Open Scrantic：重建 Johnny Castaway 屏幕保护程序引擎 | 已收录 | [来源](https://github.com/glauberlima/open-scrantic/blob/2db75008931eb744f79d0c3fb12e0d89950466ff/README.md) |
| ScooterLink：重建 Honda RoadSync 车把按键协议 | 已收录 | [来源](https://x.com/i/status/2111470520688665052) |
| Samsung TV: Aswin DG's Claude/REA-skill web-remote account | 证据不足 | [来源](https://x.com/dg_aswin/status/2111471785946562815) |
| REA 工作区模板 | 已收录 | [来源](https://github.com/dobest1024/rea-workspace-template/blob/fc15b9a4ba2a8b40510d19a2dd80209f665711c5/README.md) |
| Hitachi combination oven: a Codex/REA account using an Android app for direct control | 证据不足 | [来源](https://x.com/i/status/2111474749855670664) |
| Frontkick 与 Rikugan：基于 CREBench 的智能体对比 | 已收录 | [来源](https://www.synacktiv.com/en/publications/ufc-666-frontkick-vs-rikugan) |
| Ableton Live 12: an agent reversing attempt running for 96 hours | 证据不足 | [来源](https://x.com/i/status/2111506869395337318) |
| Makara game maker: an idea for scoped analysis of authorized inputs | 证据不足 | [来源](https://x.com/i/status/2111507612646699286) |
| ROM analysis setup: Gemini Argon with REA, Ghidra and libretro | 证据不足 | [来源](https://x.com/i/status/2111507777336098897) |
| EVM contracts: a REA idea for inspecting state-changing entry points | 证据不足 | [来源](https://x.com/i/status/2111507955711459554) |
| Non-open-hardware Xiaozhi box: AI firmware changes for a personal VPS and shared memory | 证据不足 | [来源](https://x.com/i/status/2111511824751599721) |
| Pandemic-relief websites: an idea for AI-assisted investigation of legacy backdoors | 证据不足 | [来源](https://x.com/i/status/2111516584976273866) |
| Forked pi and two Sparks: starting a GLM-5.3-flash/REA trial | 证据不足 | [来源](https://x.com/i/status/2111519607928520794) |
| Mac video downloader: an author-reported rebuild adding transcription | 证据不足 | [来源](https://x.com/i/status/2111520950814453895) |
| Codex/Claude clients: asking whether tokens are hidden in the app package | 证据不足 | [来源](https://x.com/i/status/2111521972849193128) |
| Old game saves in the browser: a REA rules-and-progress migration idea | 证据不足 | [来源](https://x.com/i/status/2111527329331638455) |
| LG TV smoothness: an idea for REA-assisted responsiveness research | 证据不足 | [来源](https://x.com/i/status/2111528528374353931) |
| 《声名狼藉：次子》原生 PC 移植 | 已收录 | [来源](https://github.com/HayatoG/iss_pc/blob/d3995feb0cea1e2edc0c71fab139d1e89f0a7305/README.md) |
| Illustrative legacy/billing demo: 212 files to a spec and twelve Sonnet agents | 证据不足 | [来源](https://x.com/i/status/2111530936441446417) |
| Windows XP/7: an AI compatibility idea instead of rewriting the whole OS | 证据不足 | [来源](https://x.com/i/status/2111546180207317426) |
| Switch Diablo II to Android: an unverified AI-assisted native-port report | 证据不足 | [来源](https://x.com/i/status/2111454921589710905) |

## 部分覆盖与别名

部分或相关目录映射：

- `song:touhou-reconstruction` — REA 发表的文章、其固定版本的证据说明及已合并的 REA PR #1475 覆盖了这份组合报告：TH08、TH095 与 TH04 的里程碑、各自定义下的进度计数，以及 TH08 浮点字面量判定依据的漏洞。完整映射指向该方法案例；TH08 项目条目仍为部分匹配。结果仍为作者报告，未单独审阅 TH095 与 TH04 仓库，也未主张构建或运行复现。
- `song:artcraft-boundary` — ArtCraft 应用页面称每个 Crafting App 都用 Rust 从零编写，并未声称进行了逆向工程；所审阅的四份 README 描述的是依据公开规范与观察到的行为完成的净室实现，不含专有代码。没有一手来源记录对 Adobe 或 Microsoft 软件的反编译或代码恢复，也没有来源确立第三方帖子所称的 REA 使用。PhotoCraft、WordCraft、GridCraft 与 DeckCraft 保留指向各自实现条目的部分映射；页面列出的 FilmCraft、LightCraft、CADCraft 等其他应用另有公开仓库，本次未审阅。保留此线索而不建立完整映射；这并非对这些应用质量的评价。
- `song:unity-valheim` — 两个关联的 REA issue 都是工具缺陷报告，而非重建案例。#1801 报告 rea-agents 6.4.0 受托管解码预算限制，对一个 Unity Assembly-CSharp.dll 和 Valheim 的 assembly_valheim.dll 均未返回任何类型或方法；#1371 报告 CLI 在一个未具名 Unity 游戏程序集上输出 JSON 时崩溃，报告者随后确认 main 分支已修复。两个讨论串均未公开恢复的 Valheim 逻辑、修改、重建产物或对照结果，也未报告对 Valheim 的复测。相关映射指向 REA 托管代码分析指南，该指南说明了这一 64 MiB 预算、以部分覆盖报告的资源限制结果和用 --type 选择已知类型的方法，但未涉及 Unity、Valheim 或该 JSON 崩溃。这不是对 REA 托管代码支持能力的评判。
- `song:large-android-apk` — 关联的 REA issue 是工具缺陷报告，而非重建案例：rea-agents 4.1.0 的 JADX 提供方在一个未具名、133 MB、含 11 个 DEX 文件的生产 APK 上耗尽 Java 堆内存。关闭时的回复说明 main 分支已加入堆内存控制和内存优化，但明确表示未针对该 APK 复测；讨论串也未写明应用名称，没有恢复的功能、重建产物或对照结果。相关映射指向 REA Android 静态分析指南，该指南说明了只用一个 JADX 工作线程且不设默认堆大小、可通过 REA_JADX_HEAP_MIB 或 Java 选项设置堆内存、Evidence 记录观测到的堆上限以及每次操作的限制，但没有针对这种规模 APK 的测试。这不是对 REA 当前 Android 支持能力的评判。
- `song:android-apidemos` — 已合并的 REA PR #738 通过无界面 JADX 新增五项静态 Android 操作：包与清单检查、类搜索、成员及选定方法的 Java／smali 检查，以及静态调用者追踪。PR 报告了一条基于 Appium 公开 ApiDemos 6.0.18 APK 的验证流程，五项 CLI 与 MCP 操作均通过，且未执行该 APK。这验证的是工具集成，而非重建：没有重建或对照 ApiDemos 的任何功能或行为。相关映射指向 REA Android 静态分析指南，其真实验证流程使用同一个以哈希固定的测试样本；该指南记录的是工具检查而非重建，因此不作完整映射。这不质疑所报告的验证结果。
- `song:dlss-amd-compute-report` — 所链接的 DLSSNR-AMD 仓库经固定版本审阅，记录了 DLSS 5 神经渲染网络的 Vulkan 重新实现，权重由使用者自行提取，并与 NVIDIA DLL 的输出对比；该项目已另行收录，此处仅作为相关映射。被回复的帖子串引用的是另一个项目 HelixSR 的发布消息（在 AMD 上运行 DLSS 3.7 网络），因此不能确定该评论指的是 DLSSNR-AMD。DLSSNR-AMD 的文档和 HelixSR 的 README 都未描述 AI 辅助的逆向工程。完整映射需先审阅该帖子串所指项目；AI 主张仍未确立。
- `song:arwing-littleplanet-ai-port-report` — 帖文中的三个链接分别指向 carlosrmz009 的 arwing、arwing2 和 littleplanet 仓库，现各自作为独立案例收录：固定版本 README 记录了以运行覆盖率为种子、可重新汇编为原映像的反汇编，带解释器回退的 C 静态重编译，以及重编译与解释执行的哈希对照。每个映射只覆盖一个项目，因此这份合并报告仍为待定。三个仓库均未将工作归因于 AI、REA 或 Opus 5.5，帖文所称单一提示即完成的说法仍无依据；一致性与运行结果均为项目报告，未经复现。
- `song:virtua-fighter-ai-decompilation` — 帖文中的两个链接指向 celsowm 的两个仓库。固定版本的 vf2-decomp 记录了 Virtua Fighter 2 Version 2.1 的 BSD-3-Clause、非一致性 C17 恢复，只有与参考 i960 执行器一致的路径才被接受；该项目现已收录，但映射仅为部分覆盖。固定版本的 vf3-decomp 是进行中的 Dreamcast 版 Virtua Fighter 3tb C 移植，有代理说明和覆盖率日志，但没有 README 或许可证文件，因此暂不收录，合并报告仍为待定。REA 的使用未确立；结果均为项目报告。
- `song:dragon-ball-budokai-browser` — 所引帖子（@0x0SojalSec，2026-10-14）称 AI 逆向了《Dragon Ball Budokai》，使其能在任意浏览器中以 60 fps 运行，支持手机和联机；帖子附一张图片，并链接一个第三方游玩网站。帖子未指明作者、方法或源码。该网站称其引擎来自某个 Tenkaichi3Decomp 仓库，而已收录的 Tenkaichi3Decomp 的 README（此处固定到具体提交）称该项目从不分发游戏本体，需要玩家自备光盘，并且与浏览器游玩网站无关。本记录不将该网站作为证据引用。保留此线索，仅与已收录的 PC 移植建立相关映射；所报告的浏览器移植并非可审阅的项目。
- `song:rea-640-windows-managed-electron-test` — 一组两条帖子的讨论串报告了在 Windows + Node 24 上实测 npm 版 rea-agents 6.4.0：约 200 个 .NET Framework 程序集在托管解码预算下的表现、一个由 AI 构造的 Electron 风格样例、一个 Trap.dll 副作用检查，以及仅差一个常量的程序集比对。样本、原始命令输出和完整环境均未公开，且帖子评估的是 REA 的静态分析能力，而非重建任何软件。保留此线索而不收录为案例；相关映射指向目录中 REA 托管代码与 JavaScript 工作流文档，这些文档描述了帖子所测试的表示预算、--type 选择及应用图分析。
- `song:pokemon-hgss-multi-agent-decompile-report` — 所引三条帖子中：@autoaiadvantage（2026-10-15）称有人用多个 AI 智能体在一个月内反编译了《宝可梦 心金/魂银》，消耗约 710 亿个 API token，估算费用约 5.6 万美元；所引 @Pirat_Nation 的帖子已被作者删除；@Alex_Vainshtein 回复指出，这项工作建立在 pret 现有的反编译和工具之上。三帖均未点名或链接该项目。分支仓库 ctrl-cheeb-del/pokeheartgold 自称已借助 LLM 智能体完全反编译、两个 ROM 均可逐字节构建，但未报告 token 用量或费用，也没有帖子确认它就是所述工作。保留此线索而不建立整理案例；相关映射只记录回复中提到的 pret 基础工作。
- `song:ringfall-th04-bullet-hell-report` — 帖子（@0xMoryo，2026-10-15）称有人用 REA 的 Ghidra 提供程序分析 1997 年 PC-98 游戏 TH04 的可执行文件，把两条弹幕环公式整理成洁净室笔记，再由 Claude Code 在一次会话中做出浏览器弹幕 Boss 战 RINGFALL；帖子只附视频。帖子说 REA 和“TH04 研究”的链接在回复中，但帖子 API 不提供回复内容；其引用的帖子是一篇 REA 通用教程文章，也未找到 RINGFALL 的源码或构建。保留此线索而不建立整理案例；相关映射指向另行整理的 REA TH04 弹幕环证据，而非 RINGFALL。
- `song:schaller-opticfilm-thinkpad-linux` — 既有扫描仪调查和独立的 ThinkPad IMX471 调校／驱动案例，覆盖此报告中的两个有限范围组成部分。映射仍为部分覆盖：均不确立完整扫描仪／相机行为、全设备兼容性或独立运行复现。
- `song:rea-electron-notes-ipc-answer-key-test` — 两条帖子组成的串文（@ofmyslippers，2026-10-15）报告用一个带已知答案的小型笔记应用对 REA 的 Electron 静态分析测试三次：IPC 通道、处理器配对和 preload API 成员均为 4/4，且正确地未发现发送方检查，每次 2.5–3 秒，2.3 KB 源码生成 1.0 MB JSON。测试应用、答案和输出均未公开（串文只链接 REA 仓库），这项工作是在评估 REA，而非重建软件。保留此线索而不建立整理案例；相关映射指向 REA 的 JavaScript 指南，其自带的 Notes Electron 示例只有一个 IPC 通道，因此并非所测应用。
- `song:rea-game-function-matcher-audit-report` — 帖子（@xmyttle，2026-10-16）转述了 REA 的计算器演示，以及 REA 博客文章《Does reverse engineering need a bigger model?》（N0zoM1z0，2026-10-13）：多个 GPT-6 系列模型接力完成《东方》系列中难以匹配的函数，另有一次审计发现部分已被接受的函数常量有误，例如原程序加 32.0f 的地方重建源码写成了 1.0f。该文固定版本的证据说明和 TH08 提交 a393f400 记录了这次浮点字面量审计，文章也说明对奖励学习的风险只是推断，并非实际观察到的利用。目录已通过《东方》重建方法一文覆盖该审计，因此此处为部分映射；关于模型接力的这篇文章本身尚未收录，此线索保持待处理。
- `song:rea-reconstruction-companion` — 固定版本仓库确立了具名的 Companion：一个采用 MIT 的 Agent Skill，与 REA 配合把证据整理成限定范围的需求、设计、分阶段实现与验证，并提供由安装程序管理、可选写入 REA 技能的路由段落，以及已接触源码的评估套件。完整映射以社区 REA 集成覆盖该技能；原有的部分映射覆盖另立条目的 Pocket Tasks 重建示例。示例与检查结果仍是维护者报告的教学材料，未确立模型试验、独立评估或运行复现。
- `song:valdiorn-audio-effects-firmware-report` — valdiorn 在 Hacker News 的评论（2026-10-15，经 @RealYDT 转述）称，借助 Opus 5.5 在模拟器中运行三家竞争对手的效果器固件，再转换成独立 C++ 库并比较结果，另外还处理了 Lexicon 224 与 Ursa Major 产品。评论没有公开代码、模拟器、库、比较数据或产品版本，也未指明所说的 Lexicon 仓库。公开的 reflecticon-224 模拟项目作者在回复中猜测被找到的就是该项目；该项目另立条目并以相关映射关联，并不视为本报告的成果。保留此线索并标为证据不足；所报告的反编译与比较均未确立。
- `yibie:all-games-are-open-source-now` — 作者的 X 长文（@rehan_shei，2026-10-04）是一篇探讨 AI 反编译与模组对游戏产业影响的随笔。文中称让 Opus 5.5 运行一夜后得到了一个可运行的逆向版 Terraria，作者又在其中加入了武器和怪物；文章还罗列了他人报告的模组与反编译案例，并称作者已把 Claude 在此过程中积累的经验开源为 universal-modder。Terraria 重建本身没有公开产物；相关映射指向文章提及、另行收录的 Universal Modder 工具包。保留此线索而不建立完整映射；该文属于评论，其中的数字与第三方案例未在此核实。
- `yibie:how-are-y-all-using-ai-to-make-recompilations` — 该来源是一场讨论：r/recomps 上 2026-10-05 的提问，询问大家如何用 AI 制作重编译移植、是否有教程。回复多为一般性建议和观点，例如订阅方案的选择、让智能体参照现有重编译工具工作以及维护重编译引擎，但都没有代码、结果或对照；其中一条回复指向 freefrank/LostOdysseyRecomp 的文档，该项目已作为独立案例收录，此处仅记为相关匹配。保留此线索，不为其单独建立重建映射。
- `yibie:finding-jingle-town-debugging-an-n64-game-without-symbols` — 这篇注明日期的文章记录了在 Snowboard Kids 2 反编译中用 GDB 与 Ares 手动检验一个运行时假设的流程，包括所用工具、步骤、观察到的三个值及作者说明的局限。完整映射将这篇调试记录作为学习资源收录；其研究的反编译项目另有案例条目，此处以相关映射链接。文中观察未经重做，文章也未声称使用 AI 或 REA。
- `hao-games:row-001` — 固定版本的 README、Makefile、素材提取脚本、Jenkinsfile 和构建 wiki 记录了基于 Super Mario 64 反编译源码的增强版原生移植：素材从原 ROM 提取，输出比较处于关闭状态。完整映射覆盖此移植；相关映射记录其源自另行收录的 n64decomp 重建项目，并不表示一致性结果。所链帖子仅指向一个反编译游戏综合存档，未作为证据使用。
- `hao-games:row-003` — 固定版本的 README、构建指南、CMake 文件、子模块、工作流和许可证记录了一个基于 libultraship 的原生移植：它转换使用者自备的美版或日版 ROM，不主张生成一致的输出。完整映射覆盖此移植。与 n64decomp 的相关映射依据共同的源码结构和抽查的两个文件，因为 README 没有指明上游项目。
- `hao-games:row-004` — 固定版本的 README、wiki 与构建文件表明，这是面向 Super Mario 64 PC 移植的在线多人与 Lua 模组项目，延续 sm64ex-coop，后者又是 sm64ex 的分支。源码会校验使用者自备的美版 ROM，PC 构建强制采用非一致性代码。项目没有记录自身的重建工作：没有反编译过程说明、对照或一致性证据。相关映射仅记录它源自另行收录的反编译重建项目，并非对多人项目本身的评价。
- `hao-games:row-020` — 固定版本的 README、构建规则、校验文件和 CI 配置支持这份美版 N64《姆吉拉的假面》反编译报告。完整映射只覆盖此仓库，不涵盖帖子所链接的存档；相关映射记录 Zelda 64: Recompiled 注明借用其头文件和函数，但它是独立的静态重编译。进行中状态、原 ROM 依赖、许可证缺失和项目报告的一致性均明确保留。
- `hao-games:row-025` — 在此前有限的 README 核查基础上，固定版本的构建文件、反编译配置、启动源码和 CI 工作流支持将 Metaforce 记为现已基于 PrimeDecomp 重写、读取使用者所选光盘镜像运行的引擎重实现。完整映射仅覆盖此仓库，与合集中的 MetroidPrimePort 项目分开。暂不提供构建、没有对应当前版本的发布、原生目标为非一致构建，以及 MIT／CC0 许可范围未划分等限制均明确保留。相关映射记录此次重写以另行收录的 PrimeDecomp 反编译为基础，并不表示 Metaforce 本身达成一致性构建。
- `hao-games:row-026` — 固定版本的 README、NOTICE、许可证、原生移植指南、Linux CI 工作流和 v0.29.0 发布，支持这一由 PrimeDecomp 反编译编译而成、借助 AI 辅助完成的《密特罗德 Prime》原生移植。完整映射仅覆盖此仓库，与合集中的 Metaforce 项目分开。受支持的光盘版本、仅覆盖非游戏代码的 MIT 授权范围以及作者报告的冒烟测试均明确保留；所链接帖子未作为证据核查。相关映射记录该移植源自另行收录的 PrimeDecomp 反编译，并不表示移植版本身达成一致性构建。
- `hao-games:row-090` — 固定版本的 README、构建指南、重编译配置、子模块列表、CI 工作流、项目历史与 GPLv3 许可，支持该具名的 Star Fox 64 N64Recomp 静态重编译。完整映射覆盖此移植，不涵盖独立的 sf64 反编译、Starship 移植或经独立测试的游戏行为。仅接受美版 1.1 ROM、CI 使用私有输入及补丁借用反编译头文件均明确保留。相关映射记录该移植从另行收录的 sf64 反编译中取用头文件和部分函数，并不表示移植版本身达成一致性构建。
- `hao-games:row-091` — 固定版本的 README、构建指南、CMake 源码配置、素材提取配置、CI 工作流和 CC0 许可，连同姊妹项目中的历史说明，支持该基于反编译、运行在 libultraship 上的 Star Fox 64 PC 移植。完整映射覆盖此移植，不涵盖 sf64 反编译、姊妹静态重编译项目或经独立测试的游戏行为。使用者自备美版 ROM 及项目报告的行为均明确保留。相关映射记录该移植编译的是另行收录的 sf64 反编译的 C 代码，并不表示移植版本身达成一致性构建。
- `hao-games:row-130` — 固定版本的 README、逆向报告、测试说明、游戏文件及第三方声明，记录了作者使用 REA MCP 检查开源 T-Rex Runner 页面，并由 Codex 重建其速度规则。完整映射覆盖此仓库范围有限的加速规则案例，不代表玩法等价；REA 另行发布的恐龙教学案例仅作为相关条目关联。作者报告的测试与手动检查未经重跑。
- `hao-games:row-134` — 固定版本的 README、网页移植与架构文档、构建、来源检查和部署脚本、许可证及 v0.1.0 发布，支持此仓库作为基于 TH08 重建源码的独立 WebAssembly 移植。完整映射覆盖该浏览器移植及作者自行完成的检查，不涵盖二进制一致性、硬件性能或独立复现的游戏过程；已收录的 TH08 重建仍作为相关条目关联。本地零售数据要求与浏览器限制均明确保留。
- `hao-games:row-135` — 固定版本的 README、自动生成的进度、判定依据与运行问题说明、工具锁定文件、初始化脚本、CI 及许可证，支持该 TH095 1.02a 重建报告。完整映射覆盖此仓库的函数级重建及可游玩的 Windows i386 构建，不涵盖整个可执行文件一致性、计划中的移植或独立复现的游戏过程；REA 的东方重建方法文章作为相关条目关联。原可执行文件要求和项目报告的数字均明确保留。
- `hao-games:row-136` — 固定版本的 README、自动生成的进度、DOS 构建、工具链、判定依据、运行与参考说明、CI 及许可证，支持该 TH04 重建报告。完整映射覆盖此仓库的四程序 DOS 重建及作者报告的差分回放，不涵盖字节一致性、完整流程、原生 x64 分支或独立复现。REA 的单函数展示仍为部分匹配，其东方重建文章为相关条目。
- `hao-games:row-137` — 固定版本的 README、REA 实例说明、匹配、构建与进度说明、目标与工具锁定文件、一项差分测试、CI 及许可证，支持该 DX-Ball 重建报告及作者记录的 REA 与 Codex 使用。完整映射覆盖这一进行中的函数级重建，不代表字节一致、已完成的可游玩 VC4 构建或独立复现；REA 的单函数声像展示仍为部分匹配。原版压缩包要求及其未经核实的下载来源均明确保留。
- `song:synacktiv-frontkick-rikugan-crebench` — Synacktiv 的文章记录了一次注明日期的对比：在 CREBench 的两个任务上比较 Binary Ninja 智能体 Frontkick 与 Rikugan，给出实验设置和逐次运行结果表，作者也指出差距主要源于提示词差异而非智能体设计。完整映射将其作为学习资源收录，相关映射指向其所用的 CREBench 论文。Frontkick 没有公开发布，运行记录未公开，本次也未重新运行。

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
