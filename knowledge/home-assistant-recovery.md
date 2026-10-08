# Home Assistant 故障监控与恢复策略

## 2026-10-09 安全检查与降噪

- HA 核心、HomeKit、4 个 Yeelight 网关、6 个小米网关、13 路 NVR 摄像头及关键安全实体均正常。
- 修复“记录易来灌溉场景请求”的事件模板：兼容 `call_service` 事件缺少 `target` 的情况；实际灌溉时间仍只在右路阀门由 `off` 变为 `on` 后确认写入。
- 移除失效的“书房空调电源状态同步到 HomeKit 开关”自动化及孤立实体注册项；保留书房空调手动控制脚本和按钮。
- 新增“外部数据服务健康”汇总：天气可用且 5 枚米家水浸代表实体中至少 3 枚可用才视为正常。异常连续 15 分钟才通知，恢复连续 10 分钟后通知一次。
- 49 个海康明确不支持的事件实体已标记为用户禁用；13 路摄像头、移动侦测、I/O、NVR 磁盘/录像/IP 冲突状态均保留。
- 烟雾传感器当前未接入；在用户增加设备前不作为巡检提醒项。
- 修改前备份位于 rasp：`/home/guosq/ha-change-backups/20261009-0655-safety-hardening/`。

## 2026-10-06 故障复盘

### 现象

- 二楼主卧窗帘不完全响应，随后大量 Yeelight 实体变为 `unavailable`。
- HA 页面无法打开，Apple Home 全部设备长期显示“正在更新”。
- 恢复 HA 后，主卧北侧卷帘一度从 HomeKit 消失。

### 根因链

1. 二楼 Yeelight Pro 网关网络仍在线，但集成内部因异常数据触发 `ZeroDivisionError`，主循环停止。原有 Ping 检测因此没有报警。
2. Xiaomi Miot 云请求持续超时，轮询任务堆积，将 HA CPU 推高到约 416%，事件循环和 HomeKit 桥接一起失去响应。
3. 临时禁用 Miot 并重启 HA 时，北侧卷帘实体尚未加载，HomeKit 启动阶段没有创建该附件；Miot 恢复后需要重载 HomeKit 才重新出现。

### 已完成修复

- 重载二楼 Yeelight Pro 配置项，主卧窗帘和主要灯光恢复。
- 临时禁用 Xiaomi Miot、校验配置后重启 HA，随后将 Miot 全局轮询周期调整到 300 秒再恢复。
- 重载 HomeKit，主卧北侧智能卷帘重新加入桥接。

## 新监控策略

### HA 内部

- 网络层：路由/AP、Yeelight 网关、小米网关每 5 分钟检测一次。
- 功能层：每个 Yeelight 网关选择 3 个代表实体，至少 2 个可用才视为集成健康。
- 服务层：除 HA、SSH 等已有服务外，增加 HomeKit 主桥 `21064` 与监控桥 `21068`。
- 通知去抖：异常持续 10 分钟才通知，恢复稳定 5 分钟才通知。

### rasp2 外部看门狗

- systemd timer 每 2 分钟运行一次，不依赖 HA 自身调度。
- 连续 3 次失败才执行恢复，所有恢复动作冷却 30 分钟。
- HA API 连续失败：先在 rasp 上运行 HA 配置校验；只有配置有效才重启 `homeassistant` 容器。
- 同一 6 小时窗口最多自动重启 HA 两次。
- Yeelight 网关在线但功能实体连续异常：只重载对应配置项，不重启 HA。
- HomeKit 主桥或监控桥连续缺失且 HA API 正常：只调用 `homekit.reload`。
- 顺义天气连续 3 次为 `unknown`/`unavailable`：只重载天气配置项，30 分钟内不重复操作。
- 不自动禁用 Xiaomi Miot，不自动操作任何灯、窗帘、门锁或其他物理设备。

## 手工检查

```bash
systemctl status ha-watchdog.timer
journalctl -u ha-watchdog.service --since today
python3 /home/guosq/workspace/raspclaw-workspace/scripts/ha-watchdog.py --dry-run
```

HA 主机：

```bash
docker stats --no-stream homeassistant
docker logs --since 30m homeassistant
```

## 回滚

- 停用外部恢复：`sudo systemctl disable --now ha-watchdog.timer`
- HA 配置备份保存在 rasp 的 `/home/guosq/backups/homeassistant/` 对应时间目录。
- 修改前先用 HA 配置检查接口验证；加载新的 `command_line` 传感器需要一次计划内重启。
