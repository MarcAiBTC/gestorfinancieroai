import streamlit as st
import pandas as pd
import yfinance as yf
import json
import os
import numpy as np
import plotly.express as px
from typing import List, Dict

PORTFOLIO_FILE = "portfolio.json"

# ---------------------------- FUNCIONES ---------------------------- #

def load_portfolio() -> pd.DataFrame:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["symbol", "quantity", "buy_price"])

def save_portfolio(df: pd.DataFrame) -> None:
    df.to_json(PORTFOLIO_FILE, orient="records", indent=2)

@st.cache_data(ttl=300)
def fetch_current_prices(symbols: List[str]) -> Dict[str, float]:
    if not symbols:
        return {}
    data = yf.download(symbols, period="1d", progress=False)["Adj Close"].iloc[-1]
    if isinstance(data, pd.Series):
        return data.to_dict()
    return {symbols[0]: float(data)}

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    prices = fetch_current_prices(df["symbol"].tolist())
    df = df.copy()
    df["current_price"] = df["symbol"].map(prices)
    df["market_value"] = df["current_price"] * df["quantity"]
    df["total_cost"] = df["buy_price"] * df["quantity"]
    df["pnl"] = df["market_value"] - df["total_cost"]
    df["return_pct"] = (df["current_price"] / df["buy_price"] - 1) * 100
    total = df["market_value"].sum()
    df["weight_pct"] = df["market_value"] / total * 100
    return df

def fetch_history(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    symbols = df["symbol"].tolist()
    quantities = df.set_index("symbol")["quantity"]
    data = yf.download(symbols, period="1y", progress=False)["Adj Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame(symbols[0])
    data = data.fillna(method="ffill")
    for col in data.columns:
        data[col] *= quantities[col]
    history = data.sum(axis=1)
    return history

def add_asset(symbol: str, qty: float, price: float) -> None:
    df = st.session_state.portfolio
    if symbol in df["symbol"].values:
        df.loc[df["symbol"] == symbol, ["quantity", "buy_price"]] = [qty, price]
    else:
        df.loc[len(df)] = [symbol, qty, price]
    st.session_state.portfolio = df
    save_portfolio(df)

def remove_asset(symbol: str) -> None:
    df = st.session_state.portfolio
    df = df[df["symbol"] != symbol]
    st.session_state.portfolio = df
    save_portfolio(df)

# ---------------------------- STREAMLIT APP ---------------------------- #

st.set_page_config(page_title="Gestor Financiero", layout="wide")
st.title("📊 Gestor Financiero IA")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# Sidebar: Añadir / Eliminar activo
with st.sidebar:
    st.header("➕ Añadir / Actualizar activo")
    with st.form("add_form", clear_on_submit=True):
        symbol = st.text_input("Ticker", max_chars=10).upper()
        qty = st.number_input("Cantidad", min_value=0.0, step=1.0)
        price = st.number_input("Precio de compra ($)", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Añadir o actualizar")
        if submitted and symbol:
            add_asset(symbol, qty, price)
            st.experimental_rerun()

    st.header("🗑️ Eliminar activo")
    if not st.session_state.portfolio.empty:
        to_remove = st.selectbox("Selecciona activo", st.session_state.portfolio["symbol"].tolist())
        if st.button("Eliminar"):
            remove_asset(to_remove)
            st.experimental_rerun()

# Mostrar datos de cartera
portfolio_df = compute_metrics(st.session_state.portfolio)

st.subheader("📋 Tu cartera actual")
st.dataframe(portfolio_df.set_index("symbol"), use_container_width=True, height=300)

if not portfolio_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Distribución por activo")
        fig = px.pie(portfolio_df, names="symbol", values="market_value", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Rentabilidad (%)")
        fig = px.bar(portfolio_df, x="symbol", y="return_pct", color="symbol", text_auto=".2f")
        st.plotly_chart(fig, use_container_width=True)

    history = fetch_history(st.session_state.portfolio)
    if not history.empty:
        st.markdown("### Evolución del valor del portfolio")
        st.line_chart(history)

    avg_return = portfolio_df["return_pct"].mean()
    daily_returns = history.pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) if not daily_returns.empty else np.nan

    st.markdown("---")
    st.markdown(f"📈 **Rentabilidad media:** {avg_return:.2f}%")
    if not np.isnan(volatility):
        st.markdown(f"📉 **Volatilidad anualizada:** {volatility:.2%}")
else:
    st.info("Agrega algunos activos para empezar.")
