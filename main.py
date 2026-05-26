from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import crear_usuario, obtener_usuario, verify_password, obtener_usuario_por_id
from app.database import (
    create_tables,
    get_connection,
    crear_tabla_registros,
    crear_tabla_indices_diarios,
    crear_tablas_historial,
    guardar_registro,
    actualizar_indice_diario,
    guardar_regulador,
    guardar_drenante,
    obtener_semana,
    obtener_reguladores,
    obtener_drenantes
)

import random
from datetime import datetime
from typing import Optional


# ---------------------------
#  INICIALIZACIÓN BD
# ---------------------------

create_tables()
crear_tabla_registros()
crear_tabla_indices_diarios()
crear_tablas_historial()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------------------
#  FAVICON
# ---------------------------

@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse(url="/static/img/cohete.png")


# ---------------------------
#  TIPS DEL DÍA
# ---------------------------

TIPS = [
    "Respira profundo. Tu cuerpo sabe más de lo que tu mente procesa.",
    "Una pausa de 30 segundos puede cambiar el tono de tu día.",
    "No tienes que hacerlo perfecto, solo presente.",
    "Tu energía es un recurso valioso: protégela.",
    "Hoy mereces suavidad, incluso si no lo sientes.",
    "Tu cuerpo te habla antes que tus pensamientos. Escúchalo.",
    "Haz algo pequeño por ti, aunque sea un sorbo de agua.",
    "No te exijas claridad cuando estás cansada.",
    "Tu ritmo es válido, aunque sea lento.",
    "Lo que sientes hoy no define quién eres.",
    "Descansar también es avanzar.",
    "Tu bienestar importa más que tu productividad.",
    "Un minuto de respiración consciente es un regalo para tu sistema.",
    "No ignores las señales del cuerpo: son sabias.",
    "Hoy puedes elegir algo que te haga bien.",
    "Tu valor no depende de tu energía.",
    "Permítete sentir sin juzgarte.",
    "Tu sistema necesita pausas, no castigos.",
    "Eres más fuerte de lo que crees.",
    "Hoy puedes empezar de nuevo, aunque sea a mitad del día."
]


# ---------------------------
#  FRASES ZENIT
# ---------------------------

FRASES_ZENIT = {
    1: ["Día pesado 🌑 Tu sistema está saturado, sé amable contigo."],
    2: ["Día bajo 🌫️ Tu energía está sensible, necesitas espacio y calma."],
    3: ["Día estable pero frágil 🌥️ Avanza despacio, tu cuerpo te está pidiendo suavidad."],
    4: ["Día moderado 🌤️ No estás mal, pero tampoco en tu mejor punto. Escucha tus límites."],
    5: ["Día sólido ✨ Tienes claridad suficiente para avanzar sin prisa."],
    6: ["Día positivo 🌞 Tu energía está firme y sostenida."],
    7: ["Día equilibrado 🔆 Tu sistema está funcionando de forma saludable."],
    8: ["Día fuerte 🔥 Tu energía está alta y bien regulada."],
    9: ["Día excepcional ✨ Tu presencia hoy es poderosa y clara."],
    10: ["Día extraordinario 🌈 Estás en un nivel de equilibrio muy alto."]
}


# ---------------------------
#  FUNCIÓN DE BLINDAJE
# ---------------------------

def blindar_usuario(usuario_id: int):
    """Verifica que el usuario exista y sea válido."""
    if usuario_id is None:
        return None

    usuario = obtener_usuario_por_id(usuario_id)
    if not usuario:
        return None

    return usuario


# ---------------------------
#  RUTA: INICIO
# ---------------------------

@app.get("/", response_class=HTMLResponse)
async def bienvenida(request: Request):
    return templates.TemplateResponse("bienvenida.html", {"request": request})


# ---------------------------
#  LOGIN
# ---------------------------

@app.post("/login")
async def login(request: Request, nombre: str = Form(...), clave: str = Form(...)):
    user = obtener_usuario(nombre)

    if not user:
        return templates.TemplateResponse(
            "bienvenida.html",
            {"request": request, "error": "El usuario no existe. ¿Quieres registrarte?"}
        )

    if not verify_password(clave, user["clave_hash"]):
        return templates.TemplateResponse(
            "bienvenida.html",
            {"request": request, "error": "La clave es incorrecta."}
        )

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM registros WHERE usuario_id = ?", (user["id"],))
    total = cursor.fetchone()[0]
    conn.close()

    if total == 0:
        return RedirectResponse(f"/cuestionario?usuario_id={user['id']}", status_code=303)

    return RedirectResponse(f"/dashboard?usuario_id={user['id']}", status_code=303)


# ---------------------------
#  REGISTRO DE USUARIO
# ---------------------------

@app.get("/registro")
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})


@app.post("/registro")
async def registro_post(request: Request, nombre: str = Form(...), clave: str = Form(...)):
    try:
        crear_usuario(nombre, clave)
        user = obtener_usuario(nombre)
        return RedirectResponse(f"/cuestionario?usuario_id={user['id']}", status_code=303)

    except Exception:
        return templates.TemplateResponse(
            "registro.html",
            {"request": request, "error": "Ese nombre ya existe. Intenta con otro."}
        )


# ---------------------------
#  CUESTIONARIO (GET)
# ---------------------------

@app.get("/cuestionario", response_class=HTMLResponse)
async def mostrar_cuestionario(request: Request, usuario_id: int = None):

    usuario = blindar_usuario(usuario_id)
    if not usuario:
        return RedirectResponse("/", status_code=303)

    # ❗ IMPORTANTE:
    # Quitamos el blindaje que redirigía al dashboard si ya había registro hoy.
    # Eso bloqueaba a usuarios nuevos.
    # El blindaje fuerte se mantiene en el POST.

    tip_del_dia = random.choice(TIPS)

    return templates.TemplateResponse(
        "cuestionario.html",
        {"request": request, "usuario_id": usuario_id, "tip_del_dia": tip_del_dia}
    )


# ---------------------------
#  CUESTIONARIO (POST)
# ---------------------------

@app.post("/cuestionario")
async def guardar_cuestionario(
    request: Request,
    usuario_id: int = Form(...),
    energia_social: int = Form(...),
    energia_fisica: int = Form(...),
    senales: str = Form(...),
    drenantes: Optional[str] = Form(None),
    reguladoras: Optional[str] = Form(None),
    emocion: str = Form(...),
    necesidades: Optional[str] = Form(None),
    diario_texto: Optional[str] = Form(None)
):

    usuario = blindar_usuario(usuario_id)
    if not usuario:
        return RedirectResponse("/", status_code=303)

    # Normalización
    senales_valores = {
        "Dolor de cabeza": 1, "Cansancio": 2, "Palpitaciones": 1,
        "Tensión muscular": 2, "Estómago revuelto": 1, "Respiración acelerada": 1,
        "Tranquil@": 4, "Neutr@": 3, "Estable": 4, "Energética": 5
    }

    emociones_valores = {
        "Triste": 1, "Ansiosa": 2, "Irritable": 2, "Estresada": 2, "Cansada": 2,
        "Neutra": 3, "Tranquila": 4, "En paz": 4, "Alegre": 5, "Motivada": 5
    }

    valor_senal = senales_valores.get(senales, 3)
    valor_emocion = emociones_valores.get(emocion, 3)

    senal_norm = valor_senal * 2
    emocion_norm = valor_emocion * 2

    indice = (energia_social + energia_fisica + senal_norm + emocion_norm) / 4

    if drenantes and drenantes.strip():
        indice -= 1

    indice_entero = max(1, min(round(indice), 10))
    frase_final = FRASES_ZENIT[indice_entero][0]

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    # BLINDAJE: un solo registro por día
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM registros
        WHERE usuario_id = ? AND fecha = ?
    """, (usuario_id, fecha_hoy))

    existe = cursor.fetchone()

    datos = {
        "fecha": fecha_hoy,
        "energia_social": energia_social,
        "energia_fisica": energia_fisica,
        "senales": senales,
        "drenantes": drenantes or "",
        "reguladoras": reguladoras or "",
        "emocion": emocion,
        "necesidades": necesidades or "",
        "notas": "",
        "indice_zenit": float(indice_entero),
        "frase": frase_final,
        "diario_texto": diario_texto or ""
    }

    if existe:
        cursor.execute("""
            UPDATE registros SET
                energia_social = :energia_social,
                energia_fisica = :energia_fisica,
                senales = :senales,
                drenantes = :drenantes,
                reguladoras = :reguladoras,
                emocion = :emocion,
                necesidades = :necesidades,
                indice_zenit = :indice_zenit,
                frase = :frase,
                diario_texto = :diario_texto
            WHERE usuario_id = :usuario_id AND fecha = :fecha
        """, {**datos, "usuario_id": usuario_id})
    else:
        guardar_registro(usuario_id, datos)

    conn.commit()
    conn.close()

    # Guardar reguladores y drenantes
    if reguladoras:
        for r in reguladoras.split(","):
            if r.strip():
                guardar_regulador(usuario_id, r.strip().lower(), fecha_hoy)

    if drenantes:
        for d in drenantes.split(","):
            if d.strip():
                guardar_drenante(usuario_id, d.strip().lower(), fecha_hoy)

    actualizar_indice_diario(usuario_id, fecha_hoy)

    return templates.TemplateResponse(
        "resultado.html",
        {"request": request, "index_val": indice_entero, "frase": frase_final, "usuario_id": usuario_id}
    )


# ---------------------------
#  DASHBOARD
# ---------------------------

@app.get("/dashboard", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request, usuario_id: int = None):

    usuario = blindar_usuario(usuario_id)
    if not usuario:
        return RedirectResponse("/", status_code=303)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM registros
        WHERE usuario_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (usuario_id,))
    registro = cursor.fetchone()

    if not registro:
        return RedirectResponse(f"/cuestionario?usuario_id={usuario_id}", status_code=303)

    fecha = registro["fecha"]

    reguladores_dia = obtener_reguladores(usuario_id, fecha)
    drenantes_dia = obtener_drenantes(usuario_id, fecha)

    dias_semana, valores_semana = obtener_semana(usuario_id)

    indice = int(registro["indice_zenit"])
    porcentaje = indice * 10

    if indice <= 2:
        emoji = "😞"
    elif indice <= 4:
        emoji = "😐"
    elif indice <= 6:
        emoji = "🙂"
    elif indice <= 8:
        emoji = "😊"
    else:
        emoji = "🤩"

    frase_dashboard = FRASES_ZENIT[indice][0]

    cursor.execute("""
        SELECT regulador, COUNT(*) AS veces
        FROM reguladores_historial
        WHERE usuario_id = ?
        AND fecha >= DATE('now', '-30 days')
        GROUP BY regulador
        ORDER BY veces DESC
    """, (usuario_id,))
    reguladores_top = cursor.fetchall()

    cursor.execute("""
        SELECT drenante, COUNT(*) AS veces
        FROM drenantes_historial
        WHERE usuario_id = ?
        AND fecha >= DATE('now', '-30 days')
        GROUP BY drenante
        ORDER BY veces DESC
    """, (usuario_id,))
    drenantes_top = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "usuario_id": usuario_id,
            "nombre_usuario": usuario["nombre"],
            "emoji_dia": emoji,
            "frase_ia": frase_dashboard,
            "energia_social": registro["energia_social"],
            "energia_fisica": registro["energia_fisica"],
            "emocion": registro["emocion"],
            "trigger": registro["senales"],
            "indice_zenit": porcentaje,
            "reguladores": reguladores_dia,
            "drenantes": drenantes_dia,
            "semana_valores": valores_semana,
            "semana_dias": dias_semana,
            "diario_texto": registro["diario_texto"],
            "reguladores_top": reguladores_top,
            "drenantes_top": drenantes_top,
        }
    )


# ---------------------------
#  DIARIO PERSONAL
# ---------------------------

@app.get("/diario", response_class=HTMLResponse)
async def ver_diario(request: Request, usuario_id: int = None):

    usuario = blindar_usuario(usuario_id)
    if not usuario:
        return RedirectResponse("/", status_code=303)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            fecha,
            MAX(diario_texto) AS diario_texto,
            MAX(necesidades) AS necesidades
        FROM registros
        WHERE usuario_id = ?
        GROUP BY fecha
        ORDER BY fecha DESC
    """, (usuario_id,))

    diarios = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "diario_historial.html",
        {"request": request, "usuario_id": usuario_id, "diarios": diarios}
    )


# ---------------------------
#  GUARDAR DIARIO (AJAX)
# ---------------------------

@app.post("/guardar_diario")
async def guardar_diario(usuario_id: int = Form(...), texto: str = Form("")):

    usuario = blindar_usuario(usuario_id)
    if not usuario:
        return {"status": "error"}

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM registros
        WHERE usuario_id = ? AND fecha = ?
    """, (usuario_id, fecha_hoy))

    existe = cursor.fetchone()

    if existe:
        cursor.execute("""
            UPDATE registros
            SET diario_texto = ?
            WHERE usuario_id = ? AND fecha = ?
        """, (texto, usuario_id, fecha_hoy))
    else:
        cursor.execute("""
            INSERT INTO registros (usuario_id, fecha, diario_texto)
            VALUES (?, ?, ?)
        """, (usuario_id, fecha_hoy, texto))

    conn.commit()
    conn.close()

    return {"status": "ok"}
