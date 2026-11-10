# Case collection coverage

[简体中文](case-coverage.zh-CN.md) · [Machine-readable ledger](../data/case-coverage.json)

Reviewed 2026-10-20 (UTC). **451 collection occurrences** become **449 inventory units** after 2 documented duplicate merges. These are reports, tools, papers, discussions and ideas.

The unique-project count is `null` until project identities are resolved. English/Chinese copies of one upstream entry are counted once. Separate reports about one project remain separate units unless an explicit alias decision joins them.

## Frozen sources

| Collection snapshot | Occurrences | Linked GitHub repositories | Catalog record |
| --- | ---: | ---: | --- |
| [songshikang0111/awesome-REA-cases · 3a1c5cdfaa3f](https://github.com/songshikang0111/awesome-REA-cases/tree/3a1c5cdfaa3f2db0dd4f587208f8870eb633de23) | 423 | 50 | [awesome-rea-cases](https://awesomerea.org/resources/awesome-rea-cases/) |
| [yibie/awesome-rea · 6df1bc922ac6](https://github.com/yibie/awesome-rea/tree/6df1bc922ac6b92dcd1b2f905c94d8cc4f3b5a3e) | 28 | 11 | [yibie-awesome-rea](https://awesomerea.org/resources/yibie-awesome-rea/) |

The ledger retains pinned file URLs, Git blob IDs, SHA-256 digests and byte counts for these enumerated snapshots.

Repository counts use normalized GitHub repository, tree and file links within each collection. In a game-organized table, each project row is an occurrence.

## Counts and states

| State | Occurrences | Inventory units | Meaning |
| --- | ---: | ---: | --- |
| Already curated (`already-curated`) | 97 | 95 | Full-scope identity mapping to a catalog resource or paper. |
| Pending (`pending`) | 21 | 21 | Primary review or complete catalog coverage remains pending; partial matches stay here. |
| Insufficient evidence (`insufficient-evidence`) | 333 | 333 | An idea, request or unsupported reconstruction claim is retained as a lead. |

115 occurrences have catalog links. They reference 118 distinct resource IDs and 2 paper ID. Match scope is recorded separately.

This ledger records a new primary-source review for 378 inventory units. Other catalog-linked entries inherit the catalog’s source-review record.

## Primary-reviewed cases

| Case | State | Primary evidence |
| --- | --- | --- |
| Universal Modder | Already curated | [Source](https://github.com/rehan-remade/universal-modder/blob/6a8865ae171b406f50892c7f46fc5f45655269eb/README.md) |
| Firefighter: a decompiled DOS game ported to Rust | Already curated | [Source](https://gitlab.com/esr/firefighter/-/blob/84861db110928202571af2042cb9762720dc2c3e/history.adoc) |
| PlxNative: reconstructing a native webOS media-client interface | Already curated | [Source](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| Agent decompilation: a byte-matching retrospective | Already curated | [Source](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote: Siri Remote protocol reconstruction | Already curated | [Source](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| Tuya RGB lights from a Mac | Insufficient evidence | [Source](https://x.com/luchoalfonso_/status/2108200739495362718) |
| BaoCut Slides: adapting an interactive web editor | Already curated | [Source](https://github.com/JimLiu/baocut/blob/b8585e0c8d7a82bdee9f0ed019cf6edb075e41c1/docs/design/slides/slides-design.md) |
| Claude Code: inspecting a compressed codebase | Insufficient evidence | [Source](https://x.com/servasyy_ai/status/2108846931183378537) |
| Urban Terror in the browser | Insufficient evidence | [Source](https://x.com/levelsio/status/2106150888289009666) |
| Binary-library rewrite | Insufficient evidence | [Source](https://x.com/leeoxiang/status/2109159806183538768) |
| Flutter build identification | Already curated | [Source](https://github.com/morluto/rea/pull/1582) |
| MIPS ELF analysis through Ghidra | Already curated | [Source](https://github.com/morluto/rea/issues/1620) |
| PSP static ELF analysis through Ghidra | Already curated | [Source](https://github.com/morluto/rea/issues/1330) |
| Touhou reconstructions: an agent-driven method across three games | Already curated | [Source](https://github.com/morluto/rea/blob/c12d9eda87aa5a022ee7e18ea96d8d03bfd12e96/website/evidence/touhou-reconstruction-method.md) |
| Dinosaur runner: recovering one acceleration rule | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Smart toilet from the desktop | Insufficient evidence | [Source](https://x.com/thinkszyg/status/2109309251533570509) |
| flipper-telink: replacement firmware for Tuya Zigbee remotes | Already curated | [Source](https://github.com/ngxson/flipper-telink/blob/d58aef2e65b30f33f560474ce460127c6f18ca30/custom_fw/ss6400zb/README.md) |
| Website rebuild: delivery report | Insufficient evidence | [Source](https://x.com/goan999999/status/2109080288823562734) |
| TradingView: reconstruction workflow claim | Insufficient evidence | [Source](https://x.com/RohOnChain/status/2109347169316839434) |
| WHOOP Android app investigation | Insufficient evidence | [Source](https://x.com/uwwgo/status/2109217632758976755) |
| ArtCraft: not proven Adobe or Office reverse engineering | Insufficient evidence | [Source](https://getartcraft.com/apps) |
| Obsidian ASAR: large-package analysis | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/746) |
| Unity/Valheim assemblies | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/1801) |
| Large multidex Android APK | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/893) |
| NativeAOT metadata recovery with Ghidra | Already curated | [Source](https://github.com/morluto/rea/issues/744) |
| Windows Calculator: reconstructing percentage rules | Already curated | [Source](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Android ApiDemos: tracing Java methods from an APK | Insufficient evidence | [Source](https://github.com/morluto/rea/pull/738) |
| Static HarmonyOS package inventory | Already curated | [Source](https://github.com/morluto/rea/pull/1447) |
| Firmware analysis | Already curated | [Source](https://github.com/morluto/rea/pull/741) |
| macOS Preview: rebuilds with and without REA and the limits of self-tests | Insufficient evidence | [Source](https://x.com/maheshboda006/status/2109154423712977359) |
| Codex browser annotations: finding the interaction bridge | Insufficient evidence | [Source](https://x.com/dotey/status/2109417222724600172) |
| BaoCut Design: porting reconstructed canvas and design-system editors | Already curated | [Source](https://github.com/JimLiu/baocut/blob/7aa049e82e1367da013b7aba80f0b79033fa04ad/packages/design-runtime/README.md) |
| Bluetooth gamepad on Windows | Insufficient evidence | [Source](https://x.com/fexisnpc/status/2103865671608307838) |
| Browserbase plugin: re-hosting Claude in Chrome’s browser bridge | Already curated | [Source](https://github.com/browserbase/claude-code-plugin/blob/b399af34a1b1cc365d1e1c0089823c4fa5e10ea5/forwarding-server.js) |
| pi-computer-use: desktop interaction for other models | Insufficient evidence | [Source](https://github.com/injaneity/pi-computer-use/blob/67e9e2f77643f84605b738a3198048a88e92190e/README.md) |
| Background Computer Use in Swift | Insufficient evidence | [Source](https://github.com/actuallyepic/background-computer-use/blob/52116acfe0f2f57174f5e0166881abe944cb6eeb/README.md) |
| GarageBand format for automated composition | Insufficient evidence | [Source](https://x.com/anshuc/status/2106131543752122774) |
| Boba Fett in Red Dead Redemption 2 | Insufficient evidence | [Source](https://x.com/ChrisGPT/status/2106925689190354989) |
| Apple Notes migration to Grape | Insufficient evidence | [Source](https://x.com/ozgrozer/status/2035124755854979272) |
| GameCube/Wii PowerPC support request | Insufficient evidence | [Source](https://github.com/morluto/rea/issues/1741) |
| Gamepad settings after Bluetooth analysis | Insufficient evidence | [Source](https://x.com/corndogjpn2/status/2109289076243525916) |
| ASUS ACPI and Linux GPU support | Insufficient evidence | [Source](https://x.com/200Tabs1Brain/status/2108983700776186112) |
| Poker table organizer | Insufficient evidence | [Source](https://x.com/lipinhobeats/status/2109435654962655526) |
| Aerobiz 2: REA and Kimi decompilation | Insufficient evidence | [Source](https://x.com/TSFisher24nrex/status/2109452544913326086) |
| Codex computer-use interoperability research | Insufficient evidence | [Source](https://x.com/thisishars/status/2109461719789735948) |
| Pump.fun reconstruction report | Insufficient evidence | [Source](https://x.com/0rdlibrary/status/2109464346103263523) |
| Super Mario Sunshine: a native PC port from an AI-assisted decompilation | Already curated | [Source](https://github.com/chasem-dev/sms-pc-port/blob/a2ff4eef099b22b2af487d1b5e3ac09ffe667d31/README.md) |
| Gaoding-inspired cover workbench | Insufficient evidence | [Source](https://x.com/Astronaut_1216/status/2109487167726903560) |
| Gaming mouse settings on macOS | Insufficient evidence | [Source](https://x.com/MovingCharts11/status/2109491501013377526) |
| Hermes Agent: Hark-assisted harness reconstruction | Insufficient evidence | [Source](https://x.com/pablothethinker/status/2109509759044854087) |
| Apple Preview: adding AI directly to a compiled app | Insufficient evidence | [Source](https://github.com/Pasta-Lab/edit-my-app/blob/7f469c1f179e2552cd3c5b46ab29b21aeadc838f/README.md) |
| PS5 security: reported AI-assisted investigation | Insufficient evidence | [Source](https://x.com/0x0SojalSec/status/2109517461921902780) |
| Air-conditioner protocol for AR gesture control | Insufficient evidence | [Source](https://x.com/justhalfbit/status/2109524402765488499) |
| wine-uwp: running packaged Windows Store apps on a patched Wine | Already curated | [Source](https://github.com/designgears/wine-uwp/blob/1cf79d025e0c18167de803820345a1c5f82fd17d/README.md) |
| Redmi TV: browser inspection for a dashboard | Insufficient evidence | [Source](https://x.com/zxlie_fehelper/status/2109533072370917846) |
| CleanMyMac: reported native-app prototype | Insufficient evidence | [Source](https://x.com/xiaoshan0413/status/2109540598633877515) |
| Nexalytics: testing REA on the author's own app | Insufficient evidence | [Source](https://x.com/wikwanat/status/2109542201927647588) |
| MetaTrader: a reported signal-analysis use case | Insufficient evidence | [Source](https://x.com/TheKing_Rapture/status/2109547879199056181) |
| Red Alert 2: an engine rewrite for reinforcement learning | Insufficient evidence | [Source](https://x.com/Chen1090874226/status/2109548112281055674) |
| Business software: an ongoing agent-assisted rebuild | Insufficient evidence | [Source](https://x.com/iamsupersocks/status/2109553690595979371) |
| CapCut transitions: a module-reconstruction lead | Insufficient evidence | [Source](https://x.com/fireandstart/status/2109554617004466397) |
| CF632BLE: a local client from scale-protocol research | Already curated | [Source](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| Android app: inspecting root checks and certificate pinning | Insufficient evidence | [Source](https://x.com/IanJKerins/status/2109559519584088093) |
| Kindle: Android firmware for WeRead | Insufficient evidence | [Source](https://x.com/hbyxabc/status/2109583911483519202) |
| Proxy client: restoring a Clash subscription bridge | Insufficient evidence | [Source](https://x.com/web3_fising/status/2109601382273880327) |
| Controlled JS/.NET samples: Codex with and without REA | Insufficient evidence | [Source](https://x.com/0xlangeai/status/2109603485914206498) |
| The Incredible Machine: a Claude-assisted browser rebuild | Insufficient evidence | [Source](https://x.com/staskulesh/status/2109605915175596275) |
| DLSS on AMD: reported AI-assisted compute-shader reconstruction | Pending | [Source](https://github.com/mochizuki0323/DLSSNR-AMD/blob/ab00d2b23584de0f42ac91eca4d7d2d2fad11465/README.md) |
| Netflix/Prime: a reported unified streaming interface | Insufficient evidence | [Source](https://x.com/HigbeyMyrta/status/2109596534350524664) |
| fowlbrowser: an existing-session browser bridge for agents | Insufficient evidence | [Source](https://github.com/argofowl/FowlBrowser/blob/18f7519fa27289885c95b67eff714401ffff51f0/README.md) |
| OpenSetter: rebuilding comment-to-DM flows with an AI setter | Insufficient evidence | [Source](https://github.com/xbirimensah/opensetter/blob/40dc5ae2fde0b3930e6b59132eaf061edb0da0a8/README.md) |
| Street Fighter III: AI refactoring of decompiled C | Insufficient evidence | [Source](https://x.com/renmu2017/status/2109581250424123651) |
| zee-rp: reconstructing supported Axure RP 11 document operations | Already curated | [Source](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| CapCut: a REA/Claude video-editor rebuild | Insufficient evidence | [Source](https://x.com/Mehal_Kay/status/2109665456735076494) |
| ClearSpace: a CleanMyMac-inspired native cleanup app | Insufficient evidence | [Source](https://x.com/iceman_shen/status/2109665812017746132) |
| Home devices: a reported desktop controller | Insufficient evidence | [Source](https://x.com/Jumpan1111/status/2109664718499762606) |
| Discontinued accounting app: blocked by encryption | Insufficient evidence | [Source](https://x.com/liguozzz/status/2109671680977367085) |
| REA analysis: a binary prompt-injection test idea | Insufficient evidence | [Source](https://x.com/riyoway/status/2109670989319868863) |
| Classic shooters: reported AI-assisted browser ports | Insufficient evidence | [Source](https://x.com/i/status/2109639780577190171) |
| Obsidian: a GPT-selected reconstruction attempt | Insufficient evidence | [Source](https://x.com/tokyo10086/status/2109676911500951649) |
| Web Flow: a REA-assisted REST specification report | Insufficient evidence | [Source](https://x.com/GeekCatX/status/2109689282336346575) |
| Nanolathe: a documented Total Annihilation engine reimplementation | Already curated | [Source](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| Android priv-app: GPT-assisted permission inspection | Insufficient evidence | [Source](https://x.com/sisiisthinking/status/2109711257779765741) |
| cooler-lcd: a Thermalright display protocol implementation | Already curated | [Source](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Camera firmware: a Codex-driven VM boot investigation | Insufficient evidence | [Source](https://x.com/elliehuxtable/status/2109715839117316150) |
| Helm Chart API v2: an AI-assisted specification draft | Pending | [Source](https://github.com/mattfarina/specs/blob/7d0395726d712e654a9aaf167603e82007811517/charts/v2.md) |
| Mobile game interactions: Codex and REA evidence mapping | Insufficient evidence | [Source](https://x.com/Steven_Soto/status/2109721540245782843) |
| Homatics ATV14: a reported Dolby Vision firmware fix | Insufficient evidence | [Source](https://x.com/qwerty__cs/status/2109722857207115879) |
| Personal website: a REA-assisted design reconstruction | Insufficient evidence | [Source](https://x.com/khaled_cli/status/2109733299115475393) |
| SaaS feature subsets: Codex observation and Replit rebuilding | Insufficient evidence | [Source](https://x.com/Andrew_Blumson/status/2109733493202981247) |
| Star Fox and Sonic CD: reported AI-assisted native ports | Pending | [Source](https://github.com/carlosrmz009/arwing/blob/d8fe7aaf67e0f4ba77c9814852d2ffaccd7d63c7/README.md) |
| AYN Odin 2 Portal: Codex-assisted native Omarchy bring-up | Insufficient evidence | [Source](https://github.com/TechLuddite/omarchy-mobile-odin2/blob/00d11efc018971f6bab711e7952ff184cad333c2/README.md) |
| Virtual Desktop Streamer: rehosting the platform layer on Linux | Already curated | [Source](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| LG TV: a reported native Claude Code terminal | Insufficient evidence | [Source](https://x.com/ceoico/status/2109774258738176000) |
| WeChat local chats: a reported Codex-assisted decryption task | Insufficient evidence | [Source](https://x.com/trendtranslate1/status/2109779123778490858) |
| Sixteen note files: a reported REA/no-REA decoder comparison | Insufficient evidence | [Source](https://x.com/operatranscend/status/2109783203892597103) |
| Android touchscreen photo frame: Codex-assisted device research | Insufficient evidence | [Source](https://x.com/LeonardVolner/status/2109785163475591510) |
| LightBurn: a reported personal laser-control rebuild | Insufficient evidence | [Source](https://x.com/LIQUID8RPF/status/2109789864891940904) |
| Echo Show 5 Gen 2: a reported Hermes intercom and camera system | Insufficient evidence | [Source](https://x.com/Kurcide/status/2109791974014496983) |
| Elgato HDR: a userspace capture path for the Elgato 4K X’s 10-bit mode | Already curated | [Source](https://x.com/talkaboutdesign/status/2109795113807630735) |
| Gardena mower: reported Codex motor control and firmware work | Insufficient evidence | [Source](https://x.com/BderKhan/status/2109840164004737341) |
| MarkText: a REA-assisted HTML export rebuild | Insufficient evidence | [Source](https://x.com/KKetemepi/status/2109839329933824026) |
| LGwebOS-menubar: a native macOS remote for LG webOS TVs | Already curated | [Source](https://x.com/greco_dev/status/2109842197654692349) |
| Screen Studio: an author-reported REA study of auto-zoom rules | Already curated | [Source](https://x.com/HanZhang415188/status/2109843188341207283) |
| Armed and Dangerous: exploring remastering approaches with Ghidra and AI | Insufficient evidence | [Source](https://x.com/NikhilVerma/status/2109911827203358998) |
| Open Claude UI: REA-informed interface reference components | Already curated | [Source](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| Fort Apocalypse: a reported Codex/Ghidra Android port | Insufficient evidence | [Source](https://x.com/JesperAdolf/status/2109865837477716324) |
| Minecraft × Plants vs. Zombies: a reported playable REA-assisted mashup | Insufficient evidence | [Source](https://x.com/Relph35432/status/2109912103813599539) |
| Three Kingdoms XIV: a reported trainer-to-MCP project | Insufficient evidence | [Source](https://x.com/0xMcDonald/status/2109913567428592046) |
| Virtua Fighter 2.1 / 3 TB: AI-assisted decompilation in progress | Pending | [Source](https://github.com/celsowm/vf2-decomp/blob/9a9f7270f090cfa0f38b0ec6a22c3e53dae4bd18/README.md) |
| Typeless: a reported local voice-input alternative built with REA | Insufficient evidence | [Source](https://x.com/TuyetloanP81840/status/2109971905336037671) |
| Supermodel: initial Real3D Pro-1000 image-generator emulation | Already curated | [Source](https://x.com/BartronPolygon/status/2110028302215999825) |
| Eleven | Already curated | [Source](https://github.com/Zfinix/eleven/blob/94760718dfd741ba93fcc9b591eb39a96c034103/README.md) |
| 48-million-row database: a second-hand REA query-optimization report | Insufficient evidence | [Source](https://x.com/mika_systems/status/2110037357164441796) |
| GTM tool: a reported REA-assisted lead and email workflow | Insufficient evidence | [Source](https://github.com/tashfeenahmed/kinetic/blob/6ccbff87d190aea8e11be993e25783f099b55a93/README.md) |
| TCLimate: reconstructing selected TCL Home cloud controls | Already curated | [Source](https://github.com/umarz317/TCLimate/blob/2a33c2013dbf3f297238131ca9eb6e287b2beb67/Docs/Investigation.md) |
| Tea-export website: reported REA-assisted rebuild | Insufficient evidence | [Source](https://x.com/i/status/2110010062597230838) |
| iTerm: Arabic text rendering informed by REA | Insufficient evidence | [Source](https://x.com/khaled_cli/status/2110091122517410164) |
| Bloomberg-style research terminal: a reported REA/Claude build | Insufficient evidence | [Source](https://x.com/ludoonchart/status/2110082824371908790) |
| Projector IR remote: inferring and testing a missing focus command | Insufficient evidence | [Source](https://x.com/notyroon/status/2110090047579926826) |
| Closed-source coding agent: reverse-engineered collaboration logic and a pi plugin | Insufficient evidence | [Source](https://x.com/aloosekite/status/2110151664846139425) |
| Smart pen: Codex-assisted decompilation and integration | Insufficient evidence | [Source](https://x.com/xhfloz/status/2110108201043775589) |
| ChatGPT app: a reported REA-assisted gradient-background modification | Insufficient evidence | [Source](https://x.com/LinearUncle/status/2110207568090198474) |
| Dragon Ball Budokai: an unverified AI-assisted browser-port report | Insufficient evidence | [Source](https://x.com/0x0SojalSec/status/2110230860717060262) |
| Ledger Reborn: an independent accounting app informed by QuickBooks study | Already curated | [Source](https://github.com/lxistired/ledger-reborn/blob/d7f6b8a1f4ad6c4ae8b10100d1c93cf15940c21d/docs/CASE_STUDY.md) |
| Visor: an independent Ray-Ban Meta glasses client | Already curated | [Source](https://github.com/macedonga/visor/blob/8caaa12df919c014c249efb71fdfa32b263f6c3e/README.md) |
| Hongguo Short Drama: REA-assisted reverse engineering to remove ads and overlays | Insufficient evidence | [Source](https://x.com/web3_goto/status/2110320554049941661) |
| Profound: a reported REA-assisted SaaS reconstruction | Insufficient evidence | [Source](https://github.com/yaojingang/profound-clone/blob/93e87c901b9c51f444b243110dd643e066aa6e22/README.md) |
| Codex Desktop: author reports trying REA to study its differences from CLI | Insufficient evidence | [Source](https://x.com/ZhenHan261538/status/2110377021402661320) |
| Mac desktop app: REA-assisted analysis and reference materials | Insufficient evidence | [Source](https://x.com/fantexi997/status/2110382256829386935) |
| Apple Weather: reported REA-assisted rebuild | Insufficient evidence | [Source](https://x.com/jasonjias/status/2110459951365980334) |
| Friday Night Funkin’: a Claude-assisted gameplay variant | Insufficient evidence | [Source](https://x.com/i/status/2110407024731439392) |
| Linux cal: tracing the 1752 calendar switch | Insufficient evidence | [Source](https://x.com/fahdmirza/status/2110453427209916612) |
| TicTacToe-AI: a bounded REA-fork reconstruction of one game method | Already curated | [Source](https://github.com/heaven-hm/re-agent/blob/a84c61e8baa65d445485722420a57ff4132b90d3/benchmarks/native-windows-ports/reports/targets/tictactoe.md) |
| Home-device protocols connected to a local LLM | Insufficient evidence | [Source](https://x.com/bitfish/status/2110539823572463953) |
| GAMEKB-K17: reconstructing a macropad configuration protocol | Already curated | [Source](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| Kirby: a reported REA investigation in progress | Insufficient evidence | [Source](https://x.com/oh_Roach/status/2110553648787013950) |
| REA in Claude Code: an isolated static-analysis A/B trial | Already curated | [Source](https://zenn.dev/keigoly/articles/8738d8d241b5a1) |
| REA 6.4.0: Windows .NET and Electron sample tests | Insufficient evidence | [Source](https://x.com/i/status/2110563764886266167) |
| CPU kernels: Claude Code orchestrates Astra with REA | Insufficient evidence | [Source](https://x.com/nkeilar/status/2110566660113625486) |
| A saved website investigated with WorkBuddy International | Insufficient evidence | [Source](https://x.com/Muma102kMichael/status/2110593537872175256) |
| apk-reverse: an Android analysis skill for coding agents | Insufficient evidence | [Source](https://github.com/zzusec/apk-reverse/blob/1b94651b1e3c4479336406b8b5c06d4c1fd7082e/README.md) |
| Hailo: a planned agent-assisted reverse-engineering run | Insufficient evidence | [Source](https://x.com/TheCogArchitect/status/2110600631144919232) |
| Wyze scale: weight data in a custom iOS app | Insufficient evidence | [Source](https://x.com/Boards86/status/2110604057287217339) |
| A license-compliance comparison during reverse engineering | Insufficient evidence | [Source](https://x.com/i/status/2110614074941927618) |
| Codex: a personal library following REA research | Insufficient evidence | [Source](https://x.com/LinearUncle/status/2110616441611542781) |
| Richman 4: REA research to a Flutter iPhone rebuild | Insufficient evidence | [Source](https://x.com/iam678/status/2110618564608880843) |
| Tuya AC: local Mac controls exposed to Claude over MCP | Insufficient evidence | [Source](https://x.com/sarequl_basar/status/2110620776915411243) |
| A HyperOS monitor: exploring exposed control services | Insufficient evidence | [Source](https://x.com/binaryify/status/2110622119419838752) |
| Notes example: tracing a CSV export button | Insufficient evidence | [Source](https://x.com/0xCortexq/status/2110623921611432090) |
| IsaacRecomp: translating Flash game bytecode to native C++ | Already curated | [Source](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| A legacy binary: an agent invents nonexistent APIs | Insufficient evidence | [Source](https://x.com/harden_369741/status/2110630792049115198) |
| Codex next-input prediction recreated for Pi | Insufficient evidence | [Source](https://x.com/a1chzt/status/2110631522403512760) |
| DOOM and Terraria: reported no-source mod experiments | Insufficient evidence | [Source](https://x.com/i/status/2110641024389271883) |
| Feishu: an author-reported isolated second app instance | Already curated | [Source](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Roko Input: Apple on-device dictation after Typeless research | Insufficient evidence | [Source](https://github.com/bassnova42/rokoinput/blob/3cd2da84ae83905b961a2de9f06bdf6bac888294/README.en.md) |
| Mi Health: timestamp repair and a cloud-data exporter | Insufficient evidence | [Source](https://github.com/LilZeeCN/mi-health-exporter/blob/1dc9274a90ccc83f02cbb3706aae2a4d55c8e90a/README.md) |
| REA and archify: interactive architecture diagrams | Insufficient evidence | [Source](https://x.com/i/status/2110570919169286424) |
| A colony-simulation engine: a decompilation research plan | Insufficient evidence | [Source](https://x.com/Promptmethus/status/2110642225361371219) |
| iX500 Scan: a macOS client for the reverse-engineered ScanSnap Wi-Fi protocol | Already curated | [Source](https://x.com/jonaswagnr/status/2110647905027604700) |
| Sonic physics in Elden Ring: an unverified REA mod report | Insufficient evidence | [Source](https://x.com/Capslock404/status/2110648710606557644) |
| iriver E30: personalizing an unsupported player's main screen | Insufficient evidence | [Source](https://x.com/MikeS190477/status/2110651009181851731) |
| A radiator-control app bridged to Home Assistant with AI | Insufficient evidence | [Source](https://x.com/Madsoulswe/status/2110651982323310818) |
| D2R Mobile: rehosting Diablo II: Resurrected’s Switch program on Apple devices | Already curated | [Source](https://x.com/OLD9Gaming/status/2110658894360097141) |
| WHOOP and Zhoop: an iPhone data path for a health agent | Insufficient evidence | [Source](https://x.com/0xLogicrw/status/2110659108076769728) |
| macOS Notes: a reported REA-assisted SwiftUI rebuild | Insufficient evidence | [Source](https://x.com/xiyue0803/status/2110670751087137197) |
| reverse-skill: investigation workflows for coding agents | Pending | [Source](https://x.com/i/status/2110680583634366777) |
| A thermofluid equation solver: ongoing REA/Opus work | Insufficient evidence | [Source](https://x.com/iamsupersocks/status/2110684985900355622) |
| A booking funnel investigated and rebuilt as a personal calendar | Insufficient evidence | [Source](https://x.com/JulianGoldieSEO/status/2110686215846699236) |
| Watch5 Pro: a reported Claude/REA health-sensor app | Insufficient evidence | [Source](https://x.com/Sp00kyD00kyXRS/status/2110693137773392155) |
| REA with local Qwen and pi: multi-target commercial-software tests | Insufficient evidence | [Source](https://x.com/deluxebear/status/2110696564335214807) |
| QUICKSURFACE AI: announced scan-to-parametric-CAD automation | Insufficient evidence | [Source](https://x.com/ManMetrologyLTD/status/2110699093333000322) |
| Spider-Man swinging in GTA V: an internally inconsistent REA claim | Insufficient evidence | [Source](https://x.com/vmrmax/status/2110699414792642732) |
| Humidity readings through an agent-built Bluetooth app | Insufficient evidence | [Source](https://x.com/real_kai42/status/2110700189912912155) |
| Grok Bot: a worker-network reverse-engineering idea not pursued | Insufficient evidence | [Source](https://x.com/leaf_sanren/status/2110702662270460232) |
| From a Little Prince game to Dragon Ball-themed HTML 3D | Insufficient evidence | [Source](https://x.com/i/status/2110713533193453572) |
| SentinelOne and Daybreak: a reported malware-analysis time reduction | Insufficient evidence | [Source](https://x.com/i/status/2110726263392387158) |
| A construction firm's SaaS workflows, observed and rebuilt | Insufficient evidence | [Source](https://x.com/andywalters/status/2110726879665660172) |
| Reversed with AI | Already curated | [Source](https://reversedwithai.com/about) |
| Mario Odyssey on macOS: a secondary Claude-assisted report | Insufficient evidence | [Source](https://x.com/swordBluesy/status/2110735780842999962) |
| REA plugin for Hermes Agent | Already curated | [Source](https://github.com/NousResearch/hermes-official-plugins/blob/6dacaaddbfd8e98dfc524096c44f712f743246b8/rea/README.md) |
| Mario's jump in Halo: an unverified six-parameter REA claim | Insufficient evidence | [Source](https://x.com/Capslock404/status/2110741739732435179) |
| Roborock Local Server: a self-hosted stand-in for Roborock’s vacuum cloud | Already curated | [Source](https://x.com/whyamas/status/2110741945874350429) |
| Arkham: a Grok Bot/REA research-workbench rebuild | Insufficient evidence | [Source](https://x.com/monokern/status/2110743454959509801) |
| A plate reader's filter-wheel fault: a Claude-assisted repair report | Insufficient evidence | [Source](https://x.com/r_gross_/status/2110745676875227179) |
| Grok Build: exploratory code study with REA and Claude Code | Insufficient evidence | [Source](https://x.com/omerfrkdemiral/status/2110749141710028914) |
| Codex CLI: inspecting model-identity prompts and routing fields | Insufficient evidence | [Source](https://x.com/jiangkoumo_/status/2110751118343164066) |
| Rust Duty: reconstructing gameplay from video, not decompilation | Insufficient evidence | [Source](https://x.com/reidhslaughter/status/2110752844328419587) |
| 2010 Rust Rewrite Mashup: Skate 3 in MW2 maps | Pending | [Source](https://x.com/thenuntheia/status/2110757135009112576) |
| A wireless CarPlay adapter: a reported REA/Grok firmware change | Insufficient evidence | [Source](https://x.com/omercoskun_tech/status/2110759012266332509) |
| A daily voice-input app: quick client inspection, hours of rebuilding | Insufficient evidence | [Source](https://x.com/pirrer/status/2110759506003304641) |
| Linux EAC: an AI devirtualization claim via IDA Assist MCP | Insufficient evidence | [Source](https://x.com/i/status/2110759663822352852) |
| Browser Counter-Strike: a colleague's AI-build claim | Insufficient evidence | [Source](https://x.com/FuSheng_0306/status/2110760621113548854) |
| REA JavaScript demo: a stale-price check at 400 ms | Insufficient evidence | [Source](https://x.com/0xAlhimik/status/2110761684411572247) |
| Galaxy-Android: a reported AI-assisted native Super Mario Galaxy port | Pending | [Source](https://x.com/ToniCipriani007/status/2110763621768716353) |
| An old phone: an author reports running OEM firmware in Wasm with Claude | Insufficient evidence | [Source](https://x.com/ShishirTandale/status/2110765881768747173) |
| BINNY | Already curated | [Source](https://github.com/openbin-ai/binny/blob/000b6aca8c9d266b38252470102ac16c98575cd8/README.md) |
| An illustrative game.exe demo: two rooms and three reconstruction oracles | Insufficient evidence | [Source](https://x.com/i/status/2110783611800522897) |
| H1Z1: research followed by an MMO built with Opus, Astra and Tripo | Insufficient evidence | [Source](https://x.com/i/status/2110784230687125852) |
| Uncharted: The Nathan Drake Collection native Windows port | Already curated | [Source](https://github.com/bc160201983/Uncharted-The-Nathan-Drake-Collection-PC-port/blob/dfc9fb6e70794bc81ae62836e3e5fb993ff50b3e/README.md) |
| Slipstream 5000: an author reports a two-day Codex decompilation | Insufficient evidence | [Source](https://x.com/i/status/2110786958649684035) |
| A Chrome dark-mode extension: REA research for improvements | Insufficient evidence | [Source](https://x.com/i/status/2110797282308153562) |
| A construction-bid decryptor: reported Claude Code research into a password error | Insufficient evidence | [Source](https://x.com/i/status/2110802464786264210) |
| Pokémon HeartGold/SoulSilver: a secondhand multi-agent decompilation and cost report | Insufficient evidence | [Source](https://x.com/i/status/2110816115718824296) |
| A Resend alternative: reported email APIs and inboxes for agents | Insufficient evidence | [Source](https://x.com/i/status/2110817677778489400) |
| Two games' RNG: a Codex/ILSpy prediction-tracking report | Insufficient evidence | [Source](https://x.com/i/status/2110817897706582486) |
| Destiny 2 build 86657: Sunrise/Dawn reconstruction research report | Already curated | [Source](https://github.com/isinternets/d2-research/blob/9a5b58f1f8408ed48b01705e0138ee25050669f2/README.md) |
| Self-owned Android/Windows 95 apps: an Opus reverse-engineering test without REA | Insufficient evidence | [Source](https://x.com/i/status/2110820518983000118) |
| RINGFALL: a reported browser boss fight built from TH04 bullet-ring notes | Insufficient evidence | [Source](https://x.com/i/status/2110844188178952423) |
| Apple Watch Ultra 2: an unverified AI-reverse-engineering report of Android connectivity | Insufficient evidence | [Source](https://x.com/i/status/2110844478239945061) |
| Plustek 8200i / ThinkPad MIPI: improve Linux drivers using Windows reference behavior | Pending | [Source](https://github.com/cschalle/hw-harness/blob/093afc5c576c200f29b771d01624a327d0ff1806/examples/plustek-film-scanner/README.md) |
| Open-BFME: a report of AI-assisted Battle for Middle Earth decompilation and byte matching | Insufficient evidence | [Source](https://x.com/i/status/2110857508470604174) |
| Greenlight video API: query fields with AI, then probe actual validation with invalid values | Insufficient evidence | [Source](https://x.com/i/status/2110868326528303367) |
| Electron Notes sample: an REA static IPC test with an answer key | Insufficient evidence | [Source](https://x.com/i/status/2110869440762196138) |
| A character on a video homepage: a report of Fu Sheng's REA mashup demonstration | Insufficient evidence | [Source](https://x.com/i/status/2110873715810660594) |
| A personal YouTube version: an REA-assisted niche-video and AI-topic dashboard report | Insufficient evidence | [Source](https://x.com/i/status/2110878456611319835) |
| decomp.wtf | Already curated | [Source](https://github.com/i12bp8/decomp.wtf/blob/575b4a30ed481ff5497dfb9ce4f599368a95a04a/README.md) |
| A local REA workbench: combine investigation and personal office workflows | Insufficient evidence | [Source](https://x.com/i/status/2110904597900673267) |
| Ledger Opus: an unverified finance-agent promotion referencing Claude for Finance | Insufficient evidence | [Source](https://x.com/i/status/2110916629244641548) |
| Immersive Portals: an AI-assisted Minecraft JE 26.2 compatibility report | Insufficient evidence | [Source](https://x.com/i/status/2110918344886927696) |
| TV firmware: an AI ad-removal idea and two implementation accounts | Insufficient evidence | [Source](https://x.com/i/status/2110919403961192504) |
| Excel reconciliation workbooks: infer a procedure from an accepted artifact for agents | Insufficient evidence | [Source](https://x.com/i/status/2110919658748719318) |
| OpenCodex / Antigravity: REA investigation of missing multi-turn tool-call signatures | Insufficient evidence | [Source](https://x.com/i/status/2110921946418602001) |
| Minesweeper and Bilibili: a secondary roundup of REA demonstration titles | Insufficient evidence | [Source](https://x.com/i/status/2110936629221450214) |
| MoonBit: Claude investigates name mangling to improve VSCode debugging | Insufficient evidence | [Source](https://x.com/i/status/2110938121080631767) |
| Obfuscated old games: a report of Claude guessing structure sizes incorrectly | Insufficient evidence | [Source](https://x.com/i/status/2110942707074183405) |
| Saturn Sonic 3D Blast: byte-matching decompilation and a native PC port | Insufficient evidence | [Source](https://x.com/i/status/2110939629516186067) |
| UU Remote on Linux: an unofficial protocol implementation | Already curated | [Source](https://github.com/VallierDev/uu-remote-linux/blob/696cf10e334b2e7fe1afcb698b354c09ee328447/README.en.md) |
| Notes CSV export: an author-reported REA check of reconstruction oracles | Already curated | [Source](https://x.com/i/status/2110963427791487391) |
| Obfuscated JavaScript request signatures: an author reports restoring data retrieval with REA | Insufficient evidence | [Source](https://x.com/i/status/2110968095850561701) |
| Immersive-translation-style extensions: investigating a bring-your-own-token alternative with Codex | Insufficient evidence | [Source](https://x.com/i/status/2110976193671709123) |
| ChatGPT Intelligent UI: asking Codex to investigate the implementation | Insufficient evidence | [Source](https://x.com/i/status/2110983483271286909) |
| Claude Code background lab: an REA-informed reimplementation of a desktop animation | Already curated | [Source](https://github.com/Henry-fan88/claude-code-background/blob/3dbd1065835508be6027137927deeddb8c30fe55/README.md) |
| ChatGPT Work Cloud: probing a cloud agent's tools through introspection | Insufficient evidence | [Source](https://x.com/i/status/2111009945865097386) |
| Indian Kanoon: a reported Claude Code legal-search integration | Insufficient evidence | [Source](https://x.com/i/status/2111027056234627119) |
| Amap anti-bot controls: a secondhand Tencent sandbox-agent incident report | Insufficient evidence | [Source](https://x.com/i/status/2111034426066956783) |
| JPCERT/CC: APK analysis and API probing on attack servers | Already curated | [Source](https://blogs.jpcert.or.jp/ja/2026/10/web_api_attacks.html) |
| Polymarket Up/Down bot: a promotional REA strategy-analysis and replay report | Insufficient evidence | [Source](https://x.com/i/status/2111049696630194596) |
| crashlens | Already curated | [Source](https://github.com/mingleiw/crashlens/blob/7188611a506e058a8f4937acf3dfd3035545f2d1/README.md) |
| Halo 3 Reforged: a reader's AI-decompilation and 128-player claim | Insufficient evidence | [Source](https://x.com/i/status/2111052865410375683) |
| Samsung AC: local-network control with reported partial Claude assistance | Insufficient evidence | [Source](https://x.com/i/status/2111055239378018407) |
| A 2000 stress.exe: a reported Opus/REA revival for Mac and the web | Insufficient evidence | [Source](https://x.com/i/status/2111061027211395485) |
| RKD Telemetry Extractor: decoding Race-Keeper track-day recordings | Already curated | [Source](https://github.com/sam-dumont/rkd-telemetry-extractor/blob/8db9f373e1a7162d3f2efa297986bdfa86d9400f/RESEARCH_NOTES.md) |
| QQPet: a cross-platform pet rebuilt from Arctic Penguin T800 | Insufficient evidence | [Source](https://x.com/aigeeknews/status/2111095142790857087) |
| Website to Next.js: a reported Claude Code template with parallel DOM-based rebuilding | Insufficient evidence | [Source](https://x.com/0xPascual/status/2111096590387601489) |
| Black Bot / Blacksidian: reported REA rebuilds with AI-provider choice | Insufficient evidence | [Source](https://x.com/i/status/2111100877083947405) |
| iOS on Android hardware: a porting idea and unverified HACKIOS/Redmi claims | Insufficient evidence | [Source](https://x.com/i/status/2111100973238329497) |
| VMP-protected sample: a reported failed DeepSeek challenge | Insufficient evidence | [Source](https://x.com/i/status/2111101746001113381) |
| Mega Man Battle Network: a secondhand AI decompilation and modding lead | Insufficient evidence | [Source](https://x.com/i/status/2111103450448572730) |
| A twelve-year-old Kindle: reported Claude safety refusal during a jailbreak attempt | Insufficient evidence | [Source](https://x.com/i/status/2111106257431961740) |
| 1997 audio software: investigating Windows 11 compatibility to continue old work | Insufficient evidence | [Source](https://x.com/i/status/2111115615628824723) |
| OpenRiseOfNations: a native macOS engine reimplementation | Already curated | [Source](https://github.com/ben-wright-1/OpenRiseOfNations/blob/2a0dfde8acdb7185c6087b10ef89b4f66731e5a0/README.md) |
| Computer integrates REA: five app-feature rebuilding demos including Figma | Insufficient evidence | [Source](https://x.com/AskPerplexity/status/2111120664543596957) |
| Claude Intercept | Already curated | [Source](https://github.com/whaesemeyer/claude-intercept/blob/c2b7d01911e11e063533dbd61a22b404b503b48d/README.md) |
| Claude client: inspecting environment telemetry with REA | Insufficient evidence | [Source](https://x.com/i/status/2111134289970765964) |
| Codex cursor: recovering drawing geometry for a Windows pointer | Insufficient evidence | [Source](https://x.com/i/status/2111142820207837308) |
| Gears of War 3: AI-assisted static recompilation and graphics work | Insufficient evidence | [Source](https://x.com/i/status/2111146922522402943) |
| WristBeam: reconstructing Garmin’s watch protocol for a Mac companion | Already curated | [Source](https://x.com/i/status/2111155441077977138) |
| Three open tools to personal apps: an REA recording, markup and dictation report | Insufficient evidence | [Source](https://x.com/i/status/2111156533002227870) |
| LmDrum firmware: Claude reportedly stops after decompilation progress | Insufficient evidence | [Source](https://x.com/i/status/2111169026160480290) |
| 1977 DES test vectors: Claude reportedly traces their random-generation environment | Insufficient evidence | [Source](https://x.com/i/status/2111170587792208361) |
| jq and Fossify Calculator: REA function identification and early inspection | Insufficient evidence | [Source](https://x.com/i/status/2111171612149985567) |
| Notion app.asar: a Claude read-only file and domain-string inspection | Insufficient evidence | [Source](https://x.com/0xKurogamii/status/2111182893313613877) |
| Grok Bot + REA: a reported software-investigation chat template | Insufficient evidence | [Source](https://x.com/ChaiWithAi/status/2111184500093026340) |
| Owned hardware for voice agents: an REA attempt inspired by earbuds and a smart ring | Insufficient evidence | [Source](https://x.com/i/status/2111158379896877249) |
| Patrick's AI reverse-engineered games directory: an ongoing resource project | Pending | [Source](https://x.com/i/status/2111185397782880475) |
| Doom: a claimed clean-room reimplementation with 19 Claude agents | Insufficient evidence | [Source](https://x.com/i/status/2111187899479658673) |
| NIST ECDSA curves: Claude traces the generation of public parameters | Pending | [Source](https://www.anthropic.com/research/ecdsa-curve-origins) |
| Niuniu AI / MT5: an REA rebuild report after a reseller relationship ended | Insufficient evidence | [Source](https://x.com/sera00111/status/2111206851606159655) |
| Mac video export: studying DaVinci and CapCut to improve a personal editor | Insufficient evidence | [Source](https://x.com/i/status/2111214346428686478) |
| Wiki Lab: a claimed REA-based Wikipedia for agents | Insufficient evidence | [Source](https://x.com/BrianDevoor/status/2111215569047314589) |
| Set-top-box APK: a short WorkBuddy extraction and analysis report | Insufficient evidence | [Source](https://x.com/i/status/2111216713245364424) |
| Base arbitrage contract: an unverified REA/Opus bytecode report | Insufficient evidence | [Source](https://x.com/i/status/2111220274226217276) |
| System UI from video: Claude measures frames and infers animation parameters | Insufficient evidence | [Source](https://x.com/i/status/2111222217849946308) |
| Linux mouse driver: reverse engineering among a week's AI projects | Insufficient evidence | [Source](https://x.com/i/status/2111224894297870413) |
| Roadster video: a Claude-assisted three.js visual teardown experiment | Insufficient evidence | [Source](https://x.com/i/status/2111225325531074716) |
| ENS v2 phishing email: a Claude-assisted investigation of dangerous agent repositories | Insufficient evidence | [Source](https://x.com/i/status/2111234225022067029) |
| Does reverse engineering need a bigger model? General and specialist models in Touhou reconstruction | Already curated | [Source](https://x.com/i/status/2111241506006700380) |
| Google Home: a blocked attempt to revive an old speaker without replacing hardware | Insufficient evidence | [Source](https://x.com/i/status/2111215951857246251) |
| A 3D home model: a reported REA-assisted Mac menu-bar controller | Insufficient evidence | [Source](https://x.com/0xProbabillity/status/2109978137794883621) |
| AMABOO Frameo: Claude Code adapts an existing Home HQ frame setup | Insufficient evidence | [Source](https://x.com/InvestingVault/status/2111250941886226471) |
| Grok Bot real-time features: a Hermes investigation with audio unresolved | Insufficient evidence | [Source](https://x.com/i/status/2111251559275487538) |
| Jiuchuan Xiaozhi AI speaker: give Muse stock firmware and hardware specifications | Insufficient evidence | [Source](https://x.com/i/status/2111251131665940519) |
| Fallout 4: a brief claim of fixes after Claude reverse engineering | Insufficient evidence | [Source](https://x.com/i/status/2111262935293038623) |
| A Windows keyboard utility: Claude builds a Linux version and checks it with a camera | Insufficient evidence | [Source](https://x.com/i/status/2111269740249489643) |
| REA Reconstruction Companion | Already curated | [Source](https://x.com/xiyue0803/status/2111273763799191896) |
| Claude Desktop app.asar: Opus reportedly opens the package during feature research | Insufficient evidence | [Source](https://x.com/i/status/2111275332989059193) |
| CLO3D DLLs: an idea to rebuild a garment-design tool with Claude/Codex | Insufficient evidence | [Source](https://x.com/i/status/2111281354910704058) |
| NJFE: a Soulear camera protocol bridge for desktop inspection | Already curated | [Source](https://github.com/WildweaselMS/NJFE/blob/992866c6609f8c813f459ff79840cf04d5883f8e/README.md) |
| LeanREA | Already curated | [Source](https://github.com/aicodeking/leanrea/blob/09ba4aa0217f82cd880f855a60b877f59f39b22b/README.md) |
| MISE.exe: Claude proposes Ghidra-derived rules instead of screenshot guesses | Insufficient evidence | [Source](https://x.com/i/status/2111312368840126836) |
| Guitar effects: emulate the original firmware, then compare a standalone C++ library | Insufficient evidence | [Source](https://news.ycombinator.com/item?id=50104955) |
| RetroScope: a local-LLM assistant for ROM instruction references | Insufficient evidence | [Source](https://x.com/i/status/2111332462811087061) |
| China Mobile app: AI investigates number-selection pages and protocols for local filtering | Insufficient evidence | [Source](https://x.com/i/status/2111337934406484446) |
| Roku TV: a firmware-modification inquiry blocked by Claude's bootloader assessment | Insufficient evidence | [Source](https://x.com/i/status/2111349282745757858) |
| Serein's nine-bot workflow: pass REA behavior specifications to an isolated builder | Insufficient evidence | [Source](https://x.com/i/status/2111365135143219711) |
| Chrome LINE: AI reads JavaScript to build a TUI and messaging API | Insufficient evidence | [Source](https://x.com/i/status/2111366415639064608) |
| Reverse Engineering Assistant: a framework advertised for offline file-analysis reports | Pending | [Source](https://x.com/i/status/2111230457568227404) |
| 731 functions: an REA reconstruction account using specification isolation and four negative controls | Insufficient evidence | [Source](https://x.com/i/status/2111165651599663599) |
| Zenith collaborative editing: a reader asks about investigating it with REA | Insufficient evidence | [Source](https://x.com/i/status/2111358914520600998) |
| Hue screen-synced lighting: Claude investigates a macOS Bluetooth mode | Insufficient evidence | [Source](https://x.com/i/status/2111385823270625370) |
| JavaScript divergence: formatting switches the game, an AI reversing-decoy idea | Insufficient evidence | [Source](https://x.com/i/status/2111386823763411016) |
| Three-model binary research: function maps, competing hypotheses and an original-binary oracle | Insufficient evidence | [Source](https://x.com/i/status/2111389348339827041) |
| re2ds: a native Nintendo DS engine for Resident Evil 2 | Already curated | [Source](https://www.reddit.com/r/ReverseEngineering/comments/1x85dp5/a_port_of_resident_evil_2_for_the_nintendo_ds/) |
| Starshield signals: a reader's idea to investigate frequencies with REA | Insufficient evidence | [Source](https://x.com/i/status/2111395824991097074) |
| Windows kernel: an REA collaboration idea for a free operating system | Insufficient evidence | [Source](https://x.com/i/status/2111405429486211272) |
| Amazon Prime tvOS: investigating IPA Universal Links to open shows from a personal app | Insufficient evidence | [Source](https://x.com/i/status/2111424789827228006) |
| Claude and Codex limits: an REA-assisted top-bar display report | Insufficient evidence | [Source](https://x.com/i/status/2111426952162947310) |
| LLVM ABI: gingerBill's account of using LLMs to investigate undocumented internals | Insufficient evidence | [Source](https://x.com/i/status/2111396413066363009) |
| Super Mario 64 DS: matching decompilation with relocation checks | Already curated | [Source](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Define correctness as PASS/FAIL, then let agents iterate | Insufficient evidence | [Source](https://x.com/arpit_bhayani/status/2109505311904309621) |
| Where "software is solved" is overstated | Insufficient evidence | [Source](https://x.com/wangdou/status/2109404200513708307) |
| Reverse Engineer Anything, tried on a live game | Insufficient evidence | [Source](https://x.com/AIWarper/status/2109060856466264566) |
| Snowboard Kids: an agent-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/decompiling-a-nintendo-64-game-in-84-days/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| All games are open source now | Insufficient evidence | [Source](https://x.com/rehan_shei/status/2106548006350942533) |
| Sonic Advance 3: an AI-assisted match of one enemy module | Already curated | [Source](https://gambiconf.substack.com/p/development-journey-on-game-decompilation) |
| Claims that genAI speeds up PC ports of classic games are either "false" or missing the point | Insufficient evidence | [Source](https://www.reddit.com/r/SBCGaming/comments/1wyhd5s/claims_that_genai_speeds_up_pc_ports_of_classic/) |
| AI-generated decompilations are garbage | Insufficient evidence | [Source](https://www.reddit.com/r/decomps/comments/1v6b9gw/aigenerated_decompilations_are_garbage/) |
| Why isn't decompilation a solved problem in the AI era? | Insufficient evidence | [Source](https://news.ycombinator.com/item?id=49646640) |
| How are y'all using ai to make recompilations? | Insufficient evidence | [Source](https://www.reddit.com/r/recomps/comments/1wyle7y/how_are_yall_using_ai_to_make_recompilations/) |
| Zelda and Banjo Recompiled dev slams the slew of poor-quality "slopcomps" | Insufficient evidence | [Source](https://www.reddit.com/r/technology/comments/1ww1twg/) |
| Snowboard Kids 2: an LLM-assisted N64 matching decompilation | Already curated | [Source](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| Finding Jingle Town: Debugging an N64 Game without Symbols | Already curated | [Source](https://blog.chrislewis.au/finding-jingle-town-debugging-an-n64-game-without-symbols/) |
| Awesome Decomp Games | Already curated | [Source](https://github.com/SubmitGame/awesome-decomp-games/blob/02727e90fe10c7b55fad3fdd4bd671c55e1fe587/README.md) |
| GoldenEye 007: an agent-assisted native port from a decompilation | Already curated | [Source](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip: an AI-assisted Super Smash Bros. native port | Already curated | [Source](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp: static recompilation with explicit mode limits | Already curated | [Source](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| Vandal Hearts: native PC port built on matching decompilations | Already curated | [Source](https://github.com/HalmyLyseas/VandalHearts-decomp-SLPM-86007/blob/75017596cc439a7141e405943afdb469b717787c/README.md) |
| KartPad: platform integration for a Mario Kart Wii recompilation | Already curated | [Source](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |
| Xenosaga I Decomp Compatibility Kit | Already curated | [Source](https://github.com/LinuxJessi/decomp-compat-kit/blob/d9bb53dac364ecfaff4f8b00ea44baec60a27abf/README.md) |
| Pre-CU Star Wars Galaxies: an idea to accelerate emulator reverse engineering with AI | Insufficient evidence | [Source](https://x.com/i/status/2111615624678088837) |
| Animal Jam / Burrow: an unconfirmed account of Claude-assisted decompilation | Insufficient evidence | [Source](https://x.com/i/status/2111623879487795255) |
| Kernel anticheat privacy: using REA to investigate machine information sent to a vendor | Insufficient evidence | [Source](https://x.com/i/status/2111627155449004086) |
| LittleBigPlanet: an AI-decompilation idea for a moddable native PC port | Insufficient evidence | [Source](https://x.com/i/status/2111639768270594300) |
| REDOC: a claimed on-chain platform for agent reverse engineering and capability reconstruction | Insufficient evidence | [Source](https://x.com/i/status/2111668130489549026) |
| A 231-function reversing studio: a REA and Opus multi-tool workflow demonstration | Insufficient evidence | [Source](https://x.com/i/status/2111563711005745602) |
| Codex ad-free app reconstruction: a 20-minute report includes wireless ADB troubleshooting | Insufficient evidence | [Source](https://x.com/i/status/2111479225890865430) |
| A pro-software licensing algorithm: an unverified report of a REA keygen in hours | Insufficient evidence | [Source](https://x.com/i/status/2111423397095723483) |
| Show Your Work: a measured dissection of REA's evidence architecture | Already curated | [Source](https://no-flag.com/2026/10/18/REA-paper/) |
| Game ad behavior: a reported Claude inspection of obfuscated JavaScript | Insufficient evidence | [Source](https://x.com/i/status/2111582817251738031) |
| LG OLED pause ads: an idea to modify firmware with Codex | Insufficient evidence | [Source](https://x.com/i/status/2111556091712581745) |
| Dhaedalida: an AI reverse-engineering comparison on a self-made licensing sample | Insufficient evidence | [Source](https://x.com/i/status/2111560797855916293) |
| FormEasy: an agent-native forms project reportedly based on studying Google Forms | Insufficient evidence | [Source](https://x.com/i/status/2111562194660016471) |
| Coding harnesses into skills: a plan to study agent orchestration implementations | Insufficient evidence | [Source](https://x.com/YashasGunderia/status/2111579690532278697) |
| Gemini Web To API: an agent installation test against stand-in services only | Insufficient evidence | [Source](https://x.com/argusiccom/status/2111585716195004425) |
| DeepSeek V4.1: a reported V8 n-day to Electron IPC investigation | Insufficient evidence | [Source](https://x.com/i/status/2111587595750637954) |
| An offline Linux reverse-engineering workspace: separating Codex from private files | Insufficient evidence | [Source](https://x.com/i/status/2111588450969231812) |
| CM 01-02 to FM26: an idea to study football-manager data migration with REA | Insufficient evidence | [Source](https://x.com/i/status/2111591082119106953) |
| Six-app two-room reconstruction: a report of 299 claims and a negative-control judge rule | Insufficient evidence | [Source](https://x.com/i/status/2111591362449592514) |
| Windows loader: static malware analysis with REA and Codex | Already curated | [Source](https://codegeeksai.github.io/en/blog/static-malware-analysis-rea-codex/) |
| T3 Code: an unverified claim of reconstruction and open-source release with 100 Claude agents | Insufficient evidence | [Source](https://x.com/axmed_bl/status/2111544615669014664) |
| An 1,842-file AI desktop shell: an animated demonstration of local/server boundaries | Insufficient evidence | [Source](https://x.com/i/status/2111446154713964643) |
| Mario Kart 8 Deluxe: 0xsvsv's Claude/REA PC-port account | Insufficient evidence | [Source](https://x.com/i/status/2111431983691862272) |
| Kerbal Space Program 2: an AI-decompilation idea for community maintenance | Insufficient evidence | [Source](https://x.com/i/status/2111434708575805636) |
| Cursor: an account of custom relays and personal Codex/Claude Code quotas | Insufficient evidence | [Source](https://x.com/FoxSnowing/status/2111465121126207605) |
| Open Scrantic: reconstructing the Johnny Castaway screensaver engine | Already curated | [Source](https://github.com/glauberlima/open-scrantic/blob/2db75008931eb744f79d0c3fb12e0d89950466ff/README.md) |
| ScooterLink: reconstructing Honda RoadSync’s handlebar-button protocol | Already curated | [Source](https://x.com/i/status/2111470520688665052) |
| Samsung TV: Aswin DG's Claude/REA-skill web-remote account | Insufficient evidence | [Source](https://x.com/dg_aswin/status/2111471785946562815) |
| REA Workspace Template | Already curated | [Source](https://github.com/dobest1024/rea-workspace-template/blob/fc15b9a4ba2a8b40510d19a2dd80209f665711c5/README.md) |
| Hitachi combination oven: a Codex/REA account using an Android app for direct control | Insufficient evidence | [Source](https://x.com/i/status/2111474749855670664) |
| Frontkick vs Rikugan: a CREBench agent comparison | Already curated | [Source](https://www.synacktiv.com/en/publications/ufc-666-frontkick-vs-rikugan) |
| Ableton Live 12: an agent reversing attempt running for 96 hours | Insufficient evidence | [Source](https://x.com/i/status/2111506869395337318) |
| Makara game maker: an idea for scoped analysis of authorized inputs | Insufficient evidence | [Source](https://x.com/i/status/2111507612646699286) |
| ROM analysis setup: Gemini Argon with REA, Ghidra and libretro | Insufficient evidence | [Source](https://x.com/i/status/2111507777336098897) |
| EVM contracts: a REA idea for inspecting state-changing entry points | Insufficient evidence | [Source](https://x.com/i/status/2111507955711459554) |
| Non-open-hardware Xiaozhi box: AI firmware changes for a personal VPS and shared memory | Insufficient evidence | [Source](https://x.com/i/status/2111511824751599721) |
| Pandemic-relief websites: an idea for AI-assisted investigation of legacy backdoors | Insufficient evidence | [Source](https://x.com/i/status/2111516584976273866) |
| Forked pi and two Sparks: starting a GLM-5.3-flash/REA trial | Insufficient evidence | [Source](https://x.com/i/status/2111519607928520794) |
| Mac video downloader: an author-reported rebuild adding transcription | Insufficient evidence | [Source](https://x.com/i/status/2111520950814453895) |
| Codex/Claude clients: asking whether tokens are hidden in the app package | Insufficient evidence | [Source](https://x.com/i/status/2111521972849193128) |
| Old game saves in the browser: a REA rules-and-progress migration idea | Insufficient evidence | [Source](https://x.com/i/status/2111527329331638455) |
| LG TV smoothness: an idea for REA-assisted responsiveness research | Insufficient evidence | [Source](https://x.com/i/status/2111528528374353931) |
| inFAMOUS Second Son native PC port | Already curated | [Source](https://github.com/HayatoG/iss_pc/blob/d3995feb0cea1e2edc0c71fab139d1e89f0a7305/README.md) |
| Illustrative legacy/billing demo: 212 files to a spec and twelve Sonnet agents | Insufficient evidence | [Source](https://x.com/i/status/2111530936441446417) |
| Windows XP/7: an AI compatibility idea instead of rewriting the whole OS | Insufficient evidence | [Source](https://x.com/i/status/2111546180207317426) |
| Switch Diablo II to Android: an unverified AI-assisted native-port report | Insufficient evidence | [Source](https://x.com/i/status/2111454921589710905) |

## Partial coverage and aliases

Partial or related catalog mappings:

- `song:touhou-reconstruction` — The REA-published essay, its pinned evidence notes and merged REA PR #1475 cover this combined report: TH08, TH095 and TH04 milestones, ledger counts under separate definitions, and the TH08 floating-literal oracle gap. The full mapping is to that method case; the TH08 project record remains a partial match. Results are author-reported. The TH095 and TH04 repositories are covered through the essay only and were not separately reviewed, and builds and runtime behavior remain unverified.
- `song:artcraft-boundary` — The ArtCraft apps page says every Crafting App is written from scratch in Rust and makes no reverse-engineering claim; the four reviewed READMEs describe clean-room implementations from public specifications and observed behavior, with no proprietary code. No primary source documents decompilation or recovery of Adobe or Microsoft software, and none establishes the third-party REA attribution. PhotoCraft, WordCraft, GridCraft and DeckCraft keep partial mappings to their implementation records; other listed apps such as FilmCraft, LightCraft and CADCraft have public repositories not reviewed here. Retain the lead without a full mapping.
- `song:unity-valheim` — Both linked REA issues document tool bugs. #1801 reports that rea-agents 6.4.0 returned no types or methods for a Unity Assembly-CSharp.dll and Valheim's assembly_valheim.dll under the managed decode budget; #1371 reports a CLI JSON-output crash on an unnamed Unity game assembly, which its reporter later found fixed on main. Neither thread publishes recovered Valheim logic, a modification, reconstructed output or a comparison, and no Valheim retest is reported. The related mapping points to REA's managed-code guide, which documents that 64 MiB budget, partial resource-limit results and --type selection of known types, but not Unity, Valheim or the JSON crash.
- `song:large-android-apk` — The linked REA issue documents a tool bug: rea-agents 4.1.0's JADX provider ran out of Java heap on an unnamed 133 MB production APK with 11 DEX files. The closing reply describes heap-control and memory changes on main but states that they were not retested against that APK, and the thread names no app, recovered feature, reconstructed output or comparison. The related mapping points to REA's Android guide, which documents one JADX worker with no default heap, optional REA_JADX_HEAP_MIB or Java heap settings, the observed heap in Evidence and per-operation limits, but no test on an APK of this size.
- `song:android-apidemos` — Merged REA PR #738 adds five static Android operations through headless JADX: package and manifest inspection, class search, member and selected-method Java/smali inspection, and static caller tracing. It reports a verification lane on Appium's public ApiDemos 6.0.18 APK in which all five CLI and MCP operations passed without executing the APK. This validates the tool integration; no ApiDemos feature or behavior was rebuilt or compared. The related mapping points to REA's Android guide, whose real-verification lane uses the same hash-pinned fixture; the guide documents that tool check, so the mapping scope is related.
- `song:super-mario-sunshine-pc` — Pinned port README, build notes, developer guide and license, with the pinned decompilation fork’s README, progress file, build notes and agent guide, support the reported native PC port and the fork’s author-stated extensive AI assistance. Full mapping covers this port built on that decompilation; GMSE01-only scope, disc-image dependence, incomplete matching, per-platform status and project-reported regression checks remain explicit. The sources do not mention REA use. A related mapping links the separately curated sms-english fork, which the port’s README names as its matching decompilation and decompilation submodule.
- `song:dlss-amd-compute-report` — The linked DLSSNR-AMD repository, reviewed at a pinned commit, documents a Vulkan reimplementation of DLSS 5’s neural-rendering network with user-extracted weights and comparisons against NVIDIA’s DLL; it is curated separately and mapped here as related only. The commented thread quotes an announcement of a different project, HelixSR, which runs a DLSS 3.7 network on AMD, so whether the comment refers to DLSSNR-AMD remains unconfirmed. Neither DLSSNR-AMD’s documentation nor HelixSR’s README describes AI-assisted reverse engineering. A full mapping needs the thread’s subject reviewed; the AI claim remains unconfirmed. The repository mochizuki0323/DLSSNR-AMD returned HTTP 404 on 2026-11-09.
- `song:arwing-littleplanet-ai-port-report` — The post’s three links resolve to carlosrmz009’s arwing, arwing2 and littleplanet repositories, each now curated as its own case: pinned READMEs document coverage-seeded disassemblies that reassemble to the original images, static recompilation to C with interpreter fallback, and recompiled-versus-interpreted hash checks. Each mapping covers one project, so the combined report stays pending. The repositories provide no attribution to AI, REA or Opus 5.5 for the work or evidence for the post’s single-prompt account; matching and runtime results are project-reported.
- `song:virtua-fighter-ai-decompilation` — The post’s two links resolve to celsowm’s repositories. The pinned vf2-decomp documents a BSD-3-Clause, non-matching C17 recovery of Virtua Fighter 2 Version 2.1 that accepts paths only when they match a reference i960 executor; it is now curated, but that mapping is partial. The pinned vf3-decomp, a work-in-progress Dreamcast Virtua Fighter 3tb C port, has agent notes and coverage logs but no README or license file, so it stays uncurated and the combined report remains pending. The repositories do not mention REA use; results are reported by the projects.
- `song:dragon-ball-budokai-browser` — The cited post (@0x0SojalSec, 2026-10-14) says AI reverse-engineered Dragon Ball Budokai so that it runs at 60 fps in any browser, including mobile and online play; it shows one image and links a third-party play website. It names no author, method or source. That website credits a Tenkaichi3Decomp repository as its engine, while the curated Tenkaichi3Decomp README, pinned here, says the project never ships the game, requires the player’s own disc and is not affiliated with browser-play sites. Retain the lead with only a related mapping to the curated PC port; the reported browser port lacks a reviewable project artifact. The cited @0x0SojalSec post 2110230860717060262 returned HTTP 404 on 2026-11-09.
- `song:rea-640-windows-managed-electron-test` — A two-post thread reports hands-on tests of npm rea-agents 6.4.0 on Windows with Node 24: about 200 .NET Framework assemblies against the managed decode budget, an AI-built Electron-style sample, a Trap.dll side-effect check and a one-constant assembly comparison. The samples, raw command output and full environment are not published, and the thread evaluates REA's static analysis rather than reconstructing any software. Retain the lead without a curated case; the related mappings point to the catalog's REA managed-code and JavaScript-workflow documentation, which describe the representation budget, --type selection and application-graph analysis that the posts test.
- `song:whoop-noop-zhoop-ios` — The cited post (@0xLogicrw, 2026-10-15) relays @hackyguru’s post that Zhoop, his fork of the community NOOP app, keeps his WHOOP strap working locally after he dropped the subscription, and adds that he feeds the data to a health AI agent. The pinned Zhoop repository is a single-commit weight-loss rebuild of NOOP for iPhone; its README says the Bluetooth, strap protocol, storage, sleep staging and calorie model are NOOP’s, unchanged, and mentions no AI agent. Zhoop documents no reverse-engineering work of its own. NOOP’s pinned README now backs the noop-whoop-ble-client-case record, mapped as related because it covers the upstream client and protocol work, not Zhoop or the reported agent use. The lead stays without a full mapping.
- `song:iw4l-skate3-mw2-rust-mashup` — The cited post (@thenuntheia, 2026-10-15) relays the 2010 Rust Rewrite Mashup, which its pinned README describes as MW2 multiplayer, a Skate 3 mode and a Minecraft world map on IW4L, a separate from-scratch Rust MW2 runtime, requiring the user’s own MW2 and extracted Xbox 360 Skate 3 files. The skate mode vendors crates from the separate Skate 3 Rust engine project at cb79689, and the world map uses MinecraftOSS. The pinned READMEs of IW4L and the engine back the iw4l-mw2-rust-runtime-case and skate-3-rust-engine-case records, both mapped as related because each covers only a component the mashup builds on, not the mashup itself. Whether the mashup adds reconstruction work of its own still needs a dedicated review.
- `song:pokemon-hgss-multi-agent-decompile-report` — Three posts are cited. @autoaiadvantage (2026-10-15) says someone decompiled Pokémon HeartGold and SoulSilver in a month with several AI agents, using about 71 billion API tokens at an estimated $56k; the cited @Pirat_Nation post was deleted by its author, and @Alex_Vainshtein replies that the work builds on pret’s existing decompilation and tooling. None names or links the project. The fork ctrl-cheeb-del/pokeheartgold says it is fully decompiled with LLM agents and builds both ROMs byte-for-byte, but it reports no token use or cost and no post identifies it as the work described. Retain the lead without a curated case; the related mapping records only the pret baseline the reply names. The cited post 2110989368454189268 returned HTTP 404 on 2026-11-09.
- `song:ringfall-th04-bullet-hell-report` — The post (@0xMoryo, 2026-10-15) says someone used REA’s Ghidra provider on the 1997 PC-98 TH04 executable, recovered two bullet-ring formulas into clean-room notes, and had Claude Code build RINGFALL, a browser bullet-hell boss fight, in one session; it carries only a video. It says REA and “the TH04 study” are linked in replies, which the post API does not expose; the quoted post is a general REA tutorial article, and no RINGFALL source or build was found. Retain the lead without a curated case; the related mapping points to REA’s separately curated TH04 bullet-ring evidence, not to RINGFALL. The cited post 2110844188178952423 returned HTTP 404 on 2026-11-09.
- `song:schaller-opticfilm-thinkpad-linux` — The existing scanner investigation and the separate ThinkPad IMX471 tuning/driver case cover two bounded components of this report. Their mappings remain partial, with complete scanner/camera behavior and all-device compatibility outside their documented scope.
- `song:rea-electron-notes-ipc-answer-key-test` — A two-post thread (@ofmyslippers, 2026-10-15) reports three runs of REA’s static Electron analysis on a small notes app with a known answer key: 4 of 4 IPC channels, handler pairs and preload API members, correctly no sender checks, 2.5–3 s a run, and 1.0 MB of JSON from 2.3 KB of source. The test app, answer key and outputs are not published (the thread links only the REA repository), and the work evaluates REA rather than reconstructing software. Retain the lead without a curated case; the related mapping points to REA’s JavaScript guide, whose own Notes Electron fixture has one IPC channel and so is not the app tested.
- `song:rea-game-function-matcher-audit-report` — The post (@xmyttle, 2026-10-16) retells REA’s Calculator demo and the REA blog essay “Does reverse engineering need a bigger model?” (N0zoM1z0, 2026-10-13): a relay of GPT-6-series models closing stubborn Touhou function matches, and an audit that found accepted functions with wrong constants, including 1.0f where the original added 32.0f. The essay, its pinned evidence notes and TH08 commit a393f400 cover that account, so the full mapping is to the essay’s record; the Touhou reconstruction-method essay, which also documents the audit, stays a partial match, and the Calculator case is related. The essay calls the reward-learning risk an inference, not an observed exploit, and nothing was rerun here.
- `song:rea-reconstruction-companion` — The pinned repository establishes the named Companion: an MIT Agent Skill that works with REA to turn evidence into scoped requirements, design, staged implementation and validation, with an optional installer-managed routing block in REA’s skill and a source-exposed evaluation kit. The full mapping covers it as a community REA integration; the existing partial mapping covers the separate Pocket Tasks worked reconstruction. Example and checker results remain maintainer-reported teaching material, and the repository supplies no model-trial or independent-evaluation results.
- `song:valdiorn-audio-effects-firmware-report` — valdiorn’s Hacker News comment (2026-10-15), summarized by @RealYDT, reports using Opus 5.5 to run three competitors’ effects firmware in an emulator, convert it to standalone C++ libraries and compare the results, plus Lexicon 224 and Ursa Major work. No code, emulator, library, comparison data or product versions are published, and the comment names no Lexicon repository. A reply by the author of the public reflecticon-224 emulation guesses that it was the one found; that project is recorded separately and mapped as related rather than as this report’s work. Retain the lead as insufficient evidence; the reported decompilations and comparisons remain unconfirmed.
- `yibie:all-games-are-open-source-now` — The author’s X article (@rehan_shei, 2026-10-04) is an essay on what AI decompilation and modding mean for the games industry. It says that Opus 5.5, run overnight, produced a working reverse-engineered Terraria to which the author added weapons and mobs, surveys other people’s reported mods and decompilations, and says the author open-sourced what Claude learned as universal-modder. The Terraria rebuild has no public artifact; the related mapping points to that separately catalogued Universal Modder toolkit, which the article names. Retain the lead without a full mapping; the essay is commentary, and its figures and third-party examples remain unchecked here.
- `yibie:how-are-y-all-using-ai-to-make-recompilations` — The source is a discussion: an r/recomps question from 2026-10-05 asking how people use AI to make recompilations and whether a tutorial exists. Replies offer general advice and opinions, such as subscription choices, prompting agents against existing recompilation tools and maintaining recompilation engines, without code, results or comparisons; one reply points to the docs of freefrank/LostOdysseyRecomp, which is already cataloged as its own case and is recorded here only as a related match. Retain the lead without a reconstruction mapping of its own.
- `yibie:finding-jingle-town-debugging-an-n64-game-without-symbols` — The dated post documents a manual GDB-and-Ares workflow for testing one runtime hypothesis in the Snowboard Kids 2 decompilation, with its tools, steps, three observed values and stated limits. Full mapping covers this debugging write-up as a learning resource; the decompilation it studies keeps its own case record, linked here as related. The observations were not repeated, and the post claims no AI or REA use.
- `song:synacktiv-frontkick-rikugan-crebench` — The Synacktiv article documents a dated comparison of the Frontkick and Rikugan Binary Ninja agents on two CREBench tasks, with the setup, a per-run table and the author’s own finding that a prompt difference, rather than the agent design, explains most of the gap. The full mapping covers it as a learning resource; related mappings link the CREBench paper it uses and the rikugan record, which Rikugan’s pinned README and license back and which covers the plugin under test, not the comparison. Frontkick has no public release, transcripts are unpublished, and nothing was rerun here.

Alias decisions:

- `song:mw2-decompilation`, `yibie:500-billion-tokens-later` → `song:mw2-decompilation` — Same Maurice Heumann decompilation retrospective; the primary article leaves the game unnamed, so a future draft must not assert the collection’s MW2 identity from that article alone.
- `song:decompwtf-agent-game-decompilation`, `yibie:decomp-wtf` → `song:decompwtf-agent-game-decompilation` — Same named decomp.wtf project; yibie supplies an additional repository lead, not independent verification.

## Updating this ledger

Review the pinned collection entry and its primary evidence before changing a state. Keep occurrence IDs stable, record explicit aliases, use typed full/partial/related catalog mappings, and leave unresolved project counts unknown.

```sh
python3 scripts/build_case_coverage.py
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

The validator checks schemas, public URLs, pinned receipts, identifiers, aliases, catalog mappings and derived counts.
