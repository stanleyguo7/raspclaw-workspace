# 家庭视频监控与 NVR 基线

最后核对：2026-09-30

本文记录摄像机、海康 NVR、Home Assistant 与 HomeKit 的当前接入状态，以及近期误报调整。禁止记录用户名、密码、Token 或带认证信息的完整 URL。

## 系统概况

- Home Assistant：`192.168.3.254`
- 海康 NVR：`192.168.3.12`，`DS-7916N-R4(C)`，固件 `V4.84.030 build 250710`
- 最大 16 通道，当前使用 13 路；约 4 TB，循环录像正常，约可保存 8 天
- HA 和 HomeKit 均统一使用 NVR 频道实体，不再保留同一摄像机的 Generic Camera 重复项
- HomeKit 摄像头桥：`HA Surveillance`，端口 `21068`

## NVR 频道映射

| 频道 | 源 IP | 名称/位置 | 型号（已知） | HA 实体 |
| --- | --- | --- | --- | --- |
| 1 | `192.168.3.87` | 北侧走廊 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_1` |
| 2 | `192.168.3.3` | 前院长椅 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_2` |
| 3 | `192.168.3.86` | 后院厨区 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_3` |
| 4 | `192.168.3.83` | 前院 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_4` |
| 5 | `192.168.3.88` | 车库内 | `DS-2CD1345V2-LA` | `camera.network_video_recorder_pin_dao_5` |
| 6 | `192.168.3.10` | 东侧走廊 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_6` |
| 7 | `192.168.3.90` | 二楼露台 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_7` |
| 8 | `192.168.3.84` | 车库门口 | `DS-2SC3Q144MY-TE` | `camera.network_video_recorder_pin_dao_8` |
| 9 | `192.168.3.84` | 车库门口云台 | `DS-2SC3Q144MY-TE` | `camera.network_video_recorder_pin_dao_9` |
| 10 | `192.168.3.85` | 车库屋顶 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_10` |
| 11 | `192.168.3.2` | 门口/前院门口 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_11` |
| 12 | `192.168.3.4` | 侧院设备区 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_12` |
| 13 | `192.168.3.81` | 院门门铃 | `DS-KVJ203` | `camera.network_video_recorder_pin_dao_13` |

- 频道 12 原地址 `.89` 已失效，现使用 `.4`。
- 频道 13 于 2026-09-29 加入 NVR，NVR 内命名“院门门铃”；在线、画面、录像轨道和音频计划均已验证。
- `.81` 原独立 Generic Camera 已去除，HA 看板和 HomeKit 均改用 NVR 频道 13。
- 通道 8、9 来自同一台双画面/云台摄像机，但属于两个独立画面。

## HA 与 HomeKit 清理结果

- HA 监控看板和 HomeKit `HA Surveillance` 当前均只使用 NVR 频道 1–13。
- 清理备份：
  - `/home/guosq/homeassistant/.storage/manual-backup-20260929-camera-cleanup`
  - `/home/guosq/homeassistant/configuration.yaml.bak-20260929-nvr13`
  - `/home/guosq/homeassistant/.storage/lovelace.dashboard_jiankong.bak-20260929-nvr13`

## 移动侦测与人车分类

- 该 NVR 不是 AcuSense/NXI 型号，不能替所有通道补充人车分析。
- 摄像机端大多支持 `human` 目标过滤；通道 8、9 支持 `human,vehicle`。
- HA 核心 Hikvision 集成会把普通 `VMD` 统一显示为 Motion，不能可靠拆分成人/车实体。
- HA 要收到实时事件，NVR 对应频道除“触发录像”外还需启用“上传中心/通知监控中心（center）”。

## 2026-09-30 误报调整

### 频道 3：后院厨区

- 9 月 29 日 21:49–23:55 共 21 次，9 月 30 日 00:06–05:23 共 76 次“有人移动”。疑似风吹植物、桌布及红外反光造成。
- 保持 `human` 和灵敏度 `20`；检测区域由 `330/396` 缩至 `176/396`。
- 排除上方植物和中央桌布，保留后方横向通道、左右步道及底部入口。
- 摄像机端与 NVR 端已同步，画面验证正常。
- 备份：
  - `/home/guosq/homeassistant/backups/manual-config/hikvision-ch3-motion-20260930-094555.xml`
  - `/home/guosq/homeassistant/backups/manual-config/hikvision-nvr-ch3-motion-20260930-094628.xml`

### 频道 11：门口/前院门口

- 近期约 3–8 次/天；疑似车罩在风和红外反光下被判成人形。
- 保持 `human`；灵敏度 `40` 降至 `20`；检测区域由 `298/396` 缩至 `234/396`。
- 排除上部中央车罩和树木，保留左侧门口及下方步道。
- 摄像机端与 NVR 端已同步，NVR 抓图验证正常。
- 备份：
  - `/home/guosq/homeassistant/backups/manual-config/hikvision-ch11-motion-20260930-100922.xml`
  - `/home/guosq/homeassistant/backups/manual-config/hikvision-nvr-ch11-motion-20260930-100922.xml`

### 后续观察顺序

1. 先观察后续夜间误报数。
2. 若仍频繁，清洁镜头/红外窗、检查蜘蛛网，并固定桌布和车罩。
3. 再考虑把红外补光从 `100` 调至 `60–70` 或使用智能补光。
4. 最后才在 HA 通知层增加去抖/冷却时间。

## 维护约定

1. 设备换 IP、更名、上下线时更新本文。
2. 新增通道后验证在线、抓图、实时画面、录像、音频（如有）、HA 与 HomeKit。
3. NVR 通道作为 HA/HomeKit 的唯一主入口，避免重复创建 Generic Camera。
4. 密码、Token 和完整认证 URL 不得写入 Git。
