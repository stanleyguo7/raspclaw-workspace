# Z10 Pro 轻量下载服务

最后验证：2026-09-14

## 概览

Z10 Pro 的 Termux 中运行 aria2 1.37.0，由 `termux-services`/runit 监管。它支持 HTTP、HTTPS、FTP、BitTorrent、磁力链接和 Metalink，适合在局域网内承担少量下载任务。

- RPC 地址：`http://192.168.3.115:6800/jsonrpc`
- 同时下载数：2
- 单任务连接数：最多 4
- 下载目录：`/storage/1ABE6CDDBE6CB345/Downloads/aria2`
- RPC 认证：随机密钥，密码文件权限为 `600`
- BT 做种：下载完成后停止（`seed-time=0`）
- 断点与任务会话：每 60 秒保存一次
- 服务配置：`~/.config/aria2/aria2.conf`
- 日志：`~/.local/state/aria2/aria2.log`

该服务只提供 JSON-RPC，没有安装公开 Web 管理界面。RPC 端口虽可从局域网访问，但所有调用都需要密钥。

## rasp2 控制工具

仓库内的 `scripts/z10pro-download.py` 是无第三方 Python 依赖的控制工具。RPC 密钥保存在 rasp2 的以下文件中，不进入 Git：

```text
~/.config/z10pro/aria2-rpc.secret
```

进入仓库后使用：

```bash
cd /home/guosq/workspace/raspclaw-workspace
```

检查服务版本：

```bash
./scripts/z10pro-download.py version
```

添加普通下载：

```bash
./scripts/z10pro-download.py add 'https://example.com/file.zip'
```

指定保存文件名：

```bash
./scripts/z10pro-download.py add 'https://example.com/file' --out file.zip
```

添加磁力链接时要保留单引号，避免 `&` 被 shell 解释：

```bash
./scripts/z10pro-download.py add 'magnet:?xt=urn:btih:...'
```

列出正在下载、等待和最近完成的任务：

```bash
./scripts/z10pro-download.py list
```

查看任务完整状态：

```bash
./scripts/z10pro-download.py status GID
```

暂停、恢复和移除任务：

```bash
./scripts/z10pro-download.py pause GID
./scripts/z10pro-download.py resume GID
./scripts/z10pro-download.py remove GID
```

清除已完成或失败任务的历史记录：

```bash
./scripts/z10pro-download.py purge
```

`remove` 只移除任务，不主动删除已经写入磁盘的文件。

## 访问下载文件

从 Samba 访问下载目录：

```text
\\192.168.3.115\Share\1ABE6CDDBE6CB345\Downloads\aria2
```

在 rasp2 上可以使用：

```bash
smbclient -N //192.168.3.115/Share \
  -D 1ABE6CDDBE6CB345/Downloads/aria2
```

也可以通过 Termux SSH 查看：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'ls -lh /storage/1ABE6CDDBE6CB345/Downloads/aria2'
```

## 服务管理

检查 aria2 和 SSH：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'export SVDIR=$PREFIX/var/service; sv status aria2; sv status sshd'
```

重启 aria2：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'export SVDIR=$PREFIX/var/service; sv restart aria2'
```

停止或重新启动：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'export SVDIR=$PREFIX/var/service; sv down aria2'
ssh -p 8022 u0_a76@192.168.3.115 \
  'export SVDIR=$PREFIX/var/service; sv up aria2'
```

查看最近日志：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'tail -100 ~/.local/state/aria2/aria2.log'
```

## 设备重启后的恢复

aria2 和 `sshd` 都已启用 runit 监管。只要 Termux 已启动且其服务管理器在运行，进程异常退出后会自动拉起。

Android 重启后若 `8022` 或 `6800` 尚未开放，可从 rasp2 执行：

```bash
adb connect 192.168.3.115:5555
adb -s 192.168.3.115:5555 shell am start \
  -n com.termux/.app.TermuxActivity
```

等待几秒后验证：

```bash
nc -z -w 2 192.168.3.115 8022
nc -z -w 2 192.168.3.115 6800
```

若 Termux 已运行但服务管理器没有启动，可用 ADB 启动：

```bash
adb -s 192.168.3.115:5555 shell run-as com.termux \
  env HOME=/data/data/com.termux/files/home \
      PREFIX=/data/data/com.termux/files/usr \
      PATH=/data/data/com.termux/files/usr/bin:/system/bin \
      SVDIR=/data/data/com.termux/files/usr/var/service \
      LOGDIR=/data/data/com.termux/files/usr/var/log \
      /data/data/com.termux/files/usr/bin/service-daemon start
```

## 安全和容量

- 不要把 RPC 密钥、SSH 私钥或 `authorized_keys` 内容提交到仓库。
- RPC 只应在可信局域网使用，不要在路由器上转发 `6800`、`5555` 或 `8022` 到公网。
- 外接硬盘在配置时约已使用 81%。大文件下载前先检查空间：

```bash
ssh -p 8022 u0_a76@192.168.3.115 \
  'df -h /storage/1ABE6CDDBE6CB345'
```

- 当前配置只允许两个并发任务，避免给 2 GB 内存和媒体播放造成过大压力。
- 下载来源和内容必须符合当地法律与服务条款。

## 配置验证记录

2026-09-14 已完成以下验证：

- `aria2c` 版本 1.37.0，HTTPS 和 BitTorrent 功能可用。
- `6800` 从 rasp2 可达，缺少正确密钥时无法调用 RPC。
- 通过 RPC 添加 HTTPS 测试任务，文件成功写入外接硬盘。
- 测试任务和测试文件已清理。
- aria2 与 Termux SSH 均处于 runit 的 `run` 状态。
