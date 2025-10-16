import socket
import ssl
import time

HOST = '127.0.0.1'
PORT = 3030
# Si tu certificado es autofirmado, puede que necesites el CA_CERT para validación.
# Para este ejemplo, simplificamos a ssl.CERT_NONE, lo cual NO es seguro en producción.
CA_CERT = 'certs/server.crt' 

# Credenciales de prueba
USERNAME = "luis"
PASSWORD = "Plapino123?"

def connect_and_login_luis():
    """Conecta de forma segura y simula el flujo de login para un usuario."""
    
    # Configuración SSL/TLS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_3 
    # Usamos CERT_NONE solo para pruebas locales, ya que no estamos cargando un CA
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE 

    try:
        # 1. Conexión TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Encapsulamiento y Conexión Segura (Handshake)
        secure_sock = context.wrap_socket(sock, server_hostname=HOST)
        secure_sock.connect((HOST, PORT))
        print(f"[*] Conexión exitosa a {HOST}:{PORT} (SSL/TLS)")

        # 3. Flujo de Login
        
        # a) Recibir el prompt inicial
        prompt = secure_sock.recv(1024).decode().strip()
        print(f"[<] Servidor: {prompt}")

        # b) Enviar la opción 'login'
        secure_sock.sendall(b"login\n")
        
        # c) Recibir prompt para 'username' (asumiendo que handle_login lo envía)
        username_prompt = secure_sock.recv(1024).decode().strip()
        print(f"[<] Servidor: {username_prompt}")
        
        # d) Enviar nombre de usuario
        print(f"[*] Enviando usuario: {USERNAME}")
        secure_sock.sendall(f"{USERNAME}\n".encode()) 
        
        # e) Recibir prompt para 'password'
        password_prompt = secure_sock.recv(1024).decode().strip()
        print(f"[<] Servidor: {password_prompt}")
        
        # f) Enviar contraseña
        print(f"[*] Enviando contraseña: {PASSWORD}")
        secure_sock.sendall(f"{PASSWORD}\n".encode())
        
        # g) Recibir 'oknonce\n' del servidor si el login es exitoso
        login_ack = secure_sock.recv(1024).decode().strip()
        print(f"[<] Respuesta Login: {login_ack}")

        if login_ack == "oknonce":
            # h) Enviar ACK al servidor
            secure_sock.sendall(b"ACK\n")
            print("[*] Login completo. Esperando el MENU del servidor...")
            
            # i) Recibir el menú
            menu = secure_sock.recv(1024).decode().strip()
            print("\n" + "="*20 + " MENÚ " + "="*20)
            print(menu)
            print("="*46 + "\n")
            
            # El cliente se desconecta (simulando que el usuario terminó la sesión)
            time.sleep(1) 

        else:
            print("[!] ERROR DE LOGIN: El servidor no respondió 'oknonce'.")

    except ConnectionRefusedError:
        print(f"[!] Conexión rechazada. ¿Está el servidor corriendo en {HOST}:{PORT}?")
    except ssl.SSLError as e:
        print(f"[!] Error SSL/TLS: {e}")
    except Exception as e:
        print(f"[!] Error inesperado: {e}")
    finally:
        if 'secure_sock' in locals():
            secure_sock.close()
            print("[*] Conexión cerrada.")

if __name__ == "__main__":
    connect_and_login_luis()