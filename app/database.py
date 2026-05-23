import sqlite3

def get_connection():
    conn = sqlite3.connect("usuarios.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla usuarios
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

    # Tabla auditoría
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
            puntaje_ia REAL,
            indice_zenit REAL,
            frase TEXT,
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
    
create_tables()
crear_tabla_registros()
crear_tabla_indices_diarios()

def guardar_registro(usuario_id, datos):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO registros (
            usuario_id, fecha, energia_social, energia_fisica,
            senales, drenantes, reguladoras, emocion,
            necesidades, notas, puntaje_ia, indice_zenit, frase
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
        datos["puntaje_ia"],
        datos["indice_zenit"],
        datos["frase"]
    ))

    conn.commit()
    registro_id = cursor.lastrowid
    conn.close()

    return registro_id

def actualizar_indice_diario(usuario_id, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener media e cantidad de registros del día
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
        # Actualizar
        cursor.execute("""
            UPDATE indices_diarios
            SET indice_promedio = ?, registros_conteo = ?
            WHERE usuario_id = ? AND fecha = ?
        """, (promedio, cantidad, usuario_id, fecha))
    else:
        # Crear
        cursor.execute("""
            INSERT INTO indices_diarios (usuario_id, fecha, indice_promedio, registros_conteo)
            VALUES (?, ?, ?, ?)
        """, (usuario_id, fecha, promedio, cantidad))

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
def guardar_regulador(usuario_id, regulador, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reguladores_historial (usuario_id, regulador, fecha)
        VALUES (?, ?, ?)
    """, (usuario_id, regulador, fecha))

    conn.commit()
    conn.close()


def guardar_drenante(usuario_id, drenante, fecha):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO drenantes_historial (usuario_id, drenante, fecha)
        VALUES (?, ?, ?)
    """, (usuario_id, drenante, fecha))

    conn.commit()
    conn.close()
