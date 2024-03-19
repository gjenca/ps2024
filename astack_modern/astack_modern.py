#!/usr/bin/env python3

import socket
import multiprocessing
import logging

class BadRequest(Exception):

    pass

class ConnectionClosed(Exception):

    pass



logging.basicConfig(level=logging.DEBUG)

class Request:

    def __init__(self,f):
        
        lines=[]
        while True:
            line=f.readline()
            line=line.decode('utf-8')
            if line=='':
                raise ConnectionClosed
            if line=='\n':
                break
            line=line.rstrip()
            logging.debug(f'Client sent {line}')
            lines.append(line)
        if not lines: # nic neposlal
            raise BadRequest
        self.method=lines[0]
        try:
            self.content=[int(line) for line in lines[1:]]
        except ValueError: 
            raise BadRequest

        
        

def handle_client(client_socket,addr):

    stack=[]

    logging.info(f'handle_client {addr} start')
    f=client_socket.makefile('rwb')
    while True:
        try:
            req=Request(f)
            logging.info(f'Request: {req.method} {req.content}')
        except BadRequest:
            logging.info('Bad request',addr)
            break 
        except ConnectionClosed:
            logging.info('Connection closed',addr)
    logging.info(f'handle_client {addr} stop')

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
s.listen(5)

while True:

    cs,addr=s.accept()
    process=multiprocessing.Process(target=handle_client,args=(cs,addr))
    process.daemon=True
    process.start()
    cs.close()



