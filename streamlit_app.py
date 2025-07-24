import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import json
import os
from typing import Dict, List, Tuple
import time

# Configuración de página
st.set_page_config(
    page_title="💼 Portfolio Manager Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00ff00;
        font-weight: bold;
    }
    .negative {
        color: #ff0000;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

class PortfolioManager:
    def __init__(self):
        self.portfolio_file = "portfolio_data.json"
        self.init_session_state()
    
    def init_session_state(self):
        """Inicializar el estado de la sesión"""
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = self.load_portfolio()
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
    
    def load_portfolio(self) -> List[Dict]:
        """Cargar portfolio desde archivo JSON"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            st.error(f"Error cargando portfolio: {e}")
            return []
    
    def save_portfolio(self, portfolio: List[Dict]):
        """Guardar portfolio en archivo JSON"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio, f, indent=2)
            st.success("✅ Portfolio guardado automáticamente")
        except Exception as e:
            st.error(f"Error guardando portfolio: {e}")
    
    @st.cache_data(ttl=300)  # Cache por 5 minutos
    def fetch_stock_data(_self, ticker: str) -> Dict:
        """Obtener datos de un activo desde Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Obtener datos adicionales
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 'N/A')
            dividend_yield = info.get('dividendYield', 0)
            
            return {
                'current_price': round(current_price, 2),
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield * 100 if dividend_yield else 0,
                'sector': info.get('sector', 'N/A'),
                'company_name': info.get('longName', ticker)
            }
        except Exception as e:
            st.error(f"Error obteniendo datos de {ticker}: {e}")
            return None
    
    def calculate_portfolio_metrics(self, portfolio: List[Dict]) -> Dict:
        """Calcular métricas del portfolio"""
        if not portfolio:
            return {
                'total_value': 0,
                'total_cost': 0,
                'total_return': 0,
                'total_return_pct': 0,
                'num_assets': 0
            }
        
        total_value = sum(asset.get('current_value', 0) for asset in portfolio)
        total_cost = sum(asset.get('total_cost', 0) for asset in portfolio)
        total_return = total_value - total_cost
        total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'num_assets': len(portfolio)
        }
    
    def update_portfolio_prices(self, portfolio: List[Dict]) -> List[Dict]:
        """Actualizar precios de todos los activos del portfolio"""
        updated_portfolio = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, asset in enumerate(portfolio):
            status_text.text(f"Actualizando {asset['ticker']}...")
            
            stock_data = self.fetch_stock_data(asset['ticker'])
            
            if stock_data:
                asset['current_price'] = stock_data['current_price']
                asset['current_value'] = asset['shares'] * stock_data['current_price']
                asset['return_amount'] = asset['current_value'] - asset['total_cost']
                asset['return_pct'] = (asset['return_amount'] / asset['total_cost']) * 100 if asset['total_cost'] > 0 else 0
                asset['company_name'] = stock_data['company_name']
                asset['sector'] = stock_data['sector']
                asset['pe_ratio'] = stock_data['pe_ratio']
                asset['dividend_yield'] = stock_data['dividend_yield']
            
            updated_portfolio.append(asset)
            progress_bar.progress((i + 1) / len(portfolio))
        
        status_text.text("✅ Actualización completada")
        time.sleep(1)
        status_text.empty()
        progress_bar.empty()
        
        return updated_portfolio

def main():
    pm = PortfolioManager()
    
    # Header principal
    st.markdown('<h1 class="main-header">💼 Portfolio Manager Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar para navegación
    with st.sidebar:
        st.markdown("### 🧭 Navegación")
        page = st.radio(
            "Seleccionar página:",
            ["📊 Dashboard", "➕ Añadir Activo", "✏️ Editar Portfolio", "📈 Análisis"]
        )
        
        st.markdown("---")
        
        # Botón de actualización
        if st.button("🔄 Actualizar Precios", type="primary"):
            with st.spinner("Actualizando datos..."):
                st.session_state.portfolio = pm.update_portfolio_prices(st.session_state.portfolio)
                pm.save_portfolio(st.session_state.portfolio)
                st.session_state.last_update = datetime.now()
                st.rerun()
        
        # Información de última actualización
        if st.session_state.last_update:
            st.caption(f"Última actualización: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Opciones de archivo
        st.markdown("### 💾 Gestión de Datos")
        
        # Descargar portfolio
        if st.session_state.portfolio:
            portfolio_json = json.dumps(st.session_state.portfolio, indent=2)
            st.download_button(
                label="📥 Descargar Portfolio",
                data=portfolio_json,
                file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Subir portfolio
        uploaded_file = st.file_uploader("📤 Cargar Portfolio", type=['json'])
        if uploaded_file:
            try:
                portfolio_data = json.load(uploaded_file)
                st.session_state.portfolio = portfolio_data
                pm.save_portfolio(portfolio_data)
                st.success("Portfolio cargado exitosamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error cargando archivo: {e}")
    
    # Contenido principal según la página seleccionada
    if page == "📊 Dashboard":
        show_dashboard(pm)
    elif page == "➕ Añadir Activo":
        show_add_asset(pm)
    elif page == "✏️ Editar Portfolio":
        show_edit_portfolio(pm)
    elif page == "📈 Análisis":
        show_analysis(pm)

def show_dashboard(pm: PortfolioManager):
    """Mostrar dashboard principal"""
    portfolio = st.session_state.portfolio
    
    if not portfolio:
        st.info("👋 ¡Bienvenido! Comienza añadiendo tu primer activo usando la barra lateral.")
        return
    
    # Calcular métricas
    metrics = pm.calculate_portfolio_metrics(portfolio)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Valor Total",
            value=f"${metrics['total_value']:,.2f}",
            delta=f"${metrics['total_return']:,.2f}"
        )
    
    with col2:
        st.metric(
            label="📈 Rentabilidad",
            value=f"{metrics['total_return_pct']:.2f}%",
            delta=f"${metrics['total_return']:,.2f}"
        )
    
    with col3:
        st.metric(
            label="💵 Inversión Total",
            value=f"${metrics['total_cost']:,.2f}"
        )
    
    with col4:
        st.metric(
            label="🎯 Activos",
            value=metrics['num_assets']
        )
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de distribución
        if portfolio:
            df = pd.DataFrame(portfolio)
            fig_pie = px.pie(
                df, 
                values='current_value', 
                names='ticker',
                title="📊 Distribución del Portfolio",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Gráfico de rendimiento
        if portfolio:
            df = pd.DataFrame(portfolio)
            df_sorted = df.sort_values('return_pct', ascending=True)
            
            colors = ['red' if x < 0 else 'green' for x in df_sorted['return_pct']]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=df_sorted['return_pct'],
                    y=df_sorted['ticker'],
                    orientation='h',
                    marker_color=colors
                )
            ])
            
            fig_bar.update_layout(
                title="📈 Rendimiento por Activo (%)",
                xaxis_title="Rentabilidad (%)",
                yaxis_title="Ticker"
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tabla detallada
    st.markdown("### 📋 Detalle del Portfolio")
    
    if portfolio:
        df = pd.DataFrame(portfolio)
        
        # Formatear columnas para mostrar
        display_df = df[['ticker', 'company_name', 'shares', 'avg_price', 'current_price', 
                        'current_value', 'return_amount', 'return_pct', 'sector']].copy()
        
        display_df.columns = ['Ticker', 'Empresa', 'Acciones', 'Precio Compra', 
                             'Precio Actual', 'Valor Actual', 'Ganancia/Pérdida', 'Rentabilidad %', 'Sector']
        
        # Formatear números
        display_df['Precio Compra'] = display_df['Precio Compra'].apply(lambda x: f"${x:.2f}")
        display_df['Precio Actual'] = display_df['Precio Actual'].apply(lambda x: f"${x:.2f}")
        display_df['Valor Actual'] = display_df['Valor Actual'].apply(lambda x: f"${x:,.2f}")
        display_df['Ganancia/Pérdida'] = display_df['Ganancia/Pérdida'].apply(lambda x: f"${x:,.2f}")
        display_df['Rentabilidad %'] = display_df['Rentabilidad %'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df, use_container_width=True)

def show_add_asset(pm: PortfolioManager):
    """Mostrar formulario para añadir activo"""
    st.markdown("### ➕ Añadir Nuevo Activo")
    
    with st.form("add_asset_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input("Ticker (ej: AAPL, MSFT)", help="Símbolo del activo en Yahoo Finance").upper()
            shares = st.number_input("Número de acciones", min_value=0.001, step=0.001, format="%.3f")
        
        with col2:
            avg_price = st.number_input("Precio promedio de compra ($)", min_value=0.01, step=0.01, format="%.2f")
            purchase_date = st.date_input("Fecha de compra", value=datetime.now().date())
        
        submitted = st.form_submit_button("📊 Añadir al Portfolio", type="primary")
        
        if submitted:
            if ticker and shares > 0 and avg_price > 0:
                # Verificar si el ticker ya existe
                existing_tickers = [asset['ticker'] for asset in st.session_state.portfolio]
                
                if ticker in existing_tickers:
                    st.warning(f"⚠️ {ticker} ya existe en el portfolio. Usa la sección de edición para modificarlo.")
                else:
                    # Obtener datos del activo
                    with st.spinner(f"Obteniendo datos de {ticker}..."):
                        stock_data = pm.fetch_stock_data(ticker)
                    
                    if stock_data:
                        new_asset = {
                            'ticker': ticker,
                            'company_name': stock_data['company_name'],
                            'shares': shares,
                            'avg_price': avg_price,
                            'total_cost': shares * avg_price,
                            'current_price': stock_data['current_price'],
                            'current_value': shares * stock_data['current_price'],
                            'return_amount': (shares * stock_data['current_price']) - (shares * avg_price),
                            'return_pct': ((stock_data['current_price'] - avg_price) / avg_price) * 100,
                            'purchase_date': purchase_date.isoformat(),
                            'sector': stock_data['sector'],
                            'pe_ratio': stock_data['pe_ratio'],
                            'dividend_yield': stock_data['dividend_yield']
                        }
                        
                        st.session_state.portfolio.append(new_asset)
                        pm.save_portfolio(st.session_state.portfolio)
                        
                        st.success(f"✅ {ticker} añadido exitosamente al portfolio!")
                        st.balloons()
                        
                        # Mostrar resumen del activo añadido
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Precio Actual", f"${stock_data['current_price']:.2f}")
                        with col2:
                            st.metric("Valor Total", f"${new_asset['current_value']:,.2f}")
                        with col3:
                            gain_loss = new_asset['return_amount']
                            st.metric("Ganancia/Pérdida", f"${gain_loss:,.2f}", f"{new_asset['return_pct']:.2f}%")
                    else:
                        st.error(f"❌ No se pudo obtener información de {ticker}. Verifica que el ticker sea correcto.")
            else:
                st.error("❌ Por favor completa todos los campos correctamente.")

def show_edit_portfolio(pm: PortfolioManager):
    """Mostrar interfaz para editar portfolio"""
    st.markdown("### ✏️ Editar Portfolio")
    
    if not st.session_state.portfolio:
        st.info("No hay activos en el portfolio para editar.")
        return
    
    # Seleccionar activo para editar
    tickers = [asset['ticker'] for asset in st.session_state.portfolio]
    selected_ticker = st.selectbox("Seleccionar activo para editar:", tickers)
    
    if selected_ticker:
        # Encontrar el activo seleccionado
        asset_index = next(i for i, asset in enumerate(st.session_state.portfolio) if asset['ticker'] == selected_ticker)
        asset = st.session_state.portfolio[asset_index]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Editar Activo")
            
            with st.form("edit_asset_form"):
                new_shares = st.number_input("Número de acciones", value=asset['shares'], min_value=0.001, step=0.001, format="%.3f")
                new_avg_price = st.number_input("Precio promedio ($)", value=asset['avg_price'], min_value=0.01, step=0.01, format="%.2f")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    update_submitted = st.form_submit_button("💾 Actualizar", type="primary")
                
                with col_btn2:
                    delete_submitted = st.form_submit_button("🗑️ Eliminar", type="secondary")
                
                if update_submitted:
                    # Actualizar datos del activo
                    with st.spinner("Actualizando activo..."):
                        stock_data = pm.fetch_stock_data(selected_ticker)
                    
                    if stock_data:
                        st.session_state.portfolio[asset_index].update({
                            'shares': new_shares,
                            'avg_price': new_avg_price,
                            'total_cost': new_shares * new_avg_price,
                            'current_price': stock_data['current_price'],
                            'current_value': new_shares * stock_data['current_price'],
                            'return_amount': (new_shares * stock_data['current_price']) - (new_shares * new_avg_price),
                            'return_pct': ((stock_data['current_price'] - new_avg_price) / new_avg_price) * 100
                        })
                        
                        pm.save_portfolio(st.session_state.portfolio)
                        st.success("✅ Activo actualizado exitosamente!")
                        st.rerun()
                
                if delete_submitted:
                    st.session_state.portfolio.pop(asset_index)
                    pm.save_portfolio(st.session_state.portfolio)
                    st.success(f"✅ {selected_ticker} eliminado del portfolio!")
                    st.rerun()
        
        with col2:
            st.markdown("#### 📊 Información Actual")
            
            # Mostrar información actual del activo
            st.metric("Empresa", asset['company_name'])
            st.metric("Sector", asset['sector'])
            st.metric("Acciones", f"{asset['shares']:.3f}")
            st.metric("Precio Compra", f"${asset['avg_price']:.2f}")
            st.metric("Precio Actual", f"${asset.get('current_price', 0):.2f}")
            st.metric("Valor Total", f"${asset.get('current_value', 0):,.2f}")
            
            gain_loss = asset.get('return_amount', 0)
            return_pct = asset.get('return_pct', 0)
            st.metric("Ganancia/Pérdida", f"${gain_loss:,.2f}", f"{return_pct:.2f}%")

def show_analysis(pm: PortfolioManager):
    """Mostrar análisis avanzado del portfolio"""
    st.markdown("### 📈 Análisis Avanzado")
    
    if not st.session_state.portfolio:
        st.info("No hay datos suficientes para el análisis.")
        return
    
    df = pd.DataFrame(st.session_state.portfolio)
    
    # Análisis por sectores
    st.markdown("#### 🏢 Análisis por Sectores")
    
    sector_analysis = df.groupby('sector').agg({
        'current_value': 'sum',
        'return_pct': 'mean',
        'ticker': 'count'
    }).round(2)
    
    sector_analysis.columns = ['Valor Total ($)', 'Rentabilidad Promedio (%)', 'Número de Activos']
    sector_analysis['Peso (%)'] = (sector_analysis['Valor Total ($)'] / sector_analysis['Valor Total ($)'].sum() * 100).round(2)
    
    st.dataframe(sector_analysis, use_container_width=True)
    
    # Gráfico de sectores
    fig_sector = px.bar(
        sector_analysis.reset_index(), 
        x='sector', 
        y='Valor Total ($)',
        title="💼 Valor por Sector",
        color='Rentabilidad Promedio (%)',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_sector, use_container_width=True)
    
    # Estadísticas generales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Estadísticas del Portfolio")
        
        total_value = df['current_value'].sum()
        total_cost = df['total_cost'].sum()
        avg_return = df['return_pct'].mean()
        volatility = df['return_pct'].std()
        
        st.metric("Valor Total", f"${total_value:,.2f}")
        st.metric("Inversión Total", f"${total_cost:,.2f}")
        st.metric("Rentabilidad Promedio", f"{avg_return:.2f}%")
        st.metric("Volatilidad", f"{volatility:.2f}%")
    
    with col2:
        st.markdown("#### 🎯 Top Performers")
        
        # Mejores y peores activos
        best_performer = df.loc[df['return_pct'].idxmax()]
        worst_performer = df.loc[df['return_pct'].idxmin()]
        
        st.success(f"🚀 Mejor: {best_performer['ticker']} (+{best_performer['return_pct']:.2f}%)")
        st.error(f"📉 Peor: {worst_performer['ticker']} ({worst_performer['return_pct']:.2f}%)")
        
        # Activo con mayor peso
        largest_holding = df.loc[df['current_value'].idxmax()]
        weight = (largest_holding['current_value'] / total_value) * 100
        st.info(f"⚖️ Mayor peso: {largest_holding['ticker']} ({weight:.1f}%)")
    
    # Diversificación
    st.markdown("#### 🎲 Análisis de Diversificación")
    
    num_sectors = df['sector'].nunique()
    num_assets = len(df)
    concentration = (df['current_value'].max() / total_value) * 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Sectores Diferentes", num_sectors)
    
    with col2:
        st.metric("Total de Activos", num_assets)
    
    with col3:
        st.metric("Concentración Máxima", f"{concentration:.1f}%")
    
    # Recomendaciones básicas
    st.markdown("#### 💡 Recomendaciones")
    
    recommendations = []
    
    if concentration > 30:
        recommendations.append("⚠️ Alta concentración en un activo. Considera diversificar.")
    
    if num_sectors < 3:
        recommendations.append("🎯 Pocos sectores representados. Añade diversificación sectorial.")
    
    if avg_return < 0:
        recommendations.append("📉 Rentabilidad promedio negativa. Revisa tu estrategia.")
    
    if volatility > 20:
        recommendations.append("🌊 Alta volatilidad. Considera activos más estables.")
    
    if not recommendations:
        recommendations.append("✅ Portfolio bien diversificado y balanceado.")
    
    for rec in recommendations:
        st.write(rec)

if __name__ == "__main__":
    main()
