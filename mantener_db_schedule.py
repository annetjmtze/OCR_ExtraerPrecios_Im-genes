import schedule
import time
import subprocess
import os
import sys

PROJECT_DIR = r'C:\Users\annet\Día5\Webhooks-y-bots-conversacionales'
PYTHON_EXE = os.path.join(PROJECT_DIR, 'venv', 'Scripts', 'python.exe')
os.chdir(PROJECT_DIR)

def ejecutar_scraper_web():
    print(f"[{time.ctime()}] Ejecutando web scraper...")
    subprocess.run([PYTHON_EXE, "-m", "data.scrapers.web_scraper"], cwd=PROJECT_DIR)
    print(f"[{time.ctime()}] Web scraper finalizado.")

def ejecutar_playwright(medicamentos=None):
    if medicamentos is None:
        # Lista de los medicamentos que quieres mantener frescos
        medicamentos = ["paracetamol", "ibuprofeno", "diclofenaco", "fluoxetina", 
                        "metformina", "omeprazol", "losartan", "naproxeno"]
    for med in medicamentos:
        print(f"[{time.ctime()}] Playwright → {med}...")
        subprocess.run([PYTHON_EXE, "data/agents/playwright_agent.py", med], cwd=PROJECT_DIR)
        time.sleep(5)  # Pequeña pausa para no saturar

# Programa cada 4 horas
schedule.every(4).hours.do(ejecutar_scraper_web)
# Playwright cada 6 horas, por ejemplo
schedule.every(6).hours.do(ejecutar_playwright)

# Si también quisieras un OCR programado (usualmente se usa bajo demanda, pero puedes agregarlo):
# def ejecutar_ocr():
#     ...

# Primera ejecución inmediata
ejecutar_scraper_web()
ejecutar_playwright()

while True:
    schedule.run_pending()
    time.sleep(60)