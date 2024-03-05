#!/usr/bin/env python3
import socket
import sys
import os

s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server=sys.argv[1]
nick=sys.argv[2]

greeting_msg=f'MYNICK:{nick}'
addr_port_server=(server,9999)
s.sendto(greeting_msg.encode('utf-8'),addr_port_server)
if os.fork():
    # Parent: caka, ci server neposle SAYS: spravu
    while True:
        data,addr=s.recvfrom(1024)
        if addr!=addr_port_server:
            continue
        msg=data.decode('utf-8')
        if msg.startswith('SAYS:'):
            print(msg[5:])
else:
    while True:
        line=input('> ')
        line=line.rstrip()
        msg=f'ISAY:{line}'
        s.sendto(msg.encode('utf-8'),addr_port_server)



