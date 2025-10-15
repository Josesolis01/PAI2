import socket
import ssl
import json

def connect_and_communicate(request_data, server_host='localhost', server_port=8080):
    """Establece la conexión SSL/TLS y envía una solicitud JSON."""
    
    # --- Configuración de SSL/TLS Segura (Requisito 33, 36) ---
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # *** CRÍTICO: HABILITAR LA VERIFICACIÓN DE AUTENTICIDAD ***
    # Se carga el almacén de confianza. En pruebas, puede ser el propio certificado del servidor.
    # Para producción, es el certificado de la CA que firmó el certificado del servidor.
    # NOTA: Debes tener el certificado del servidor (o de la CA) en 'trusted_cert.pem'.
    # Si usas el mismo archivo que el servidor ('cert.pem'), renómbralo a 'trusted_cert.pem' o ajusta la ruta.
    try:
        ssl_context.load_verify_locations(cafile='trusted_cert.pem')
    except Exception as e:
        # En caso de no encontrar el archivo, se debe notificar al usuario (punto de fallo en seguridad).
        print(f"ADVERTENCIA DE SEGURIDAD: No se pudo cargar el certificado de confianza. {e}")
        # En un sistema real, no se debería proceder si no se puede asegurar la autenticidad.
        return {"status": "FATAL_ERROR", "message": "Fallo en la configuración de autenticidad."}

    # ssl_context.check_hostname = True (Esto se habilita automáticamente con CERT_REQUIRED)
    ssl_context.verify_mode = ssl.CERT_REQUIRED # Exigir la verificación del certificado del servidor.

    # --- Lógica de conexión y comunicación ---
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Los datos de la solicitud deben enviarse en formato JSON
        message_to_send = json.dumps(request_data)

        with ssl_context.wrap_socket(client_socket, server_hostname=server_host) as ssl_socket:
            
            # Conectarse al servidor (Se realiza el Handshake SSL/TLS y la verificación del certificado)
            ssl_socket.connect((server_host, server_port))
            print(f"Conectado y AUTENTICADO al servidor SSL en {server_host}:{server_port} [SSL/TLS activo].")

            # Enviar la solicitud (las credenciales o el mensaje viajan de forma CONFIDENCIAL e ÍNTEGRA)
            ssl_socket.sendall(message_to_send.encode('utf-8'))
            print(f"Solicitud enviada: {request_data.get('command')}")

            # Recibir respuesta del servidor
            response_data = ssl_socket.recv(1024).decode('utf-8')
            return json.loads(response_data)

    except ssl.SSLCertVerificationError as e:
        print(f"FALLO DE SEGURIDAD (AUTENTICIDAD): El certificado del servidor NO es válido o no es de confianza. {e}")
        return {"status": "SECURITY_ERROR", "message": "Fallo en la verificación del certificado SSL."}
    except Exception as e:
        print(f"Error de conexión o comunicación: {e}")
        return {"status": "ERROR", "message": "Error de red o servidor."}

# --- EJEMPLO DE USO CON EL PROTOCOLO DEFINIDO ---
if __name__ == "__main__":
    session_token = None
    
    # 1. Intento de Login con credenciales válidas
    print("\n--- 1. Intentando iniciar sesión ---")
    login_request = {
        "command": "LOGIN",
        "username": "roadwarrior",
        "password": "secureVPN"
    }
    login_response = connect_and_communicate(login_request)
    print(f"Respuesta del servidor: {login_response}")
    
    if login_response.get("status") == "SUCCESS":
        session_token = login_response.get("session_id")

    # 2. Enviar un mensaje después del login (Requisito 70)
    if session_token:
        print("\n--- 2. Enviando un mensaje autenticado ---")
        message_request = {
            "command": "SEND_MESSAGE",
            "session_id": session_token,
            "message": "Este es mi informe de trabajo remoto, con menos de 144 caracteres."
        }
        message_response = connect_and_communicate(message_request)
        print(f"Respuesta del servidor: {message_response}")
    else:
        print("\n--- 2. No se puede enviar el mensaje; login fallido. ---")