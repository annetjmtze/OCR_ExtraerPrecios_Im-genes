import asyncio
import logging
from data.agents.rappi_agent import RappiAgent

logging.basicConfig(level=logging.INFO)

async def main():
    agent = RappiAgent(headless=False)
    resultado = await agent.search_medication("paracetamol 500mg")
    if resultado:
        print(f"\n✅ Encontrado:")
        print(f"   Precio: ${resultado['precio']}")
        print(f"   Farmacia: {resultado['farmacia']}")
        print(f"   Link: {resultado['link_producto']}")
    else:
        print("❌ No se encontró el medicamento.")

if __name__ == "__main__":
    asyncio.run(main())