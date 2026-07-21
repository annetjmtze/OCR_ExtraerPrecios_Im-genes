FROM python:3.14-slim

# Instalar dependencias del sistema y Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Descargar e instalar Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright (para que tenga los controladores necesarios, pero usaremos Chrome del sistema)
RUN playwright install

# Variables de entorno para que Playwright use Chrome del sistema
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV CHROME_PATH=/usr/bin/google-chrome-stable

# Copiar el código fuente
COPY . .

# Comando por defecto (se sobrescribe en Railway si es necesario)
CMD ["python", "scheduler.py"]