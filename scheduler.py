"""
Scheduler automático para scraping con APScheduler.
Se ejecuta en Railway como un proceso independiente.
"""
import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# FUNCIONES DE SCRAPING (importar desde tus módulos)
# ============================================================
def run_web_scraper():
    """Ejecuta el web scraper de farmacias."""
    logger.info("🕷️ Ejecutando web scraper...")
    try:
        # Importar y ejecutar tu web scraper
        from data.scrapers.web_scraper import main as web_scraper_main
        web_scraper_main()
        logger.info("✅ Web scraper finalizado correctamente")
    except Exception as e:
        logger.error(f"❌ Error en web scraper: {e}")

def run_playwright_agents():
    """Ejecuta los agentes de Playwright (Rappi y Uber Eats)."""
    logger.info("🎭 Ejecutando agentes Playwright...")
    try:
        # Lista de medicamentos a monitorear
        medicamentos = ["paracetamol", "ibuprofeno", "diclofenaco", 
                       "fluoxetina", "metformina", "omeprazol", 
                       "losartan", "naproxeno"]
        
        for med in medicamentos:
            logger.info(f"   🔍 Buscando {med}...")
            # Importar y ejecutar playwright_agent
            from data.agents.playwright_agent import main as playwright_main
            playwright_main(med)
        
        logger.info("✅ Agentes Playwright finalizados correctamente")
    except Exception as e:
        logger.error(f"❌ Error en agentes Playwright: {e}")

def run_all_scrapers():
    """Ejecuta todo el pipeline de scraping."""
    logger.info("=" * 60)
    logger.info(f"🚀 INICIANDO PIPELINE COMPLETO - {datetime.now()}")
    logger.info("=" * 60)
    
    run_web_scraper()
    run_playwright_agents()
    
    logger.info("=" * 60)
    logger.info(f"✅ PIPELINE COMPLETADO - {datetime.now()}")
    logger.info("=" * 60)

# ============================================================
# CONFIGURAR Y ARRANCAR SCHEDULER
# ============================================================
def start_scheduler():
    """Inicia el scheduler con las tareas programadas."""
    logger.info("⏰ Iniciando APScheduler...")
    
    scheduler = BackgroundScheduler()
    
    # Tarea 1: Scraping completo cada 6 horas
    scheduler.add_job(
        run_all_scrapers,
        trigger=IntervalTrigger(hours=6),
        id='scraping_completo',
        name='Scraping completo cada 6h',
        replace_existing=True
    )
    logger.info("   📅 Programado: scraping completo cada 6 horas")
    
    # Tarea 2: Solo agentes Playwright cada 12 horas (Rappi/Uber)
    scheduler.add_job(
        run_playwright_agents,
        trigger=IntervalTrigger(hours=12),
        id='playwright_agents',
        name='Agentes Playwright cada 12h',
        replace_existing=True
    )
    logger.info("   📅 Programado: agentes Playwright cada 12 horas")
    
    scheduler.start()
    logger.info("✅ Scheduler iniciado correctamente")
    
    # Ejecutar una vez al arrancar (opcional, pero recomendado)
    logger.info("🔄 Ejecutando primer ciclo inmediatamente...")
    run_all_scrapers()
    
    return scheduler

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🐘 DR. AHORRO - SCHEDULER AUTOMÁTICO")
    logger.info(f"📦 Entorno: {'PRODUCCIÓN (PostgreSQL)' if os.getenv('DATABASE_URL') else 'DESARROLLO (SQLite)'}")
    logger.info("=" * 60)
    
    scheduler = start_scheduler()
    
    try:
        # Mantener el proceso vivo
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("⏹️ Deteniendo scheduler...")
        scheduler.shutdown()
        logger.info("👋 Scheduler detenido")