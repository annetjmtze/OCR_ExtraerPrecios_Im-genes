import os
# ── FORZAR USO DE CHROME ──
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/usr/bin'
os.environ['CHROME_PATH'] = '/usr/bin/google-chrome-stable'

import asyncio
import sys
import json
import re
import random
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)
from data.database import save_precio

load_dotenv(os.path.join(ROOT_DIR, '.env'))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ubereats_agent")

class UberEatsAgent:
    def __init__(self, headless=False):
        self.headless = headless
        self.cookies_file = os.path.join(ROOT_DIR, "data", "auth", "cookies_ubereats.json")
        os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)

    async def _random_pause(self):
        await asyncio.sleep(random.uniform(3, 8))

    async def _load_cookies(self, context):
        if not os.path.exists(self.cookies_file):
            logger.warning(f"⚠️ No se encontró archivo de cookies: {self.cookies_file}. Continuando sin autenticación.")
            return
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            logger.info(f"🍪 {len(cookies)} cookies cargadas.")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando cookies: {e}. Continuando sin autenticación.")

    async def _close_cookie_banner(self, page):
        try:
            accept_btn = await page.wait_for_selector(
                "button:has-text('Aceptar'), button:has-text('Aceptar cookies'), button[aria-label='Aceptar']",
                timeout=3000
            )
            if accept_btn:
                await accept_btn.click()
                logger.info("🍪 Banner de cookies cerrado.")
                await asyncio.sleep(1)
                return True
        except:
            pass
        return False

    async def search_medication(self, medication: str) -> Optional[Dict[str, Any]]:
        async with async_playwright() as p:
            # ── USAR GOOGLE CHROME ──
            browser = await p.chromium.launch(
                channel="chrome",  # usa Chrome del sistema
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768}
            )
            await self._load_cookies(context)
            page = await context.new_page()

            try:
                # ── Navegar a home ──
                await page.goto("https://www.ubereats.com/mx", timeout=30000)
                await asyncio.sleep(3)
                await self._close_cookie_banner(page)

                # ── Manejar dirección ──
                try:
                    address_input = await page.wait_for_selector(
                        "input[placeholder*='dirección'], input[placeholder*='entrega'], input[name='searchTerm']",
                        timeout=5000
                    )
                    if address_input:
                        logger.info("📍 Ingresando dirección: Uruapan")
                        await address_input.fill("Uruapan")
                        await self._random_pause()
                        await address_input.press("Enter")
                        await asyncio.sleep(3)
                except:
                    logger.info("✅ No se solicitó dirección, continuando...")

                # ── Navegar a la URL de búsqueda ──
                search_url = f"https://www.ubereats.com/mx/search?q={medication.replace(' ', '%20')}"
                logger.info(f"🌐 Navegando a: {search_url}")
                await page.goto(search_url, timeout=30000)
                await asyncio.sleep(5)
                await self._close_cookie_banner(page)

                # ── Obtener items ──
                raw_items = await page.query_selector_all("div[data-testid='store-item'], div[data-testid='feed-item'], article, section, li")
                logger.info(f"📦 Encontrados {len(raw_items)} elementos candidatos.")

                items = []
                for el in raw_items:
                    try:
                        text = await el.inner_text()
                        if "Ir al contenido" in text or "Menu" in text or "Buscar" in text:
                            continue
                        if "OXXO" in text or "Farmacias" in text or "Costo de envío" in text or "MX$" in text or "$" in text:
                            items.append(el)
                    except:
                        continue

                logger.info(f"📦 Después de filtrar: {len(items)} items relevantes.")

                if not items:
                    html_debug = await page.content()
                    with open("ubereats_debug.html", "w", encoding="utf-8") as f:
                        f.write(html_debug)
                    await page.screenshot(path="ubereats_no_items.png")
                    logger.warning("No se encontraron items relevantes.")
                    await browser.close()
                    return None

                first_item = items[0]
                item_text = await first_item.inner_text()
                logger.info(f"📝 Primer item: {item_text[:200]}...")

                # ── Extraer nombre de la tienda ──
                farmacia = "Farmacia en Uber Eats"
                try:
                    lines = item_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) < 50 and "Costo de envío" not in line and not re.search(r'\$\s*\d+', line):
                            if "OXXO" in line or "Farmacias" in line or "Soriana" in line or "Comer" in line:
                                farmacia = line
                                break
                except:
                    pass

                # ── Extraer precio ──
                precio = None
                try:
                    match = re.search(r'(?:MX\$|MXN|\$)\s*(\d+\.?\d*)', item_text)
                    if not match:
                        match = re.search(r'(\d+\.?\d*)\s*(?:MX\$|MXN|\$)', item_text)
                    if match:
                        precio = float(match.group(1))
                except:
                    pass

                # ── Nombre del producto ──
                nombre = medication
                try:
                    lines = item_text.split('\n')
                    for line in lines:
                        if medication.lower() in line.lower():
                            nombre = line.strip()
                            break
                except:
                    pass

                # ── Link ──
                href = None
                try:
                    link_elem = await first_item.query_selector("a[href*='/store/'], a[href*='/item/'], a[href*='/restaurant/']")
                    if not link_elem:
                        link_elem = await first_item.query_selector("a")
                    if link_elem:
                        href = await link_elem.get_attribute("href")
                        if href:
                            if 'add-product' in href or 'icon' in href:
                                href = None
                            elif not href.startswith("http"):
                                href = "https://www.ubereats.com" + href
                except:
                    pass

                if not href:
                    try:
                        logger.info("🖱️ Intentando obtener link mediante clic en el producto...")
                        async with page.expect_navigation(timeout=15000) as nav_info:
                            await first_item.click()
                        href = page.url
                        if '/store/' in href or '/item/' in href:
                            logger.info(f"✅ Link obtenido por clic: {href}")
                            await page.go_back()
                            await page.wait_for_load_state("networkidle")
                            await self._random_pause()
                        else:
                            href = None
                    except Exception as e:
                        logger.warning(f"Error en clic: {e}")

                # ── Screenshot ──
                screenshot_bytes = await page.screenshot(full_page=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_dir = os.path.join(ROOT_DIR, "data", "screenshots", "ubereats")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(screenshot_dir, f"{medication.replace(' ', '_')}_{timestamp}.png")
                with open(screenshot_path, "wb") as f:
                    f.write(screenshot_bytes)

                resultado = {
                    "medicamento": medication,
                    "farmacia": farmacia,
                    "precio": precio,
                    "precio_promo": None,
                    "link_producto": href,
                    "plataforma": "ubereats",
                    "entrega_estimada": "30-45 min",
                    "fuente": "agente_ubereats",
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "imagen_url": screenshot_path
                }

                if precio:
                    try:
                        save_precio({
                            "medicamento": medication.lower(),
                            "nombre_raw": nombre,
                            "farmacia": farmacia,
                            "precio": precio,
                            "url": href,
                            "imagen_url": screenshot_path,
                            "fuente": "agente_ubereats",
                            "fecha": resultado["fecha"],
                        })
                        logger.info(f"💾 Guardado: {medication} - ${precio}")
                    except Exception as e:
                        logger.error(f"Error guardando en BD: {e}")

                await browser.close()
                return resultado

            except Exception as e:
                logger.error(f"❌ Error en búsqueda de {medication}: {e}", exc_info=True)
                try:
                    await page.screenshot(path=f"error_ubereats_{medication.replace(' ', '_')}.png")
                except:
                    pass
                await browser.close()
                return None