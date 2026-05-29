import requests
import json

# =========================================
# BUSCAR PRODUCTO
# =========================================

def buscar_producto(codigo_barras):

    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo_barras}.json"

    try:

        response = requests.get(url)

        print("STATUS CODE:")
        print(response.status_code)

        data = response.json()

        print("JSON COMPLETO:")
        print(json.dumps(data, indent=2))

        # =========================================
        # SI EXISTE
        # =========================================

        if data.get("status") == 1:

            producto = data.get("product", {})

            nombres_posibles = []

            posibles_campos = [

                producto.get("product_name"),
                producto.get("generic_name"),
                producto.get("product_name_es"),
                producto.get("abbreviated_product_name")

            ]

            for nombre in posibles_campos:

                if nombre:

                    nombre = str(nombre).strip()

                    if nombre not in nombres_posibles:

                        nombres_posibles.append(nombre)

            return {

                "encontrado": True,

                "nombres": nombres_posibles,

                "marca": producto.get("brands", ""),

                "categoria": producto.get("categories", "")

            }

        else:

            print("NO ENCONTRADO EN API")

            return {
                "encontrado": False
            }

    except Exception as e:

        print("ERROR REAL:")
        print(e)

        return {
            "encontrado": False
        }