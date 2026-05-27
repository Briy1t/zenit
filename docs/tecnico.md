# OCUMENTACIÓN TÉCNICA INTERNA – EVOLUCIÓN DEL PROYECTO
Proyecto: ZENIT  
Autora: Briyit 

## 1) Inicio del proyecto: MindBalance (versión Flask)
El proyecto comenzó como una aplicación simple llamada MindBalance, construida con:

- index.html
- app.py (Flask)
- datos.json
- styles.css

El objetivo inicial era registrar el estado diario del usuario mediante un formulario HTML.

### 1.1 Estructura inicial del formulario
El formulario incluía:

- Energía social (0–10)
- Energía física (0–10)
- Señales corporales
- Drenantes
- Reguladoras
- Necesidades para mañana
- Estado emocional
- Notas adicionales
- Los datos se enviaban mediante:

```bahs
<form action="/guardar" method="POST">
```
Y se almacenaban en:

```bahs
datos.json
```

## 1.2 Tecnologías usadas

- Flask
- HTML + CSS
- FontAwesome
- Google Fonts
- JavaScript simple

### 1.3 Limitaciones detectadas

- JSON no era escalable
- No había sesiones ni usuarios
- No existía dashboard
- No había análisis ni visualizaciones
- No había separación entre frontend y backend

## 2) Evolución del proyecto: de formulario simple a sistema con IA (Flask)
El proyecto creció hacia un sistema que analizaba el estado emocional del usuario y generaba un dashboard.

### 2.1 Mejoras visuales (styles_v2.css)
Se añadieron:

- Variables CSS
- Tema oscuro
- Contenedores con sombras
- Inputs estilizados
- Scrollbar personalizada
- Botón con gradiente
- Tipografías Urbanist y JetBrains Mono

### 2.2 Integración de IA semántica
Se instalaron:

- openai
- torch
- jinja2

La IA analizaba:

- Señales corporales
- Emociones 
- Energia social
- Energia fisica 
- Notas adicionales

Y generaba:

- Factores de bajón
- Factores de regulación
- Frase del día segun el puntaje 

Índice emocional

### 2.3 Persistencia en JSON
Se mantuvo datos.json, pero surgieron limitaciones:

- No permitía múltiples usuarios
- No permitía consultas complejas
- No era seguro
- No permitía dashboards avanzados

### 2.4 Primer dashboard (Flask)
Se creó dashboard.html con:

- Índice del día
- Promedio semanal
- Cambio respecto a ayer
- Frase del día
- Factores de bajón
- Factores de regulación

Gráfico PNG generado por Flask

### 2.5 Limitaciones de Flask

- Sesiones limitadas
- Estructura difícil de escalar
- IA lenta
- JSON insuficiente
- Lógica mezclada con presentación

Esto llevó a la decisión de migrar a FastAPI.

## 3) Migración de Flask a FastAPI
La migración requirió reescribir todo el backend.

### 3.1 Reestructuración completa
Se eliminó app.py y se creó:

```Código
main.py
```
Responsable de:

- Endpoints
- Plantillas
- Formularios
- Conexión a SQLite
- Lógica del cuestionario
- Dashboard
- Autenticación

### 3.2 Eliminación de código heredado de Flask
Problemas encontrados:

- Decoradores antiguos (@app.route)
- Uso de render_template
- Uso de request.form
- Plantillas que no cargaban

Solución:

- Reemplazar por @app.get y @app.post

```text
 Antes (Flask)


python
@app.route('/ruta', methods=['GET'])
@app.route('/ruta', methods=['POST'])


Ahora (FastAPI)


python
@app.get('/ruta')
@app.post('/ruta')
```

- Usar TemplateResponse
- Usar Form()
- Eliminar todo rastro de Flask

### 3.3 Problemas con dependencias y entorno virtual
Errores como:

```Código
python-multipart is required to use Form
```

Solución:

- Instalar python-multipart
- Crear entorno virtual venv/
- Instalar Python 3.12.1

### 3.4 Creación del módulo de autenticación (auth.py)
Se creó auth.py con funciones para:

- Registrar usuario
- Validar credenciales
- Redirigir al cuestionario
- Manejar errores

Encriptación de contraseñas 

Para mejorar la seguridad:

- Se implementó hashing con bcrypt 
- Nunca se guarda la contraseña en texto plano

Proceso:

- La contraseña se convierte en hash al registrarse
- Se almacena el hash en la base de datos
- En el login se compara la contraseña ingresada con el hash

Esto garantiza:

- Seguridad ante filtraciones
- Imposibilidad de recuperar la contraseña original
- Buenas prácticas de autenticación

### 3.5 IA semántica (fase intermedia)
Se instaló:

- transformers
- torch

Problemas:

- Lenta
- Inestable
- Incoherente
- Consumía demasiada memoria
- Fallaba con texto vacío

Se decidió eliminar la IA.

### 3.6 Rediseño del cuestionario
Se reemplazó texto libre por:

- Listas de emociones
- Listas de sensaciones corporales
- Campos libres solo para drenantes y reguladores

### 3.7 Problemas con SQLite
Errores como:

```text
TypeError: 'NoneType' object is not subscriptable
```

Causados por:

- Campos opcionales vacíos
- Registros incompletos

Solución:

- Validaciones
- Valores por defecto
- Manejo de None
- Reescritura de consultas

### 3.8 Dashboard en FastAPI
Incluía:

- Índice diario
- Promedio semanal
- Frase del día
- Factores de regulación y desregulación
- Gráficos dinámicos

Problemas:

- Gráficos no cambiaban
- Frases incorrectas
- Rutas con lógica antigua de IA

Solución:

- Reescritura completa del cálculo del índice
- Limpieza de lógica heredada
- Separación entre datos diarios y mensuales

### 3.9 Rediseño visual
Se abandonó el azul y se adoptó:

- Fondo cielo
- Colores suaves
- simbolo de un cohete 
- Estética emocional

### 3.10 Gota emocional dinámica
Intento inicial: cohete SVG → falló por capas complejas.
Solución:

- Crear una gota emocional
- Cambia de color
- Cambia de expresión
- Se anima con gota.js

### 3.11 Diario personal y “Dibuja aquí”
Se añadió:

- Diario personal
- Canvas para dibujar

El dibujo:

- Se descarga como imagen
- No se guarda en la base de datos

### 3.12 Dashboard mensual
Se añadieron:

- Factores más repetidos del mes
- Porcentajes
- Contadores

Nuevas consultas SQL

## 4) Ajustes finales del dashboard
Reorganización visual

- Márgenes y jerarquía
- Nombre del usuario en tablas

## 5) Problemas con el diario personal

### 5.1 Endpoint incorrecto
El diario se guardaba dentro del cuestionario → datos mezclados.

Solución:

- Endpoint independiente
- Tabla/campo separado

### 5.2 Botón en contenedor incorrecto
El diario no se enviaba porque el botón pertenecía al formulario equivocado.

Solución:

- Botón “Guardar diario” independiente
- POST separado

## 6) Seguridad del flujo
En main.py se añadió:
- Verificación de sesión
- Redirección si no hay autenticación
- Protección de rutas sensibles