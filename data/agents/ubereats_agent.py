import asyncio
import os
import sys
import random
import logging
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)
from data.database import save_precio
from data.agents.playwright_agent import save_image

load_dotenv(os.path.join(ROOT_DIR, '.env'))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ubereats_agent")

class UberEatsAgent:
    def __init__(self, headless=True):
        self.email = os.getenv("UBEREATS_EMAIL")
        self.password = os.getenv("UBEREATS_PASSWORD")
        self.headless = headless
        self.auth_file = os.path.join(ROOT_DIR, "data", "auth", "auth_ubereats.json")
        self.screenshot_dir = os.path.join(ROOT_DIR, "data", "screenshots", "ubereats")
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def _random_pause(self, min_sec=3, max_sec=8):
        time.sleep(random.uniform(min_sec, max_sec))

    async def _login(self, context):
        # Similar al de Rappi pero para Uber Eats
        page = await context.new_page()
        await page.goto("https://www.ubereats.com/mx/login", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        # Selectores de email
        email_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[placeholder*='email']",
            "input[aria-label*='email']",
        ]
        email_input = None
        for selector in email_selectors:
            try:
                email_input = await page.wait_for_selector(selector, timeout=2000)
                if email_input and await email_input.is_visible():
                    break
            except:
                continue
        if not email_input:
            raise Exception("No se encontró el campo de email en Uber Eats")
        await email_input.fill(self.email)
        await asyncio.sleep(1)

        # Botón "Siguiente" si existe
        next_btn = await page.query_selector("button:has-text('Siguiente')")
        if next_btn:
            await next_btn.click()
            await asyncio.sleep(2)

        # Contraseña
        password_selectors = [
            "input[type='password']",
            "input[name='password']",
            "input[placeholder*='contraseña']",
        ]
        password_input = None
        for selector in password_selectors:
            try:
                password_input = await page.wait_for_selector(selector, timeout=2000)
                if password_input and await password_input.is_visible():
                    break
            except:
                continue
        if not password_input:
            raise Exception("No se encontró el campo de contraseña en Uber Eats")
        await password_input.fill(self.password)
        await asyncio.sleep(1)

        # Botón login
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Ingresar')",
            "button:has-text('Iniciar sesión')",
        ]
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = await page.wait_for_selector(selector, timeout=2000)
                if submit_button and await submit_button.is_visible():
                    break
            except:
                continue
        if not submit_button:
            raise Exception("No se encontró el botón de login en Uber Eats")
        await submit_button.click()
        await page.wait_for_url("https://www.ubereats.com/mx/", timeout=15000)
        await context.storage_state(path=self.auth_file)
        await page.close()
        logger.info("✅ Login Uber Eats exitoso, estado guardado.")

    async def search_medication(self, medication: str) -> Optional[Dict[str, Any]]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            )

            if os.path.exists(self.auth_file):
                context = await browser.new_context(storage_state=self.auth_file)
                logger.info("🔑 Estado Uber Eats cargado.")
            else:
                await self._login(context)

            page = await context.new_page()

            try:
                await page.goto("https://www.ubereats.com/mx/", timeout=30000)
                await page.wait_for_load_state("networkidle")
                self._random_pause()

                # Buscar input
                search_selectors = [
                    "input[aria-label='Buscar']",
                    "input[placeholder*='Buscar']",
                    "input[type='search']",
                ]
                search_input = None
                for selector in search_selectors:
                    try:
                        search_input = await page.wait_for_selector(selector, timeout=3000)
                        if search_input and await search_input.is_visible():
                            break
                    except:
                        continue
                if not search_input:
                    raise Exception("No se encontró el campo de búsqueda en Uber Eats")

                await search_input.fill(medication)
                await search_input.press("Enter")
                self._random_pause()

                # Esperar resultados
                result_selectors = [
                    "div[data-testid='feed-item']",
                    "div[class*='store-card']",
                    "div[class*='item']",
                ]
                found = False
                for selector in result_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        found = True
                        break
                    except:
                        continue
                if not found:
                    raise Exception("No se encontraron resultados en Uber Eats")

                # Screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_bytes = await page.screenshot(full_page=False)
                folder = "ubereats"
                filename = f"{medication.replace(' ', '_')}/{timestamp}.png"
                imagen_url = save_image(screenshot_bytes, folder, filename)

                # Extraer datos del primer resultado
                product_card = page.locator("div[data-testid='feed-item']").first

                try:
                    farmacia = await product_card.locator("span[data-testid='store-name']").text_content()
                    farmacia = farmacia.strip()
                except:
                    farmacia = "Farmacia en Uber Eats"

                try:
                    precio_text = await product_card.locator("span[data-testid='price']").text_content()
                    precio = float(precio_text.replace("$", "").replace(",", "").strip())
                except:
                    precio = None

                try:
                    promo_text = await product_card.locator("span[data-testid='discount-price']").text_content()
                    precio_promo = float(promo_text.replace("$", "").replace(",", "").strip())
                except:
                    precio_promo = None

                try:
                    link_element = product_card.locator("a").first
                    href = await link_element.get_attribute("href")
                    if href and not href.startswith("http"):
                        href = "https://www.ubereats.com" + href
                except:
                    href = None

                entrega = "30-40 min"
                resultado = {
                    "medicamento": medication,
                    "farmacia": farmacia,
                    "precio": precio,
                    "precio_promo": precio_promo,
                    "link_producto": href,
                    "plataforma": "ubereats",
                    "entrega_estimada": entrega,
                    "fuente": "agente_ubereats",
                    "fecha": datetime.now(timezone.utc).isoformat(),
                    "imagen_url": imagen_url
                }

                if precio is not None:
                    registro = {
                        "medicamento": medication.lower(),
                        "nombre_raw": medication,
                        "farmacia": farmacia,
                        "precio": precio,
                        "url": href,
                        "imagen_url": imagen_url,
                        "fuente": "agente_ubereats",
                        "fecha": resultado["fecha"],
                        "ciudad": None,
                        "precio_promo": precio_promo,
                        "vigencia": None,
                    }
                    save_precio(registro)
                    logger.info(f"💾 Guardado Uber Eats: {medication} - ${precio}")

                await browser.close()
                return resultado

            except Exception as e:
                logger.error(f"❌ Error en Uber Eats: {e}")
                await browser.close()
                return None