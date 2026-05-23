from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from app.auth import crear_usuario, obtener_usuario, verify_password

from app.database import (
    create_tables,
    get_connection,
    crear_tabla_registros,
    crear_tabla_indices_diarios,
    guardar_registro,
    actualizar_indice_diario,
    crear_tablas_historial,
    guardar_regulador,
    guardar_drenante
)

from app.logger import registrar_evento

from ia_local import clasificar_texto_local
from datetime import datetime


# Inicializar BD
create_tables()
crear_tabla_registros()
crear_tabla_indices_diarios()
crear_tablas_historial()



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------------
#  RUTAS
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
            {
                "request": request,
                "error": "El usuario no existe. ¿Quieres registrarte?"
            }
        )

    if not verify_password(clave, user["clave_hash"]):
        return templates.TemplateResponse(
            "bienvenida.html",
            {
                "request": request,
                "error": "La clave es incorrecta."
            }
        )

    # PRIMERA VEZ → no tiene registros
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM registros WHERE usuario_id = ?", (user["id"],))
    total = cursor.fetchone()[0]
    conn.close()

    if total == 0:
        return RedirectResponse(
            url=f"/cuestionario?usuario_id={user['id']}",
            status_code=303
        )

    return RedirectResponse(
        url=f"/dashboard?usuario_id={user['id']}",
        status_code=303
    )


# ---------------------------
#  REGISTRO DE USUARIO
# ---------------------------

@app.get("/registro")
async def registro(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})


@app.post("/registro")
async def registro_post(
    request: Request,
    nombre: str = Form(...),
    clave: str = Form(...)
):
    try:
        crear_usuario(nombre, clave)
        user = obtener_usuario(nombre)

        return RedirectResponse(
            url=f"/cuestionario?usuario_id={user['id']}",
            status_code=303
        )

    except Exception as e:
        return templates.TemplateResponse(
            "registro.html",
            {
                "request": request,
                "error": "Ese nombre ya existe. Intenta con otro."
            }
        )



# ---------------------------
#  AUDITORÍA
# ---------------------------

@app.get("/auditoria")
async def ver_auditoria():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM auditoria ORDER BY fecha DESC")
    datos = cursor.fetchall()

    conn.close()
    return {"auditoria": [dict(row) for row in datos]}


# ---------------------------
#  CUESTIONARIO (GET)
# ---------------------------

@app.get("/cuestionario", response_class=HTMLResponse)
async def mostrar_cuestionario(request: Request, usuario_id: int):
    return templates.TemplateResponse(
        "cuestionario.html",
        {
            "request": request,
            "usuario_id": usuario_id
        }
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
    drenantes: str = Form(...),
    reguladoras: str = Form(...),
    emocion: str = Form(...),
    necesidades: str = Form(...),
    notas: str = Form("")
):

    # IA semántica
    senales_score = clasificar_texto_local(senales)
    drenantes_score = clasificar_texto_local(drenantes)
    reguladoras_score = clasificar_texto_local(reguladoras)
    emocion_score = clasificar_texto_local(emocion)

    # Cálculo del índice
    indice_zenit = (
        energia_social +
        energia_fisica +
        senales_score +
        drenantes_score +
        reguladoras_score +
        emocion_score
    ) / 6

    # Frase del día
    FRASES = {
        1: "Tu sistema está saturado 😵‍💫 Descansar también es avanzar.",
        2: "Has sostenido más de lo que parece 💜 Sé amable contigo.",
        3: "Tu equilibrio es moderado 😌 Mantén tus reguladores cerca.",
        4: "Día sólido ✨ Aprovecha tu claridad.",
        5: "Día brillante 🚀 Tu sistema está en su punto más alto."
    }

    nivel = max(1, min(int(round(indice_zenit)), 5))
    frase = FRASES[nivel]

    # Datos para guardar
    datos = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "energia_social": energia_social,
        "energia_fisica": energia_fisica,
        "senales": senales,
        "drenantes": drenantes,
        "reguladoras": reguladoras,
        "emocion": emocion,
        "necesidades": necesidades,
        "notas": notas,
        "puntaje_ia": float(indice_zenit),
        "indice_zenit": float(indice_zenit),
        "frase": frase
    }

    # Guardar registro
    guardar_registro(usuario_id, datos)

    # Guardar reguladores uno por uno
    for r in reguladoras.split(","):
        if r.strip():
            guardar_regulador(usuario_id, r.strip(), datos["fecha"])

    # Guardar drenantes uno por uno
    for d in drenantes.split(","):
        if d.strip():
            guardar_drenante(usuario_id, d.strip(), datos["fecha"])

    # Actualizar índice diario
    actualizar_indice_diario(usuario_id, datos["fecha"])

    # RETURN FINAL
    return templates.TemplateResponse(
        "resultado.html",
        {
            "request": request,
            "index_val": round(indice_zenit, 1),
            "frase": frase,
            "usuario_id": usuario_id
        }
    )


# ---------------------------
#  DASHBOARD (GET)
# ---------------------------

@app.get("/dashboard", response_class=HTMLResponse)
async def mostrar_dashboard(request: Request, usuario_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM registros
        WHERE usuario_id = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (usuario_id,))
    registro = cursor.fetchone()

    conn.close()

    if not registro:
        return RedirectResponse(
            url=f"/cuestionario?usuario_id={usuario_id}",
            status_code=303
        )

    
    usuario = obtener_usuario_por_id(registro["usuario_id"])
    if not usuario:
        return RedirectResponse(
            url="/registro",
            status_code=303
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "nombre_usuario": usuario["nombre"],
            "emoji_dia": "😊",
            "frase_ia": registro["frase"],
            "energia_social": registro["energia_social"],
            "energia_fisica": registro["energia_fisica"],
            "emocion": registro["emocion"],
            "trigger": registro["senales"],
            "reguladores": registro["reguladoras"],
            "drenantes": registro["drenantes"]
        }
    )

