import socket
import ssl
import json
# Importar una librería de hashing para simular el almacenamiento seguro
# Por ejemplo: 'from hashlib import sha256'
# Para este ejemplo, usaremos una función placeholder simple.

# --- SIMULACIÓN DE SEGURIDAD Y DATOS ---
def hash_password(password):
    """Simulación de función de hashing seguro para almacenamiento de credenciales."""
    # En un entorno real, usarías bcrypt o Argon2, no sha256.
    # Usamos sha256 solo como placeholder.
    import hashlib
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Simulación de Base de Datos Inicial de Usuarios (Requisitos 67, 91)
# Contraseñas almacenadas de forma "segura" (hasheadas)
USER_DB = {
    "empleado1": hash_password("pass123"), # Usuario preexistente
    "roadwarrior": hash_password("secureVPN") # Usuario preexistente
}

# Simulación de gestión de sesiones activas (para autenticidad en envío de mensajes)
ACTIVE_SESSIONS = {}

# --- LÓGICA DEL SERVIDOR ---
def handle_client(conn):
    """Maneja la lógica de la sesión con el cliente."""
    try:
        # Recibir datos. Asumimos que los datos vienen en formato JSON (protocolo).
        raw_data = conn.recv(1024).decode('utf-8')
        if not raw_data:
            return

        request = json.loads(raw_data)
        command = request.get("command")
        
        # Lógica de comandos
        if command == "LOGIN":
            username = request.get("username", "")
            password = request.get("password", "")
            
            # Verificar credenciales de forma segura (Requisito 63, 112)
            hashed_input = hash_password(password)
            if USER_DB.get(username) == hashed_input:
                # Simulación de Inicio de sesión exitoso (Requisito 105)
                session_id = f"session_{username}_{hash_password(str(username))[:8]}"
                ACTIVE_SESSIONS[session_id] = username
                response = {"status": "SUCCESS", "message": "Inicio de sesión exitoso.", "session_id": session_id}
            else:
                # Simulación de Inicio de sesión fallido (Requisito 105, 64)
                response = {"status": "ERROR", "message": "Credenciales inválidas."}

        elif command == "SEND_MESSAGE":
            session_id = request.get("session_id", "")
            message = request.get("message", "")[:144] # Máximo 144 caracteres (Requisito 103)

            # Verificar si el usuario está autenticado
            if session_id in ACTIVE_SESSIONS:
                username = ACTIVE_SESSIONS[session_id]
                # Aquí se realizaría el registro del mensaje (Requisito 94, 75)
                print(f"[{username}] MENSAJE RECIBIDO (INTEGRIDAD Y CONFIDENCIALIDAD ASEGURADA POR TLS): {message}")
                response = {"status": "SUCCESS", "message": "Mensaje enviado y recibido correctamente."} # (Requisito 108)
            else:
                response = {"status": "ERROR", "message": "No autenticado. Por favor, inicie sesión."}

        else:
            response = {"status": "ERROR", "message": "Comando desconocido."}

        conn.sendall(json.dumps(response).encode('utf-8'))

    except json.JSONDecodeError:
        error_response = {"status": "ERROR", "message": "Formato de solicitud JSON inválido."}
        conn.sendall(json.dumps(error_response).encode('utf-8'))
    except Exception as e:
        print(f"Error durante la comunicación: {e}")
        
def start_ssl_server():
    host = '0.0.0.0' 
    port = 8080
    # NOTA: Debes generar 'cert.pem' y 'key.pem' (certificado y clave privada del servidor).
    certfile = 'cert.pem' 
    keyfile = 'key.pem' 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5) # Aumentamos el backlog a 5 para manejar más clientes (prueba de capacidad)

    print(f"Servidor SSL escuchando en el puerto {port}...")

    # Configuración de SSL/TLS (Requisito 33, 36)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # Se podría configurar: ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3 para asegurar TLS 1.3
    # Y configurar ciphers: ssl_context.set_ciphers('TLS_AES_256_GCM_SHA384:...') para Cipher Suites robustos
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

    try:
        while True:
            conn_socket, addr = server_socket.accept()
            print(f"Conexión TCP establecida con: {addr}")

            try:
                # Envolver la conexión con SSL
                with ssl_context.wrap_socket(conn_socket, server_side=True) as ssl_conn:
                    print(f"Handshake SSL/TLS completado con {addr}.")
                    handle_client(ssl_conn)
            except ssl.SSLError as e:
                print(f"Error en la conexión SSL/TLS: {e}")
            except Exception as e:
                print(f"Error al manejar la conexión: {e}")
            finally:
                print(f"Cerrando conexión con {addr}")
                # En una implementación multi-hilo o async, esto se haría en un thread/task separado.

    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_ssl_server()