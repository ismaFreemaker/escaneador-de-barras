import sqlite3

DB_FILE = "productos.db"

# =========================================
# CONEXIÓN
# =========================================

def conectar():

    return sqlite3.connect(DB_FILE)

# =========================================
# CREAR TABLA
# =========================================

def crear_tabla():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS productos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            codigo_barras TEXT,

            nombre TEXT,

            marca TEXT,

            categoria TEXT

        )

    """)

    conn.commit()

    conn.close()

# =========================================
# INSERTAR PRODUCTO
# =========================================

def insertar_producto(
    codigo_barras,
    nombre,
    marca,
    categoria
):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO productos (

            codigo_barras,
            nombre,
            marca,
            categoria

        )

        VALUES (?, ?, ?, ?)

    """, (

        codigo_barras,
        nombre,
        marca,
        categoria

    ))

    conn.commit()

    conn.close()

# =========================================
# OBTENER PRODUCTOS
# =========================================

def obtener_productos():

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            codigo_barras,
            nombre,
            marca,
            categoria
        FROM productos

    """)

    productos = cursor.fetchall()

    conn.close()

    return productos