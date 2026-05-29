import requests
import json

# =========================================
# LIMPIAR TEXTO
# =========================================

def limpiar_texto(texto):

    if not texto:
        return ""

    texto = str(texto).strip()

    return texto

# =========================================
# AGREGAR SI EXISTE
# =========================================

def agregar_nombre(lista, valor):

    valor = limpiar_texto(valor)

    if valor:

        if valor not in lista:

            lista.append(valor)

# =========================================
# BUSCAR PRODUCTO
# =========================================

def buscar_producto(codigo_barras):

    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_barras}.json"

    try:

        response = requests.get(url, timeout=10)

        print("\n==============================")
        print("BUSCANDO PRODUCTO")
        print("==============================")

        print("CÓDIGO:")
        print(codigo_barras)

        print("\nSTATUS:")
        print(response.status_code)

        data = response.json()

        # =========================================
        # NO EXISTE
        # =========================================

        if data.get("status") != 1:

            print("\nNO ENCONTRADO EN OPENFOODFACTS")

            return {
                "encontrado": False
            }

        # =========================================
        # PRODUCTO
        # =========================================

        producto = data.get("product", {})

        nombres = []

        # =========================================
        # CAMPOS IMPORTANTES
        # =========================================

        agregar_nombre(
            nombres,
            producto.get("product_name")
        )

        agregar_nombre(
            nombres,
            producto.get("product_name_es")
        )

        agregar_nombre(
            nombres,
            producto.get("generic_name")
        )

        agregar_nombre(
            nombres,
            producto.get("generic_name_es")
        )

        agregar_nombre(
            nombres,
            producto.get("abbreviated_product_name")
        )

        # =========================================
        # FALLBACK
        # =========================================

        if not nombres:

            agregar_nombre(
                nombres,
                producto.get("brands")
            )

        # =========================================
        # SI TODAVÍA NO HAY
        # =========================================

        if not nombres:

            nombres.append("Producto sin nombre")

        # =========================================
        # MARCA
        # =========================================

        marca = limpiar_texto(
            producto.get("brands")
        )

        # =========================================
        # CATEGORÍA
        # =========================================

        categoria = limpiar_texto(
            producto.get("categories")
        )

        # =========================================
        # DEBUG
        # =========================================

        print("\nNOMBRES ENCONTRADOS:")

        for n in nombres:

            print("-", n)

        print("\nMARCA:")
        print(marca)

        print("\nCATEGORÍA:")
        print(categoria)

        # =========================================
        # RESPUESTA
        # =========================================

        return {

            "encontrado": True,

            "nombres": nombres,

            "marca": marca,

            "categoria": categoria

        }

    except Exception as e:

        print("\nERROR REAL:")
        print(str(e))

        return {

            "encontrado": False

        }