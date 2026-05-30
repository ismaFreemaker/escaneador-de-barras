import streamlit as st
import pandas as pd

from api_productos import buscar_producto

from database import (
    crear_tabla,
    insertar_producto,
    obtener_productos
)
from PIL import Image

try:
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None

# =========================================
# CONFIG
# =========================================

st.set_page_config(
    page_title="Catálogo Inteligente",
    layout="wide"
)

# =========================================
# DB
# =========================================

crear_tabla()

# =========================================
# SESSION STATE
# =========================================

if "codigo_barras" not in st.session_state:
    st.session_state.codigo_barras = ""

# =========================================
# TITLE
# =========================================

st.title("Catálogo Inteligente")

st.write(
    "Escaneá productos usando la cámara del celular."
)

# =========================================
# SCANNER
# =========================================

# Nuevo scanner nativo usando la cámara de Streamlit

def _decode_barcodes_from_pil(image_pil):
    if zbar_decode is None:
        return []

    try:
        results = zbar_decode(image_pil)
    except Exception:
        return []

    codes = []
    for r in results:
        try:
            codes.append(r.data.decode('utf-8'))
        except Exception:
            pass
    return codes

st.subheader("Escáner (cámara)")

if zbar_decode is None:
    st.warning(
        "La librería `pyzbar` no está disponible. Instala las dependencias: `pip install -r requirements.txt` y, si hace falta, la librería nativa `zbar`."
    )

st.write("Tomá una foto del código de barras con la cámara.")

img_file = st.camera_input("Usar cámara")

if img_file is not None:
    try:
        image = Image.open(img_file)
        codes = _decode_barcodes_from_pil(image)

        if codes:
            codigo_detectado = codes[0]
            st.session_state.codigo_barras = codigo_detectado
            st.success(f"Código detectado: {codigo_detectado}")
        else:
            st.info("No se detectó ningún código en la imagen.")

    except Exception as e:
        st.error(f"Error decodificando la imagen: {e}")

# =========================================
# INPUT
# =========================================

codigo_barras = st.text_input(
    "Código de barras",
    key="codigo_barras"
)

codigo_barras = (
    codigo_barras
    .replace("\n", "")
    .replace("\r", "")
    .replace(" ", "")
    .strip()
)

# =========================================
# DEBUG
# =========================================

st.write("Código:", repr(codigo_barras))
st.write(
    "Session State:",
    st.session_state.codigo_barras
)

# =========================================
# BUSCAR AUTOMÁTICAMENTE
# =========================================

resultado = None

if codigo_barras:

    st.success(
        f"Código recibido: {codigo_barras}"
    )

    resultado = buscar_producto(
        codigo_barras
    )

# =========================================
# RESULTADO
# =========================================

if resultado:

    st.write(resultado)

    if resultado.get("encontrado"):

        st.success(
            "Producto encontrado"
        )

        nombres = resultado.get(
            "nombres",
            []
        )

        if not nombres:

            nombres = [
                "Producto sin nombre"
            ]

        nombre_seleccionado = st.selectbox(
            "Elegí el nombre correcto",
            nombres
        )

        nombre_editado = st.text_input(
            "Editar nombre",
            value=nombre_seleccionado
        )

        marca = st.text_input(
            "Marca",
            value=resultado.get(
                "marca",
                ""
            )
        )

        categoria = st.text_input(
            "Categoría",
            value=resultado.get(
                "categoria",
                ""
            )
        )

        if st.button(
            "Guardar producto"
        ):
            insertar_producto(
                codigo_barras,
                nombre_editado,
                marca,
                categoria
            )

            st.success(
                "Producto guardado"
            )

            # Limpiar para el siguiente escaneo
            st.session_state.codigo_barras = ""

            st.experimental_rerun()

        if st.button("Guardar y siguiente"):

            insertar_producto(
                codigo_barras,
                nombre_editado,
                marca,
                categoria
            )

            st.success("Producto guardado, listo para el siguiente")

            # Limpiar el campo para escanear el próximo producto
            st.session_state.codigo_barras = ""

            st.experimental_rerun()

    else:

        st.error(
            "No se encontró el producto"
        )

# =========================================
# TABLA
# =========================================

st.divider()

st.subheader(
    "Productos guardados"
)

productos = obtener_productos()

if productos:

    df = pd.DataFrame(
        productos,
        columns=[
            "codigo_barras",
            "nombre",
            "marca",
            "categoria"
        ]
    )

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.info(
        "Todavía no hay productos."
    )