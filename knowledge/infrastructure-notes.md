# Infrastructure Notes

## SSH

- 阿里云 ECS：`ssh root@aliyun-ecs`
- 若连接失败：优先检查 `~/.ssh/config`、DNS/hosts 别名解析

## RSS 服务（阿里云）

- 项目路径：`/opt/stanley-rss-reader`
- 定时任务：
  - `0 7 * * * /opt/stanley-rss-reader/run_rss_aliyun.sh >> /var/log/stanley-rss-cron.log 2>&1`
- 时区：`Asia/Shanghai`
