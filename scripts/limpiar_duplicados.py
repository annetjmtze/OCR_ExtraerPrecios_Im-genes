#!/usr/bin/env python3
"""
Limpia duplicados de la tabla precios en PostgreSQL.
Mantiene el registro con el ID más alto (más reciente) para cada
combinación de medicamento, farmacia y fecha (sin hora).
"""
import os
import sys
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL no está configurada")
    sys.exit(1)

def main():
    print("🔍 Conectando a la base de datos...")
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    cur = conn.cursor()

    # Identificar duplicados (agrupar por medicamento, farmacia, fecha sin hora)
    # Usamos SUBSTRING(fecha, 1, 10) porque fecha es TEXT con formato 'YYYY-MM-DD HH:MM:SS'
    print("🔍 Buscando duplicados...")
    cur.execute("""
        SELECT id
        FROM (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY medicamento, farmacia, SUBSTRING(fecha, 1, 10)
                       ORDER BY id DESC
                   ) AS rn
            FROM precios
        ) t
        WHERE rn > 1
    """)
    rows = cur.fetchall()

    if not rows:
        print("✅ No hay duplicados para eliminar")
        conn.close()
        return

    ids = [row["id"] for row in rows]
    print(f"🔍 Se encontraron {len(ids)} duplicados para eliminar")

    # Eliminar en lotes de 100 para no saturar la conexión
    batch_size = 100
    total_eliminados = 0
    total_lotes = (len(ids) + batch_size - 1) // batch_size

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i+batch_size]
        placeholders = ",".join(["%s"] * len(batch))
        cur.execute(f"DELETE FROM precios WHERE id IN ({placeholders})", batch)
        eliminados = cur.rowcount
        total_eliminados += eliminados
        conn.commit()
        lote_actual = i // batch_size + 1
        print(f"   ✅ Lote {lote_actual}/{total_lotes}: eliminados {eliminados} registros")

    print(f"✅ Total eliminados: {total_eliminados}")
    conn.close()

if __name__ == "__main__":
    main()