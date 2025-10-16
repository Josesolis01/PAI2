import socket
import ssl
import threading # <-- ¡NUEVA IMPORTACIÓN!
from messaging_service import ensure_tables
from auth_service import handle_registration, handle_login
from session_service import handle_session # Se usa como target del hilo

HOST = "127.0.0.1"
PORT = 3030
certfile = 'certs/server.crt'
keyfile = 'certs/server.key'

# -------------------------------------------------------------------------
# FUNCION PARA MANEJAR TODA LA LÓGICA DE LA CONEXIÓN (se ejecuta en el HILO)
# -------------------------------------------------------------------------
def client_handler(conn, addr):
    """Maneja el flujo de login y sesión para un cliente, incluyendo el cierre."""
    try:
        # PRIMER PROMPT
        conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
        data = conn.recv(1024)
        if not data:
            return
        opcion = data.decode().strip().lower()
        
        # LÓGICA DE REGISTRO
        if opcion == "nuevo":
            _ = handle_registration(conn)
            conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")
            data = conn.recv(1024)
            if not data:
                return
            opcion = data.decode().strip().lower()

        # LÓGICA DE LOGIN
        if opcion == "login":
            username = None
            while username is None:
                username = handle_login(conn)
                if username is None:
                    continue
                
                try:
                    # Finalización de Handshake (opcional: nonce)
                    conn.sendall(b"oknonce\n")
                    ack = conn.recv(1024)
                except Exception:
                    username = None
                    break

                # INICIAR SESIÓN (bucle de menú)
                handle_session(conn, addr, username)
        else:
            conn.sendall(b"Opcion o datos incorrectos.\n")

    except Exception as e:
        print(f"Error en el manejo de {addr}: {e}")
    finally:
        # ASEGURAR QUE LA CONEXIÓN SE CIERRA AL TERMINAR EL HILO
        print(f"Conexión cerrada con: {addr}")
        conn.close()

# -------------------------------------------------------------------------
ensure_tables()
print(f"Servidor SSL escuchando en {HOST}:{PORT}...")

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    # Aumentamos el backlog a 300 para indicar al SO que espere más conexiones
    server_socket.listen(300) 

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    while True:
        # Espera por una nueva conexión TCP
        conn, addr = server_socket.accept()
        print(f"Conexión aceptada de: {addr}")

        # Envolver la conexión en SSL/TLS
        ssl_conn = ssl_context.wrap_socket(conn, server_side=True)

        # CAMBIO CLAVE: Iniciar un nuevo hilo para manejar esta conexión
        client_thread = threading.Thread(
            target=client_handler, 
            args=(ssl_conn, addr)
        )
        client_thread.start()
        # El bucle while True vuelve inmediatamente a server_socket.accept()
        
except Exception as e:
    print(f"Error fatal del servidor: {e}")
finally:
    server_socket.close()