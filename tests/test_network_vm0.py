#!/usr/bin/evg python3
# -*- mode: python; mode: view -*-
# FIXME: replace this logic with mass-parallel one (fping/nmap?)

from testinfra import get_host
from netaddr import IPNetwork


def test_network_vm0(host):
    ansible_vars = host.ansible.get_variables()
    if ansible_vars["inventory_hostname"] == "vm0":
        vm1 = get_host("ansible://vm1")
        vm1_vars = vm1.ansible.get_variables()
        for dev in ansible_vars["addr_addr"]:
            if dev["dev"] != "eth1":
                continue
            for ip in map(lambda x: str(IPNetwork(x).ip), dev["addr"]):
                for remote_dev in vm1_vars["addr_addr"]:
                    if remote_dev["dev"] != "eth1":
                        continue
                    for remote_ip in map(
                        lambda x: str(IPNetwork(x).ip), remote_dev["addr"]
                    ):
                        host.run_test(
                            "ping -4 -q -c 2 -B -w 2 -I {} {}".format(ip, remote_ip)
                        )
