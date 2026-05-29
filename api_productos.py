import requests

# =========================================
# LIMPIAR TEXTO
# =========================================

def limpiar_texto(texto):

    if not texto:
        return ""

    return str(texto).strip()

# =========================================
# AGREGAR NOMBRE
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

    url = (
        f"https://world.openfoodfacts.org/api/v0/product/"
        f"{codigo_barras}.json"
    )

    headers = {

        "User-Agent": "CatalogoInteligente/1.0"

    }

    try:

        response = requests.get(

            url,
            headers=headers,
            timeout=10

        )

        print("\n===================")
        print("STATUS:")
        print(response.status_code)

        # =========================================
        # JSON
        # =========================================

        data = response.json()

        # =========================================
        # EXISTE PRODUCTO
        # =========================================

        if data.get("status") != 1:

            print("PRODUCTO NO ENCONTRADO")

            return {

                "encontrado": False

            }

        # =========================================
        # PRODUCTO
        # =========================================

        producto = data.get("product", {})

        nombres = []

        # =========================================
        # NOMBRES POSIBLES
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
        # SI NO HAY NOMBRES
        # =========================================

        if not nombres:

            nombres.append(
                "Producto sin nombre"
            )

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

        print("NOMBRES:")
        print(nombres)

        print("MARCA:")
        print(marca)

        print("CATEGORIA:")
        print(categoria)

        # =========================================
        # RESPUESTA LIMPIA
        # =========================================

        return {

            "encontrado": True,

            "nombres": nombres,

            "marca": marca,

            "categoria": categoria

        }

    except Exception as e:

        print("ERROR:")
        print(str(e))

        return {

            "encontrado": False

        }