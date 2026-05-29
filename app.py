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
# DB
# =========================================

crear_tabla()

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

scanner_html = """

<div id="reader" style="width:100%"></div>

<script src="https://unpkg.com/html5-qrcode"></script>

<script>

let ultimoCodigo = "";

function beep() {

    const audio = new Audio(
        "https://actions.google.com/sounds/v1/alarms/beep_short.ogg"
    );

    audio.play();
}

function onScanSuccess(decodedText) {

    if(decodedText === ultimoCodigo){
        return;
    }

    ultimoCodigo = decodedText;

    beep();

    const streamlitDoc = window.parent.document;

    const input = streamlitDoc.querySelector(
        'input[type="text"]'
    );

    if(input){

        input.focus();

        input.value = decodedText;

        input.dispatchEvent(
            new Event('input', { bubbles: true })
        );

        input.dispatchEvent(
            new Event('change', { bubbles: true })
        );
    }
}

const scanner = new Html5QrcodeScanner(
    "reader",
    {
        fps: 10,
        qrbox: 250
    }
);

scanner.render(onScanSuccess);

</script>

"""

st.components.v1.html(
    scanner_html,
    height=700
)

# =========================================
# INPUT
# =========================================

codigo_barras = st.text_input(
    "Código de barras"
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

# =========================================
# BUSCAR AUTOMÁTICAMENTE
# =========================================

resultado = None

if codigo_barras:

    resultado = buscar_producto(
        codigo_barras
    )

# =========================================
# RESULTADO
# =========================================

if resultado:

    st.write(resultado)

    if resultado.get("encontrado"):

        st.success("Producto encontrado")

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

            st.success(
                "Producto guardado"
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