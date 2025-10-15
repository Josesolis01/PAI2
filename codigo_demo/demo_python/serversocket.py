import socket
import os
import bcrypt
from postgresql_functions import *
from nonce_functions import *
import json
from time_functions import *
import secrets
import ssl


HOST = "127.0.0.1"
PORT = 3030

certfile = 'certs/server.crt'  # Ruta al archivo del certificado del servidor
keyfile = 'certs/server.key'    # Ruta al archivo de la clave privada del servidor

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)  # Escuchar una conexión


print(f"Servidor SSL escuchando en el puerto {PORT}...")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
# Cargar el certificado y la clave del servidor (firmados por la CA local)
ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

# Asegurar que la tabla de mensajes exista
init_mensajeria()


def is_strong_password(password):
    if len(password) < 8:
        return False, "La contrasena debe tener al menos 8 caracteres."
    if not any(char.isdigit() for char in password.decode()):
        return False, "La contrasena debe contener al menos un numero."
    if not any(char.isalpha() for char in password.decode()):
        return False, "La contrasena debe contener al menos una letra."
    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",.<>/?`~" for char in password.decode()):
        return False, "La contrasena debe contener al menos un simbolo."
    return True, ""

with ssl_context.wrap_socket(server_socket, server_side=True) as ssl_socket:
        # Aceptar una conexión
    conn, addr = ssl_socket.accept()
    print(f"Conexión establecida con: {addr}")

    with conn:
        print(f"Connected by {addr}")

        conn.sendall(b"Eres nuevo usuario o quieres loggearte? nuevo/login\n")

        data = conn.recv(1024)
        if data:
            opcion = data.decode().strip().lower()
            print(f"Respuesta del cliente: {opcion}")

            if opcion == "nuevo":
                conn.sendall(b"Introduce un nombre de usuario:\n")

                username = conn.recv(1024).decode().strip()
                print("Nombre de usuario:" + username)
                if usuario_existe(username):
                    conn.sendall(b"Usuario ya existe. Prueba con otro.\n")
                else:
                   while True:
                        conn.sendall(b"Introduce una contrasena:\n")
                        password = conn.recv(1024).strip()

                        is_valid, reason = is_strong_password(password)

                        if is_valid:
                            password_txt = password.decode("utf-8")
                            crear_usuario(username, password_txt)
                            conn.sendall(b"Registro completado. Por favor, inicia sesion a continuacion.\n")
                            opcion = "login"
                            break
                        else:
                            conn.sendall(reason.encode() + b"\n")

            if opcion == "login":

                while True:
                    conn.sendall(b"Introduce un nombre de usuario:\n")
                    username = conn.recv(1024).decode().strip()
                    print("Nombre de usuario: " + username)
                    is_locked, tiempo_restante = bloqueado(username)
                    if is_locked is True:
                        msg = f"Usuario bloqueado temporalmente. Intente de nuevo en {tiempo_restante} segundos.\n"
                        conn.sendall(msg.encode())
                        continue
                    else:
                        conn.sendall(b"Introduce una contrasena:\n")
                        password = conn.recv(1024).strip()

                    if usuario_existe(username):
                        password_txt = password.decode("utf-8")
                        verficacion = verificar_usuario(username, password_txt)
                        if verficacion == False:
                            is_locked, restantes = registrar_fallo(username)
                            if is_locked:
                                msg = f"Usuario bloqueado por {LOCK_SECONDS} segundos.\n"
                                conn.sendall(msg.encode())
                                continue
                            else:
                                msg = f"intentos restantes: {restantes}. Vuelve a intentarlo"
                                conn.sendall(msg.encode())

                        else:
                            conn.sendall(b"Login exitoso.\n")
                            nonce_server = secrets.token_hex(16)
                            conn.sendall(nonce_server.encode())
                            ack = conn.recv(1024)  # Esperar ACK del cliente
                            print(f"ACK del cliente recibido: {ack.decode().strip()}")
                            # Iniciar bucle persistente de sesión: repetir menú hasta cerrar sesión
                            menu = (
                                b"\nQue deseas hacer?\n"
                                b"1. Enviar mensaje\n"
                                b"2. Leer mensajes\n"
                                b"3. Cerrar sesion\n"
                                b">\n"
                            )
                            print(f"Iniciando bucle de sesión para usuario: {username}")
                            while True:
                                # Enviar el menú
                                try:
                                    conn.sendall(menu)
                                except Exception:
                                    break
                                # Leer la opción del cliente
                                ACK_menu = conn.recv(1024)  # Esperar ACK del cliente
                                print(f"ACK del cliente recibido: {ACK_menu.decode().strip()}")
                                # Esperar la opción del usuario
                                opcion_sesion_data = conn.recv(1024)
                                if not opcion_sesion_data:
                                    break
                                opcion_sesion = opcion_sesion_data.decode().strip()
                                print(f"Opcion de sesion recibida: {opcion_sesion}")
                                payload_json = None

                                if opcion_sesion == "1":
                                    # Enviar mensaje a otro usuario
                                    conn.sendall(b"Introduce el nombre del destinatario:\n")
                                    destinatario = conn.recv(1024).strip().decode('utf-8')
                                    if not usuario_existe(destinatario):
                                        mensaje_a_enviar = "\n Error: El destinatario no existe. Operacion cancelada.\n"
                                    else:
                                        conn.sendall(b"Introduce el mensaje:\n")
                                        contenido = conn.recv(4096).strip().decode('utf-8')
                                        ok = enviar_mensaje(username, destinatario, contenido)
                                        if ok:
                                            mensaje_a_enviar = "Mensaje enviado correctamente.\n"
                                        else:
                                            mensaje_a_enviar = "Error al enviar el mensaje.\n"

                                elif opcion_sesion == "2":
                                    print(f"El usuario {username} ha solicitado leer mensajes.")
                                    # Leer mensajes dirigidos al usuario
                                    msgs = leer_mensajes(username)
                                    obtenidos = len(msgs)
                                    print(f"Mensajes obtenidos: {obtenidos}")

                                    if len(msgs) == 0:
                                        mensaje_a_enviar = "No hay mensajes nuevos.\n"
                                    else:
                                        payload_json = json.dumps(msgs)
                                elif opcion_sesion == "3":
                                    try:
                                        conn.sendall(b"Cerrando sesion. Adios.\n")
                                    except Exception:
                                        pass
                                    print(f"Cerrando conexión con {addr}")
                                    try:
                                        conn.shutdown(socket.SHUT_RDWR)
                                    except Exception:
                                        pass
                                    try:
                                        conn.close()
                                    except Exception:
                                        pass
                                    break

                                else:
                                    mensaje_a_enviar = "Opcion no valida.\n"

                                # Enviar mensaje de resultado o payload antes del siguiente menú
                                if payload_json is not None:
                                    try:
                                        conn.sendall(payload_json.encode())
                                    except Exception:
                                        break
                                elif mensaje_a_enviar is not None:
                                    try:
                                        conn.sendall(mensaje_a_enviar.encode())
                                    except Exception:
                                        break

            else:
                conn.sendall(b"Usuario o contrasena incorrectos (FINAL).\n")
