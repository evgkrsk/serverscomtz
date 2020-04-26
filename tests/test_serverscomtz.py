#!/usr/bin/evg python3
# -*- mode: python; mode: view -*-

from netaddr import IPNetwork


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
        for dev in ansible_vars["tunnel_devices"]:
            peer = str(IPNetwork(dev["peer"]).ip)
            assert peer
            show_tunnels = host.check_output("ip l2tp show tunnel")
            if "id" in dev:
                id = dev["id"]
            else:
                id = "1"
            assert "to {}".format(peer) in show_tunnels
            assert "Tunnel {},".format(id) in show_tunnels
