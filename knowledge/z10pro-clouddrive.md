# ZIDOO Z10 Pro CloudDrive2 挂载

最后验证：2026-09-17（从 `rasp2` 操作）

## 当前架构

```text
Zidoo 海报墙
  -> /storage/emulated/0/mnt/CloudDrive/movie
  -> CloudDrive2 1.0.18（Zidoo root 进程）
  -> AList WebDAV（rasp2:5244/dav）
  -> AList 3.64.0 原生代理
  -> 夸克 CDN
```

- AList 地址：`http://192.168.3.119:5244`
- WebDAV 地址：`http://192.168.3.119:5244/dav`
- CloudDrive2 挂载：`/storage/emulated/0/mnt/CloudDrive`
- 海报墙来源：`storage://mnt/CloudDrive/movie`
- AList 夸克 WebDAV 策略：`native_proxy`
- AList 使用专用只读 WebDAV 账号，基本路径为 `/pan/quark`；凭据不得写入仓库。

目录枚举、鉴权和影片数据均经过 `rasp2`。夸克原始下载链接要求同时携带与签名匹配的 Cookie、Referer 和 User-Agent；WebDAV 的 HTTP 302 无法把这些请求头交给 CloudDrive2。实测 302 模式下 CloudDrive2 取得直链后，夸克 CDN 返回 `412 Precondition Failed`，表现为“能看到文件但无法播放”，因此改用 AList 原生代理。

2026-09-16 将 AList 从 3.58.0 升级到 3.64.0。新版自动把夸克驱动配置迁移到 AdditionVersion 3，启用 3 路分片下载（每片 10 MiB）及新版 Cookie 刷新逻辑。曾对一个连续读取样本测到约 6.1 MiB/s，但这不能代表播放器的随机 Range 读取；见下方“已知限制”。

2026-09-17 从 CloudDrive2 官网所列 GitHub Release 下载 Android 核心服务 APK，卸载 1.0.17 后干净安装 1.0.18（versionCode 226）。官方 APK 的 SHA-256 为 `519267ecbb593f59842dfdf544d6ff4bf3bba3c7bc559f7f6ce38ad37c62865b`。重装前的完整应用数据备份保存在 rasp2 的受限备份目录中，不进入 Git 仓库；恢复时只还原账号、挂载和服务配置，保留 1.0.18 新安装的程序二进制与 Web 资源。

## 为什么由 root 进程启动

Zidoo Android 9 的应用进程 seccomp 会拦截 CloudDrive2 的 `fusermount3`/`umount`，普通应用进程无法建立 FUSE 挂载。当前做法是通过 root ADB 启动 CloudDrive2 core。

Android 9 的 app 可见存储还有独立挂载命名空间，因此服务脚本会把 FUSE 挂载绑定到：

```text
/mnt/runtime/default/emulated/0/mnt/CloudDrive
```

否则 root shell 能看到文件，但 Zidoo 海报墙只会看到空目录。

Zidoo 原生 `DvdPlayer` 的 SELinux 域默认也不允许访问 `fuse:s0`。守护脚本使用官方 Magisk `magiskpolicy`，只追加读取 FUSE 目录/文件所需的最小规则，SELinux 仍保持 `Enforcing`。规则只加载到当前内核，重启后由守护脚本按 boot ID 重新加载。

## rasp2 守护服务

已安装：

| 项目 | 路径/状态 |
| --- | --- |
| 检查脚本 | `/usr/local/sbin/zidoo-clouddrive-ensure` |
| systemd 服务 | `zidoo-clouddrive-ensure.service`（oneshot） |
| systemd 定时器 | `zidoo-clouddrive-ensure.timer`（每 2 分钟） |
| CloudDrive 日志 | Zidoo `/data/local/tmp/clouddrive-root.log` |
| SELinux 规则工具 | `/usr/local/lib/zidoo-clouddrive/magiskpolicy-armv7` |

仓库内的可恢复副本位于 [`../configs/rasp2/zidoo-clouddrive/`](../configs/rasp2/zidoo-clouddrive/)。

### 状态检查

```bash
systemctl status zidoo-clouddrive-ensure.timer
systemctl list-timers zidoo-clouddrive-ensure.timer
sudo systemctl start zidoo-clouddrive-ensure.service
```

检查 Zidoo 挂载：

```bash
adb connect 192.168.3.115:5555
adb shell 'mount | grep CloudDrive'
adb shell 'ls /mnt/runtime/default/emulated/0/mnt/CloudDrive/movie | head'
```

### 安装/恢复

```bash
sudo install -m 0755 \
  configs/rasp2/zidoo-clouddrive/zidoo-clouddrive-ensure.sh \
  /usr/local/sbin/zidoo-clouddrive-ensure
sudo install -d -m 0755 /usr/local/lib/zidoo-clouddrive
sudo install -m 0755 \
  configs/rasp2/zidoo-clouddrive/magiskpolicy-armv7 \
  /usr/local/lib/zidoo-clouddrive/magiskpolicy-armv7
sudo install -m 0644 \
  configs/rasp2/zidoo-clouddrive/zidoo-clouddrive-ensure.service \
  /etc/systemd/system/zidoo-clouddrive-ensure.service
sudo install -m 0644 \
  configs/rasp2/zidoo-clouddrive/zidoo-clouddrive-ensure.timer \
  /etc/systemd/system/zidoo-clouddrive-ensure.timer
sudo systemctl daemon-reload
sudo systemctl enable --now zidoo-clouddrive-ensure.timer
```

仓库中的 `magiskpolicy-armv7` 取自 Magisk v30.7 官方 APK，SHA-256：`e5fafc1fa9486950ce9ba476f5723754d260014515ced72b4560238e6c560f3a`。

### 停用/回滚

```bash
sudo systemctl disable --now zidoo-clouddrive-ensure.timer
```

如需彻底停用，再到 Zidoo 停止 root CloudDrive2 进程并卸载挂载；不要在影片播放或海报墙扫描期间强制卸载。

## 当前缓存参数

- 下载线程：2
- 最小读取块：512 KiB
- 默认预读：2 MiB
- 内存缓冲池：128 MiB
- 目录缓存 TTL：40 秒，不持久化
- 文件磁盘缓存容量上限：512 MiB
- 没有启用任何文件夹磁盘缓存规则；最后检查时实际占用为 0

这意味着当前主要依赖 CloudDrive2 内存预读和 AList 分片代理，不会像旧 rclone 方案一样在 `rasp2` 使用大容量文件缓存。

## 夸克视频播放验证与限制

当前配置已经解决两类 Zidoo 本地问题：

1. 海报墙/图库看不到 CloudDrive 的 Android 挂载命名空间；
2. `DvdPlayer` 被 SELinux 拒绝遍历 FUSE，误报“不支持格式”。

1.0.17 阶段，原生播放器对 MP4/MKV 的随机 Range 请求曾触发 AList/夸克链路 `416`、`context canceled` 或 CloudDrive2 `file corrupted`；37 GB 4K DV MKV 的夸克转码接口也曾返回 `plf_invalid`。

2026-09-17 干净安装官方 CloudDrive2 1.0.18 后，使用 Zidoo 原生播放器实测同一条 4K DV/HDR MKV：播放器成功识别 H.265 3840×2076、HDR、Dolby Digital Plus 5.1，播放时间从 0 连续推进到 27 秒，未再出现“不支持格式”、FUSE SELinux 拒绝或启动阶段的 `416`。这证明该文件目前可以经 CloudDrive2 + AList 原生代理播放，但短时验证不能保证长片全程和所有夸克节点始终无卡顿。

因此：

- CloudDrive2 1.0.18 已通过目录浏览、海报墙和 4K DV/HDR 短时原生播放验证，可继续作为当前海报墙来源；
- 若长片仍出现卡顿、`416` 或 `file corrupted`，优先使用夸克 TV 客户端调用外部播放器，或先下载/缓存到本地磁盘；
- 不要把一次 27 秒实播等同于所有影片、所有时段均稳定，上游 CDN、账号限速和随机 Range 行为仍可能变化。

## 海报墙与旧 SMB 状态

- 2026-09-16 已从海报墙删除旧的 `smb://192.168.3.119/quark/movie` 与 `show` 来源。
- 当前保留本地 USB 来源和 `storage://mnt/CloudDrive/movie`。
- `rasp2` 的 `smbd`、`nmbd`、`winbind`、`samba-ad-dc` 已停止并禁用；UDP 137/138 与 TCP 139/445 均不监听。

恢复 Samba（仅在确有需要时）：

```bash
sudo systemctl enable --now smbd nmbd winbind
```

## 安全注意事项

- 不提交 AList 密码、夸克 Cookie、CloudDrive2 数据库或 token。
- CloudDrive2 挂载为只读，避免播放器或海报墙误改网盘内容。
- Zidoo ADB root 仅在可信局域网使用。
- 不要把夸克 WebDAV 策略改回 `302_redirect`；CloudDrive2 无法携带夸克直链所需的 Cookie、Referer 和 User-Agent，请保持 `native_proxy`。
