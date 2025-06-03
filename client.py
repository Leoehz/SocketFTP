import socket
import os
import re
from client_config import BASE_DIR
from clientlib import request_file

HOST = "127.0.0.1"  # Host de Server
PORT = 65432  # Puerto del Server

pattern_get = r'^get\s([\w.-_]+)$'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        command = input('> ')
        if not command:
            continue

        # Detectar si es ejecucion local o en el server
        if command[0] == '!':
            command = command[1:]
            if command == 'ls':
                print('\n'.join(os.listdir(BASE_DIR)))
            else:
                print('Comando local invalido.')
            continue

        # Si no es ejecucion local se contacta con el server
        elif re.match(pattern_get, command):
            match = re.match(pattern_get, command)
            filename = match.group(1)
            request_file(s, filename)

        else:
            s.sendall(command.encode())
            response = s.recv(1024)
            print(response.decode())

