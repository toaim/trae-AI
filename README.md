# TCC 事务管理示例

这是一个轻量级的 TCC（Try-Confirm-Cancel）事务管理示例实现，适用于在单体或服务编排层面模拟/实现事务协调。

## 特性

- 统一的事务记录与状态机（pending/trying/confirmed/canceled/failed）
- 支持多参与者的 Try/Confirm/Cancel 回调
- 失败自动触发 Cancel
- 内置内存存储（可替换）

## 安装与使用

```python
from tcc import Participant, TCCManager

inventory = Participant(
    name="inventory",
    try_action=lambda payload: payload.setdefault("reserved", True),
    confirm_action=lambda payload: payload.update({"inventory_confirmed": True}),
    cancel_action=lambda payload: payload.update({"inventory_canceled": True}),
)

wallet = Participant(
    name="wallet",
    try_action=lambda payload: payload.setdefault("frozen", True),
    confirm_action=lambda payload: payload.update({"wallet_confirmed": True}),
    cancel_action=lambda payload: payload.update({"wallet_canceled": True}),
)

manager = TCCManager()
record = manager.begin("txn-001", [inventory, wallet], payload={"order_id": "123"})
manager.try_all(record.transaction_id)
manager.confirm(record.transaction_id)
```

## 扩展建议

- 将 `TCCStore` 替换为数据库/缓存实现，以持久化事务状态。
- 为每个参与者实现幂等控制与重试机制。
- 在 Confirm/Cancel 阶段加入超时与补偿策略。
