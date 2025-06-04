# Importaciones
import sys
import os
import re
from server_config import BASE_SERVER_DIR, BUFFER_SIZE

import logging
from log import setup_logging

# Configuración y logger
setup_logging()
logger = logging.getLogger('serverlib')

# Patrones para comandos
pattern_get = r'^get\s([\w.-_]+)$'
pattern_cd = r'^cd\s+([\w/.-_]+)$'

def handle_ls(conn):
    response = '\n'.join(os.listdir(BASE_SERVER_DIR))
    conn.sendall(response.encode())

def handle_echo(conn, data):
    conn.sendall(data)

def handle_pwd(conn):
    response = os.getcwd()
    conn.sendall(response.encode())

def handle_cd(command, conn):
    match = re.match(pattern_cd, command)
    if not match:
        conn.sendall(b'Error: Comando cd malformado')
        return

    directory = match.group(1)
    logger.info(f"Valor de directorio: {directory}")
    try:
        os.chdir(directory)
        conn.sendall(f"Directorio cambiado a: {os.getcwd()}".encode())
        logger.info(f"Directorio cambiado a: {os.getcwd()}")
    except Exception as e:
        conn.sendall(f"Error al cambiar de directorio: {e}".encode())

def handle_exit(conn, addr):
    logger.info(f'El cliente {addr} pidió finalizar la sesión')
    conn.sendall(b'Sesion finalizada!')
    return 'logout'

def handle_get(conn, command):
    match = re.match(pattern_get, command)
    if not match:
        conn.sendall(b'Error: Comando get malformado')
        return

    filename = match.group(1)
    file_path = os.path.join(BASE_SERVER_DIR, filename)

    if not os.path.isfile(file_path):
        response = 'Archivo inexistente en directorio remoto.'
        conn.sendall(response.encode())
    else:
        filesize = os.path.getsize(file_path)
        conn.sendall(f"OK {filesize}\n".encode('utf-8'))
        logger.info(f"Enviando archivo: {filename}, Tamaño: {filesize} bytes")
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                conn.sendall(chunk)
        logger.info(f"Archivo {filename} enviado completamente.")

def handle_command(command, conn, data, addr):
    if command == 'ls':
        handle_ls(conn)
    elif command == 'echo':
        handle_echo(conn, data)
    elif re.match(pattern_cd, command):
        handle_cd(command, conn)
    elif command == 'pwd':
        handle_pwd(conn)
    elif re.match(pattern_get, command):
        handle_get(conn, command)
    elif command == 'exit':
        return handle_exit(conn, addr)
    else:
        conn.sendall(b'Comando invalido')
        logger.error('Comando inválido enviado')

def set_server_base_dir():
    try:
        os.chdir(BASE_SERVER_DIR)
    except Exception as e:
        sys.exit(1)