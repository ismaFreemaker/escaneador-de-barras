import streamlit as st
import pandas as pd
import time

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

if "ultimo_codigo" not in st.session_state:

    st.session_state.ultimo_codigo = ""

if "resultado_api" not in st.session_state:

    st.session_state.resultado_api = None

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

function onScanSuccess(decodedText, decodedResult) {

    if(decodedText === ultimoCodigo){
        return;
    }

    ultimoCodigo = decodedText;

    beep();

    const streamlitDoc = window.parent.document;

    const input = streamlitDoc.querySelector('input[type="text"]');

    if(input){

        input.value = decodedText;

        input.dispatchEvent(
            new Event('input', { bubbles: true })
        );

        input.dispatchEvent(
            new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: true,
                keyCode: 13
            })
        );
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
    height=700
)

# =========================================
# INPUT CÓDIGO
# =========================================

codigo_barras = st.text_input(
    "Código de barras"
).strip()
st.write("Código actual:", codigo_barras)
if st.button("TEST API"):

    resultado = buscar_producto(codigo_barras)

    st.write(resultado)
# =========================================
# BÚSQUEDA AUTOMÁTICA
# =========================================

if (
    codigo_barras
    and codigo_barras != st.session_state.ultimo_codigo
):

    st.session_state.ultimo_codigo = codigo_barras

    with st.spinner("Buscando producto..."):

        resultado = buscar_producto(codigo_barras)

        time.sleep(0.5)

        st.session_state.resultado_api = resultado

# =========================================
# MOSTRAR RESULTADO
# =========================================

resultado = st.session_state.resultado_api

if resultado:

    if resultado["encontrado"]:

        st.success(
            f"Código detectado: {codigo_barras}"
        )

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

            # =========================================
            # LIMPIAR
            # =========================================

            st.session_state.resultado_api = None
            st.session_state.ultimo_codigo = ""

            st.rerun()

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