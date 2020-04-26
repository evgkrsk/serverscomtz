#!/usr/bin/evg python3
# -*- mode: python; mode: view -*-

from netaddr import IPNetwork
from re import search


def test_bridge_role(host):
    ansible_vars = host.ansible.get_variables()
    if "bridge_devices" in ansible_vars:
        for dev in ansible_vars["bridge_devices"]:
            assert host.interface(dev["dev"]).exists
            for port in dev["ports"]:
                assert host.interface(port).exists
            if "address" in dev:
                assert (
                    str(IPNetwork(dev["address"]).ip)
                    in host.interface(dev["dev"]).addresses
                )


def test_tunnel_role(host):
    ansible_vars = host.ansible.get_variables()
    if "tunnel_devices" in ansible_vars:
        show_tunnels = host.check_output("ip l2tp show tunnel")
        for dev in ansible_vars["tunnel_devices"]:
            peer = str(IPNetwork(dev["peer"]).ip)
            assert peer
            if "id" in dev:
                id = dev["id"]
            else:
                id = "1"
            assert "to {}".format(peer) in show_tunnels
            assert "Tunnel {},".format(id) in show_tunnels


def test_kvm_role(host):
    ansible_vars = host.ansible.get_variables()
    if "kvm_vm" in ansible_vars:
        virsh_list = host.check_output("virsh list")
        for vm in ansible_vars["kvm_vm"]:
            if "state" in vm:
                state = vm["state"]
            else:
                state = "running"
            if state == "running":
                assert search("{}.+{}".format(vm["name"], state), virsh_list)


def test_addr_role(host):
    ansible_vars = host.ansible.get_variables()
    if "addr_addr" in ansible_vars:
        for addr in ansible_vars["addr_addr"]:
            host_addr = set(
                filter(lambda x: ":" not in x, host.interface(addr["dev"]).addresses)
            )
            addr_addr = set(map(lambda x: str(IPNetwork(x).ip), addr["addr"]))
            if "exclusive" in addr:
                exclusive = addr["exclusive"]
            else:
                exclusive = True
            if exclusive:
                assert addr_addr == host_addr
            else:
                assert addr_addr <= host_addr
