import socket
from nonce_functions import *
import json
import secrets
import ssl


HOST = "localhost"
PORT = 3030
CERT_DIR = "certs"               
CA_CERT = f"{CERT_DIR}/ca.crt"   
message = "Hola desde el cliente!"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
# Indica el certificado raíz de confianza (CA que firmó el certificado del servidor)
ssl_context.load_verify_locations("certs/ca.crt")
# Obliga a verificar el certificado del servidor
ssl_context.verify_mode = ssl.CERT_REQUIRED
# Verificación de nombre de host (debe coincidir con CN o SAN del certificado)
ssl_context.check_hostname = True

with ssl_context.wrap_socket(client_socket, server_hostname=HOST) as s:
        # Conectarse al servidor
    s.connect((HOST, PORT))
    print(f"Conectado al servidor SSL en {HOST}:{PORT}")
    registro_exitoso = False

    pregunta = s.recv(1024).decode().strip()
    print(pregunta)

    opcion = input("> ").strip().lower()
    s.sendall(opcion.encode())

    if opcion == "nuevo":
        prompt_user = s.recv(1024).decode().strip()
        print(prompt_user)
        username = input("> ").strip()
        s.sendall(username.encode())

        while True:
            prompt_pass = s.recv(1024).decode().strip()
            print(prompt_pass)
            password = input("> ").strip()
            s.sendall(password.encode())

            resp = s.recv(1024).decode().strip()
            print(resp)

            if "Registro completado." in resp:
                opcion = "login"
                registro_exitoso = True
                break

    if opcion == "login":
        print("Implementando la funcionalidad de login\n")
        while True:
            prompt_user = s.recv(1024).decode().strip()
            print(prompt_user)

            username = input("> ").strip()
            s.sendall(username.encode())

            prompt_pass = s.recv(1024).decode().strip()
            print(prompt_pass)
            password = input("> ").strip()

            s.sendall(password.encode())

            resp = s.recv(1024).decode().strip()
            print(resp)

            if "Login exitoso" in resp:
                nonce_server = s.recv(1024).decode().strip()
                s.sendall(b"ack de nonce del servidor")

                while True:
                    menu_prompt = s.recv(1024).decode().strip()
                    s.sendall(b"ack")
                    if not menu_prompt or "Cerrando sesion" in menu_prompt:
                        print("Sesion cerrada.")
                        break

                    print(menu_prompt)
                    opcion_sesion = input().strip()
                    s.sendall(opcion_sesion.encode())

                    if opcion_sesion == "1":
                        print(s.recv(1024).decode().strip())

                        print(s.recv(1024).decode().strip())
                        destinatario = input("> ").strip()
                        s.sendall(destinatario.encode())
                        print(destinatario)

                        print(s.recv(1024).decode().strip())
                        cantidad = input("> ").strip()
                        s.sendall(cantidad.encode())

                        print(cantidad)
                        print(s.recv(1024).decode().strip())

                        datos = datos_transaccion(cantidad, destinatario, nonce_server)
                        s.sendall(json.dumps(datos).encode())
                        ack_datos = s.recv(1024).decode().strip()
                        print(ack_datos)

                        nonce_cliente = secrets.token_hex(16)
                        s.sendall(nonce_cliente.encode())
                        ack_nonce = s.recv(1024).decode().strip()
                        print(ack_nonce)
                        print(s.recv(4096).decode().strip())
                        break
                    elif opcion_sesion == "2":
                        pass
                    else:
                        print(s.recv(1024).decode().strip())

            elif "Usuario bloqueado temporalmente" in resp:
                print(resp)
            elif "intentos restantes" in resp:
                print(resp)
            else:
                print("usuario bloqueado o error no especificado")
                break

    else:
        print("Opción no reconocida. Terminando conexión.")
