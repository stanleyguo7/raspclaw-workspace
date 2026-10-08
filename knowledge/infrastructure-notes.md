# Infrastructure Notes

更新时间：2026-10-08（Asia/Shanghai）

更细的局域网设备清单、Zidoo 登录和 CloudDrive2 恢复方式分别维护在：

- [`lan-machines.md`](./lan-machines.md)
- [`z10pro-access.md`](./z10pro-access.md)
- [`z10pro-clouddrive.md`](./z10pro-clouddrive.md)

## 主机与网络角色

- `rasp`：`192.168.3.254`，Home Assistant 与家庭自动化核心。
- `rasp2`：`192.168.3.119`，OpenClaw、家庭娱乐、媒体库与下载任务。
- `iStoreOS`：`192.168.3.253`，旁路由、DNS/代理与 IPTV 列表服务。
- `Zidoo Z10 Pro`：`192.168.3.115`，家庭影院播放器、Samba 媒体盘与 HA 异机备份目标；ADB 为 `192.168.3.115:5555`。
- 主路由：`192.168.3.1`。

## SSH

- rasp：`ssh guosq@192.168.3.254`
- rasp2：当前 OpenClaw 主机，局域网地址 `192.168.3.119`
- iStoreOS：优先使用 `192.168.3.253`
- 阿里云 ECS：`ssh root@aliyun-ecs`；若别名失效，再检查 `~/.ssh/config` 或直连已登记地址。

## 数据与备份约定

- HA 配置：rasp `/home/guosq/homeassistant`
- HA 配置仓库：rasp `/home/guosq/.openclaw/workspace/stanley-ha`
- Jellyfin 配置：rasp2 `/home/guosq/services/jellyfin/config`
- Zidoo 只读媒体挂载：rasp2 `/mnt/z10pro/1ABE6CDDBE6CB345`
- Zidoo 可写挂载：rasp2 `/mnt/z10pro-write/1ABE6CDDBE6CB345`
- HA 加密备份副本：Zidoo `Movie/.HomeAssistantBackups`
- 密钥、令牌和 Cookie 只保存在各主机受保护的 `.secrets`、应用数据或环境文件中，不写入本仓库。

## rasp2 systemd 说明

- `zidoo-clouddrive-ensure.timer` 每 2 分钟检查 Zidoo CloudDrive2 root FUSE 挂载及 Android app 可见绑定；恢复方式见 [`z10pro-clouddrive.md`](./z10pro-clouddrive.md)。
- rasp2 的 Samba 服务已停止并禁用，不监听 137/138/139/445；媒体盘由 Zidoo 提供 Samba，rasp2 只作为客户端挂载。

## 运维入口

- 服务权威清单：`knowledge/service-inventory.md`
- HA 配置版本：GitHub `stanleyguo7/stanley-ha`
- 娱乐中心代码：GitHub `siqiguo/stanley-funhub`
- 本知识库：GitHub `stanleyguo7/raspclaw-workspace`
