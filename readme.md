# slaac.py
## Use an IPv4 address to see if a host can be pinged over a IPv6 scope-local addr

 I wrote this while trying to fiddle around with a very
 hacked together IPv6 setup in a research lab. It may not be that useful to anyone else.

 Given an interface and an IPv4 address, the script will check to see
 if the host is Pingable over its statelss link-local v6 address
 Interface is required under the assumptions that v6 routes are not setup,
 and thus scapy may have l2 issues

 This works because IPv6 SLAAC uses the host MAC addr to generate a scope-local
 address, so all we need is l2 info from a ping or other packet.
 
 ###RFCs of note:
    4291
    2373


###REQUIRES:
    Python 3 scapy fork (scapy-python3 in pip)
        
###USAGE: 
    # ./slaac.py [ipv4 address] [interface for ipv6]
