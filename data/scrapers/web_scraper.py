import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# -------------------- FUNCIÓN AUXILIAR DE LIMPIEZA --------------------
def limpiar_precio(texto):
    """Limpia caracteres no numéricos y convierte a float."""
    if not texto:
        return None
    limpio = re.sub(r'[^\d.]', '', texto)
    try:
        return float(limpio)
    except ValueError:
        return None

# -------------------- FARMACIAS DEL AHORRO --------------------
def scrape_ahorro(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-MX,es;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        price_elem = soup.select_one('[data-price-type="oldPrice"] .price')
        if not price_elem:
            price_elem = soup.select_one('[data-price-type="finalPrice"] .price')
        if not price_elem:
            price_elem = soup.select_one('.product-info-price .price')
        if not price_elem:
            price_elem = soup.select_one('span.price')
        precio = limpiar_precio(price_elem.text) if price_elem else None

        promo_elem = soup.select_one('.special-price .price')
        precio_promo = limpiar_precio(promo_elem.text) if promo_elem else None

        vigencia = None

        name_elem = soup.select_one('h1.page-title span')
        if not name_elem:
            name_elem = soup.select_one('h1 span')
        nombre = name_elem.text.strip() if name_elem else "Paracetamol 500 mg"

        return {
            "medicamento_buscado": "paracetamol",
            "nombre_en_farmacia": nombre,
            "farmacia": "Farmacias del Ahorro",
            "precio": precio,
            "precio_promo": precio_promo,
            "vigencia_promo": vigencia,
            "url_producto": url,
            "fuente": "scraper_web",
            "fecha_consulta": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error en Farmacias del Ahorro: {e}")
        return None

# -------------------- BENAVIDES --------------------
def scrape_benavides(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'es-MX,es;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        price_elem = soup.select_one('.price')
        if not price_elem:
            price_elem = soup.select_one('.product-info-price .price')
        if not price_elem:
            price_elem = soup.select_one('[data-price-type="finalPrice"] .price')
        precio = limpiar_precio(price_elem.text) if price_elem else None

        if not precio:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'dl4Objects' in script.string:
                    match = re.search(r'dl4Objects\s*=\s*(\[.*?\]);', script.string, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            for obj in data:
                                if obj.get('event') == 'view_item' and obj.get('pageType') == 'product':
                                    items = obj.get('ecommerce', {}).get('items', [])
                                    if items:
                                        precio = float(items[0].get('price', 0))
                                        break
                        except:
                            pass
                    break

        precio_promo = None
        vigencia = None

        name_elem = soup.select_one('h1.page-title span')
        if not name_elem:
            name_elem = soup.select_one('h1 span')
        nombre = name_elem.text.strip() if name_elem else "Perfalgan Paracetamol"

        return {
            "medicamento_buscado": "paracetamol",
            "nombre_en_farmacia": nombre,
            "farmacia": "Farmacias Benavides",
            "precio": precio,
            "precio_promo": precio_promo,
            "vigencia_promo": vigencia,
            "url_producto": url,
            "fuente": "scraper_web",
            "fecha_consulta": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error en Farmacias Benavides: {e}")
        return None

# -------------------- PROBEMEDIC (NUEVA) --------------------
def scrape_probemedic(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el precio del texto con regex
        texto = soup.get_text()
        match = re.search(r'\$(\d+\.\d{2})', texto)
        precio = float(match.group(1)) if match else None

        # Nombre (desde el título)
        title = soup.find('title')
        nombre = title.text.strip() if title else "Paracetamol 500mg 10 tabletas"

        return {
            "medicamento_buscado": "paracetamol",
            "nombre_en_farmacia": nombre,
            "farmacia": "Probemedic",
            "precio": precio,
            "precio_promo": None,
            "vigencia_promo": None,
            "url_producto": url,
            "fuente": "scraper_web",
            "fecha_consulta": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error en Probemedic: {e}")
        return None

# -------------------- EJECUCIÓN PRINCIPAL --------------------
if __name__ == "__main__":
    # Productos de Probemedic (todos funcionan)
    urls_probemedic = [
        "https://www.probemedic.mx/paracetamol-500mg-10-tabletas.html",
        "https://www.probemedic.mx/ibuprofeno-800-mg-10-tabletas.html",
        "https://www.probemedic.mx/fluoxetina-20-mg-14-capsulas.html",
        "https://www.probemedic.mx/diclofenaco-100-mg-20-tabletas.html"
    ]

    # Otras farmacias
    urls_otras = {
        "ahorro": "https://www.fahorro.com/paracetamol-500-mg-oral-20-tabletas-marca-del-ahorro.html",
        "benavides": "https://www.benavides.com.mx/perfalgan-paracetamol-1-ud-frasco-ampula"
    }

    resultados = []

    # Scrapear Farmacias del Ahorro
    print("🔍 Scrapeando Farmacias del Ahorro...")
    res_ahorro = scrape_ahorro(urls_otras["ahorro"])
    if res_ahorro:
        resultados.append(res_ahorro)
        print("✅ Farmacias del Ahorro OK")

    # Scrapear Farmacias Benavides
    print("🔍 Scrapeando Farmacias Benavides...")
    res_benav = scrape_benavides(urls_otras["benavides"])
    if res_benav:
        resultados.append(res_benav)
        print("✅ Farmacias Benavides OK")

    # Scrapear todos los productos de Probemedic
    for url in urls_probemedic:
        print(f"🔍 Scrapeando Probemedic: {url.split('/')[-1]}...")
        res_prob = scrape_probemedic(url)
        if res_prob:
            resultados.append(res_prob)
            print(f"✅ Probemedic OK: ${res_prob['precio']}")
        else:
            print(f"❌ Probemedic falló para {url}")

    # Guardar resultados
    if resultados:
        import os
        os.makedirs("data/scrapers", exist_ok=True)
        with open("data/scrapers/resultados_farmacias.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        print(f"\n📁 {len(resultados)} resultados guardados en data/scrapers/resultados_farmacias.json")
        print("\n📋 Resumen:")
        for r in resultados:
            print(f"  - {r['farmacia']}: ${r['precio']} - {r['nombre_en_farmacia']}")
    else:
        print("❌ No se obtuvo ningún resultado.")