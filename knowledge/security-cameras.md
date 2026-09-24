# 家庭视频监控设备清单

最后核对：2026-09-24

本文记录已确认的摄像机、门口机和录像机地址。只记录设备与网络信息，不记录用户名、密码、Token 或完整认证 URL。

## 海康视频设备

| IP 地址 | 名称/位置 | 设备类型 | 型号 | Home Assistant 实体 | 2026-09-24 状态 |
| --- | --- | --- | --- | --- | --- |
| `192.168.3.2` | 前院门口 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_2` | 在线；JPEG/HLS 正常 |
| `192.168.3.3` | 前院长椅 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_3` | 在线；JPEG/HLS 正常 |
| `192.168.3.10` | 东侧走廊 | IP 摄像机 | 待确认 | `camera.192_168_3_10` | 在线；JPEG/HLS 正常 |
| `192.168.3.81` | 院门门铃 | 室外门口机 | `DS-KVJ203` | `camera.192_168_3_81` | 在线；JPEG/HLS 正常 |
| `192.168.3.83` | 前院 | IP 摄像机 | 待确认 | `camera.192_168_3_83` | 在线；JPEG/HLS 正常 |
| `192.168.3.84` | 车库门口 | IP 摄像机 | 待确认 | `camera.192_168_3_84` | 在线；JPEG/HLS 正常 |
| `192.168.3.85` | 车库屋顶 | IP 摄像机 | 待确认 | `camera.192_168_3_85` | 在线；JPEG/HLS 正常 |
| `192.168.3.86` | 后院 | IP 摄像机 | 待确认 | `camera.192_168_3_86` | 在线；JPEG/HLS 正常 |
| `192.168.3.87` | 北侧走廊 | IP 摄像机 | 待确认 | `camera.192_168_3_87` | 在线；JPEG/HLS 正常 |
| `192.168.3.88` | 车库内 | IP 摄像机 | 待确认 | `camera.192_168_3_88` | 在线；JPEG/HLS 正常 |
| `192.168.3.89` | 待确认摄像机 | IP 摄像机 | 待确认 | `camera.192_168_3_89` | 离线；已从监控看板隐藏 |
| `192.168.3.90` | 二楼露台 | IP 摄像机 | 待确认 | `camera.192_168_3_90` | 在线；JPEG/HLS 正常 |

## 录像机

| IP 地址 | 设备类型 | 型号 | 用途 | Home Assistant 状态 |
| --- | --- | --- | --- | --- |
| `192.168.3.12` | 海康 NVR | `DS-7916N-R4(C)` | 集中录像与通道管理 | 不作为独立摄像机实体；误加的 `.12` 实体已移除 |

NVR 的 `192.168.3.12` 可返回视频通道，但该画面属于录像机通道，不应把 NVR 本身记为一台独立摄像头。

### NVR 频道映射

| NVR 频道 | 名称/位置 | Home Assistant 实体 |
| --- | --- | --- |
| 1 | 北侧走廊 | `camera.network_video_recorder_pin_dao_1` |
| 2 | 前院长椅 | `camera.network_video_recorder_pin_dao_2` |
| 3 | 后院 | `camera.network_video_recorder_pin_dao_3` |
| 4 | 前院 | `camera.network_video_recorder_pin_dao_4` |
| 5 | 车库内 | `camera.network_video_recorder_pin_dao_5` |
| 6 | 东侧走廊 | `camera.network_video_recorder_pin_dao_6` |
| 7 | 二楼露台 | `camera.network_video_recorder_pin_dao_7` |
| 8 | 车库门口 | `camera.network_video_recorder_pin_dao_8` |
| 9 | 院门门铃 | `camera.network_video_recorder_pin_dao_9` |
| 10 | 车库屋顶 | `camera.network_video_recorder_pin_dao_10` |
| 11 | 前院门口 | `camera.network_video_recorder_pin_dao_11` |
| 12 | 未使用 | `camera.network_video_recorder_pin_dao_12`，无有效画面 |

## 其他摄像机

| IP 地址 | 名称 | 型号 | Home Assistant 状态 |
| --- | --- | --- | --- |
| `192.168.3.140` | 小米室内摄像机 | 小米智能摄像机 云台版2K2（`chuangmi.camera.029a02`） | Xiaomi MIoT 控制实体可读；图像实体待打通 |

## 视频接入约定

- Home Assistant 主机：`192.168.3.254`。监控看板使用 Hikvision 集成提供的 NVR 频道 1-11；原 Generic Camera 实体继续保留，供 HomeKit 和故障回退使用。
- `.2`、`.3`、`.81` 使用新版海康主码流路径 `/Streaming/Channels/101`。
- `.10`、`.83`-`.90` 已知设备使用旧版路径 `/h264/ch1/main/av_stream`。
- 静态图像使用 Hikvision ISAPI 通道 `101` 抓图。
- HA 原生实时卡片会把 `stream_source` 交给内置 go2rtc；RTSP 地址必须能独立完成认证。
- 外部 go2rtc 容器当前不参与这些 HA 摄像机的实时链路。

## HomeKit Bridge

- 摄像头专用桥接名称：`HA Surveillance`，端口 `21068`。
- 配置来源：`rasp:/home/guosq/homeassistant/configuration.yaml` 中的 `homekit` / `HA Surveillance` 段。
- 当前桥接 11 个在线实体：`.2`、`.3`、`.10`、`.81`、`.83`、`.84`、`.85`、`.86`、`.87`、`.88`、`.90`。
- 离线的 `.89` 不加入 HomeKit Bridge。
- 2026-09-24 已将 HomeKit 显示名称从“摄像头 1～9”更新为本文记录的实际位置名称，并成功执行 `homekit.reload`。
- Home Assistant 会警告多个摄像头放在单一 bridge 中的性能不如每台独立 accessory；当前为避免重新逐台配对，保留既有单桥结构。

## 维护约定

1. 摄像机、门口机或 NVR 换 IP、更名、上下线时更新本文的核对日期和状态。
2. 密码、Token 和完整带认证的 RTSP URL 不得写入 Git。
3. 新增设备后同时验证静态 JPEG 和 HLS 实时流，不只以端口可达为成功标准。
4. NVR 通道和独立 IP 摄像机要分开记录，避免重复或误识别。
