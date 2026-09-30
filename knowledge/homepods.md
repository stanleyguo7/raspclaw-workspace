# HomePod 设备与访问基线

最后核对：2026-09-30

本文记录家中 HomePod mini 的位置、Home Assistant 与 Music Assistant 访问方式。不得记录 Apple 账户、密码、Token 或 HomeKit 配对密钥。

## 设备清单

| 位置 / Apple 名称 | 型号 | HA `media_player` | HA `remote` | Music Assistant AirPlay 播放器 ID |
| --- | --- | --- | --- | --- |
| 一楼客厅：`F1客厅 (2)` | HomePod mini | `media_player.f1ke_ting_2_f1ke_ting_2` | `remote.f1ke_ting_2_f1ke_ting_2` | `ap4e63698c8ab0` |
| 二楼主卧：`F2主卧` | HomePod mini | `media_player.f2zhu_wo_f2zhu_wo` | `remote.f2zhu_wo_f2zhu_wo` | `apa207c1535328` |
| 二楼小满房间：`F2小满房间` | HomePod mini | `media_player.2407147352_2407147352` | `remote.2407147352_2407147352` | `apf27b944e343e` |
| 二楼小元房间：`F2小元房间` | HomePod mini | `media_player.f2xiao_yuan_fang_jian_f2xiao_yuan_fang_jian` | `remote.f2xiao_yuan_fang_jian_f2xiao_yuan_fang_jian` | `ap42f47b9626c9` |
| 地下一层茶室：`B1茶室` | HomePod mini | `media_player.b1cha_shi_b1cha_shi` | `remote.b1cha_shi_b1cha_shi` | `apae551bb444d6` |

`F2小满房间` 在 HA Apple TV 集成中的实体名沿用了设备的另一广播名称 `2407147352…`，但配置条目标题和 Music Assistant 名称均为 `F2小满房间`。

## Home Assistant 访问

- 接入方式：官方 Apple TV 集成，通过局域网 Zeroconf/AirPlay 自动发现。
- 2026-09-30 已确认 5 个配置条目均处于 `loaded` 状态。
- 每台设备当前提供 `media_player` 和 `remote` 实体，可用于播放状态、音量、暂停/继续及基础遥控。
- 当前集成不提供 HomePod 内置温度和湿度实体。若以后需要精确数值，优先考虑 Apple 家庭自动化读取后通过局域网 webhook 回传 HA。

## Music Assistant 访问

- 服务位置：rasp2（局域网 `http://192.168.3.119:8095`）。
- 播放器接入：AirPlay provider；5 台 HomePod 均已启用且当前配置标记为 `available: true`。
- 同步组：`Homepods`
- 同步组 ID：`syncgroup_uuzedche`
- 组成员：上述 5 个 AirPlay 播放器；`dynamic_members: true`。
- 每台 AirPlay 播放器同时有内部 Sendspin bridge，用于 Music Assistant 的统一播放与同步控制；日常调用应优先使用主 AirPlay 播放器 ID，不直接调用 `spb_*` 协议子播放器。

## 适合的使用场景

1. **全屋或分房间音乐**：在 Music Assistant 中向单台 HomePod 播放，或使用 `Homepods` 组进行五房间同步播放。
2. **起床、睡前和茶室场景**：按时间或 HA 场景启动指定歌单，并同时调用 Yeelight 场景调整灯光。
3. **门铃与访客提示**：院门门铃/NVR 事件触发后，在客厅、主卧或茶室播报；应设置冷却时间，避免监控误报造成连续播报。
4. **水浸、燃气和设备故障播报**：把 HA 的安全传感器异常转成语音提醒；HomePod 播报只能作为补充，不能替代实体声光报警器。
5. **分区通知**：夜间只通知主卧，白天优先客厅和茶室，儿童房避免在睡眠时段播报。
6. **温湿度联动（待实现）**：由 Apple 家庭读取 HomePod 传感器并回传 HA 后，可做房间舒适度、空调/除湿及历史曲线。

## 自动化注意事项

- AirPlay 开始播放可能打断 HomePod 当前内容；播报前要保存或尊重当前播放状态，并限制音量。
- 全屋同步对无线网络和设备在线状态敏感；关键提醒不应只依赖同步组。
- 新自动化先在一台 HomePod、小音量、白天时段测试，再扩大到同步组。
- 儿童房和卧室应设置静默时段；燃气、水浸等严重事件可例外，但仍要避免过高音量。
