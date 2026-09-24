# 家庭视频监控设备清单

最后核对：2026-09-24

本文记录已确认的摄像机、门口机和录像机地址。只记录设备与网络信息，不记录用户名、密码、Token 或完整认证 URL。

## 海康视频设备

| IP 地址 | 名称/位置 | 设备类型 | 型号 | Home Assistant 实体 | 2026-09-24 状态 |
| --- | --- | --- | --- | --- | --- |
| `192.168.3.2` | 前院门口 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_2` | 在线；JPEG/HLS 正常 |
| `192.168.3.3` | 前院长椅 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_3` | 在线；JPEG/HLS 正常 |
| `192.168.3.4` | 侧院设备区 | IP 摄像机 | `DS-2CD1245-LA` | `camera.network_video_recorder_pin_dao_12` | 在线；NVR 频道 JPEG/实时流正常 |
| `192.168.3.10` | 东侧走廊 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_10` | 在线；JPEG/HLS 正常 |
| `192.168.3.81` | 院门门铃 | 室外门口机 | `DS-KVJ203` | `camera.192_168_3_81` | 在线；JPEG/HLS 正常 |
| `192.168.3.83` | 前院 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_83` | 在线；JPEG/HLS 正常 |
| `192.168.3.84` | 车库门口/车库门口云台 | 双画面 IP 摄像机 | `DS-2SC3Q144MY-TE` | NVR 频道 8、9 | 在线；两路 NVR 画面正常 |
| `192.168.3.85` | 车库屋顶 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_85` | 在线；JPEG/HLS 正常 |
| `192.168.3.86` | 后院 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_86` | 在线；JPEG/HLS 正常 |
| `192.168.3.87` | 北侧走廊 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_87` | 在线；JPEG/HLS 正常 |
| `192.168.3.88` | 车库内 | IP 摄像机 | `DS-2CD1345V2-LA` | `camera.192_168_3_88` | 在线；JPEG/HLS 正常 |
| `192.168.3.90` | 二楼露台 | IP 摄像机 | `DS-2CD1245-LA` | `camera.192_168_3_90` | 在线；JPEG/HLS 正常 |

侧院设备区摄像机原记录地址为 `192.168.3.89`，该地址已不可达；NVR 当前报告的新地址为 `192.168.3.4`。

## 录像机

| IP 地址 | 设备类型 | 型号 | 用途 | Home Assistant 状态 |
| --- | --- | --- | --- | --- |
| `192.168.3.12` | 海康 NVR | `DS-7916N-R4(C)` | 集中录像与通道管理 | 不作为独立摄像机实体；误加的 `.12` 实体已移除 |

NVR 的 `192.168.3.12` 可返回视频通道，但该画面属于录像机通道，不应把 NVR 本身记为一台独立摄像头。

### NVR 频道映射

| NVR 频道 | 源 IP | 名称/位置 | Home Assistant 实体 |
| --- | --- | --- | --- |
| 1 | `192.168.3.87` | 北侧走廊 | `camera.network_video_recorder_pin_dao_1` |
| 2 | `192.168.3.3` | 前院长椅 | `camera.network_video_recorder_pin_dao_2` |
| 3 | `192.168.3.86` | 后院 | `camera.network_video_recorder_pin_dao_3` |
| 4 | `192.168.3.83` | 前院 | `camera.network_video_recorder_pin_dao_4` |
| 5 | `192.168.3.88` | 车库内 | `camera.network_video_recorder_pin_dao_5` |
| 6 | `192.168.3.10` | 东侧走廊 | `camera.network_video_recorder_pin_dao_6` |
| 7 | `192.168.3.90` | 二楼露台 | `camera.network_video_recorder_pin_dao_7` |
| 8 | `192.168.3.84` | 车库门口 | `camera.network_video_recorder_pin_dao_8` |
| 9 | `192.168.3.84` | 车库门口云台 | `camera.network_video_recorder_pin_dao_9` |
| 10 | `192.168.3.85` | 车库屋顶 | `camera.network_video_recorder_pin_dao_10` |
| 11 | `192.168.3.2` | 前院门口 | `camera.network_video_recorder_pin_dao_11` |
| 12 | `192.168.3.4` | 侧院设备区 | `camera.network_video_recorder_pin_dao_12` |

院门门铃 `192.168.3.81` 未接入该 NVR，继续使用独立 Generic Camera 实体。

## Hikvision 事件链路诊断

2026-09-24 对 NVR、Home Assistant 集成和代表性摄像机进行了实测。

### 当前状态

- Home Assistant `2026.2.2` 使用核心 `hikvision` 集成，底层依赖 `pyHik 0.4.2`，通过 `/ISAPI/Event/notification/alertStream` 接收本地推送。
- 初次检查时，NVR 频道 1-12 的 `VMD`（移动侦测）均只配置了 `record` 联动，没有 `center` 或 `HTTP` 联动；连续监听事件流 30 秒只收到 3 次 `videoloss/inactive` 心跳，HA 最近 24 小时内也没有 motion 触发。
- 20:57 复查时，频道 3（后院）和频道 11（前院门口）已增加 `center`，其余频道仍只有 `record`。HA 已收到频道 11 一次、频道 3 三次完整的 `on/off` 移动事件，证明 NVR → ISAPI event stream → HA 链路正常。
- 频道 11 于 20:27:56 触发、20:28:36 恢复；频道 3 于 20:55:49、20:56:20、20:56:56 三次触发，最后于 20:57:26 恢复。时间均为 `Asia/Shanghai`。
- 因此，HA 中存在 binary sensor 实体不等于 NVR 正在推送对应事件；每个需要实时事件的频道都必须配置 `center`。

### 智能类型未区分的原因

1. 当前录像机是 `DS-7916N-R4(C)`，不是带 AcuSense 分析能力的 `NXI` 系列。它能集中录像和转发普通事件，但不能依靠录像机自身为所有通道补充人/车分类。
2. 摄像机端实际具备一定分类能力。实测移动侦测配置中：`DS-2CD1245-LA` 和 `DS-2CD1345V2-LA` 的 `targetType` 为 `human`；`.84` 的 `DS-2SC3Q144MY-TE` 为 `human,vehicle`。这些标签没有通过当前 NVR 的通用 `VMD` 事件完整传递给 HA。
3. `pyHik 0.4.2` 使用固定事件映射。`VMD` 统一映射成 `Motion`，不会在 HA 中拆成人/车实体，也不暴露 `targetType`。
4. NVR 还声明了 `personDensityDetection`、`objectsThrownDetection`、`channelOccupy` 和 `ChannelPassingEvent` 等事件，但它们不在当前 `pyHik` 的事件映射中。HA 会根据 NVR trigger 配置创建这些实体，实时解析器遇到未知类型时却会丢弃事件，因此这些实体不能视为已经可用。

### 修复顺序

1. 在 NVR 每个需要监测的频道中保留“触发录像”，同时启用“上传中心/通知监控中心”，并核对布防时间；使 trigger 的 `notificationMethod` 至少包含 `center`。
2. 核对 HA 使用的海康账号具有“远程：通知监控中心/触发报警输出”权限，并保持 Web 认证为 `digest/basic`。
3. 重新加载 Hikvision 集成后，现场触发一个频道；先确认 alert stream 出现 `VMD active/inactive` 和正确频道，再确认对应 HA motion 实体产生 `on/off` 历史。
4. 人/车分类不要依赖当前 HA binary sensor。若要保留摄像机的 `targetType`，应在 `rasp2` 运行独立 ISAPI 事件桥接，解析原始事件并发布为 MQTT/HA 事件；或使用支持该字段的新版本解析器/自定义集成。直接修改 HA 容器内核心文件会在升级时丢失，不作为长期方案。
5. 若设备事件报文仍不带目标类别，再使用 NVR 事件录像作为候选片段，由 OpenCV 规则初筛后提交 AI 分析。

参考资料：

- [Home Assistant Hikvision 集成](https://www.home-assistant.io/integrations/hikvision)
- [Hikvision ISAPI Event Notification Alert 结构](https://open.hikvision.com/hardware/v2/XML%E6%96%87%E4%BB%B6/XML_EventNotificationAlert.html)
- [Hikvision Notify Surveillance Center 说明](https://enpinfo.hikvision.com/hkwsen/unzip/20230410194813_20373_doc/GUID-242A4133-7B2F-4AE3-A56B-21A9581ED330.html)
- [DS-7900N-R4(C) 规格表](https://dealer-static.hikvision.com/upload/file/doc/DOC000091742-DS-7900N-R4%28C%29_20230308.pdf)
- [pyHik 事件解析源码](https://github.com/mezz64/pyHik/blob/master/pyhik/hikvision.py)

## 其他摄像机

| IP 地址 | 名称 | 型号 | Home Assistant 状态 |
| --- | --- | --- | --- |
| `192.168.3.140` | 小米室内摄像机 | 小米智能摄像机 云台版2K2（`chuangmi.camera.029a02`） | Xiaomi MIoT 控制实体可读；图像实体待打通 |

## 视频接入约定

- Home Assistant 主机：`192.168.3.254`。监控看板使用 Hikvision 集成提供的 NVR 频道 1-12，并保留独立的 `.81` 院门门铃画面。
- 原 Generic Camera 实体继续保留作故障回退；`.81` 因未接入 NVR，仍作为当前使用实体。
- `.2`、`.3`、`.81` 使用新版海康主码流路径 `/Streaming/Channels/101`。
- `.10`、`.83`-`.90` 已知设备使用旧版路径 `/h264/ch1/main/av_stream`。
- 静态图像使用 Hikvision ISAPI 通道 `101` 抓图。
- HA 原生实时卡片会把 `stream_source` 交给内置 go2rtc；RTSP 地址必须能独立完成认证。
- 外部 go2rtc 容器当前不参与这些 HA 摄像机的实时链路。

## HomeKit Bridge

- 摄像头专用桥接名称：`HA Surveillance`，端口 `21068`。
- 配置来源：`rasp:/home/guosq/homeassistant/configuration.yaml` 中的 `homekit` / `HA Surveillance` 段。
- 当前桥接 13 个画面实体：Hikvision NVR 频道 1-12，以及未接入 NVR 的 `.81` 院门门铃。
- 频道 8 和 9 都来自 `.84`，分别显示“车库门口”和“车库门口云台”。
- 2026-09-24 已将桥接从 Generic Camera 切换到上述 Hikvision 频道，并成功执行配置检查和 `homekit.reload`。
- Home Assistant 会警告多个摄像头放在单一 bridge 中的性能不如每台独立 accessory；当前为避免重新逐台配对，保留既有单桥结构。

## 维护约定

1. 摄像机、门口机或 NVR 换 IP、更名、上下线时更新本文的核对日期和状态。
2. 密码、Token 和完整带认证的 RTSP URL 不得写入 Git。
3. 新增设备后同时验证静态 JPEG 和 HLS 实时流，不只以端口可达为成功标准。
4. NVR 通道和独立 IP 摄像机要分开记录，避免重复或误识别。
