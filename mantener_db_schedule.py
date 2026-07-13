import schedule
import time
import subprocess
import os
import sys

PROJECT_DIR = r'C:\Users\annet\Día5\Webhooks-y-bots-conversacionales'
PYTHON_EXE = os.path.join(PROJECT_DIR, 'venv', 'Scripts', 'python.exe')
os.chdir(PROJECT_DIR)

def ejecutar_scraper():
    print(f"[{time.ctime()}] Ejecutando scraper...")
    subprocess.run([PYTHON_EXE, "-m", "data.scrapers.web_scraper"], cwd=PROJECT_DIR)
    print(f"[{time.ctime()}] Scraper finalizado.")

# Programa cada 4 horas
schedule.every(4).hours.do(ejecutar_scraper)

# Primera ejecución inmediata
ejecutar_scraper()

while True:
    schedule.run_pending()
    time.sleep(60)  # Verifica cada minuto