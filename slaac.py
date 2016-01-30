#!/usr/bin/env python3
"""
I wrote this while trying to fiddle around with a very
hacked together IPv6 setup in a research lab.

given an interface and an IPv4 address, the script will check to see
if the host is Pingable over it's statelss link-local v6 address

Interface is required under the assumptions that v6 routes are not setup,
and thus scapy may have l2 issues

This works because IPv6 SLAAC uses the host's MAC addr to generate a scope-local
address, so all we need is l2 info from a ping or other packet.

RFC's of note:
    4291
    2373


REQUIRES:
    Python 3's scapy fork (scapy-python3 in pip)

USAGE: 
    # ./slaac.py [ipv4 address] [interface for ipv6]
"""
import os
import sys
from scapy.all import srp, Ether, IP, ICMP, IPv6, ICMPv6EchoRequest
print("-----")


def generateLinkLocal(mac):
    """
    This works in two steps:
    ---Make a EUI-64 ID
    ---Turn that into a link-local address
    RFC 2373 defines how to create a EUI-64 ID for a 48-bit mac
    """

    #mac = "3c:a9:f4:b8:26:c0"
    UL_bitflip_mask = 0b00000010
    new_UL_bit = hex(bytes.fromhex(mac[0:2])[0] ^ UL_bitflip_mask)[2:]
    #make a link-local address

    IPv6_addr = "fe80::"+new_UL_bit+mac[3:5]+":"+mac[6:8]+"ff:fe"+mac[9:11]+":"+mac[12:14]+mac[15:17]
    return IPv6_addr


if os.geteuid() != 0:
    print("Root needed")
    exit(1)

if len(sys.argv) < 3:
    print("Missing argument. Usage:")
    print(" #prb46 [ipv4 address] [ipv6 interface]")
    exit(1)

target = sys.argv[1]
iface6 = sys.argv[2]
print("pinging {0}".format(target))
#send ping to addr
ans, unans = srp(Ether()/IP(dst=target)/ICMP(), timeout=4, iface_hint=target, verbose=0)

if len(ans) == 0:
    print("No Response from host")
    exit(1)

mac = ans[0][1].src
IPv6_tgt = generateLinkLocal(mac)
src_mac = ans[0][0].src
src_IPv6 = generateLinkLocal(src_mac)
print("Remote Mac: {0}".format(mac))
print("Remote IPv6 Scope Local Addr: {0}".format(IPv6_tgt))
print("Local IPv6/Mac: {0}, {1}".format(src_IPv6, src_mac))
#This is meant for situations in which IPv6 setup is not 100%, so we
#might want to assign an interface ourselves
ans6, unans6 = srp(Ether(dst=mac, src=src_mac)/IPv6(dst=IPv6_tgt, src=src_IPv6)/ICMPv6EchoRequest(), 
        iface=iface6, timeout=4, verbose=0)

if len(ans6) == 0:
    print("Host could not be reached on IPv6")
    exit(1)

for packet6 in ans6[0]:
    print(packet6.summary())
    print("---From: {0}".format(packet6.payload.src))

