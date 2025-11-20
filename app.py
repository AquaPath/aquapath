"""
AquaPath - Sistema de Optimización de Pozos y Reservorios
Aplicación Web para Optimización de Infraestructura Hídrica en Barranca, Lima

Universidad Peruana de Ciencias Aplicadas
Curso: Complejidad Algorítmica
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Agregar path de módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from algorithms.graph_algorithms import WaterNetworkOptimizer
from utils.visualization import (
    plot_network_graph, 
    plot_mst_comparison,
    generate_report_data,
    create_statistics_summary
)

# Configuración de la página
st.set_page_config(
    page_title="AquaPath - Optimización Hídrica",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #06A77D;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #06A77D;
    }
    .stButton>button {
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #06A77D;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Carga los datasets de comunidades y pozos"""
    try:
        communities = pd.read_csv('data/Dataset_Barranca.csv')
        wells = pd.read_csv('data/Pozos_Barranca.csv')
        return communities, wells
    except FileNotFoundError:
        st.error("❌ Error: No se encontraron los archivos de datos. Asegúrate de tener Dataset_Barranca.csv y Pozos_Barranca.csv en la carpeta 'data'.")
        st.stop()


def main():
    """Función principal de la aplicación"""
    
    # Header
    st.markdown('<p class="main-header">💧 AquaPath</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #555;">Sistema de Optimización de Pozos y Reservorios en Barranca, Lima</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando datos..."):
        communities_df, wells_df = load_data()
    
    # Sidebar - Parámetros de optimización
    st.sidebar.image("https://via.placeholder.com/300x100/2E86AB/FFFFFF?text=AquaPath", use_column_width=True)
    st.sidebar.markdown("## ⚙️ Parámetros de Optimización")
    
    # Selección de algoritmo
    algorithm = st.sidebar.selectbox(
        "Algoritmo de Optimización",
        ["MST (Kruskal)", "Híbrido (Dijkstra + Kruskal)"],
        help="Selecciona el algoritmo para optimizar la red"
    )
    
    # Tipo de servicio
    service_types = ['TODOS', 'EMERGENCIA', 'NORMAL']
    service_type = st.sidebar.selectbox(
        "Tipo de Servicio",
        service_types,
        index=1,
        help="Filtra comunidades por tipo de servicio"
    )
    
    # Número de pozos (solo para híbrido)
    k_wells = 3
    if algorithm == "Híbrido (Dijkstra + Kruskal)":
        k_wells = st.sidebar.slider(
            "Número de Pozos a Utilizar",
            min_value=1,
            max_value=len(wells_df),
            value=3,
            help="Selecciona cuántos pozos incluir en la optimización"
        )
    
    # Presupuesto máximo
    use_budget = st.sidebar.checkbox("Establecer Presupuesto Máximo", value=False)
    budget = None
    if use_budget:
        budget = st.sidebar.number_input(
            "Presupuesto Máximo (S/)",
            min_value=50000,
            max_value=1000000,
            value=300000,
            step=10000,
            help="Define el presupuesto máximo disponible"
        )
    
    # Distrito específico
    districts = ['Todos'] + sorted(communities_df['DISTRITO'].unique().tolist())
    selected_district = st.sidebar.selectbox(
        "Filtrar por Distrito",
        districts,
        help="Filtra comunidades por distrito"
    )
    
    st.sidebar.markdown("---")
    optimize_button = st.sidebar.button("🚀 Ejecutar Optimización", use_container_width=True)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🗺️ Visualización de Red", "📈 Análisis", "📄 Reporte"])
    
    # TAB 1: Dashboard
    with tab1:
        st.markdown('<p class="sub-header">Resumen del Sistema</p>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Filtrar comunidades
        filtered_communities = communities_df.copy()
        if service_type != 'TODOS':
            filtered_communities = filtered_communities[
                filtered_communities['TIPO_DE_SERVICIO'] == service_type
            ]
        if selected_district != 'Todos':
            filtered_communities = filtered_communities[
                filtered_communities['DISTRITO'] == selected_district
            ]
        
        with col1:
            st.metric(
                "🏘️ Comunidades Analizadas",
                len(filtered_communities),
                help="Número total de comunidades en el análisis"
            )
        
        with col2:
            operational_wells = len(wells_df[wells_df['Estado'] == 'Operativo'])
            st.metric(
                "💧 Pozos Operativos",
                operational_wells,
                help="Pozos disponibles para distribución"
            )
        
        with col3:
            total_demand = filtered_communities['CANTIDAD_DISTRIBUCIÓN'].sum()
            st.metric(
                "📊 Demanda Total",
                f"{total_demand:,} m³",
                help="Volumen total de agua requerido"
            )
        
        with col4:
            total_households = filtered_communities['VIVIENDAS_BENEFICIADAS'].sum()
            st.metric(
                "🏠 Viviendas Beneficiadas",
                f"{total_households:,}",
                help="Número de viviendas a conectar"
            )
        
        st.markdown("---")
        
        # Información del dataset
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📍 Datos de Comunidades")
            st.dataframe(
                filtered_communities[[
                    'DISTRITO', 'ZONA', 'TIPO_DE_SERVICIO', 
                    'CANTIDAD_DISTRIBUCIÓN', 'VIVIENDAS_BENEFICIADAS'
                ]].head(10),
                use_container_width=True,
                height=300
            )
        
        with col2:
            st.markdown("### 🔧 Pozos Disponibles")
            st.dataframe(
                wells_df[[
                    'ID_Pozo', 'Distrito', 'Caudal_Lps', 
                    'Estado', 'Uso_Principal'
                ]].head(10),
                use_container_width=True,
                height=300
            )
        
        # Mapa de ubicación (placeholder)
        st.markdown("### 🗺️ Mapa de Optimización - Barranca")
        st.info("📍 Visualización geoespacial de pozos y comunidades en la provincia de Barranca, Lima")
        
        # Crear un mapa simple con las coordenadas
        map_data = filtered_communities[['COORDENADA_NORTE', 'COORDENADA_ESTE']].copy()
        map_data.columns = ['lat', 'lon']
        # Convertir UTM a lat/lon aproximado (simplificado)
        map_data['lat'] = -10.75 + (map_data['lat'] - 8805000) / 111000
        map_data['lon'] = -77.76 + (map_data['lon'] - 213500) / 111000
        st.map(map_data, zoom=11)
    
    # TAB 2: Visualización
    with tab2:
        if not optimize_button:
            st.info("👆 Configura los parámetros en el panel lateral y presiona 'Ejecutar Optimización' para visualizar la red.")
        else:
            with st.spinner("🔄 Optimizando red de distribución..."):
                # Filtrar datos según distrito
                filtered_comm = communities_df.copy()
                if selected_district != 'Todos':
                    filtered_comm = filtered_comm[filtered_comm['DISTRITO'] == selected_district]
                
                # Crear optimizador
                optimizer = WaterNetworkOptimizer(filtered_comm, wells_df)
                
                # Ejecutar según algoritmo seleccionado
                if algorithm == "MST (Kruskal)":
                    # Construir grafo completo
                    G = optimizer.build_complete_graph(service_type=service_type)
                    
                    # Aplicar Kruskal
                    mst, total_cost, exec_time, stats = optimizer.kruskal_mst(budget=budget)
                    
                else:  # Híbrido
                    mst, stats = optimizer.hybrid_optimization(
                        k_wells=k_wells,
                        service_type=service_type
                    )
                    G = optimizer.graph
                
                st.success(f"✅ Optimización completada en {stats['execution_time']:.4f} segundos")
                
                # Guardar en session state
                st.session_state['mst'] = mst
                st.session_state['original_graph'] = G
                st.session_state['stats'] = stats
                
                # Visualizar comparación
                st.markdown("### 🔍 Comparación: Grafo Completo vs MST Optimizado")
                fig_comparison = plot_mst_comparison(G, mst, stats)
                st.pyplot(fig_comparison)
                
                # Métricas de optimización
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 Costo Total", f"S/ {stats['total_cost']:,.0f}")
                
                with col2:
                    st.metric("📏 Longitud Total", f"{stats['total_distance']:.2f} km")
                
                with col3:
                    efficiency = ((G.number_of_edges() - mst.number_of_edges()) / G.number_of_edges()) * 100
                    st.metric("⚡ Eficiencia", f"+{efficiency:.1f}%", delta="vs. Red Completa")
                
                with col4:
                    st.metric("⏱️ Tiempo Ejecución", f"{stats['execution_time']:.4f} s")
    
    # TAB 3: Análisis
    with tab3:
        if 'stats' not in st.session_state:
            st.info("👆 Ejecuta primero la optimización en la pestaña 'Visualización de Red'")
        else:
            stats = st.session_state['stats']
            mst = st.session_state['mst']
            
            st.markdown('<p class="sub-header">📊 Análisis Detallado de la Red</p>', unsafe_allow_html=True)
            
            # Estadísticas visuales
            fig_stats = create_statistics_summary(stats)
            st.pyplot(fig_stats)
            
            st.markdown("---")
            
            # Información del algoritmo
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🧮 Información del Algoritmo")
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Algoritmo:</strong> Kruskal (MST)<br>
                    <strong>Complejidad Temporal:</strong> {stats['complexity']}<br>
                    <strong>Complejidad Espacial:</strong> O(V + E)<br>
                    <strong>Nodos Procesados:</strong> {stats['nodes']}<br>
                    <strong>Aristas Evaluadas:</strong> {stats['edges']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📈 Resultados Principales")
                st.markdown(f"""
                <div class="metric-card">
                    <strong>Reducción de Costos:</strong> {efficiency:.1f}% vs red completa<br>
                    <strong>Pozos Utilizados:</strong> {stats['wells']}<br>
                    <strong>Comunidades Conectadas:</strong> {stats['communities']}<br>
                    <strong>Costo Promedio/km:</strong> S/ {stats['avg_cost_per_km']:,.2f}
                </div>
                """, unsafe_allow_html=True)
            
            # Distribución de comunidades
            st.markdown("### 🏘️ Distribución de Comunidades por Distrito")
            district_counts = communities_df.groupby('DISTRITO').size().reset_index(name='Cantidad')
            st.bar_chart(district_counts.set_index('DISTRITO'))
    
    # TAB 4: Reporte
    with tab4:
        if 'stats' not in st.session_state:
            st.info("👆 Ejecuta primero la optimización en la pestaña 'Visualización de Red'")
        else:
            stats = st.session_state['stats']
            mst = st.session_state['mst']
            
            st.markdown('<p class="sub-header">📄 Reporte de Optimización de Infraestructura Hídrica</p>', unsafe_allow_html=True)
            
            # Resumen ejecutivo
            st.markdown("### 📋 Resumen Ejecutivo")
            st.markdown(f"""
            <div class="info-box">
                <strong>Objetivo del Análisis:</strong><br>
                Determinar la ubicación óptima de pozos y/o reservorios para minimizar costos de instalación 
                y maximizar cobertura en comunidades de Barranca, Lima.
                <br><br>
                <strong>Resultados Principales:</strong>
                <ul>
                    <li>Reducción de costos: {efficiency:.1f}% respecto a enfoque tradicional</li>
                    <li>Comunidades conectadas: {stats['communities']} zonas</li>
                    <li>Longitud de red optimizada: {stats['total_distance']:.2f} km</li>
                    <li>Inversión total estimada: S/ {stats['total_cost']:,.0f}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Desglose de costos
            st.markdown("### 💰 Desglose de Costos")
            df_costs, df_schedule = generate_report_data(stats, mst)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(df_costs, use_container_width=True, hide_index=True)
            
            with col2:
                st.metric("COSTO TOTAL DE INVERSIÓN", f"S/ {df_costs['Costo (S/)'].sum():,.0f}", help="Inversión total del proyecto")
            
            # Cronograma
            st.markdown("### 📅 Cronograma de Implementación")
            st.dataframe(df_schedule, use_container_width=True, hide_index=True)
            
            # Recomendaciones técnicas
            st.markdown("### 🔧 Recomendaciones Técnicas")
            st.markdown("""
            <div class="info-box">
                <strong>1. Implementación Prioritaria:</strong><br>
                Iniciar instalación en áreas Norte (Barranca-Centro) por mayor densidad poblacional y menor costo de instalación.
                <br><br>
                <strong>2. Consideraciones Hidrogeológicas:</strong><br>
                Verificar estudios de suelos en zonas identificadas antes de perforación. Considerar tabla freática en época de lluvias.
                <br><br>
                <strong>3. Sostenibilidad del Proyecto:</strong><br>
                Establecer plan de mantenimiento preventivo de 24 meses con presupuesto estimado del 4% de la inversión inicial.
                </div>
            """, unsafe_allow_html=True)
            
            # Botón de exportación
            st.markdown("---")
            if st.button("📥 Exportar Reporte Completo", use_container_width=True):
                st.success("✅ Funcionalidad de exportación en desarrollo. El reporte se generará en formato PDF.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        <p>© 2025 AquaPath | Universidad Peruana de Ciencias Aplicadas<br>
        Desarrollado por: July Paico, Jesús Paucar, Moisés Espinoza | Curso: Complejidad Algorítmica</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
