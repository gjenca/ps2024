#!/usr/bin/env python3

import socket
import multiprocessing
import logging
import re
import pathlib

DOCUMENT_ROOT='./doc'

MIME_TYPES={
    '.html':'text/html',
    '.txt':'text/plain',
    '.gif':'image/gif',
    '.jpg':'image/jpg',
    '':'application/octet-stream',
}

class BadRequest(Exception):

    pass

class ConnectionClosed(Exception):

    pass

STATUS_OK=(200,'OK')
STATUS_BAD_REQUEST=(400,'Bad request')
STATUS_NOT_FOUND=(404,'Not found')

logging.basicConfig(level=logging.DEBUG)

class Request:

    def __init__(self,f):
        
        lines=[]
        while True:
            line=f.readline()
            line=line.decode('ascii')
            if line=='':
                if not lines:
                    raise ConnectionClosed
                else:
                    logging.error('Klient zavrel spojenie priskoro')
                    raise ConnectionClosed
            if line=='\r\n':
                break
            line=line.rstrip()
            logging.debug(f'Client sent {line}')
            lines.append(line)
        if not lines: # nic neposlal
            raise BadRequest
        m=re.match('^([^ ]+) ([^ ]+) ([^ ]+)$',lines[0])
        if not m:
            raise BadRequest
        self.method=m.group(1)
        self.url=m.group(2)
        self.protocol=m.group(3)
        self.headers={}
        for line in lines[1:]:
            m=re.match('^([^ :]+): (.*)$',line)
            if not m:
                raise BadRequest
            self.headers[m.group(1).lower()]=m.group(2)
    
    def __repr__(self):
        
        return f'Request: {self.method} {self.url} {self.headers}'


class Response:

    def __init__(self,status,headers,content):

        self.status=status
        self.content=content
        self.headers=headers

    def send(self,f):
        
        f.write(f'HTTP/1.1 {self.status[0]} {self.status[1]}\r\n'.encode('ascii'))
        f.write(f'Content-length: {len(self.content)}\r\n'.encode('ascii'))
        for header_name,header_value in self.headers.items():
            f.write(f'{header_name}: {header_value}\r\n'.encode('ascii'))
        f.write('\r\n'.encode('ascii'))
        f.write(self.content)
        f.flush()


    def __repr__(self):

        return f'''Response(
            {self.status[0]} {self.status[1]},
            {self.content})'''

class ErrorResponse(Response):

    def __init__(self,status):
        
        self.status=status
        self.content=f'''
        <html>
        <body>
        <h1>
        {status[0]} {status[1]}
        </h1>
        </body>
        </html>'''.encode('ascii')
        self.headers={'Content-type':'text/html'}
        


def method_GET(request):

    filename=DOCUMENT_ROOT+request.url
    try:
        with open(filename,'rb') as f:
            content=f.read()
    except FileNotFoundError:
        return ErrorResponse(STATUS_NOT_FOUND)
    extension=pathlib.Path(filename).suffix
    mime_type=MIME_TYPES.get(extension,'application/octet-stream')
    logging.info(f'MIME_TYPE:{mime_type}')
    return Response(
        STATUS_OK,
        {'Content-type':mime_type},
        content)


METHODS={
    'GET':method_GET,
}


def handle_client(client_socket,addr):

    logging.info(f'handle_client {addr} start')
    f=client_socket.makefile('rwb')
    while True:
        try:
            req=Request(f)
            logging.info(f'Request: {req}')
        except BadRequest:
            logging.info(f'Bad request {addr}')
            break 
        except ConnectionClosed:
            logging.info(f'Connection closed {addr}')
            break
        if req.method in METHODS:
            response=METHODS[req.method](req)
        else:
            response=Response(STATUS_BAD_REQUEST)
        logging.info(f'{response}')
        response.send(f)
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



