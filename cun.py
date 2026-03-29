#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Análisis de Deserción Estudiantil - CUN
VERSIÓN OPTIMIZADA: Procesamiento rápido de CSV
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import time  # Para medir tiempos

# ============================================================
# CONFIGURACIÓN INICIAL OPTIMIZADA
# ============================================================

st.set_page_config(
    page_title="Análisis de Deserción Estudiantil - CUN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS mínimo esencial (eliminado estilos pesados)
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; text-align: center; }
    .metric-container {
        background: white; border-radius: 10px; padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid; margin: 0.5rem 0;
    }
    .border-red { border-left-color: #ef4444; }
    .border-orange { border-left-color: #f59e0b; }
    .border-green { border-left-color: #10b981; }
    .border-blue { border-left-color: #3b82f6; }
    .text-red { color: #ef4444; }
    .text-orange { color: #f59e0b; }
    .text-green { color: #10b981; }
    .text-blue { color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIONES OPTIMIZADAS (Vectorizadas)
# ============================================================

def limpiar_columnas(df):
    """Limpia nombres de columnas"""
    df.columns = [str(col).strip().replace('<br>', '').replace('\n', '') 
                  for col in df.columns]
    return df

def procesar_csv_optimizado(file, placeholder_status):
    """
    Versión ultra rápida del procesamiento
    """
    t_inicio = time.time()
    
    # 1. LECTURA (debe ser < 1 seg)
    t0 = time.time()
    try:
        # Intentar leer directamente, saltando filas de encabezado duplicado si existen
        df_raw = pd.read_csv(file)
        # Eliminar filas donde 'id' sea 'id' (fila de encabezado duplicada de Forms)
        if 'id' in df_raw.columns:
            df_raw = df_raw[df_raw['id'] != 'id']
    except Exception as e:
        # Si falla, intentar con encoding diferente
        file.seek(0)
        df_raw = pd.read_csv(file, encoding='latin1')
    
    t1 = time.time()
    placeholder_status.text(f"📄 CSV cargado: {len(df_raw)} filas ({(t1-t0):.2f}s)")
    
    if len(df_raw) == 0:
        return pd.DataFrame()
    
    # 2. LIMPIEZA BÁSICA (< 0.5 seg)
    t0 = time.time()
    df = limpiar_columnas(df_raw)
    
    # Convertir numéricas de una vez (vectorizado)
    cols_numericas = ['semestre', 'promedio_acumulado', 'promedio_ultimo', 
                     'materias_perdidas', 'frecuencia_semanal', 'estrato', 
                     'horas_semanales', 'dependientes', 'satisfaccion_programa', 
                     'probabilidad_continuar_percibida']
    
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    t1 = time.time()
    placeholder_status.text(f"🔧 Datos limpios ({(t1-t0):.2f}s)")
    
    # 3. PROCESAMIENTO VECTORIZADO (sin apply donde sea posible)
    t0 = time.time()
    
    # Crear DataFrame resultado
    result = pd.DataFrame()
    result['id'] = df['id']
    result['programa'] = df['programa']
    result['semestre'] = pd.to_numeric(df['semestre'], errors='coerce').fillna(1)
    result['jornada'] = df.get('Jornada', 'No especificada')
    result['promedio_acumulado'] = df['promedio_acumulado']
    result['promedio_ultimo'] = df['promedio_ultimo']
    result['materias_perdidas'] = df['materias_perdidas'].fillna(0)
    
    # Porcentaje créditos (normalizar si está en escala 0-100)
    pct = df['pct_creditos_aprobados']
    result['pct_creditos_aprobados'] = np.where(pct > 1, pct/100, pct)
    
    # Variables binarias vectorizadas (usando map en lugar de apply)
    result['acceso_plataforma'] = (df.get('acceso_plataforma_mes', '')
                                   .astype(str).str.lower().str.strip()
                                   .isin(['si', 'sí', 'yes', '1'])).astype(int)
    
    result['frecuencia_semanal'] = df['frecuencia_semanal'].fillna(0)
    result['estrato'] = df['estrato'].fillna(2)
    result['estrato_bajo'] = (result['estrato'] <= 2).astype(int)
    
    result['trabaja'] = (df.get('trabaja', '')
                        .astype(str).str.lower().str.strip()
                        .isin(['si', 'sí', 'yes', '1'])).astype(int)
    
    result['horas_semanales'] = df['horas_semanales'].fillna(0)
    result['dependientes'] = df['dependientes'].fillna(0)
    
    # Intención de desertar (vectorizado)
    piensa_desertar = df.get('piensa_desertar', '').astype(str).str.lower()
    result['piensa_desertar_frecuente'] = piensa_desertar.str.contains('frecuente').astype(int)
    result['piensa_desertar_alguna_vez'] = (piensa_desertar.str.contains('frecuente|alguna')).astype(int)
    
    result['satisfaccion_programa'] = df['satisfaccion_programa'].fillna(5)
    result['probabilidad_continuar_percibida'] = df['probabilidad_continuar_percibida'].fillna(5)
    result['evento_estresante'] = df.get('evento_estresante', 'Ninguno').fillna('Ninguno')
    
    # Dificultad pago (vectorizado con np.select)
    dificultad = df.get('dificultad_pago', '').astype(str).str.lower()
    conditions = [
        dificultad.str.contains('grave'),
        dificultad.str.contains('algun'),
        dificultad.str.contains('ningun')
    ]
    choices = [1.0, 0.5, 0.0]
    result['dificultad_pago'] = np.select(conditions, choices, default=0.0)
    
    t1 = time.time()
    placeholder_status.text(f"⚙️ Variables calculadas ({(t1-t0):.2f}s)")
    
    # 4. CÁLCULO DE ÍNDICES (Vectorizado completo)
    t0 = time.time()
    
    # Dificultad percibida (vectorizado)
    dif_perc = df.get('dificultad_percibida', '').astype(str).str.lower()
    score_dificultad = np.select(
        [dif_perc.str.contains('much'), dif_perc.str.contains('algo'), dif_perc.str.contains('poc')],
        [0.9, 0.5, 0.1],
        default=0.5
    )
    
    # Índice riesgo académico (vectorizado)
    prom_norm = (4 - result['promedio_ultimo'].fillna(3)) / 3
    mat_norm = (result['materias_perdidas'] / 5).clip(0, 1)
    cred_factor = 1 - result['pct_creditos_aprobados'].fillna(1)
    
    result['indice_riesgo_academico'] = (
        prom_norm * 0.35 + mat_norm * 0.25 + score_dificultad * 0.25 + cred_factor * 0.15
    ).clip(0, 1)
    
    # Índice engagement (vectorizado)
    frec_norm = (result['frecuencia_semanal'] / 7).clip(0, 1)
    
    # Participación (vectorizado)
    part = df.get('participacion_sincronica', '').astype(str).str.lower()
    score_part = np.select(
        [part.str.contains('siempre'), part.str.contains('regular'), part.str.contains('aveces|1-2')],
        [1.0, 0.7, 0.4],
        default=0.0
    )
    
    # Consulta profesores
    consulta = df.get('consulta_profesores', '').astype(str).str.lower()
    score_consulta = np.select(
        [consulta.str.contains('siempre'), consulta.str.contains('regular'), consulta.str.contains('aveces|1-2')],
        [1.0, 0.7, 0.4],
        default=0.0
    )
    
    # Claridad propósito
    claridad = df.get('claridad_proposito', '').astype(str).str.lower()
    score_claridad = np.select(
        [claridad.str.contains('muy'), claridad.str.contains('algo'), claridad.str.contains('nada')],
        [1.0, 0.5, 0.2],
        default=0.5
    )
    
    result['indice_engagement'] = (
        result['acceso_plataforma'] * 0.25 +
        frec_norm * 0.25 +
        score_part * 0.20 +
        score_consulta * 0.20 +
        score_claridad * 0.10
    ).clip(0, 1)
    
    t1 = time.time()
    placeholder_status.text(f"📊 Índices calculados ({(t1-t0):.2f}s)")
    
    # 5. PROBABILIDAD DE DESERCIÓN (Vectorizado)
    t0 = time.time()
    
    # Factores de riesgo (vectorizados)
    bajo_engagement = 1 - result['indice_engagement']
    piensa_desertar_score = result['piensa_desertar_frecuente'] * 0.8 + result['piensa_desertar_alguna_vez'] * 0.4
    dif_econ = result['dificultad_pago'] * 0.8 + (result['trabaja'] * (result['horas_semanales'] > 30).astype(int) * 0.3)
    evento_estres = (result['evento_estresante'] != 'Ninguno').astype(int) * 0.5
    baja_satisf = (10 - result['satisfaccion_programa']) / 10
    
    result['probabilidad_desercion'] = (
        result['indice_riesgo_academico'] * 0.30 +
        bajo_engagement * 0.20 +
        piensa_desertar_score * 0.25 +
        dif_econ * 0.15 +
        evento_estres * 0.05 +
        baja_satisf * 0.05
    ).clip(0, 1)
    
    # Ajuste por intención frecuente
    mask_frec = result['piensa_desertar_frecuente'] == 1
    result.loc[mask_frec, 'probabilidad_desercion'] = result.loc[mask_frec, 'probabilidad_desercion'].clip(lower=0.7)
    
    # Categorización (vectorizada)
    result['riesgo_categoria'] = pd.cut(
        result['probabilidad_desercion'],
        bins=[-0.1, 0.4, 0.7, 1.0],
        labels=['BAJO', 'MEDIO', 'ALTO']
    ).astype(str)
    
    t1 = time.time()
    placeholder_status.text(f"🎯 Riesgo calculado ({(t1-t0):.2f}s)")
    
    # 6. RECOMENDACIONES (Vectorizado con condiciones múltiples)
    t0 = time.time()
    
    # Crear máscaras para cada tipo de recomendación
    mask_alto_intencion = (result['riesgo_categoria'] == 'ALTO') & (result['piensa_desertar_frecuente'] == 1)
    mask_alto_academico = (result['riesgo_categoria'] == 'ALTO') & (result['indice_riesgo_academico'] > 0.6) & ~mask_alto_intencion
    mask_alto_economico = (result['riesgo_categoria'] == 'ALTO') & (result['dificultad_pago'] > 0.5) & ~(mask_alto_intencion | mask_alto_academico)
    mask_alto_otro = (result['riesgo_categoria'] == 'ALTO') & ~(mask_alto_intencion | mask_alto_academico | mask_alto_economico)
    
    mask_medio_engagement = (result['riesgo_categoria'] == 'MEDIO') & (result['indice_engagement'] < 0.4)
    mask_medio_promedio = (result['riesgo_categoria'] == 'MEDIO') & (result['promedio_ultimo'] < 3.0) & ~mask_medio_engagement
    mask_medio_otro = (result['riesgo_categoria'] == 'MEDIO') & ~(mask_medio_engagement | mask_medio_promedio)
    
    # Asignar recomendaciones
    result['recomendacion'] = "Monitoreo estándar. Mantener buenas prácticas actuales."  # Default BAJO
    result.loc[mask_alto_intencion, 'recomendacion'] = "Intervención psicológica inmediata. Contacto directo por parte del programa."
    result.loc[mask_alto_academico, 'recomendacion'] = "Tutorías académicas urgentes y seguimiento de desempeño semanal."
    result.loc[mask_alto_economico, 'recomendacion'] = "Canalizar a bienestar institucional para apoyo financiero/condonaciones."
    result.loc[mask_alto_otro, 'recomendacion'] = "Revisión integral por comité de permanencia estudiantil."
    result.loc[mask_medio_engagement, 'recomendacion'] = "Programa de acompañamiento virtual y motivacional."
    result.loc[mask_medio_promedio, 'recomendacion'] = "Tutorías académicas preventivas y técnicas de estudio."
    result.loc[mask_medio_otro, 'recomendacion'] = "Monitoreo mensual y contacto periódico por tutor."
    
    # Metadata
    result['fecha_prediccion'] = datetime.now()
    result['modelo_version'] = 'GoogleForms_Opt_v1.0'
    result['target_desercion'] = ((result['probabilidad_desercion'] > 0.6) | 
                                  (result['piensa_desertar_frecuente'] == 1)).astype(int)
    
    t1 = time.time()
    placeholder_status.text(f"💡 Recomendaciones listas ({(t1-t0):.2f}s)")
    
    t_total = time.time() - t_inicio
    placeholder_status.success(f"✅ Análisis completado en {t_total:.2f} segundos")
    
    return result

# ============================================================
# INTERFAZ OPTIMIZADA
# ============================================================

def render_header():
    st.markdown('<div class="main-title">🎓 Análisis de Deserción Estudiantil - CUN</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">'
                'Procesamiento optimizado de Google Forms</div>', unsafe_allow_html=True)

def render_sidebar():
    st.sidebar.markdown("## 🎛️ Panel de Control")
    
    # Carga de archivo única y rápida
    st.sidebar.markdown("### 📁 Cargar Encuesta")
    
    uploaded_file = st.sidebar.file_uploader(
        "Seleccionar archivo CSV",
        type=['csv'],
        key="file_uploader_unique"
    )
    
    # Placeholder para mensajes de estado
    status_placeholder = st.sidebar.empty()
    
    if uploaded_file is not None:
        # Mostrar info del archivo
        file_details = f"📄 {uploaded_file.name} ({uploaded_file.size/1024:.1f} KB)"
        st.sidebar.caption(file_details)
        
        if st.sidebar.button("🚀 Analizar Datos", type="primary", use_container_width=True):
            # Procesar con medición de tiempo
            df_procesado = procesar_csv_optimizado(uploaded_file, status_placeholder)
            
            if not df_procesado.empty:
                st.session_state['datos_procesados'] = df_procesado
                st.session_state['procesado'] = True
                st.rerun()
    
    # Botón limpiar
    if 'datos_procesados' in st.session_state:
        if st.sidebar.button("🗑️ Limpiar Datos", use_container_width=True):
            del st.session_state['datos_procesados']
            del st.session_state['procesado']
            st.rerun()
    
    return st.session_state.get('datos_procesados', pd.DataFrame())

# ============================================================
# VISUALIZACIONES (Mantenidas igual pero optimizadas)
# ============================================================

def render_kpis(df):
    if len(df) == 0:
        return
    
    cols = st.columns(4)
    metricas = [
        (len(df), "Total Estudiantes", "blue"),
        ((df['riesgo_categoria'] == 'ALTO').sum(), "Riesgo Alto", "red"),
        ((df['riesgo_categoria'] == 'MEDIO').sum(), "Riesgo Medio", "orange"),
        ((df['riesgo_categoria'] == 'BAJO').sum(), "Riesgo Bajo", "green")
    ]
    
    for col, (valor, label, color) in zip(cols, metricas):
        with col:
            st.markdown(f"""
            <div class="metric-container border-{color}">
                <div style="font-size: 2rem; font-weight: 700; color: {'#3b82f6' if color=='blue' else '#ef4444' if color=='red' else '#f59e0b' if color=='orange' else '#10b981'}">{valor}</div>
                <div style="font-size: 0.9rem; color: #666;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_dashboard(df):
    """Renderiza todo el dashboard"""
    if len(df) == 0:
        return
    
    render_kpis(df)
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribución", "🚨 Alertas", "📚 Por Programa"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            # Gráfico de riesgo
            riesgo_counts = df['riesgo_categoria'].value_counts()
            colors = {'ALTO': '#ef4444', 'MEDIO': '#f59e0b', 'BAJO': '#10b981'}
            fig = px.pie(values=riesgo_counts.values, names=riesgo_counts.index, 
                        color=riesgo_counts.index, color_discrete_map=colors,
                        title="Distribución de Riesgo")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Histograma de probabilidades
            fig = px.histogram(df, x='probabilidad_desercion', nbins=20,
                             color='riesgo_categoria', color_discrete_map=colors,
                             title="Distribución de Probabilidades")
            fig.add_vline(x=0.7, line_dash="dash", line_color="red")
            fig.add_vline(x=0.4, line_dash="dash", line_color="orange")
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla resumen
        st.dataframe(df[['id', 'programa', 'promedio_ultimo', 'probabilidad_desercion', 
                        'riesgo_categoria', 'recomendacion']].sort_values('probabilidad_desercion', ascending=False),
                    use_container_width=True, height=400)
    
    with tab2:
        alertas = df[df['riesgo_categoria'] == 'ALTO']
        if len(alertas) > 0:
            st.error(f"🚨 {len(alertas)} estudiantes en riesgo ALTO")
            st.dataframe(alertas[['id', 'programa', 'semestre', 'probabilidad_desercion', 'recomendacion']],
                        use_container_width=True)
            
            csv = alertas.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Alertas", csv, "alertas.csv", "text/csv")
        else:
            st.success("No hay alertas de alto riesgo")
    
    with tab3:
        prog = df.groupby('programa').agg({
            'id': 'count',
            'probabilidad_desercion': 'mean',
            'riesgo_categoria': lambda x: (x=='ALTO').sum()
        }).round(2)
        prog.columns = ['Total', 'Riesgo_Prom', 'Alertas']
        st.dataframe(prog.sort_values('Riesgo_Prom', ascending=False), use_container_width=True)

# ============================================================
# MAIN
# ============================================================

def main():
    render_header()
    
    # Cargar datos
    df = render_sidebar()
    
    if len(df) == 0:
        st.info("""
        ### 👋 Bienvenido
        
        **Instrucciones:**
        1. Usa el panel lateral para subir tu CSV de Google Forms
        2. El análisis tomará menos de 2 segundos
        3. Visualiza los resultados en las pestañas
        
        **Formato esperado:** Archivo CSV descargado desde Google Forms con columnas: id, programa, semestre, promedio_ultimo, etc.
        """)
        return
    
    # Mostrar dashboard
    render_dashboard(df)
    
    # Exportar
    st.sidebar.markdown("---")
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("⬇️ Descargar Todo (CSV)", csv, 
                              f"analisis_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

if __name__ == "__main__":
    main()