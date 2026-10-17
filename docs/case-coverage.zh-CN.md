# 案例合集覆盖记录

[English](case-coverage.md) · [机器可读记录](../data/case-coverage.json)

核查日期：2026-10-17（UTC）。**372 个合集出现项**经 2 次有记录的重复合并后，对应 **370 个清单单元**。其中包括报告、工具、论文、讨论和想法，不能当作独立且已核验的项目数量。

项目身份归并尚未完成，因此独立项目数为 `null`，并非零。同一上游条目的中英文版本只计一次。同一项目的不同报告仍分别计为清单单元，除非已有明确的别名合并决定。

## 固定来源

| 合集快照 | 条目数 | 目录记录 |
| --- | ---: | --- |
| [songshikang0111/awesome-REA-cases · 2c9ce9597f0a](https://github.com/songshikang0111/awesome-REA-cases/tree/2c9ce9597f0afcbafaa79de0293083224a974e91) | 344 | [awesome-rea-cases](https://awesomerea.org/zh/resources/#awesome-rea-cases) |
| [yibie/awesome-rea · 6df1bc922ac6](https://github.com/yibie/awesome-rea/tree/6df1bc922ac6b92dcd1b2f905c94d8cc4f3b5a3e) | 28 | [yibie-awesome-rea](https://awesomerea.org/zh/resources/#yibie-awesome-rea) |

记录保留固定版本文件 URL、Git blob 标识、SHA-256 和字节数，仅描述这些已清点快照，不代表上游后续版本或整个领域。这里不再发布完整的上游简介或 README 正文。

## 数量与状态

| 状态 | 出现项 | 清单单元 | 含义 |
| --- | ---: | ---: | --- |
| 已收录 (`already-curated`) | 35 | 34 | 完整范围已对应目录资源或论文；不代表独立运行复现。 |
| 待核查 (`pending`) | 288 | 287 | 一手核查或完整目录覆盖尚待完成；部分映射也保留在此状态。 |
| 证据不足 (`insufficient-evidence`) | 49 | 49 | 将想法、请求或尚缺支持的重建说法保留为线索。 |

37 个出现项含目录链接；共关联 33 个不同资源 ID 和 1 个论文 ID。映射范围单独记录，不能将这些群体相加当作独立项目数。

此记录为 23 个清单单元记载了新的一手来源核查。其他已有目录链接的条目对应目录中独立的来源核查记录；链接本身不代表重新核查了整篇合集报告。此记录没有独立复现运行实验。

此记录刻意不包含仓库 README 扫描 ID 或扫描数量。成功读取 README、被上游合集列出和案例经过来源核查，是不同事实。

## 本轮一手核查案例

| 案例 | 状态 | 一手证据 |
| --- | --- | --- |
| PlxNative：重建原生 webOS 媒体客户端接口 | 已收录 | [来源](https://github.com/GLinnik21/plx-native/blob/0b0b22092b204432834c75f32148dbd16ec3493b/README.md) |
| 智能体反编译：字节匹配验收复盘 | 已收录 | [来源](https://momo5502.com/posts/2026-10-09-game-decompilation/) |
| open-appleremote：Siri Remote 协议重建 | 已收录 | [来源](https://github.com/a-funk/open-appleremote/blob/1e6e190c3c29a3d2d8cad2c38c09f8953e9633e3/README.md) |
| TH08：精确源码重建与单独验证的移植 | 待核查 | [来源](https://github.com/N0zoM1z0/th08/blob/08c7f00f81e35db8206d917b14f47883930beef6/README.md) |
| 恐龙跑酷：恢复一条加速规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| Windows Calculator：重建百分比规则 | 已收录 | [来源](https://github.com/morluto/rea/blob/c360cfcd6d7901514b16dd6113eba2e0b0fdf422/website/evidence/calculator-and-dino.md) |
| CF632BLE：基于体脂秤协议研究的本地客户端 | 已收录 | [来源](https://github.com/guyru/cf632ble/blob/c029ef5cfefbd323ffe2a194a75db5cc47aa6d5c/README.md) |
| zee-rp：重建 Axure RP 11 的受支持文档操作 | 已收录 | [来源](https://github.com/LilZeeCN/zee-rp/blob/473761e6a08f051e1666944db690332ef27a6038/README.md) |
| Nanolathe：附研究文档的 Total Annihilation 引擎重实现 | 已收录 | [来源](https://github.com/nanolathe-gg/nanolathe/blob/5007ba75354c06fc9752a2822d37ff1e1443b77b/README.md) |
| cooler-lcd：Thermalright 显示屏协议实现 | 已收录 | [来源](https://github.com/kristjaningi/cooler-lcd/blob/9a343678ba102de784b2302f79c53fd6ddc31ab9/README.md) |
| Virtual Desktop Streamer：在 Linux 上重建平台适配层 | 已收录 | [来源](https://github.com/cudanexus/vd-streamer-linux/blob/e65c302f13639f044742bdc4951ab1a424c1c929/README.md) |
| Open Claude UI：基于 REA 调查的界面参考组件 | 已收录 | [来源](https://github.com/Caho1/open-claude-ui/blob/ddf3aea1711db62fd6d24343bbab500a5ae69f64/README.md) |
| GAMEKB-K17：重建宏键盘配置协议 | 已收录 | [来源](https://github.com/dvdarkin/gamekb-k17/blob/e61f444793857c0e10a31692674335ee4ee9c89e/README.md) |
| IsaacRecomp：将 Flash 游戏字节码转换为原生 C++ | 已收录 | [来源](https://github.com/whylurking/IsaacRecomp/blob/7736f3d2961051b66cd315bcf5a719e9024d889d/README.md) |
| 飞书：作者报告的隔离第二应用实例 | 已收录 | [来源](https://benx.ai/blog/posts/rea-reverse-engineer-feishu-dual-instance/) |
| Super Mario 64 DS：带重定位核对的匹配反编译 | 已收录 | [来源](https://github.com/tangosdev/sm64ds-decomp/blob/af8636d638322b88738ef7ad4b4f28ed9c5be24f/README.md) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/the-long-tail-of-llm-assisted-decompilation/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/using-coding-agents-to-decompile-nintendo-64-games/) |
| Snowboard Kids 2：大模型辅助的 N64 匹配反编译 | 已收录 | [来源](https://blog.chrislewis.au/snowboard-kids-2-is-100-decompiled/) |
| GoldenEye 007：基于反编译成果的智能体辅助原生移植 | 已收录 | [来源](https://github.com/jkdansereau/goldeneye-pc-port/blob/fda76b69837e6c5aae436e0d3e798989e49b06d2/README.md) |
| BattleShip：AI 辅助的 Super Smash Bros. 原生移植 | 已收录 | [来源](https://github.com/JRickey/BattleShip/blob/39e978fbffe06a24f718bdf1ca740f27ad6a7dec/README.md) |
| ssbu-recomp：明确玩法边界的静态重编译 | 已收录 | [来源](https://github.com/Denkishi/ssbu-recomp/blob/938e66bb7be0ba4123e291211895412da421b705/README.md) |
| KartPad：Mario Kart Wii 重编译的平台集成 | 已收录 | [来源](https://github.com/chrissotraidis/kartpad/blob/7e99c6776263caa85dccde2de6281cb092778877/README.md) |

## 部分覆盖与别名

部分目录映射：

- `song:touhou-reconstruction` — TH08 部分已有精选条目；组合报告中的 TH04 和 TH095 部分仍不在该映射范围内。
- `song:schaller-opticfilm-thinkpad-linux` — 扫描仪 USB 调查已有精选条目；同一合集条目还报告 MIPI 相机工作，后者不在此次目录映射的覆盖范围内。

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
