# 🚀 Bot de Telegram desplegado en Railway

Proyecto desarrollado para demostrar el despliegue de una aplicación utilizando **Railway**.

## 📋 Descripción
Este proyecto consiste en un bot de Telegram desarrollado en Python utilizando la librería `python-telegram-bot`. El bot responde a comandos básicos y consulta información sobre medicamentos mediante la API de Anthropic (Claude).

La aplicación fue desplegada en Railway utilizando Webhooks de Telegram.

---

# 🛠️ Tecnologías utilizadas

- Python 3.10 o superior
- python-telegram-bot
- Anthropic API
- python-dotenv
- Railway
- Git
- GitHub

---

# 📁 Estructura del proyecto

```
Deployment-Real-Railway/
│── main.py
│── requirements.txt
│── README.md
│── .gitignore
│── .env.example
```

---

# ⚙️ Requisitos

Antes de comenzar es necesario tener instalado:

- Python 3.10 o superior
- pip
- Git

Opcional:

- Railway CLI

---
# 🔄 Funcionamiento

El bot utiliza Webhooks para recibir los mensajes enviados por Telegram.

Cuando un usuario envía un mensaje:

1. Telegram envía una petición POST al endpoint `/webhook`.
2. Railway recibe la petición.
3. El bot procesa el mensaje.
4. Si se utiliza el comando `/medicamento`, el bot consulta la API de Anthropic y devuelve la información obtenida.
5. Para cualquier otro mensaje, responde repitiendo el texto recibido.

---
# 💻 Ejecutar el proyecto localmente

## 1. Clonar el repositorio

```bash
git clone https://github.com/annetjmtze/Deployment-Real-Railway.git
```

Entrar al proyecto

```bash
cd Deployment-Real-Railway
```

---

## 2. Crear un entorno virtual

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

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

## 4. Configurar las variables de entorno

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_TOKEN` | Token del bot generado con BotFather. |
| `ANTHROPIC_API_KEY` | API Key de Anthropic. |
| `WEBHOOK_URL` | URL pública generada por Railway. |
| `PORT` | Puerto asignado automáticamente por Railway. |

Ejemplo de archivo `.env`:

```env
TELEGRAM_TOKEN=xxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
WEBHOOK_URL=https://deployment-real-railway-production.up.railway.app
PORT=8080
```
---

## 5. Ejecutar la aplicación

```bash
python main.py
```

---

# ☁️ Deploy en Railway

## Opción 1 (Recomendada): Desde GitHub

1. Crear una cuenta en Railway.
2. Iniciar sesión con GitHub.
3. Seleccionar **New Project**.
4. Elegir **Deploy from GitHub Repo**.
5. Seleccionar este repositorio.
6. Railway detectará automáticamente el proyecto.
7. Configurar las variables de entorno necesarias.
8. Esperar a que termine el Build.
9. Abrir la URL generada por Railway.

Railway realizará nuevos despliegues automáticamente cada vez que se haga un **push** a la rama conectada, si el autodeploy está habilitado. 

---

## Opción 2: Utilizando Railway CLI

Instalar Railway CLI

```bash
npm install -g @railway/cli
```

Iniciar sesión

```bash
railway login
```

Inicializar el proyecto

```bash
railway init
```

Desplegar

```bash
railway up
```

Este comando sube el proyecto, construye la aplicación y realiza el despliegue automáticamente. 

---

# 🌐 URL del proyecto desplegado

<https://deployment-real-railway-production.up.railway.app>

> **Nota**
>
> Al acceder desde un navegador a la URL de Railway es normal obtener un **404 Not Found**.
>
> Esto se debe a que el proyecto corresponde a un bot de Telegram y únicamente expone el endpoint `/webhook`, utilizado por Telegram para enviar las actualizaciones del bot.
---
## 🤖 Comandos disponibles

- /start
- /ayuda
- /medicamento <nombre>

Ejemplo:

/medicamento Paracetamol

# 📦 Dependencias

Todas las dependencias se encuentran en:

```
requirements.txt
```

Para instalarlas:

```bash
pip install -r requirements.txt
```

---
## ✅ Prueba de funcionamiento

Para comprobar que el despliegue fue exitoso:

1. Buscar el bot en Telegram.
2. Enviar el mensaje:

```text
funciona
```

3. El bot responderá:

```text
funciona
```

Esta prueba verifica que el webhook está correctamente configurado y que Railway recibe y procesa las solicitudes enviadas por Telegram.
---
## 📷 Evidencia

Prueba de funcionamiento del bot desde una cuenta diferente a la de desarrollo.

![Prueba del bot](screenshots/prueba_funciona.png)

# 👩‍💻 Autor

**Annet Martínez**

Ingeniería en Tecnologías de la Información y Comunicaciones

GitHub: <https://github.com/annetjmtze>

Repositorio:
<https://github.com/annetjmtze/Deployment-Real-Railway>

Proyecto desplegado:
<https://deployment-real-railway-production.up.railway.app>

---