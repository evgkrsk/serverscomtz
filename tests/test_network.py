#!/usr/bin/env python3
# -*- mode: python; mode: view -*-
# FIXME: replace this logic with mass-parallel one (fping/nmap?)

from testinfra import get_host
from netaddr import IPNetwork
from sys import exit


def check_net(first, second):
    "Check connectivity and return number of errors occurred"
    errors = 0
    fmt = "ansible://{}?ansible_inventory=inventory/hosts.yaml"
    host1 = get_host(fmt.format(first))
    host2 = get_host(fmt.format(second))
    host1_vars = host1.ansible.get_variables()
    host2_vars = host2.ansible.get_variables()

    print("{} -> {}".format(first, second))

    for dev in host1_vars["addr_addr"]:
        if dev["dev"] != "eth1":
            continue
        for ip in map(lambda x: str(IPNetwork(x).ip), dev["addr"]):
            for remote_dev in host2_vars["addr_addr"]:
                if remote_dev["dev"] != "eth1":
                    continue
                for remote_ip in map(
                    lambda x: str(IPNetwork(x).ip), remote_dev["addr"]
                ):
                    result = host1.run(
                        "ping -4 -q -c 2 -B -w 2 -I {} {}".format(ip, remote_ip)
                    )
                    if not result.succeeded:
                        errors += 1
                    print(
                        "{} -> {} , success: {}".format(ip, remote_ip, result.succeeded)
                    )
    print()
    return errors


errors1 = check_net("vm0", "vm1")
errors2 = check_net("vm1", "vm0")

if errors1 + errors2 > 0:
    exit(1)
