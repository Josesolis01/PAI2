from postgresql_functions import init_mensajeria, enviar_mensaje, leer_mensajes

def ensure_tables():
    init_mensajeria()

def send_message(emisor: str, destinatario: str, contenido: str) -> bool:
    return enviar_mensaje(emisor, destinatario, contenido)

def fetch_messages(usuario: str) -> list:
    return leer_mensajes(usuario)