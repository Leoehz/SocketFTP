#!/usr/bin/env python3

import socket
import sys
import os
import re
import selectors
import logging
from log import setup_logging
from serverlib import BASE_SERVER_DIR, handle_command, set_server_base_dir

# Creación del selector (multiplexador I/O)
sel = selectors.DefaultSelector()

# Configuración y logger
setup_logging()
logger = logging.getLogger('server')

HOST = "127.0.0.1"
PORT = 65432

# Manejador de eventos para cada socket
def service_connection(key, mask):
    conn = key.fileobj
    addr = key.data
    try:
        data = conn.recv(1024)
        if data:
            command = data.decode().strip()
            logger.info(f'[{addr}] Comando recibido: "{command}"')
            result = handle_command(command, conn, data, addr)
            if result == 'logout':
                logger.info(f"Sesión cerrada con {addr}")
                sel.unregister(conn)
                conn.close()
        else:
            logger.info(f"Cliente {addr} desconectado")
            sel.unregister(conn)
            conn.close()
    except Exception as e:
        logger.error(f"Error con el cliente {addr}: {e}")
        sel.unregister(conn)
        conn.close()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    logger.info(f"Conexión aceptada de {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, data=addr)

def main():
    # Setear el directorio base del servidor
    #set_server_base_dir()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logger.info(f'Escuchando en el host {HOST}:{PORT}')
        logger.info(f'Configurado el directorio {BASE_SERVER_DIR}')
        s.setblocking(False)    # Se configura el socket en modo no bloqueante
        sel.register(s, selectors.EVENT_READ, data=None)    # Se registra el socket en el selector para eventos de lectura sin asociar ningun dato a este evento

        try:
            while True:
                events = sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        accept_wrapper(key.fileobj)
                    else:
                        service_connection(key, mask)

                # Mensaje de espera de conexión entrante
                logger.info("Esperando conexiones ...")
        except KeyboardInterrupt:
            logger.info("Servidor detenido manualmente")
        finally:
            sel.close()

if __name__ == '__main__':
    main()
