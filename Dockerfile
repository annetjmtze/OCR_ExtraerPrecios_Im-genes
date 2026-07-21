FROM python:3.14-slim

# Instalar dependencias del sistema (incluyendo algunas que Playwright necesita)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# NO instalar Chromium desde apt, dejamos que Playwright lo maneje

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y los browsers (esto descarga en ~/.cache/ms-playwright)
RUN playwright install chromium

# Copiar el resto del código
COPY . .

# Limpiar cualquier variable de entorno que pueda interferir
ENV PLAYWRIGHT_BROWSERS_PATH=""
ENV CHROME_PATH=""

CMD ["python", "scheduler.py"]