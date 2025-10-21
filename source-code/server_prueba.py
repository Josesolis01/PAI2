import socket
import ssl
import threading  # 1. Importamos el módulo de hilos
from messaging_service import ensure_tables
from auth_service import handle_registration, handle_login
from session_service import handle_session

HOST = "127.0.0.1"
PORT = 3030
certfile = 'certs/server.crt'
keyfile = 'certs/server.key'

# 2. Creamos una función para manejar la lógica de cada cliente
#    Todo el código que antes estaba en el 'with conn:' se mueve aquí.
def handle_client(conn, addr):
    print(f"Nuevo hilo iniciado para manejar la conexión de: {addr}")
    try:
        # El 'with conn:' asegura que el socket del cliente se cierre al final
        with conn:
            # primer prompt: nuevo/login
            conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
            data = conn.recv(1024)
            if not data:
                return # Si no hay datos, el hilo termina
            opcion = data.decode().strip().lower()
            if opcion == "nuevo":
                _ = handle_registration(conn)
                # Damos otra oportunidad de login tras el registro
                conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
                data = conn.recv(1024)
                if not data:
                    return
                opcion = data.decode().strip().lower()

            if opcion == "login":
                username = None
                while username is None:
                    username = handle_login(conn)
                    if username is None:
                        continue
                    try:
                        conn.sendall(b"oknonce\n")
                        _ = conn.recv(1024) # Esperamos el ACK del cliente
                    except Exception:
                        username = None
                        break

                    # Iniciar sesión persistente
                    handle_session(conn, addr, username)
                    # Una vez que handle_session termina, el bucle se rompe y el hilo finaliza
                    break # Salimos del bucle de login para que el hilo termine
            else:
                conn.sendall(b"Opcion no valida. Cerrando conexion.\n")
    except Exception as e:
        print(f"Error con el cliente {addr}: {e}")
    finally:
        print(f"Conexión con {addr} cerrada. Hilo terminado.")


# --- CONFIGURACIÓN DEL SOCKET PRINCIPAL (sin cambios) ---
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
server_socket.bind((HOST, PORT))
server_socket.listen(300) # Aumentamos la cola de escucha

# Asegurar tablas
ensure_tables()

print(f"Servidor SSL concurrente escuchando en {HOST}:{PORT}...")

with ssl_context.wrap_socket(server_socket, server_side=True) as ssl_socket:
    while True:
        # 3. El bucle principal ahora solo acepta conexiones y crea hilos
        conn, addr = ssl_socket.accept()
        # Creamos un hilo que ejecutará la función 'handle_client'
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True  # Permite que el programa principal termine aunque los hilos sigan activos
        client_thread.start() # Iniciamos el hilo