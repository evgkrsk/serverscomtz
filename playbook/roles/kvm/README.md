# -*- mode: yaml; mode: view -*-
# kvm

Роль для конфигурации хоста qemu-kvm на debian/ubuntu.

### Что она делает

* Настраивает ноду как хост виртуальных машин
* Создаёт пулы хранения
* Скачивает по заданной пользователем ссылке образы-шаблоны виртуальных машин
* Вносит в них изменения посредством `virt-sysprep` (сейчас поддерживается лишь centos7)
  * Включает serial console с автологином **root** (для использования через `virsh console`)
  * Устанавливает hostname (опционально)
  * Конфигурирует сетевые интерфейсы (опционально)
  * Задаёт пароль **root** (опционально)
  * Интегрирует в образ публичный ключ (опционально)
* Создаёт виртуальные машины с заданными параметрами в заданном пуле
  * Поддерживается только сеть типа *linux bridge*
* Управляет состоянием виртуальных машин (вкл/выкл)
* Удаляет виртуальные машины с их дисками
* Удаляет пулы хранения

### Чего оно не делает

* Не изменяет параметры уже созданных виртуальных машин

## Структура переменных

```yaml
kvm_accept_existing_disks: bool # (default: false) Не фейлиться, если диск для ВМ уже существует
kvm_leave_hostname: bool # (default: false) Не устанавливать sysprep'ом hostname
kvm_pool:                # Задаёт storage pool
- name: string # Имя пула; при типе logical должно совпадать с именем VG
  type: string # Тип пула (logical|dir)
  path: string # Путь к пулу (/dev/vgname в случае "logical", и /file/system/path в случае "dir")
  state: string                 # Состояние пула (active|absent)

kvm_sysprep_root_key: string # Ключ SSH, который можно интегрировать суперпользователю в ВМ
kvm_template_default: string # Имя образа-шаблона по-умолчанию, берётся версия сжатая xz
kvm_templates_uri: string    # URI, откуда скачивать шаблоны

kvm_vm:
- name: string       # (ОБЯЗАТЕЛЬНО) Имя ВМ
  pool_name: string  # (ОБЯЗАТЕЛЬНО) Используемый пул хранения
  template_name: string # (default: kvm_template_default) Имя образа-шаблона
  cpu_count: int        # (default: 1) Кол-во виртуальных ЦПУ
  cpu_custom: bool # (default: false) не использовать атрибут host-model для описания гостевого ЦПУ
  disk_bus: string # (default: virtio) шина виртуального хранилища (virtio|ide|scsi|sata|usb)
  disk_format: string    # (default: raw) Формат образа ВМ (raw|qcow2)
  disk_gb: int  # (default: 16) Объём образа ВМ, ГБ (16 ГБ или больше)
  memory_mb: int                # (default: 1024) Объём RAM, МБ
  state: string # (default: running) Состояние ВМ (running|shutdown|destroyed|paused|undefined); undefined полностью удаляет ВМ с первым диском
  sysprep_domain: string # (default: from ansible_nodename) Доменное имя для sysprep
  sysprep_hostname: string     # (default: name) Имя хоста для sysprep
  sysprep_ifcfg:               # Конфигурация интерфейсов.
    - dev: string              # Имя интерфейса (например, eth0)
      nic_bridge: string # (ОБЯЗАТЕЛЬНО) Мост на хосте, в который включается ВМ
      nic_model: string # (default: virtio) модель виртуальной сетевой карты (virtio|e1000|rtl8139)
      bootproto: string # (default: "none") Протокол загрузки (none|dhcp)
      address: CIDR     # IP-адрес (для static)
      gateway: ipv4     # Шлюз по-умолчанию
  sysprep_root_pass: string     # Пароль root

```
Все элементы словарей в списке `kvm_vm` (кроме `name` и `state`) читаются только при создании ВМ.

## Пример
#### Типовая кофигурация сервера с внутренней приватной сетью и виртуальной машиной за NAT, образ на LVM

```yaml
  roles:
    - bridge
    - kvm

bridge_devices:
  - dev: br1
    address: 192.168.100.1/24
    ports: []

kvm_template_default: CentOS-7-x86_64-GenericCloud.qcow2

kvm_pool:
  - name: images
    type: dir
    path: /var/lib/libvirt/images

  - name: main
    type: logical
    path: /dev/main

kvm_vm:
  - name: example.com
    memory_mb: 2048
    pool_name: main
    disk_gb: 40
    cpu_count: 2
    sysprep_ifcfg:
      - dev: eth0
        nic_bridge: br1
        address: 192.168.100.10/24
        gateway: 192.168.100.1
```

## Зависимости
bridge
