# Infrastructure Notes

局域网设备、地址、角色及服务入口统一维护在 [`lan-machines.md`](./lan-machines.md)。

## SSH

- 阿里云 ECS：`ssh root@aliyun-ecs`
- 若连接失败：优先检查 `~/.ssh/config`、DNS/hosts 别名解析
- ZIDOO Z10 Pro：见 [`z10pro-access.md`](./z10pro-access.md)

## RSS 服务（阿里云）

- 项目路径：`/opt/stanley-rss-reader`
- 定时任务：
  - `0 7 * * * /opt/stanley-rss-reader/run_rss_aliyun.sh >> /var/log/stanley-rss-cron.log 2>&1`
- 时区：`Asia/Shanghai`
