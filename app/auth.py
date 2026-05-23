import bcrypt
import secrets
from app.database import get_connection


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def crear_usuario(nombre, clave):
    conn = get_connection()
    cursor = conn.cursor()

    clave_hash = hash_password(clave)

    cursor.execute("""
        INSERT INTO usuarios (nombre, clave_hash)
        VALUES (?, ?)
    """, (nombre, clave_hash))

    conn.commit()
    conn.close()

def obtener_usuario(nombre):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE nombre = ?", (nombre,))
    user = cursor.fetchone()

    conn.close()
    return user

def obtener_usuario_por_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user

def generar_token_recuperacion(nombre):
    token = secrets.token_hex(16)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE usuarios
        SET token_recuperacion = ?
        WHERE nombre = ?
    """, (token, nombre))

    conn.commit()
    conn.close()

    return token

def resetear_clave(token, nueva_clave):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM usuarios WHERE token_recuperacion = ?
    """, (token,))
    user = cursor.fetchone()

    if not user:
        return False

    nueva_hash = hash_password(nueva_clave)

    cursor.execute("""
        UPDATE usuarios
        SET clave_hash = ?, token_recuperacion = NULL
        WHERE id = ?
    """, (nueva_hash, user["id"]))

    conn.commit()
    conn.close()

    return True