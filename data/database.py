import os
import sqlite3
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import re
import unicodedata

# ============================================================
# CONFIGURACIÓN
# ============================================================
DATABASE_URL = os.getenv("DATABASE_URL")
IS_PROD = DATABASE_URL is not None
DB_PATH = "data/precios.db"

def get_connection():
    if IS_PROD:
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS precios (
            id SERIAL PRIMARY KEY,
            medicamento TEXT NOT NULL,
            nombre_raw TEXT,
            farmacia TEXT NOT NULL,
            ciudad TEXT,
            precio REAL NOT NULL,
            precio_promo REAL,
            vigencia TEXT,
            url TEXT,
            imagen_url TEXT,
            fuente TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medicamento ON precios(medicamento)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fecha ON precios(fecha)')
    conn.commit()
    conn.close()

def normalizar_texto(texto: str) -> str:
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'\s+', ' ', texto)
    return texto

# ============================================================
# GUARDAR PRECIO (compatible con ambos motores)
# ============================================================
def save_precio(data: Dict[str, Any]):
    required = ['medicamento', 'farmacia', 'precio', 'fuente', 'fecha']
    for field in required:
        if field not in data or data[field] is None:
            raise ValueError(f"Campo '{field}' obligatorio")
    
    # ── Convertir fecha al formato adecuado según motor ──
    fecha_str = data['fecha']
    if not IS_PROD:
        # SQLite: eliminar zona horaria y microsegundos
        # Quitar 'Z' o '+00:00'
        fecha_str = fecha_str.replace('Z', '').replace('+00:00', '')
        # Quitar microsegundos (si existen)
        if '.' in fecha_str:
            fecha_str = fecha_str.split('.')[0]
        # Reemplazar 'T' por espacio
        fecha_str = fecha_str.replace('T', ' ')
        # Ahora es 'YYYY-MM-DD HH:MM:SS'
    # Si es PostgreSQL, se mantiene el formato ISO con zona
    
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_PROD:
        cursor.execute('''
            INSERT INTO precios (
                medicamento, nombre_raw, farmacia, ciudad, precio, precio_promo,
                vigencia, url, imagen_url, fuente, fecha
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['medicamento'],
            data.get('nombre_raw'),
            data['farmacia'],
            data.get('ciudad'),
            data['precio'],
            data.get('precio_promo'),
            data.get('vigencia'),
            data.get('url'),
            data.get('imagen_url'),
            data['fuente'],
            fecha_str  # Usar la fecha convertida
        ))
    else:
        cursor.execute('''
            INSERT INTO precios (
                medicamento, nombre_raw, farmacia, ciudad, precio, precio_promo,
                vigencia, url, imagen_url, fuente, fecha
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['medicamento'],
            data.get('nombre_raw'),
            data['farmacia'],
            data.get('ciudad'),
            data['precio'],
            data.get('precio_promo'),
            data.get('vigencia'),
            data.get('url'),
            data.get('imagen_url'),
            data['fuente'],
            fecha_str
        ))
    
    conn.commit()
    conn.close()

# ============================================================
# BÚSQUEDA PRINCIPAL (últimas 24 horas)
# ============================================================
def get_precios(medicamento: str, horas: int = 24) -> List[Dict[str, Any]]:
    medicamento_norm = normalizar_texto(medicamento)
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_PROD:
        fecha_limite = (datetime.utcnow() - timedelta(hours=horas)).isoformat()
        cursor.execute('''
            SELECT * FROM precios
            WHERE LOWER(medicamento) LIKE %s AND fecha >= %s
            ORDER BY fecha DESC
        ''', (f'%{medicamento_norm}%', fecha_limite))
    else:
        # SQLite: fecha límite en 'YYYY-MM-DD HH:MM:SS'
        fecha_limite = (datetime.utcnow() - timedelta(hours=horas)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            SELECT * FROM precios
            WHERE LOWER(medicamento) LIKE ? AND fecha >= ?
            ORDER BY fecha DESC
        ''', (f'%{medicamento_norm}%', fecha_limite))
    
    rows = cursor.fetchall()
    conn.close()
    
    if IS_PROD:
        return rows
    else:
        return [dict(row) for row in rows]

# ============================================================
# RESUMEN (24h)
# ============================================================
def get_resumen(medicamento: str) -> List[Dict[str, Any]]:
    return get_precios(medicamento, horas=24)

# ============================================================
# HISTÓRICO (sin límite de tiempo)
# ============================================================
def get_last_precios(medicamento: str, limit: int = 5) -> List[Dict[str, Any]]:
    medicamento_norm = normalizar_texto(medicamento)
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_PROD:
        cursor.execute('''
            SELECT * FROM precios
            WHERE LOWER(medicamento) LIKE %s
            ORDER BY fecha DESC
            LIMIT %s
        ''', (f'%{medicamento_norm}%', limit))
    else:
        cursor.execute('''
            SELECT * FROM precios
            WHERE LOWER(medicamento) LIKE ?
            ORDER BY fecha DESC
            LIMIT ?
        ''', (f'%{medicamento_norm}%', limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    if IS_PROD:
        return rows
    else:
        return [dict(row) for row in rows]

def count_precios() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM precios')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def contar_por_fuente():
    """
    Cuenta cuántos registros hay por cada fuente (agente_rappi, agente_ubereats, etc.)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if IS_PROD:
        cursor.execute("SELECT fuente, COUNT(*) FROM precios GROUP BY fuente")
    else:
        cursor.execute("SELECT fuente, COUNT(*) FROM precios GROUP BY fuente")
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convertir a diccionario
    resultado = {}
    for row in rows:
        if IS_PROD:
            fuente = row['fuente']
            count = row['count']
        else:
            fuente = row[0]
            count = row[1]
        resultado[fuente] = count
    
    return resultado