#!/usr/bin/env python3
import socket


clients={}

bind_addr=("",9999)
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(bind_addr)
while True:
    data_b,client_addr=s.recvfrom(1024)
    data=data_b.decode('utf-8')
    data=data.rstrip()
    data_splitted=data.split(':')
    if len(data_splitted)<2:
        continue
    request_type=data_splitted[0]
    print(data_splitted)
    if request_type=='MYNICK':
        clients[client_addr]=data_splitted[1] # ulozi si nick
    elif request_type=="ISAY":
        if client_addr not in clients:
            continue
        nick=clients[client_addr]
        what=":".join(data_splitted[1:])
        msg_b=f'SAYS:{nick}:{what}'.encode('utf-8')
        for addr in clients:
            if addr!=client_addr:
                s.sendto(msg_b,addr)
    else:
        print(f'Unknown request type:{request_type}')

                
                




