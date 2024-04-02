#!/usr/bin/env python3

import socket
import multiprocessing
import logging

class BadRequest(Exception):

    pass

class ConnectionClosed(Exception):

    pass

STATUS_OK=(100,'OK')
STATUS_REQUEST_CONTENT_EMPTY=(201,'Content empty')
STATUS_NOT_A_NUMBER=(202,'Not a number')
STATUS_BAD_REQUEST=(301,'Bad request')
STATUS_REQUEST_CONTENT_NONEMPTY=(204,'Content nonempty')
STATUS_STACK_TOO_SHORT=(203,'Stack too short')
STATUS_STACK_EMPTY=(205,'Stack empty')



logging.basicConfig(level=logging.DEBUG)

class Request:

    def __init__(self,f):
        
        lines=[]
        while True:
            line=f.readline()
            line=line.decode('utf-8')
            if line=='':
                if not lines:
                    raise ConnectionClosed
                else:
                    logging.error('Klient zavrel spojenie priskoro')
                    raise ConnectionClosed
            if line=='\n':
                break
            line=line.rstrip()
            logging.debug(f'Client sent {line}')
            lines.append(line)
        if not lines: # nic neposlal
            raise BadRequest
        self.method=lines[0]
        self.content=lines[1:]
        
class Response:

    def __init__(self,status,content=[]):

        self.status=status
        self.content=content

    def send(self,f):
        
        f.write(f'{self.status[0]} {self.status[1]}\n'.encode('utf-8'))
        for item in self.content:
            f.write(f'{item}\n'.encode('utf-8'))
        f.write('\n'.encode('utf-8'))
        f.flush()

    def __repr__(self):

        return f'''Response(
            {self.status[0]} {self.status[1]},
            {self.content})'''
        

def method_PUSH(request,stack):

    if not request.content:
        return Response(STATUS_REQUEST_CONTENT_EMPTY)
    if not all(s.isdigit() for s in request.content):
        return Response(STATUS_NOT_A_NUMBER)
    for num_s in request.content:
        stack.append(int(num_s))
    return Response(STATUS_OK)

def method_ADD(request,stack):

    if request.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY)
    if len(stack)<=1:
        return Response(STATUS_STACK_TOO_SHORT)
    n1=stack.pop()
    n2=stack.pop()
    stack.append(n1+n2)
    return Response(STATUS_OK)

def method_MULTIPLY(request,stack):

    if request.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY)
    if len(stack)<=1:
        return Response(STATUS_STACK_TOO_SHORT)
    n1=stack.pop()
    n2=stack.pop()
    stack.append(n1*n2)
    return Response(STATUS_OK)

def method_PEEK(request,stack):

    logging.debug('PEEK zije')
    if request.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY)
    if not stack:
        return Response(STATUS_STACK_EMPTY)
    return Response(STATUS_OK,[stack[-1]])

def method_ZAP(request,stack):

    if request.content:
        return Response(STATUS_REQUEST_CONTENT_NONEMPTY)
    stack[:]=[]
    return Response(STATUS_OK)

METHODS={
    'PUSH':method_PUSH,
    'ADD':method_ADD,
    'MULTIPLY':method_MULTIPLY,
    'PEEK':method_PEEK,
    'ZAP':method_ZAP,
}


def handle_client(client_socket,addr):

    stack=[]

    logging.info(f'handle_client {addr} start')
    f=client_socket.makefile('rwb')
    while True:
        try:
            req=Request(f)
            logging.info(f'Request: {req.method} {req.content}')
        except BadRequest:
            logging.info(f'Bad request {addr}')
            break 
        except ConnectionClosed:
            logging.info(f'Connection closed {addr}')
            break
        if req.method in METHODS:
            response=METHODS[req.method](req,stack)
        else:
            response=Response(STATUS_BAD_REQUEST)
        logging.info(f'{response}')
        response.send(f)
        logging.debug(f'stack: {stack}')
        if response.status==STATUS_BAD_REQUEST:
            break
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



