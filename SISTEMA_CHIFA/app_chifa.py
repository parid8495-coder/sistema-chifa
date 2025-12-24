import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Chifa - Pedidos", layout="centered")

# Título e instrucciones
st.title("🍜 Pedidos Chifa")
st.write("Selecciona tus platos y confirma tu pedido.")

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    # Definimos el alcance (scope)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # Cargar credenciales
    # Intentamos buscar el archivo solo por su nombre
    creds = ServiceAccountCredentials.from_json_keyfile_name('credenciales.json', scope)
    
    # Autorizar cliente
    client = gspread.authorize(creds)
    
    # Abrir la hoja de cálculo
    sheet = client.open("Pedidos Chifa").sheet1
    return sheet

# --- DATOS DEL MENÚ ---
MENU = {
    "CHAUFAS": {
        "Chaufa de Pollo": 15.00,
        "Chaufa de Carne": 18.00,
        "Chaufa Especial": 22.00,
        "Chaufa Aeropuerto": 20.00
    },
    "TALLARINES": {
        "Tallarín con Pollo": 16.00,
        "Tallarín Taypa": 24.00
    },
    "BEBIDAS": {
        "Inca Kola 500ml": 3.00,
        "Coca Cola 500ml": 3.00
    }
}

# --- INTERFAZ DE USUARIO ---
carrito = []
total = 0.0

# Mostrar el menú
for categoria, platos in MENU.items():
    st.header(categoria)
    for plato, precio in platos.items():
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"**{plato}**")
            st.caption(f"S/ {precio:.2f}")
        with col2:
            # Checkbox para seleccionar
            if st.checkbox("Agregar", key=plato):
                carrito.append({"Plato": plato, "Precio": precio})
                total += precio

st.divider()

# --- RESUMEN DEL PEDIDO ---
st.subheader("📝 Tu Pedido")

if len(carrito) > 0:
    df = pd.DataFrame(carrito)
    st.table(df)
    st.markdown(f"### Total a Pagar: S/ {total:.2f}")

    # Formulario para datos del cliente
    with st.form("form_pedido"):
        nombre = st.text_input("Tu Nombre:")
        direccion = st.text_input("Dirección de entrega:")
        telefono = st.text_input("Teléfono / Yape:")
        
        enviado = st.form_submit_button("✅ ENVIAR PEDIDO A COCINA")
        
        if enviado:
            if nombre and direccion:
                try:
                    # Conectar y guardar
                    hoja = conectar_google_sheets()
                    fila = [nombre, direccion, telefono, str(df['Plato'].tolist()), total, "Pendiente"]
                    hoja.append_row(fila)
                    st.success(f"¡Gracias {nombre}! Tu pedido ha sido enviado al restaurante.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al conectar con la hoja: {e}")
            else:
                st.warning("Por favor completa tu nombre y dirección.")
else:
    st.info("Selecciona al menos un plato para comenzar.")
