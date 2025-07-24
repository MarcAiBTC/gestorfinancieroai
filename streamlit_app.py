import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Gestor de Portfolio", layout="wide")
st.title("📊 Gestor de Portfolio Financiero")

st.markdown("""
Este asistente te permite gestionar tus inversiones en bolsa de forma sencilla.
Añade los activos que tienes, a qué precio los compraste y la cantidad.  
La app calculará automáticamente su valor actual, rentabilidad y distribución en cartera.
""")

# Inicializar la cartera
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=["Activo", "Ticker", "Tipo", "Precio Compra", "Cantidad"])

# Formulario para añadir activos
with st.form("add_asset"):
    col1, col2, col3 = st.columns(3)
    activo = col1.text_input("Nombre del activo", placeholder="Ej: Alphabet")
    ticker = col2.text_input("Ticker", placeholder="Ej: GOOGL")
    tipo = col3.selectbox("Tipo", ["Acción", "Índice", "Oro", "Otro"])
    
    col4, col5 = st.columns(2)
    precio_compra = col4.number_input("Precio de compra (€)", min_value=0.0, format="%.2f")
    cantidad = col5.number_input("Cantidad", min_value=0.0, format="%.2f")
    
    submitted = st.form_submit_button("➕ Añadir activo")
    if submitted and ticker and cantidad > 0:
        nuevo = {
            "Activo": activo,
            "Ticker": ticker.upper(),
            "Tipo": tipo,
            "Precio Compra": precio_compra,
            "Cantidad": cantidad
        }
        st.session_state.portfolio = pd.concat([st.session_state.portfolio, pd.DataFrame([nuevo])], ignore_index=True)

# Mostrar la cartera
st.subheader("📋 Tu Cartera de Inversión")
portfolio = st.session_state.portfolio.copy()

if not portfolio.empty:
    precios_actuales = []
    for t in portfolio["Ticker"]:
        try:
            datos = yf.Ticker(t).history(period="1d")
            ultimo_precio = datos["Close"].iloc[-1]
        except:
            ultimo_precio = None
        precios_actuales.append(ultimo_precio)

    portfolio["Precio Actual"] = precios_actuales
    portfolio["Valor Actual"] = portfolio["Precio Actual"] * portfolio["Cantidad"]
    portfolio["Valor Compra"] = portfolio["Precio Compra"] * portfolio["Cantidad"]
    portfolio["Rentabilidad %"] = ((portfolio["Precio Actual"] - portfolio["Precio Compra"]) / portfolio["Precio Compra"]) * 100

    total_valor = portfolio["Valor Actual"].sum()
    portfolio["% del Portfolio"] = (portfolio["Valor Actual"] / total_valor) * 100

    st.dataframe(portfolio.style.format({
        "Precio Compra": "€{:.2f}",
        "Precio Actual": "€{:.2f}",
        "Valor Actual": "€{:.2f}",
        "Valor Compra": "€{:.2f}",
        "Rentabilidad %": "{:.2f}%",
        "% del Portfolio": "{:.2f}%"
    }))

    st.markdown(f"**💰 Valor total actual de tu portfolio:** €{total_valor:,.2f}")
else:
    st.info("Todavía no has añadido ningún activo.")
