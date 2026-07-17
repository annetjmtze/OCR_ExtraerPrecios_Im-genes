import os
import sys
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# ── Configurar path ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Importar agentes ──
from data.agents.playwright_agent import main as playwright_main
from data.agents.rappi_agent import RappiAgent
from data.agents.ubereats_agent import UberEatsAgent
from data.database import init_db, get_connection, contar_por_fuente

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================
# FUNCIONES ASÍNCRONAS PARA CADA AGENTE
# ============================================================

async def ejecutar_agentes_delivery():
    """Ejecuta los agentes de Rappi y Uber Eats para medicamentos clave."""
    medicamentos = [
        "paracetamol 500mg",
        "ibuprofeno 400mg",
        "omeprazol 20mg",
        "naproxeno 500mg"
    ]
    
    rappi = RappiAgent(headless=True)
    ubereats = UberEatsAgent(headless=True)
    
    for med in medicamentos:
        logger.info(f"🔍 Buscando {med} en Rappi...")
        try:
            await rappi.search_medication(med)
        except Exception as e:
            logger.error(f"❌ Error en Rappi para {med}: {e}")
        
        logger.info(f"🔍 Buscando {med} en Uber Eats...")
        try:
            await ubereats.search_medication(med)
        except Exception as e:
            logger.error(f"❌ Error en Uber Eats para {med}: {e}")

async def ejecutar_agentes_playwright():
    """Ejecuta los agentes Playwright (farmacias físicas) para medicamentos clave."""
    medicamentos = [
        "paracetamol",
        "ibuprofeno",
        "omeprazol",
        "naproxeno",
        "metformina",
        "losartan"
    ]
    
    for med in medicamentos:
        logger.info(f"🎭 Ejecutando Playwright para {med}...")
        try:
            # playwright_main es asíncrono, hay que await
            await playwright_main(med)
        except Exception as e:
            logger.error(f"❌ Error en Playwright para {med}: {e}")

# ============================================================
# PIPELINE COMPLETO (se ejecuta cada 6 horas)
# ============================================================

def pipeline_completo():
    """Ejecuta todos los agentes secuencialmente."""
    logger.info("=" * 60)
    logger.info(f"🚀 INICIANDO PIPELINE COMPLETO - {datetime.now()}")
    logger.info("=" * 60)
    
    # 1. Web Scraper (si existe)
    try:
        from scrapers.web_scraper import main as scraper_main
        logger.info("🕷️ Ejecutando web scraper...")
        scraper_main()
        logger.info("✅ Web scraper finalizado")
    except ImportError:
        logger.info("ℹ️ Web scraper no disponible, continuando...")
    except Exception as e:
        logger.error(f"❌ Error en web scraper: {e}")
    
    # 2. Agentes Playwright (farmacias físicas)
    try:
        logger.info("🎭 Ejecutando agentes Playwright...")
        asyncio.run(ejecutar_agentes_playwright())
        logger.info("✅ Agentes Playwright finalizados")
    except Exception as e:
        logger.error(f"❌ Error en agentes Playwright: {e}")
    
    # 3. Agentes de Delivery (Rappi + Uber Eats)
    try:
        logger.info("🛵 Ejecutando agentes de delivery...")
        asyncio.run(ejecutar_agentes_delivery())
        logger.info("✅ Agentes de delivery finalizados")
    except Exception as e:
        logger.error(f"❌ Error en agentes de delivery: {e}")
    
    # 4. Resumen de la ejecución
    try:
        fuente_counts = contar_por_fuente()
        logger.info("📊 Registros por fuente:")
        for fuente, count in fuente_counts.items():
            logger.info(f"   {fuente}: {count} registros")
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen: {e}")
    
    logger.info("=" * 60)
    logger.info(f"✅ PIPELINE COMPLETADO - {datetime.now()}")
    logger.info("=" * 60)

# ============================================================
# MAIN - INICIAR SCHEDULER
# ============================================================

if __name__ == "__main__":
    # Inicializar base de datos
    init_db()
    logger.info("🗄️ Base de datos inicializada")
    
    # Verificar conexión
    try:
        conn = get_connection()
        conn.close()
        logger.info("✅ Conexión a base de datos exitosa")
    except Exception as e:
        logger.error(f"❌ Error conectando a base de datos: {e}")
        sys.exit(1)
    
    # Crear scheduler
    scheduler = BlockingScheduler()
    
    # Programar pipeline cada 6 horas
    scheduler.add_job(
        pipeline_completo,
        'interval',
        hours=6,
        id='pipeline_6h',
        next_run_time=datetime.now()  # Ejecutar inmediatamente al iniciar
    )
    logger.info("⏰ Pipeline programado cada 6 horas")
    
    # Programar job de respaldo: solo agentes Playwright cada 12 horas (opcional)
    # scheduler.add_job(
    #     lambda: asyncio.run(ejecutar_agentes_playwright()),
    #     'interval',
    #     hours=12,
    #     id='playwright_12h'
    # )
    
    try:
        logger.info("🚀 Scheduler iniciado...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("⏹️ Scheduler detenido por el usuario")
    except Exception as e:
        logger.error(f"❌ Error en scheduler: {e}")
        sys.exit(1)