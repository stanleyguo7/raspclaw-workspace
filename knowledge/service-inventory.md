# 家庭服务权威清单

更新时间：2026-10-08 11:00（Asia/Shanghai）

本文件记录当前实际运行的服务位置、依赖和恢复顺序。密码、令牌、Cookie 与配对码不写入仓库。

## 1. 服务拓扑

### rasp — 家庭自动化核心（192.168.3.254）

| 服务 | 运行方式 | 入口/端口 | 主要数据或配置 | 说明 |
|---|---|---|---|---|
| Home Assistant | Docker，host 网络 | `http://192.168.3.254:8123` | `/home/guosq/homeassistant` | 家庭设备、自动化、看板与 HomeKit 核心 |
| HomeKit bridges | HA 内置 | TCP `21064`–`21068` | HA 配置 | 五个桥，依赖 HA 正常加载 |
| go2rtc | Docker | Web `1984`；RTSP `8554`；WebRTC `8555` | `/opt/go2rtc` | 摄像头转流 |
| MQTT / Mosquitto | Docker | `1883` | workspace `mqtt/` | HA 与自动化消息总线 |
| n8n | Docker | `http://192.168.3.254:5678` | workspace `n8n/` + Docker volume | RSS/自动化编排 |
| 光猫管理转发 | user systemd | `http://192.168.3.254:8085` → `192.168.8.1:80` | `port_forward_8085_to_192.168.8.1_80.py` | 仅作管理入口 |

当前保留容器只有：`homeassistant`、`go2rtc`、`mqtt`、`n8n`。旧的 rasp 本机 Music Assistant、rclone 和 HA 测试容器已移除。

### rasp2 — OpenClaw 与家庭娱乐（192.168.3.119）

| 服务 | 运行方式 | 入口/端口 | 主要数据或配置 | 说明 |
|---|---|---|---|---|
| OpenClaw Gateway | user systemd | 本机控制面；经 Tailscale 访问 | `~/.openclaw` | 当前智能助手主节点 |
| Stanley FunHub | user systemd | 首页 `http://192.168.3.119:8790`；下载 `/downloads/` | `/home/guosq/workspace/stanley-funhub` | 娱乐资讯与夸克→Zidoo 下载的统一入口/进程 |
| Jellyfin | Docker，host 网络 | `http://192.168.3.119:8096` | `/home/guosq/services/jellyfin/config` | 只保留 Zidoo 本地媒体库；Swiftfin 客户端使用 |
| Music Assistant | Docker，host 网络 | Web `8095`；Stream `8097`；附加端口 `8927` | workspace `services/music-assistant/data` | 音乐库与播放器编排 |
| AList | Docker | `http://192.168.3.119:5244` | `/home/guosq/alist/data` | 夸克目录访问支撑；不再作为 Jellyfin 直接媒体库 |
| rclone | Docker | RC 仅本机 `127.0.0.1:5572` | `/home/guosq/rclone` | 云盘挂载与底层访问 |
| 夸克只读 HTTP 桥 | user systemd | 仅本机 `127.0.0.1:8787` | `quark-rclone-http.service` | 为下载管理器提供 Range 读取 |
| 夸克→Zidoo 下载模块 | FunHub 内置 WSGI 模块 | `http://192.168.3.119:8790/downloads/` | FunHub `downloads/` 与 `data/downloads/` | 文件/文件夹下载、暂停续传、删除、Jellyfin 刷新与刮削；旧 8788 服务已停用 |
| Docker Registry | system service | `5000` | 系统 registry 配置 | 局域网镜像缓存/仓库 |
| HA 异机备份同步 | user timer | 每日约 `06:15` | `~/.local/bin/ha-backup-sync.sh` | 从 rasp 同步受保护备份到 Zidoo |

### iStoreOS — 网络与 IPTV（192.168.3.253）

- 家庭旁路由、DNS 与 PassWall2 代理链路。
- HA 主机默认网关/DNS 经 iStoreOS；代理健康应检测真实外网访问，不只检测端口。
- IPTV 代理入口：`http://192.168.3.253:4022`。
- IPTV EPG：`http://192.168.3.253/iptv/epg.xml.gz`。
- APTV 负责直播；Jellyfin 不再加载 IPTV 直播源。

### Zidoo Z10 Pro — 播放与存储（192.168.3.115）

- 外接盘通过 Samba 提供媒体文件；rasp2 同时维护只读和可写挂载。
- Jellyfin 从只读挂载读取 `Movie`；下载管理器向可写挂载写入。
- 新下载内容默认进入 `Movie`，完成后触发 Jellyfin 刷新/元数据处理。
- HA 受保护备份放在隐藏目录 `Movie/.HomeAssistantBackups`，避免进入媒体库。

## 2. 关键链路

### 家庭自动化

`设备/网关 → Home Assistant (rasp) → HomeKit bridges → Apple Home`

- 易来使用 4 个本地 Yeelight Pro 网关。
- Xiaomi Miot 云轮询已放宽，避免云端超时拖垮 HA。
- HomeKit 全部“正在更新”时，先检查 HA API 延迟/CPU，再检查桥端口，不要先重配 Apple Home。

### 本地影视

`夸克/AList → rclone HTTP bridge → 下载管理器 → Zidoo Movie → Jellyfin → Swiftfin/Apple TV`

- Jellyfin 不直接扫描夸克网盘，只扫描 Zidoo 本地文件。
- 4K 播放优先直放；TrueHD/PGS 可能触发转码或字幕烧录，rasp2 不适合重型 4K 软件转码。

### 音乐

`Music Assistant (rasp2) → HomePod/功放/网络播放器`

### HA 备份

`HA 自动加密备份 (rasp) → rasp2 每日同步 → Zidoo .HomeAssistantBackups`

首次同步的 3 份备份已做 SHA-256 一致性校验。Zidoo 不等于真正异地备份，但可防 rasp 系统盘损坏。

## 3. 恢复顺序

1. 网络基础：主路由、iStoreOS、DNS/代理。
2. rasp：Docker → MQTT → Home Assistant → go2rtc → HomeKit bridges。
3. Zidoo Samba 挂载：先确认只读/可写路径均可访问。
4. rasp2：rclone/AList → 夸克 HTTP 桥 → FunHub（含下载模块）→ Jellyfin/Music Assistant。
5. 最后检查 HA 备份同步 timer 与最近一次结果。

## 4. 快速检查

### rasp

```bash
docker ps
curl -fsS http://127.0.0.1:8123/ >/dev/null
curl -fsS http://127.0.0.1:1984/ >/dev/null
ss -ltn | grep -E ':1883|:5678|:8123|:2106[4-8]'
```

### rasp2

```bash
docker ps
systemctl --user --no-pager --type=service --state=running
curl -fsS http://127.0.0.1:8096/System/Info/Public >/dev/null
curl -fsS http://127.0.0.1:8095/ >/dev/null
curl -fsS http://127.0.0.1:8790/ >/dev/null
curl -fsS http://127.0.0.1:8790/downloads/health >/dev/null
systemctl --user status ha-backup-sync.timer
```

## 5. 已知限制与待跟踪项

- Samsung TV 集成存在 UPnP `ui2` 数据类型兼容告警，电视实体可能加载失败。
- 华为 Mesh 路由集成偶发 `auth_general`，应优先重认证而非恢复旧 Ping 节点。
- Yeelight Pro 1.04 仍有未来 HA 版本兼容警告；当前已加色温零值保护，升级集成后需确认补丁是否仍存在。
- 摄像头集中在一个 HomeKit bridge 可用，但 HA 会建议按 accessory 模式拆分；属于后续优化项。
