# -*- mode: yaml; mode: view -*-
# addr

*ВНИМАНИЕ! При некорректной конфигурации сетевых адресов вы можете потерять управление сервером.*

Роль для добавления произвольного списка IP-адресов на сетевые интерфейсы (пока поддерживаются лишь IPv4). Все изменения делаются лишь в памяти, без сохранения на диск.

## Структура данных

```yaml
addr_addr:
- dev: string                   # ОБЯЗАТЕЛЬНОЕ имя сетевого интерфейса
  exclusive: bool               # default: True - должны ли на интерфейсы быть ТОЛЬКО указанные адреса
  addr:                         # list
  - CIDR                        # адрес в CIDR-нотации
```
