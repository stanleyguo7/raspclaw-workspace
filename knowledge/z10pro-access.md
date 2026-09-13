# ZIDOO Z10 Pro 访问与维护

最后验证：2026-09-13（从 `rasp2` 操作）

## 设备信息

- 地址：`192.168.3.115`
- 型号：ZIDOO Z10 Pro
- Android：9（SDK 28）
- 构建：`thor32-userdebug`，32 位 ARM 用户空间
- CPU：6 核 ARM，最高约 1.3 GHz
- GPU：Mali-G51 / OpenGL ES 3.2
- 内存：标称 2 GB，系统可见约 1.53 GiB
- 闪存：标称 32 GB，`/data` 可用容量约 24 GiB
- 当前显示输出：1920×1080 @ 60 Hz

## 访问入口

| 用途 | 地址/端口 | 身份 | 说明 |
| --- | --- | --- | --- |
| ADB | `192.168.3.115:5555` | Android shell；执行 `adb root` 后为 root | 需要先在电视端开启开发者选项、网络调试，并确认本机 RSA 授权 |
| Termux SSH | `192.168.3.115:8022` | `u0_a76` | 使用 `rasp2` 现有 SSH 公钥；已禁用密码认证 |
| Zidoo 控制服务 | `9528`–`9530` | HTTP/API | 端口可达，供 Zidoo 控制中心使用 |
| 标准 SSH | `22` | — | 未开启；日常使用 Termux 的 `8022` |
| Samba | `//192.168.3.115/Share` | 匿名 | 可见 `Storage` 与 `1ABE6CDDBE6CB345` |

Termux 的 Android 应用 UID 会在卸载重装后变化，因此 `u0_a76` 不是永久值。可用以下命令重新确认：

```bash
adb -s 192.168.3.115:5555 shell dumpsys package com.termux \
  | grep 'userId='
```

例如 `userId=10076` 对应用户名 `u0_a76`。

## 从 rasp2 访问

### ADB 与临时 root

```bash
adb connect 192.168.3.115:5555
adb devices -l
adb -s 192.168.3.115:5555 root
adb -s 192.168.3.115:5555 shell
```

已验证该 `userdebug/test-keys` 固件允许 `adbd` 以 `uid=0(root)` 运行，无需刷入 Magisk，也未修改系统分区。`adb root` 可能在设备重启后失效，届时重新执行即可。

ADB root 只作用于 ADB shell；Termux SSH 仍是 Android 应用用户，不是 root SSH。不要为了方便将 root SSH 暴露到局域网。

### Termux SSH

```bash
ssh -p 8022 u0_a76@192.168.3.115
```

配置使用 `rasp2` 的 `~/.ssh/id_rsa.pub`，私钥不得复制到本仓库或 Z10 Pro。服务端已设置：

```text
PasswordAuthentication no
```

如果端口 `8022` 在设备重启或 Termux 被系统回收后关闭，可通过 ADB 重新启动：

```bash
adb connect 192.168.3.115:5555
adb -s 192.168.3.115:5555 shell run-as com.termux \
  env HOME=/data/data/com.termux/files/home \
      PREFIX=/data/data/com.termux/files/usr \
      PATH=/data/data/com.termux/files/usr/bin:/system/bin \
      TMPDIR=/data/data/com.termux/files/usr/tmp \
      /data/data/com.termux/files/usr/bin/sshd
```

验证端口和密钥登录：

```bash
nc -z -w 2 192.168.3.115 8022
ssh -p 8022 -o BatchMode=yes u0_a76@192.168.3.115 'id; uname -a'
```

### Samba

列出共享并进入 `Share`：

```bash
smbclient -N -L //192.168.3.115
smbclient -N //192.168.3.115/Share
```

检查共享磁盘空间：

```bash
smbclient -N //192.168.3.115/Share -c 'df'
```

## 本次配置过程

1. 在 Z10 Pro 图形界面开启开发者选项和网络 ADB，并在屏幕上允许 `rasp2` 的调试 RSA 指纹。
2. 在 `rasp2` 安装 Android Platform Tools，连接 `192.168.3.115:5555` 并验证设备状态为 `device`。
3. 确认固件允许原生 `adb root`；未刷机、未安装 Magisk。
4. 从 Termux 官方 GitHub Release 下载并安装适配 `armeabi-v7a` 的 Termux 0.118.3。
5. 首次启动 Termux 完成 bootstrap，随后安装 OpenSSH。
6. 将 `rasp2` 的 RSA 公钥写入 Termux 的 `~/.ssh/authorized_keys`，权限分别设为目录 `700`、文件 `600`。
7. 禁用 SSH 密码认证，启动 `sshd`，并从 `rasp2` 对端口 `8022` 做实际回连验证。
8. 检查硬件、内存、存储、网络、显示和运行进程。

安装时使用的官方 APK：

```text
termux-app_v0.118.3+github-debug_armeabi-v7a.apk
SHA-256: 89416397b70f9ff67a0044e8abe6ef82487cd48fcf543e2d23e02688cc541cf0
```

## 2026-09-13 状态快照

- 连续运行约 41 天；CPU 总体约 83% 空闲，负载约 `3.56 / 3.66 / 3.50`。
- 可用内存约 350–500 MiB，约 470 MiB swap 正在使用；Android 曾触发低内存回收。
- 内置 `/data`：24 GiB，已用 10 GiB，剩余 14 GiB（43%）。
- 外接 `1ABE6CDDBE6CB345`：3.6 TiB，已用 2.9 TiB，剩余约 731 GiB（81%）。
- `eth0` 工作正常，局域网 ping 延迟约 1.2 ms，无丢包。
- 存在少量僵尸和不可中断进程，且内核温度接口读取会阻塞。设备空闲时建议做一次正常重启。

## 安全注意事项

- ADB 端口 `5555` 当前在局域网开放，且已允许 root；仅应在可信内网使用。
- 不要提交私钥、`authorized_keys` 内容、账号令牌或 Google 登录信息。
- 不使用来源不明的 root 包；当前固件已有临时 ADB root 能力。
- 排障时先使用只读命令。重启、卸载应用、修改系统文件前应确认设备当前没有播放或磁盘写入任务。
