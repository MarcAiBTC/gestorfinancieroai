# 💼 Portfolio Manager Pro

Un gestor de portfolio financiero profesional, visual e interactivo desarrollado en Python con Streamlit. Diseñado para inversores reales que buscan una herramienta intuitiva para gestionar y analizar sus inversiones.

## 🚀 Características Principales

### ✨ Interfaz Visual e Intuitiva
- **Diseño moderno**: Interfaz limpia y profesional con Streamlit
- **Fácil de usar**: Diseñado para usuarios sin conocimientos de programación
- **Responsive**: Se adapta a diferentes tamaños de pantalla
- **Todo en USD**: Todas las cifras mostradas en dólares americanos

### 📊 Portfolio Dinámico
- **Añadir/Eliminar activos**: Gestión sencilla de acciones, ETFs, índices, oro, etc.
- **Formularios intuitivos**: Ingreso de datos simple y validado
- **Tabla editable**: Modificación rápida de cantidades y precios

### 📈 Datos en Tiempo Real
- **Yahoo Finance API**: Conexión automática para precios actualizados
- **Cálculos automáticos**:
  - Precio actual vs precio de compra
  - Rentabilidad individual y total del portfolio
  - Peso de cada activo en el portfolio
  - Valor acumulado y ganancias/pérdidas

### 📊 Gráficos Integrados
- **Gráfico circular**: Distribución porcentual por activo
- **Gráfico de barras**: Rendimiento individual de cada activo
- **Análisis por sectores**: Diversificación del portfolio
- **Evolución temporal**: Seguimiento del performance

### 💾 Persistencia de Datos
- **Guardado automático**: El portfolio se guarda automáticamente en formato JSON
- **Importar/Exportar**: Descarga y carga de archivos de portfolio
- **Recuperación automática**: Los datos se cargan automáticamente al iniciar

### 🧠 Análisis Inteligente
- **Métricas avanzadas**: Rentabilidad, volatilidad, diversificación
- **Estadísticas del portfolio**: Análisis completo del rendimiento
- **Recomendaciones**: Sugerencias basadas en la composición del portfolio
- **Análisis sectorial**: Distribución y performance por industrias

## 🛠️ Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Local

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu-usuario/portfolio-manager-pro.git
cd portfolio-manager-pro
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv portfolio_env
source portfolio_env/bin/activate  # En Windows: portfolio_env\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**:
```bash
streamlit run main.py
```

5. **Abrir en el navegador**:
La aplicación se abrirá automáticamente
