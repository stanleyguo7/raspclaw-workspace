# ZIDOO Z10 Pro CloudDrive2 挂载

最后验证：2026-09-16（从 `rasp2` 操作）

## 当前架构

```text
Zidoo 海报墙
  -> /storage/emulated/0/mnt/CloudDrive/movie
  -> CloudDrive2 1.0.17（Zidoo root 进程）
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

2026-09-16 将 AList 从 3.58.0 升级到 3.64.0。新版自动把夸克驱动配置迁移到 AdditionVersion 3，启用 3 路分片下载（每片 10 MiB）及新版 Cookie 刷新逻辑。Zidoo 端对同一 4K 文件的连续读取实测约 6.1 MiB/s（约 49 Mbit/s），无 412 错误。

## 为什么由 root 进程启动

Zidoo Android 9 的应用进程 seccomp 会拦截 CloudDrive2 的 `fusermount3`/`umount`，普通应用进程无法建立 FUSE 挂载。当前做法是通过 root ADB 启动 CloudDrive2 core。

Android 9 的 app 可见存储还有独立挂载命名空间，因此服务脚本会把 FUSE 挂载绑定到：

```text
/mnt/runtime/default/emulated/0/mnt/CloudDrive
```

否则 root shell 能看到文件，但 Zidoo 海报墙只会看到空目录。

## rasp2 守护服务

已安装：

| 项目 | 路径/状态 |
| --- | --- |
| 检查脚本 | `/usr/local/sbin/zidoo-clouddrive-ensure` |
| systemd 服务 | `zidoo-clouddrive-ensure.service`（oneshot） |
| systemd 定时器 | `zidoo-clouddrive-ensure.timer`（每 2 分钟） |
| CloudDrive 日志 | Zidoo `/data/local/tmp/clouddrive-root.log` |

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
sudo install -m 0644 \
  configs/rasp2/zidoo-clouddrive/zidoo-clouddrive-ensure.service \
  /etc/systemd/system/zidoo-clouddrive-ensure.service
sudo install -m 0644 \
  configs/rasp2/zidoo-clouddrive/zidoo-clouddrive-ensure.timer \
  /etc/systemd/system/zidoo-clouddrive-ensure.timer
sudo systemctl daemon-reload
sudo systemctl enable --now zidoo-clouddrive-ensure.timer
```

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
