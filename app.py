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

import queue
import cv2
import numpy as np
import av

from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

# Cola para pasar códigos detectados desde el processor al hilo principal
barcode_queue = queue.Queue()

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


st.subheader("Escáner en vivo (cámara)")

if zbar_decode is None:
    st.warning(
        "La librería `pyzbar` no está disponible. Instala las dependencias: `pip install -r requirements.txt` y, si hace falta, la librería nativa `zbar`."
    )


class BarcodeProcessor(VideoProcessorBase):
    def __init__(self):
        self._last = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        if zbar_decode is not None:
            try:
                decoded = zbar_decode(img)
            except Exception:
                decoded = []

            for d in decoded:
                try:
                    code = d.data.decode("utf-8")
                except Exception:
                    code = None

                if code and code != self._last:
                    self._last = code
                    try:
                        barcode_queue.put_nowait(code)
                    except Exception:
                        pass

        # opcional: dibujar rectángulos (si pyzbar devolviera polígonos)
        return av.VideoFrame.from_ndarray(img, format="bgr24")


webrtc_ctx = webrtc_streamer(
    key="barcode-webrtc",
    video_processor_factory=BarcodeProcessor,
    media_stream_constraints={"video": True, "audio": False},
)

# Leer la cola y actualizar estado principal
try:
    codigo_detectado = barcode_queue.get_nowait()
except Exception:
    codigo_detectado = None

if codigo_detectado:
    st.session_state.codigo_barras = codigo_detectado
    st.success(f"Código detectado: {codigo_detectado}")
    # opcional: detener el stream para evitar detectarlo múltiples veces
    if webrtc_ctx and webrtc_ctx.state.playing:
        try:
            webrtc_ctx.stop()
        except Exception:
            pass
    # forzar rerun para que el input actualice y se realice la búsqueda
    st.experimental_rerun()

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