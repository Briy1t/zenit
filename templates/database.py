import sqlite3
from datetime import datetime, timedelta

# ---------------------------------------
# CONEXIÓN
# ---------------------------------------

def get_connection():
    conn = sqlite3.connect("/tmp/usuarios.db")
    conn.row_factory = sqlite3.Row
    
    # Activar claves foráneas en SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------------------
# TABLAS PRINCIPALES
# ---------------------------------------

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            clave_hash TEXT NOT NULL,
            email TEXT,
            token_recuperacion TEXT,
            creado_en TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            accion TEXT,
            fecha TEXT
        )
    """)

    conn.commit()
    conn.close()


def crear_tabla_registros():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            energia_social INTEGER,
            energia_fisica INTEGER,
            senales TEXT,
            drenantes TEXT,
            reguladoras TEXT,
            emocion TEXT,
            necesidades TEXT,
            notas TEXT,
            indice_zenit REAL,
            frase TEXT,
            diario_texto TEXT DEFAULT '',
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


def crear_tabla_indices_diarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS indices_diarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            indice_promedio REAL NOT NULL,
            registros_conteo INTEGER NOT NULL,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)

    conn.commit()
    conn.close()


def crear_tablas_historial():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reguladores_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            regulador TEXT,
            fecha TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drenantes_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            drenante TEXT,
            fecha TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------
# GUARDAR REGISTRO
# ---------------------------------------

def guardar_registro(usuario_id, datos):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO registros (
            usuario_id, fecha, energia_social, energia_fisica,
            senales, drenantes, reguladoras, emocion,
            necesidades, notas, indice_zenit, frase,
            diario_texto
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        usuario_id,
        datos["fecha"],
        datos["energia_social"],
        datos["energia_fisica"],
        datos["senales"],
        datos["drenantes"],
        datos["reguladoras"],
        datos["emocion"],
        datos["necesidades"],
        datos["notas"],
        datos["indice_zenit"],
        datos["frase"],
        datos["diario_texto"] or ""
    ))

    conn.commit()
    registro_id = cursor.lastrowid
    conn.close()
    
    return registro_id


# ---------------------------------------
# ÍNDICE DIARIO
# ---------------------------------------

def actualizar_indice_diario(usuario_id, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT AVG(indice_zenit) AS promedio, COUNT(*) AS cantidad
        FROM registros
        WHERE usuario_id = ? AND fecha = ?
    """, (usuario_id, fecha))

    fila = cursor.fetchone()
    promedio = fila["promedio"]
    cantidad = fila["cantidad"]

    cursor.execute("""
        SELECT id FROM indices_diarios
        WHERE usuario_id = ? AND fecha = ?
    """, (usuario_id, fecha))

    existente = cursor.fetchone()

    if existente:
        cursor.execute("""
            UPDATE indices_diarios
            SET indice_promedio = ?, registros_conteo = ?
            WHERE usuario_id = ? AND fecha = ?
        """, (promedio, cantidad, usuario_id, fecha))
    else:
        cursor.execute("""
            INSERT INTO indices_diarios (usuario_id, fecha, indice_promedio, registros_conteo)
            VALUES (?, ?, ?, ?)
        """, (usuario_id, fecha, promedio, cantidad))

    conn.commit()
    conn.close()


# ---------------------------------------
# HISTORIAL REGULADORES / DRENANTES
# ---------------------------------------

def guardar_regulador(usuario_id, regulador, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reguladores_historial (usuario_id, regulador, fecha)
        VALUES (?, ?, ?)
    """, (usuario_id, regulador.lower(), fecha))

    conn.commit()
    conn.close()


def guardar_drenante(usuario_id, drenante, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drenantes_historial (usuario_id, drenante, fecha)
        VALUES (?, ?, ?)
    """, (usuario_id, drenante.lower(), fecha))

    conn.commit()
    conn.close()


def obtener_reguladores(usuario_id, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT LOWER(regulador) AS nombre, COUNT(*) AS frecuencia
        FROM reguladores_historial
        WHERE usuario_id = ? AND fecha = ?
        GROUP BY LOWER(regulador)
    """, (usuario_id, fecha))

    datos = cursor.fetchall()
    conn.close()

    total = sum([row["frecuencia"] for row in datos]) or 1

    resultado = []
    for row in datos:
        efectividad = round((row["frecuencia"] / total) * 100)
        resultado.append({
            "nombre": row["nombre"],
            "frecuencia": row["frecuencia"],
            "efectividad": efectividad
        })

    return resultado


def obtener_drenantes(usuario_id, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT LOWER(drenante) AS nombre, COUNT(*) AS frecuencia
        FROM drenantes_historial
        WHERE usuario_id = ? AND fecha = ?
        GROUP BY LOWER(drenante)
    """, (usuario_id, fecha))

    datos = cursor.fetchall()
    conn.close()

    total = sum([row["frecuencia"] for row in datos]) or 1

    resultado = []
    for row in datos:
        impacto = round((row["frecuencia"] / total) * 100)
        resultado.append({
            "nombre": row["nombre"],
            "frecuencia": row["frecuencia"],
            "impacto": impacto
        })

    return resultado


# ---------------------------------------
# SEMANA (PORCENTAJES)
# ---------------------------------------

def obtener_semana(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    hoy = datetime.now().date()
    dias = []
    valores = []

    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        dia_str = dia.strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT indice_zenit
            FROM registros
            WHERE usuario_id = ? AND fecha = ?
        """, (usuario_id, dia_str))

        fila = cursor.fetchone()

        dias.append(dia.strftime("%a"))
        valores.append((fila["indice_zenit"] * 10) if fila else 0)

    conn.close()
    return dias, valores

def crear_indices():
    conn = get_connection()
    cursor = conn.cursor()

    # Índice único para evitar usuarios duplicados
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_usuario_nombre
        ON usuarios(nombre)
    """)

    conn.commit()
    conn.close()


