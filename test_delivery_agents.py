import asyncio
import json
from data.agents.rappi_agent import RappiAgent

async def main():
    medicamentos_rappi = ["paracetamol 500mg", "ibuprofeno 400mg", "omeprazol 20mg"]

    rappi = RappiAgent(headless=False)  # headless=False para ver el navegador

    print("🔍 Probando Rappi...")
    for med in medicamentos_rappi:
        res = await rappi.search_medication(med)
        if res:
            print(f"✅ Rappi - {med}: ${res['precio']} en {res['farmacia']}")
            print(f"   Link: {res['link_producto']}")
        else:
            print(f"❌ Rappi - {med}: falló")

if __name__ == "__main__":
    asyncio.run(main())
    