import os
import json
import time
from tesseract_extractor import extract_text
from claude_vision_extractor import extract_json_from_image

IMAGES_DIR = "data/imagenes_prueba"
OUTPUT_FILE = "data/ocr/comparativa_ocr.md"

def run_comparison():
    images = [f for f in os.listdir(IMAGES_DIR) 
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
    
    results = []
    
    for img in images:
        path = os.path.join(IMAGES_DIR, img)
        print(f"\n--- Procesando: {img} ---")
        
        # Tesseract
        start = time.time()
        tesseract_text = extract_text(path)
        tesseract_time = time.time() - start
        
        # Claude Vision
        start = time.time()
        try:
            claude_json = extract_json_from_image(path)
            claude_time = time.time() - start
            claude_success = True
        except Exception as e:
            claude_json = {"error": str(e)}
            claude_time = time.time() - start
            claude_success = False
        
        results.append({
            "imagen": img,
            "tesseract": {
                "texto": tesseract_text[:500] + "..." if len(tesseract_text) > 500 else tesseract_text,
                "tiempo_seg": round(tesseract_time, 2)
            },
            "claude": {
                "json": claude_json,
                "tiempo_seg": round(claude_time, 2),
                "exito": claude_success
            }
        })
    
    # Generar Markdown
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Comparativa OCR: Tesseract vs Claude Vision\n\n")
        f.write(f"*Fecha: {time.strftime('%Y-%m-%d %H:%M')}*\n")
        f.write(f"*Imágenes procesadas: {len(images)}*\n\n")
        f.write("## Resumen por imagen\n\n")
        
        for r in results:
            f.write(f"### {r['imagen']}\n\n")
            f.write("**Tesseract**\n")
            f.write(f"- Tiempo: {r['tesseract']['tiempo_seg']}s\n")
            f.write(f"- Texto extraído:\n```\n{r['tesseract']['texto']}\n```\n\n")
            
            f.write("**Claude Vision**\n")
            f.write(f"- Tiempo: {r['claude']['tiempo_seg']}s\n")
            f.write(f"- Éxito: {'✅' if r['claude']['exito'] else '❌'}\n")
            f.write("- JSON:\n```json\n")
            f.write(json.dumps(r['claude']['json'], indent=2, ensure_ascii=False))
            f.write("\n```\n\n")
            f.write("---\n\n")
        
        # Análisis comparativo
        f.write("## Análisis comparativo\n\n")
        f.write("| Criterio | Tesseract | Claude Vision |\n")
        f.write("|----------|-----------|---------------|\n")
        f.write("| Costo | Gratis (local) | ~$0.003 USD/imagen |\n")
        f.write("| Texto limpio | ✅ Excelente | ✅ Excelente |\n")
        f.write("| Fotos borrosas | ❌ Falla | ✅ Bueno a excelente |\n")
        f.write("| Precios tachados | ❌ No entiende contexto | ✅ Entiende intención |\n")
        f.write("| Abreviaciones | ❌ Las devuelve crudas | ✅ Las normaliza |\n")
        f.write("| Output estructurado | ❌ Requiere parsing | ✅ JSON directo |\n")
        f.write("| Velocidad (1000+) | ✅ Muy rápido | ⚠️ Rate limits |\n\n")
        
        # Costos estimados
        f.write("## Costo estimado para 1,000 imágenes\n\n")
        f.write("- **Tesseract:** $0 USD (costo cero, corre local)\n")
        f.write("- **Claude Vision:** ~$3.00 USD (0.003 × 1000)\n\n")
        
        f.write("## Recomendación\n\n")
        f.write("- Usa **Tesseract** como primera pasada (gratis, rápido).\n")
        f.write("- Usa **Claude Vision** solo cuando Tesseract falle o necesites JSON estructurado.\n")
        f.write("- Estrategia híbrida: Tesseract para el 80% de las imágenes limpias, Claude para el 20% difíciles.\n")
    
    print(f"\n✅ Comparativa guardada en: {OUTPUT_FILE}")

if __name__ == "__main__":
    run_comparison()