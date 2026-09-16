# Infrastructure Notes

局域网设备、地址、角色及服务入口统一维护在 [`lan-machines.md`](./lan-machines.md)。

## SSH

- 阿里云 ECS：`ssh root@aliyun-ecs`
- 若连接失败：优先检查 `~/.ssh/config`、DNS/hosts 别名解析
- ZIDOO Z10 Pro：见 [`z10pro-access.md`](./z10pro-access.md)
- ZIDOO CloudDrive2 挂载与 rasp2 守护：见 [`z10pro-clouddrive.md`](./z10pro-clouddrive.md)

## rasp2 systemd 服务

- `zidoo-clouddrive-ensure.timer`：每 2 分钟检查 Zidoo CloudDrive2 root FUSE 挂载及 Android app 可见绑定；恢复脚本与运维说明见 [`z10pro-clouddrive.md`](./z10pro-clouddrive.md)。
- Samba 已于 2026-09-16 停止并禁用，rasp2 不再监听 137/138/139/445。

## RSS 服务（阿里云）

- 项目路径：`/opt/stanley-rss-reader`
- 定时任务：
  - `0 7 * * * /opt/stanley-rss-reader/run_rss_aliyun.sh >> /var/log/stanley-rss-cron.log 2>&1`
- 时区：`Asia/Shanghai`
