import socket
import ssl
from messaging_service import ensure_tables
from auth_service import handle_registration, handle_login
from session_service import handle_session
from postgresql_functions import create_database_if_not_exists


HOST = "127.0.0.1"
PORT = 3030
certfile = 'certs/server.crt'
keyfile = 'certs/server.key'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)


create_database_if_not_exists()
# Asegurar tablas
ensure_tables()

print(f"Servidor SSL escuchando en {HOST}:{PORT}...")

with ssl_context.wrap_socket(server_socket, server_side=True) as ssl_socket:
    while True:
        conn, addr = ssl_socket.accept()
        print(f"Conexión establecida con: {addr}")
        with conn:
            # primer prompt: nuevo/login
            conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
            data = conn.recv(1024)
            if not data:
                continue
            opcion = data.decode().strip().lower()
            if opcion == "nuevo":
                _ = handle_registration(conn)  # fuerza registro; cliente deberá re-logear
                conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
                data = conn.recv(1024)
                if not data:
                    continue
                opcion = data.decode().strip().lower()

            if opcion == "login":
                username = None
                # intentar login hasta que tenga éxito o se desconecte
                while username is None:
                    username = handle_login(conn)
                    if username is None:
                        # handle_login ya envió mensajes de error; intentar de nuevo
                        continue
                    # Si login OK, enviar nonce (si requiere)
                    # generar nonce si lo necesitas, aquí solo procedemos al session
                    try:
                        # opcional: handshake con nonce
                        # nonce = secrets.token_hex(16)
                        # conn.sendall(nonce.encode())
                        conn.sendall(b"oknonce\n")  # marcador para el cliente; ajusta según tu protocolo
                        ack = conn.recv(1024)
                    except Exception:
                        username = None
                        break

                    # iniciar sesión persistente
                    handle_session(conn, addr, username)
            else:
                conn.sendall(b"Usuario o contrasena incorrectos (FINAL).\n")