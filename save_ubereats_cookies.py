import asyncio
import json
import os
from playwright.async_api import async_playwright

async def main():
    # Crear carpeta si no existe
    os.makedirs("data/auth", exist_ok=True)

    async with async_playwright() as p:
        # ── Lanzar Chrome real (evita detección) ──
        browser = await p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()

        # ── Navegar a la página principal de Uber Eats ──
        await page.goto("https://www.ubereats.com/mx")
        await page.wait_for_load_state("networkidle")

        print("\n🔐 INICIA SESIÓN MANUALMENTE en el navegador que se abrió.")
        print("   - Busca el botón 'Iniciar sesión' o 'Acceder' en la esquina superior derecha.")
        print("   - Haz clic y completa el login con: drahorro.agente@gmail.com")
        print("   - Cuando veas la página principal de Uber Eats (con tu nombre o dirección),")
        input("   - Presiona ENTER en esta terminal...\n")

        # ── Guardar cookies ──
        cookies = await context.cookies()
        with open("data/auth/cookies_ubereats.json", "w", encoding="utf-8") as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)

        print(f"✅ {len(cookies)} cookies guardadas en data/auth/cookies_ubereats.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    