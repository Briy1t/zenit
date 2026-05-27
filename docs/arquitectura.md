# DOCUMENTACIÓN TÉCNICA – ARQUITECTURA DE ZENIT
Autora: Briyit

Este documento describe la arquitectura técnica de ZENIT, explicando las decisiones de diseño, los componentes utilizados y el propósito de cada uno dentro del sistema.

## 1) Visión general de la arquitectura

ZENIT está construido bajo una arquitectura cliente-servidor ligera, optimizada para simplicidad, seguridad y facilidad de mantenimiento.

La aplicación se divide en:

- Frontend: HTML + CSS + JavaScript (Jinja2 para plantillas)
- Backend: FastAPI
- Base de datos: SQLite
- Sesiones: Cookies firmadas
- Visualizaciones: Chart.js + SVG dinámico

Esta arquitectura permite:

- Carga rápida
- Bajo consumo de recursos
- Código fácil de extender
- Seguridad suficiente para un proyecto personal

## 2) Backend – FastAPI

### ¿Por qué FastAPI?

- Velocidad y eficiencia
- Sintaxis clara y moderna
- Manejo nativo de JSON
- Integración sencilla con plantillas
- Validación automática de datos
- Ideal para proyectos personales y APIs

### ¿Qué hace FastAPI en ZENIT?

- Gestiona rutas (/dashboard, /cuestionario, /diario, etc.)
- Procesa formularios
- Calcula el índice emocional
- Guarda y recupera datos de SQLite
- Maneja sesiones del usuario
- Renderiza plantillas HTML con Jinja2

## 3) Frontend – Jinja2 + HTML + CSS + JS

### ¿Por qué Jinja2?

- Permite generar HTML dinámico desde Python
- Facilita pasar datos del backend al frontend
- Evita usar frameworks pesados como React o Vue
- Perfecto para proyectos ligeros

### ¿Qué hace el frontend?

- Muestra la interfaz del cuestionario
- Renderiza la gota emocional
- Genera gráficos semanales
- Permite escribir y guardar el diario
- Muestra el historial de días

## 4) Base de datos – SQLite

### ¿Por qué SQLite?

- No requiere servidor
- Ideal para proyectos personales
- Muy rápida para lecturas pequeñas
- Fácil de versionar y migrar
- Perfecta para almacenar datos diarios

### ¿Qué guarda SQLite?

Tabla `registros`:

- Fecha
- Energía social
- Energía física
- Señales corporales
- Emoción
- Necesidades
- Drenantes
- Reguladoras
- Diario personal
- Índice ZENIT
- Frase del día
- Usuario (ID)

## 5) Sesiones – Cookies firmadas

### ¿Por qué cookies firmadas?

- No exponen datos sensibles
- No pueden ser modificadas por el usuario
- Son seguras y ligeras
- Evitan pasar `usuario_id` por la URL
- Mantienen el flujo protegido

### ¿Qué guardan?
- usuario_id

## 6) Visualizaciones – Chart.js + SVG

### Chart.js

Usado para:

- Gráfico semanal
- Gráfico de reguladores
- Gráfico de drenantes
- Estadísticas del mes

### SVG dinámico (gota emocional)

- Cambia de color
- Cambia de tamaño
- Cambia de expresión

## 7) Estructura del proyecto
```text
/zenit
├── main.py
├── requirements.txt
├── README.md
├── /templates
├── /static
└── /docs
```


## 8) Flujo de datos

1. Usuario inicia sesión
2. Usuario completa el cuestionario
3. Usuario guarda el diario
4. Dashboard genera estadísticas
5. Historial muestra días anteriores

## 9) Decisiones de diseño

- Simplicidad
- Seguridad mínima pero sólida
- Arquitectura ligera
- Datos locales
- Interfaz emocional y visual

## 10) Limitaciones actuales

- No hay API externa
- No hay autenticación avanzada
- No hay exportación de datos

## 11) Próximos pasos

- Añadir JWT
- Exportar diario a PDF
- Modo oscuro
- Estadísticas mensuales

