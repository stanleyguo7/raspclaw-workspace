# 局域网机器与服务清单

最后核对：2026-09-16

网段：`192.168.3.0/24`

本文是家庭局域网设备地址与访问入口的事实清单。只记录主机名、IP、角色、端口和认证方式，不记录密码、私钥、Cookie、Token 或恢复码。敏感信息应放入加密保险库，参见 [`z10pro-secure-vault.md`](./z10pro-secure-vault.md)。

## 已确认的机器

| 名称 | IP 地址 | 系统/配置 | 主要角色 | 访问方式 |
| --- | --- | --- | --- | --- |
| `rasp2` | `192.168.3.119`（有线） | ARM64、4 核、8 GB RAM、32 GB 系统盘 | OpenClaw、AList、rclone、Music Assistant、Zidoo CloudDrive2 挂载守护、自动化与运维节点 | `ssh guosq@rasp2` 或 `ssh guosq@192.168.3.119` |
| `rasp` | `192.168.3.254`（有线，优先）、`192.168.3.150`（Wi-Fi） | ARM64、4 核、4 GB RAM、32 GB 系统盘 | Home Assistant、Docker 服务 | `ssh guosq@rasp` 或 `ssh guosq@192.168.3.254` |
| `istoreos` | `192.168.3.253` | GL.iNet GL-MT3000、ARM64、约 512 MB RAM、iStoreOS 21.02.4 | 旁路由 | 从 rasp2 执行 `ssh root@192.168.3.253`，已配置公钥认证 |
| `z10pro` | `192.168.3.115` | ZIDOO Z10 Pro、Android 9、6 核、2 GB RAM、32 GB 闪存 | 本地影音、外接硬盘、Samba、aria2 下载 | ADB root、Termux SSH、Samba；详见 [`z10pro-access.md`](./z10pro-access.md) |

### 地址说明

- `rasp` 的 `.254` 与 `.150` 拥有相同设备 MAC，是同一台机器的有线和 Wi-Fi 接口，不是两台 Home Assistant。
- 访问 `rasp` 和 Home Assistant 时优先使用有线地址 `192.168.3.254`。
- `rasp2` 的有线 MAC：`2c:cf:67:54:4f:7d`。
- `rasp` 的设备 MAC：`2c:cf:67:ae:e3:ba`。
- `istoreos` 的 MAC：`94:83:c4:64:9c:b5`。
- `z10pro` 的 MAC：`80:0a:80:55:6a:00`。

## 服务入口

| 服务 | 地址 | 所在机器 | 说明 |
| --- | --- | --- | --- |
| Home Assistant | `http://192.168.3.254:8123` | `rasp` | 有线主入口；`.150:8123` 是同机 Wi-Fi 地址 |
| AList Web | `http://192.168.3.119:5244` | `rasp2` | AList 管理与文件入口 |
| AList WebDAV | `http://192.168.3.119:5244/dav` | `rasp2` | Apple TV/Infuse 等客户端使用；需要 AList 账号 |
| Zidoo CloudDrive2 挂载守护 | `zidoo-clouddrive-ensure.timer` | `rasp2` | 每 2 分钟检查 Zidoo root FUSE 挂载；不开放新端口 |
| Z10 Pro ADB | `192.168.3.115:5555` | `z10pro` | 已授权后可执行 `adb root`；只在可信内网使用 |
| Z10 Pro Termux SSH | `192.168.3.115:8022` | `z10pro` | 用户 `u0_a76`，仅密钥认证 |
| Z10 Pro aria2 RPC | `http://192.168.3.115:6800/jsonrpc` | `z10pro` | 需要 RPC 密钥；详见 [`z10pro-download-service.md`](./z10pro-download-service.md) |
| Z10 Pro Samba | `//192.168.3.115/Share` | `z10pro` | 当前允许匿名访问，包含内置存储与外接硬盘 |
| Zidoo 控制服务 | `192.168.3.115:9528`–`9530` | `z10pro` | Zidoo 控制中心接口 |
| iStoreOS 管理页面 | `http://192.168.3.253` / `https://192.168.3.253` | `istoreos` | 管理凭据不写入本文 |

## SSH 与命令入口

### rasp2

```bash
ssh guosq@rasp2
```

### rasp / Home Assistant 主机

```bash
ssh guosq@rasp
```

若主机名无法解析：

```bash
ssh guosq@192.168.3.254
```

### iStoreOS 旁路由

```bash
ssh root@192.168.3.253
```

2026-09-15 已通过 `rasp2 → rasp → istoreos` 的现有信任链，将 rasp2 的 `~/.ssh/id_rsa.pub` 加入 iStoreOS。现已验证 rasp2 可直接以 root 公钥登录；私钥没有离开 rasp2，也没有写入仓库。

设备信息：

- 型号：GL.iNet GL-MT3000
- 架构：MediaTek MT7981 / ARM64 Cortex-A53
- 系统：iStoreOS 21.02.4，revision `2024101112`
- 内核：Linux 5.4.211

### Z10 Pro

普通 Termux 环境：

```bash
ssh -p 8022 u0_a76@192.168.3.115
```

Android root 环境：

```bash
adb connect 192.168.3.115:5555
adb -s 192.168.3.115:5555 root
adb -s 192.168.3.115:5555 shell
```

## 已知但 IP 尚未确认的设备

| 设备 | 当前用途 | 获取 IP 的建议 |
| --- | --- | --- |
| Apple TV | Apple Home 家庭中枢、Infuse、海外流媒体、AirPlay | Apple TV 的“设置 → 网络”，或 Home Assistant/路由器客户端列表 |
| 三星 The Frame 画壁电视 | 客厅显示与艺术模式 | “设置 → 支持 → 关于本电视/网络状态” |
| ART MASTER Murals | 壁画歌词音箱、相册与氛围显示 | Art OS 的“设置 → 网络 → 当前网络” |
| 极米 H3 | 投影播放设备 | 极米网络设置或路由器客户端列表 |

确认这些设备的 IP 后，应补充：设备名、接口类型、MAC、固定地址方式、可访问服务和最后验证日期。

## 当前资源提醒

- `rasp2`：系统盘约 29 GB，已使用约 62%，当前负载较低。
- `rasp`：系统盘约 29 GB，已使用约 88%，应优先清理或迁移 Docker 日志、镜像及缓存。
- `z10pro`：外接硬盘约 3.6 TiB，已使用约 81%；Android 内存较小，不适合承载核心基础设施。
- `istoreos`：承担旁路由职责，新增服务时应避免影响 DNS、代理和网络转发。其 `/overlay` 约 125 MB，已使用约 92%，新增插件前应先清理或扩容。

## 已停用服务

- `rasp2` Samba：2026-09-16 已停止并禁用 `smbd`、`nmbd`、`winbind`、`samba-ad-dc`，不再监听 UDP 137/138 或 TCP 139/445。

## 维护约定

1. 重要设备在 DHCP 中绑定固定地址，避免客户端配置失效。
2. 机器新增、退役、换 IP 或改变角色时更新本文，并修改“最后核对”日期。
3. 同一机器存在有线和 Wi-Fi 地址时明确标注，服务入口优先使用有线地址。
4. 新服务记录协议、端口、所在机器和用途；认证材料只记录存放位置，不记录内容。
5. 不将 SSH 私钥、密码、AList/夸克凭据、Home Assistant Token 或 Apple 账户信息提交到 Git。
6. 每次修改后执行敏感信息检查，再提交并推送到 GitHub。
