import streamlit as st
import pandas as pd

from api_productos import buscar_producto

from database import (
    crear_tabla,
    insertar_producto,
    obtener_productos
)

# =========================================
# CONFIG
# =========================================

st.set_page_config(
    page_title="Catálogo Inteligente",
    layout="wide"
)

# =========================================
# CREAR TABLA
# =========================================

crear_tabla()

# =========================================
# SESSION STATE
# =========================================

if "codigo_barras" not in st.session_state:

    st.session_state.codigo_barras = ""

# =========================================
# TÍTULO
# =========================================

st.title("Catálogo Inteligente")

st.write(
    "Escaneá un producto usando la cámara del celular."
)

# =========================================
# SCANNER HTML5
# =========================================

scanner_html = """

<div id="reader" style="width:300px"></div>

<script src="https://unpkg.com/html5-qrcode"></script>

<script>

function onScanSuccess(decodedText, decodedResult) {

    const streamlitDoc = window.parent.document;

    const input = streamlitDoc.querySelector('input[type="text"]');

    if(input){

        input.value = decodedText;

        input.dispatchEvent(new Event('input', { bubbles: true }));

    }
}

let html5QrcodeScanner = new Html5QrcodeScanner(
    "reader",
    {
        fps: 10,
        qrbox: 250
    }
);

html5QrcodeScanner.render(onScanSuccess);

</script>

"""

st.components.v1.html(
    scanner_html,
    height=600
)

# =========================================
# INPUT CÓDIGO
# =========================================

codigo_barras = st.text_input(
    "Código de barras"
).strip()

# =========================================
# MOSTRAR CÓDIGO
# =========================================

if codigo_barras:

    st.success(f"Código detectado: {codigo_barras}")

# =========================================
# BUSCAR
# =========================================

if st.button("Buscar producto"):

    if codigo_barras:

        resultado = buscar_producto(codigo_barras)

        # =========================================
        # SI ENCUENTRA
        # =========================================

        if resultado["encontrado"]:

            st.success("Producto encontrado")

            nombres = resultado["nombres"]

            if not nombres:

                nombres = ["Producto sin nombre"]

            nombre_seleccionado = st.selectbox(

                "Elegí el nombre correcto",

                nombres

            )

            nombre_editado = st.text_input(

                "O editalo manualmente",

                value=nombre_seleccionado

            )

            marca = st.text_input(

                "Marca",

                value=resultado["marca"]

            )

            categoria = st.text_input(

                "Categoría",

                value=resultado["categoria"]

            )

            # =========================================
            # GUARDAR
            # =========================================

            if st.button("Guardar producto"):

                insertar_producto(

                    codigo_barras,
                    nombre_editado,
                    marca,
                    categoria

                )

                st.success("Producto guardado")

        else:

            st.error(
                "No se encontró el producto"
            )

# =========================================
# MOSTRAR CATÁLOGO
# =========================================

st.divider()

st.subheader("Productos guardados")

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