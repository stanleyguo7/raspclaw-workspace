# 石头扫地机器人清单

最后核对：2026-09-24

本文记录 Home Assistant 中已接入的石头扫地机器人、局域网地址、所在位置和控制实体。只记录设备信息，不记录 Roborock 账号、Token、设备密钥或其他认证材料。

## 设备与位置

| IP 地址 | 设备名称 | 型号 | 所处位置/负责区域 | Home Assistant 实体 | 2026-09-24 状态 |
| --- | --- | --- | --- | --- | --- |
| `192.168.3.51` | G30S Pro（B1） | `roborock.vacuum.a278` | 地下室洗衣房；负责 B1 | `vacuum.g30s_pro_b1` | 在线；在充电座 |
| `192.168.3.57` | G30S Pro（一楼） | `roborock.vacuum.a278` | 一楼 | `vacuum.g30s_pro_yi_lou` | 在线；在充电座 |
| `192.168.3.62` | P20 Ultra Plus（公区儿童房2楼） | `roborock.vacuum.a225` | 二楼公区、儿童房 | `vacuum.p20_ultra_plus_er_ceng_gong_qu` | 在线；在充电座 |
| `192.168.3.63` | P20 Ultra Plus（主卧2楼） | `roborock.vacuum.a225` | 二楼主卧 | `vacuum.p20_ultra_plus_er_lou_zhu_wo` | 在线；在充电座 |

IP 来自 Roborock 集成返回的设备网络信息，并通过 Home Assistant 主机的局域网邻居表核对。地址可能随 DHCP 变化；自动化优先使用稳定的 Home Assistant 实体 ID。

## 自然语言路由

后续收到清扫指令时，按以下规则选择机器人：

| 用户表达 | 目标实体 |
| --- | --- |
| 地下室、B1、洗衣房 | `vacuum.g30s_pro_b1` |
| 一楼 | `vacuum.g30s_pro_yi_lou` |
| 二楼公区、儿童房 | `vacuum.p20_ultra_plus_er_ceng_gong_qu` |
| 二楼主卧、主卧 | `vacuum.p20_ultra_plus_er_lou_zhu_wo` |

若用户只说“二楼”而未说明公区还是主卧，不应同时启动两台机器人；先确认目标区域。若用户明确说“二楼全部”，可同时启动两台二楼机器人。

## Home Assistant 调用

整机全屋清扫使用标准 Vacuum 服务：

```yaml
action: vacuum.start
target:
  entity_id: vacuum.g30s_pro_yi_lou
```

暂停、继续和返回充电座分别使用：

```text
vacuum.pause
vacuum.start
vacuum.return_to_base
```

设备还提供地图、当前房间、清扫状态、电量/耗材、拖布模式和勿扰模式等实体。各机器也有预设清扫按钮，例如“全屋清洁”“先扫后拖”“精细慢拖”和“强力扫地”。执行用户未明确要求的强力模式、拖地模式或跨区域清扫前，应先确认。

## 调用约定

1. 启动前读取目标 vacuum 实体状态；若为 `unavailable`，不要下发命令，并报告设备离线。
2. 清扫属于会驱动物理设备的操作。用户明确要求“清扫/打扫”即视为本次启动授权；仅询问状态或能力时不得启动。
3. 用户指定楼层或区域时只调用对应实体。目标含糊时先确认，避免启动错误楼层的机器人。
4. 返回充电座、暂停或继续时，优先沿用当前正在工作的机器人；多台同时工作时需明确目标。
5. IP、设备名称、位置或实体 ID 变化后，更新本文的核对日期和映射。
