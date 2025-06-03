import socket
import os
from client_config import BASE_DIR, BUFFER_SIZE

def request_file(sock, filename):
    """Solicita y recibe un archivo del servidor"""
    try:
        # 1. Enviar el comando 'get' al servidor
        command = f"get {filename}"
        sock.sendall(command.encode('utf-8'))
        print(f"Solicitando archivo: {filename}")

        # 2. Recibir la respuesta inicial del servidor (OK <tamaño> o Error)
        initial_response_bytes = sock.recv(1024)
        initial_response = initial_response_bytes.decode('utf-8').strip()
        
        print(f"Respuesta del servidor: {initial_response}")

        if initial_response.startswith("OK"):
            try:
                parts = initial_response.split(' ', 1)
                filesize = int(parts[1])
                print(f"Transferencia iniciada. Tamaño del archivo: {filesize} bytes.")

                # Preparar para recibir el archivo
                local_filepath = os.path.join(BASE_DIR, os.path.basename(filename))
                bytes_recibidos = 0
                with open(local_filepath, 'wb') as f: # Abrir en modo binario 'wb'
                    while bytes_recibidos < filesize:
                        # Calcular cuántos bytes leer en esta iteración para no exceder filesize
                        bytes_a_leer = min(BUFFER_SIZE, filesize - bytes_recibidos)
                        chunk = sock.recv(bytes_a_leer)
                        if not chunk:
                            # Conexión cerrada prematuramente por el servidor
                            print("Error: La conexión se cerró inesperadamente por el servidor.")
                            break
                        f.write(chunk)
                        bytes_recibidos += len(chunk)
                        porcentaje = (bytes_recibidos / filesize) * 100
                        print(f"\rProgreso: {porcentaje:.2f}% ", end='')
                        # print(f"Recibidos {bytes_recibidos}/{filesize} bytes", end='\r')

                if bytes_recibidos == filesize:
                    print(f"\nArchivo '{filename}' descargado exitosamente como '{local_filepath}'.")
                else:
                    print(f"\nError: Se esperaban {filesize} bytes pero se recibieron {bytes_recibidos}.")
                    if os.path.exists(local_filepath): # Borrar archivo incompleto
                        os.remove(local_filepath)

            except (IndexError, ValueError) as e:
                print(f"Error: Respuesta 'OK' del servidor malformada o tamaño inválido: {initial_response} ({e})")
            except Exception as e:
                print(f"Error al recibir o guardar el archivo: {e}")

        elif initial_response.startswith("Error:"):
            print(f"Error del servidor: {initial_response}")
        else:
            print(f"Respuesta desconocida del servidor: {initial_response}")

    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")