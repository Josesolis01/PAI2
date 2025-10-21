import socket
import ssl
import threading
import time

HOST = "localhost"
PORT = 3030
CA_CERT = "certs/ca.crt"

# --- Configuración de la prueba ---
NUM_CLIENTS = 300  # ¡Prueba con 10, 50, 100 o hasta 300!
USER_TO_TEST = "marta" # Un usuario que ya debe existir en tu DB
PASS_TO_TEST = "Marta123?" # La contraseña de ese usuario

def run_client(client_id):
    """
    Esta función simula un único cliente.
    """
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CA_CERT)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED

    try:
        with socket.create_connection((HOST, PORT)) as sock:
            with ssl_context.wrap_socket(sock, server_hostname=HOST) as ssock:
                print(f"[Cliente {client_id}]: Conectado al servidor.")
                
                # 1. Esperar el primer prompt
                ssock.recv(1024)
                
                # 2. Enviar opción "login"
                ssock.sendall(b"login")
                
                # 3. Enviar usuario
                ssock.recv(1024) # Esperar prompt de usuario
                ssock.sendall(USER_TO_TEST.encode())
                
                # 4. Enviar contraseña
                ssock.recv(1024) # Esperar prompt de contraseña
                ssock.sendall(PASS_TO_TEST.encode())
                
                # 5. Recibir respuesta de login y cerrar
                response = ssock.recv(1024).decode(errors='ignore')
                if "Login exitoso" in response:
                    print(f"[Cliente {client_id}]: Login exitoso. Desconectando.")
                else:
                    print(f"[Cliente {client_id}]: Falló el login. Respuesta: {response.strip()}")

    except Exception as e:
        print(f"[Cliente {client_id}]: Error - {e}")

# --- Bucle principal para lanzar los hilos ---
if __name__ == "__main__":
    threads = []
    print(f"Lanzando {NUM_CLIENTS} clientes de prueba...")

    for i in range(NUM_CLIENTS):
        # Creamos un hilo por cada cliente
        thread = threading.Thread(target=run_client, args=(i,))
        threads.append(thread)
        thread.start()
        time.sleep(0.05) # Pequeña pausa para no sobrecargar la red al instante

    # Esperamos a que todos los hilos terminen
    for thread in threads:
        thread.join()

    print("Prueba de estrés completada.")