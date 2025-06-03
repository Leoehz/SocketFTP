#!/usr/bin/env python3

import socket
import sys
import os
import re
from server_config import BASE_DIR, BUFFER_SIZE
import logging
from log import setup_logging

HOST = "127.0.0.1"  # Direccion
PORT = 65432  # Puerto donde va a escuchar

setup_logging()
logger = logging.getLogger('server')

pattern_get = r'^get\s([\w.-_]+)$' # Patron para identificar get archivo.txt

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    logger.info(f'Escuchando en el host {HOST}:{PORT}')
    logger.info(f'Configurado el directorio {BASE_DIR}')
    while True:
        conn, addr = s.accept()
        with conn:
            logger.info(f"Conexion recibida por {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode()
                logger.info(f'Se recibio "{command}"')
                if command == 'ls':
                    response = '\n'.join(os.listdir(BASE_DIR))
                    conn.sendall(response.encode())
                elif command == 'echo':
                    conn.sendall(data)
                elif re.match(pattern_get, command):
                    match = re.match(pattern_get, command)
                    filename = match.group(1)
                    file_path = os.path.join(BASE_DIR, filename)

                    if not os.path.isfile(file_path):
                        response = 'Archivo inexistente en directorio remoto.'
                        conn.sendall(response.encode())
                    else:
                        # Si el archivo existe, obtener su peso e informarlo
                        filesize = os.path.getsize(file_path)
                        conn.sendall(f"OK {filesize}\n".encode('utf-8'))
                        logger.info(f"Enviando archivo: {filename}, Tamaño: {filesize} bytes")

                        # 2. Enviar el archivo en trozos
                        with open(file_path, 'rb') as f: # Abrir en modo binario 'rb'
                            while True:
                                chunk = f.read(BUFFER_SIZE)
                                if not chunk:
                                    break # Fin del archivo
                                conn.sendall(chunk)
                        logger.info(f"Archivo {filename} enviado completamente.")
                    
                    pass
                elif command == 'exit':
                    logger.info('Saliendo.')
                    sys.exit()
                else:
                    response = 'Comando invalido'
                    conn.sendall(response.encode())

