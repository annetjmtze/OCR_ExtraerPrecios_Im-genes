# 🤖 Dr. Ahorro Bot

> Bot conversacional multicanal para consultar información y precios públicos de medicamentos en México utilizando **Claude (Anthropic)** como motor de inteligencia artificial y **Web Scraping** para obtener precios reales desde farmacias con sitios web.

---

# 📌 Tabla de Contenidos

- [🚀 Características](#-características)
- [🛠️ Tecnologías](#️-tecnologías)
- [🧠 Arquitectura](#-arquitectura)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [📋 Requisitos Previos](#-requisitos-previos)
- [⚙️ Instalación y Configuración](#️-instalación-y-configuración)
- [🚀 Uso](#-uso)
- [🌐 Web Scraping de Farmacias](#-web-scraping-de-farmacias)
- [🔧 Variables de Entorno](#-variables-de-entorno)
- [🧪 Posibles Errores y Soluciones](#-posibles-errores-y-soluciones)
- [🚧 Mejoras Futuras](#-mejoras-futuras)
- [🙏 Créditos](#-créditos)
- [📜 Licencia](#-licencia)

---

# 🚀 Características

- ✅ Funciona tanto en **Telegram** como en **WhatsApp**.
- ✅ Utiliza **Claude (Anthropic)** para interpretar consultas sobre medicamentos.
- ✅ Obtiene precios públicos mediante **Web Scraping** desde farmacias con sitios web.
- ✅ Guarda los resultados del scraping en formato **JSON**.
- ✅ Arquitectura modular y fácil de mantener.
- ✅ Respuestas adaptadas al formato de cada plataforma.
- ✅ Fácil de extender a nuevos canales como Discord o Messenger.
- ✅ Registro automático del webhook de WhatsApp.

---

# 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3.14+ | Lenguaje principal |
| Flask | Webhook para WhatsApp |
| Twilio API | Integración con WhatsApp |
| python-telegram-bot | Bot de Telegram |
| Anthropic Claude | Procesamiento mediante IA |
| Requests | Solicitudes HTTP |
| BeautifulSoup4 | Extracción de información HTML |
| lxml | Parser HTML |
| python-dotenv | Variables de entorno |
| ngrok | Exposición del servidor local |

---

# 🧠 Arquitectura

```text
                         Telegram
                             │
                             ▼
                  ┌────────────────────┐
                  │ Telegram Handler   │
                  └─────────┬──────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │ Claude (Anthropic LLM) │
                │ Normalizador           │
                └─────────┬──────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │                                    │
        ▼                                    ▼
 Web Scraper                         WhatsApp Handler
(Requests + BS4)                            │
        │                                   ▼
        ▼                          Flask + Webhook
 resultados_farmacias.json                │
                                          ▼
                                      WhatsApp
```

### Principio de diseño

El sistema está dividido en módulos independientes.

- Los **handlers** reciben los mensajes desde Telegram y WhatsApp.
- El **normalizador** procesa la consulta mediante Claude.
- El **módulo de Web Scraping** consulta precios públicos cuando es necesario.
- Los resultados del scraping se almacenan en archivos JSON para su reutilización y análisis.

---

# 📁 Estructura del Proyecto

```text
dr-ahorro-bot/
│
├── bot/
│   ├── __init__.py
│   ├── telegram_handler.py
│   └── whatsapp_handler.py
│
├── config/
│   └── __init__.py
│
├── data/
│   ├── __init__.py
│   └── scrapers/
│       ├── web_scraper.py
│       └── resultados_farmacias.json
│
├── llm/
│   ├── __init__.py
│   └── normalizer.py
│
├── screenshots/
│
├── hallazgos_scraping.md
├── .env
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

# 📋 Requisitos Previos

Antes de ejecutar el proyecto necesitas:

- Python 3.14 o superior
- Cuenta de Anthropic
- Cuenta de Twilio
- Bot creado mediante BotFather
- ngrok instalado

---

# ⚙️ Instalación y Configuración

## 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/dr-ahorro-bot.git

cd dr-ahorro-bot
```

---

## 2. Crear un entorno virtual

### Windows

```cmd
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

Copiar el archivo:

```bash
cp .env.example .env
```

Completar las credenciales:

```env
# Telegram
TELEGRAM_BOT_TOKEN=

# Claude
ANTHROPIC_API_KEY=

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

# Webhook
WEBHOOK_URL=https://xxxxx.ngrok-free.app/webhook

PORT=5000
```

---

## 5. Ejecutar ngrok

```bash
ngrok http 5000
```

Actualizar la URL pública en:

```env
WEBHOOK_URL=https://tu-url.ngrok-free.app/webhook
```

---

# 🚀 Uso

## Ejecutar únicamente Telegram

```bash
python main.py --channel telegram
```

---

## Ejecutar únicamente WhatsApp

```bash
python main.py --channel whatsapp --port 5000
```

---

## Ejecutar ambos canales

```bash
python main.py --channel all
```

---

# 🌐 Web Scraping de Farmacias

El proyecto incorpora un módulo de **Web Scraping** encargado de consultar precios públicos de medicamentos disponibles en farmacias mexicanas con sitios web.

## Objetivo

Obtener precios reales para complementar la información proporcionada por el bot.

## Tecnologías utilizadas

- Requests
- BeautifulSoup4
- Selectores CSS
- HTML estático

## Ejecutar el scraper

```bash
python data/scrapers/web_scraper.py
```

## Resultado

Los datos obtenidos se almacenan automáticamente en:

```text
data/scrapers/resultados_farmacias.json
```

Ejemplo de salida:

```json
{
    "medicamento_buscado": "Paracetamol",
    "nombre_encontrado": "Paracetamol 500 mg",
    "farmacia": "Farmacia de ejemplo",
    "precio": 49.50,
    "precio_promedio": 38.00,
    "vigencia_precio": "2026-07-15",
    "url_producto": "https://...",
    "fuente": "scrape_web",
    "fecha_consulta": "2026-07-07T10:30:00"
}
```

Durante el desarrollo también se documentan observaciones técnicas en:

```text
hallazgos_scraping.md
```

En este archivo se registran:

- Farmacias evaluadas.
- Sitios compatibles con scraping.
- Problemas encontrados.
- Técnicas utilizadas.
- Hallazgos durante la implementación.

---

# 🔧 Variables de Entorno

| Variable | Descripción | Obligatoria |
|-----------|-------------|-------------|
| TELEGRAM_BOT_TOKEN | Token del bot de Telegram | ✅ |
| ANTHROPIC_API_KEY | API Key de Claude | ✅ |
| TWILIO_ACCOUNT_SID | Cuenta de Twilio | WhatsApp |
| TWILIO_AUTH_TOKEN | Token de Twilio | WhatsApp |
| TWILIO_WHATSAPP_NUMBER | Número Sandbox | WhatsApp |
| WEBHOOK_URL | URL pública de ngrok | WhatsApp |
| PORT | Puerto de Flask | No |

---

# 🧪 Posibles Errores y Soluciones

| Error | Solución |
|--------|----------|
| ModuleNotFoundError | Ejecutar `pip install -r requirements.txt` |
| Error 404 en Telegram | Verificar el Token del bot |
| Webhook no registrado | Revisar la URL pública de ngrok |
| Claude no responde | Verificar la API Key |
| WhatsApp no responde | Revisar Twilio y el webhook |
| Error durante el scraping | Verificar la estructura HTML del sitio o actualizar los selectores CSS |

---

# 🚧 Mejoras Futuras

- Consultar múltiples farmacias automáticamente.
- Implementar Selenium para sitios con JavaScript.
- Integrar OCR para obtener precios desde imágenes.
- Calcular el precio promedio entre diferentes farmacias.
- Almacenar el historial de consultas.
- Agregar una base de datos para persistencia de resultados.
- Exponer una API REST para consultar medicamentos y precios.

---

# 🙏 Créditos

Proyecto desarrollado con fines educativos para practicar:

- Arquitectura de software en Python.
- Bots conversacionales.
- Integración con Telegram.
- Integración con WhatsApp mediante Twilio.
- Webhooks con Flask.
- Consumo de APIs.
- Modelos LLM con Anthropic Claude.
- Técnicas de Web Scraping con Requests y BeautifulSoup.

---

# 📜 Licencia

Este proyecto fue desarrollado con fines académicos y educativos.

---

⭐ Si este proyecto te resulta útil, considera darle una estrella al repositorio.