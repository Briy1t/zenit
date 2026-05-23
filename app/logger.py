from app.database import get_connection
from datetime import datetime

def registrar_evento(usuario, accion):
    conn = get_connection()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO auditoria (usuario, accion, fecha)
        VALUES (?, ?, ?)
    """, (usuario, accion, fecha))

    conn.commit()
    conn.close()
