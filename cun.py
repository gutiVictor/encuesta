#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard de Análisis de Deserción Estudiantil - CUN
VERSIÓN CON LOGO INSTITUCIONAL
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import time
import base64
from io import BytesIO

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Análisis de Deserción Estudiantil - CUN",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS con estilos para el logo
st.markdown("""
<style>
    .logo-container {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #f0f9f4 0%, #e6f4ea 100%);
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .main-title { 
        font-size: 2rem; 
        font-weight: 800; 
        color: #1e3a8a; 
        text-align: center;
        margin: 0.5rem 0;
    }
    .subtitle {
        text-align: center;
        color: #2e7d52;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .metric-container {
        background: white; border-radius: 10px; padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-left: 4px solid; margin: 0.5rem 0;
    }
    .border-red { border-left-color: #ef4444; }
    .border-orange { border-left-color: #f59e0b; }
    .border-green { border-left-color: #10b981; }
    .border-blue { border-left-color: #3b82f6; }
    .filter-box {
        background-color: #f0f4f8; padding: 15px; border-radius: 10px; 
        border: 1px solid #d1d5db; margin: 10px 0;
    }
    .filter-active {
        background-color: #dbeafe; border: 1px solid #3b82f6;
    }
    .sidebar-logo {
        text-align: center;
        padding: 10px;
        background: white;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNCIÓN PARA CARGAR LOGO
# ============================================================

def render_header_with_logo():
    """Renderiza el encabezado con logo de CUN"""
    # Crear tres columnas para centrar el contenido
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        # Mostrar logo
        try:
            #insertar logo
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image("./cun-2.png", width=200, use_container_width=False)
        except:
            st.warning("Logo no encontrado")
        
        # Título y subtítulo
        st.markdown('<div class="main-title">🎓 Sistema de Análisis de Deserción Estudiantil</div>', 
                   unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Corporación Unificada Nacional de Educación Superior (CUN)</div>', 
                   unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; color: #6b7280; font-size: 0.9rem; margin-bottom: 2rem;">'
                   'Ingeniería de Sistemas - Trabajo de Grado <br>Lyda Alejandra Barbosa Amado Docente - Ingeniería de Sistemas</div>', 
                   unsafe_allow_html=True)

def render_sidebar_logo():
    """Muestra versión pequeña del logo en sidebar"""
    st.sidebar.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    try:
        st.sidebar.image("/mnt/kimi/upload/cun-1.png", width=120, use_container_width=False)
    except:
        pass
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown("<h3 style='text-align: center; color: #2e7d52; margin-top: 0;'>CUN</h3>", 
                       unsafe_allow_html=True)

# ============================================================
# PROCESAMIENTO DE DATOS (Mantenido igual)
# ============================================================

def limpiar_columnas(df):
    df.columns = [str(col).strip().replace('<br>', '').replace('\n', '') 
                  for col in df.columns]
    return df

def procesar_csv_optimizado(file, placeholder_status):
    t_inicio = time.time()
    
    try:
        df_raw = pd.read_csv(file)
        if 'id' in df_raw.columns:
            df_raw = df_raw[df_raw['id'] != 'id']
    except:
        file.seek(0)
        df_raw = pd.read_csv(file, encoding='latin1')
    
    if len(df_raw) == 0:
        return pd.DataFrame()
    
    df = limpiar_columnas(df_raw)
    
    cols_numericas = ['semestre', 'promedio_acumulado', 'promedio_ultimo', 
                     'materias_perdidas', 'frecuencia_semanal', 'estrato', 
                     'horas_semanales', 'dependientes', 'satisfaccion_programa', 
                     'probabilidad_continuar_percibida']
    
    for col in cols_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    result = pd.DataFrame()
    result['id'] = df['id']
    result['programa'] = df['programa'].astype(str)
    result['semestre'] = pd.to_numeric(df['semestre'], errors='coerce').fillna(1).astype(int)
    result['jornada'] = df.get('Jornada', 'No especificada')
    result['promedio_acumulado'] = pd.to_numeric(df['promedio_acumulado'], errors='coerce')
    result['promedio_ultimo'] = pd.to_numeric(df['promedio_ultimo'], errors='coerce')
    result['materias_perdidas'] = pd.to_numeric(df['materias_perdidas'], errors='coerce').fillna(0)
    
    pct = pd.to_numeric(df['pct_creditos_aprobados'], errors='coerce')
    result['pct_creditos_aprobados'] = np.where(pct > 1, pct/100, pct)
    
    result['acceso_plataforma'] = (df.get('acceso_plataforma_mes', '')
                                   .astype(str).str.lower().str.strip()
                                   .isin(['si', 'sí', 'yes', '1'])).astype(int)
    result['frecuencia_semanal'] = pd.to_numeric(df['frecuencia_semanal'], errors='coerce').fillna(0)
    result['estrato'] = pd.to_numeric(df['estrato'], errors='coerce').fillna(2)
    result['estrato_bajo'] = (result['estrato'] <= 2).astype(int)
    result['trabaja'] = (df.get('trabaja', '').astype(str).str.lower().str.strip()
                        .isin(['si', 'sí', 'yes', '1'])).astype(int)
    result['horas_semanales'] = pd.to_numeric(df['horas_semanales'], errors='coerce').fillna(0)
    result['dependientes'] = pd.to_numeric(df['dependientes'], errors='coerce').fillna(0)
    
    piensa_desertar = df.get('piensa_desertar', '').astype(str).str.lower()
    result['piensa_desertar_frecuente'] = piensa_desertar.str.contains('frecuente').astype(int)
    result['piensa_desertar_alguna_vez'] = piensa_desertar.str.contains('frecuente|alguna').astype(int)
    result['satisfaccion_programa'] = pd.to_numeric(df['satisfaccion_programa'], errors='coerce').fillna(5)
    result['probabilidad_continuar_percibida'] = pd.to_numeric(df['probabilidad_continuar_percibida'], errors='coerce').fillna(5)
    result['evento_estresante'] = df.get('evento_estresante', 'Ninguno').fillna('Ninguno')
    
    dificultad = df.get('dificultad_pago', '').astype(str).str.lower()
    result['dificultad_pago'] = np.select(
        [dificultad.str.contains('grave'), dificultad.str.contains('algun')],
        [1.0, 0.5], default=0.0
    )
    
    dif_perc = df.get('dificultad_percibida', '').astype(str).str.lower()
    score_dificultad = np.select(
        [dif_perc.str.contains('much'), dif_perc.str.contains('algo'), dif_perc.str.contains('poc')],
        [0.9, 0.5, 0.1], default=0.5
    )
    
    prom_norm = (4 - result['promedio_ultimo'].fillna(3)) / 3
    mat_norm = (result['materias_perdidas'] / 5).clip(0, 1)
    cred_factor = 1 - result['pct_creditos_aprobados'].fillna(1)
    
    result['indice_riesgo_academico'] = (prom_norm * 0.35 + mat_norm * 0.25 + 
                                         score_dificultad * 0.25 + cred_factor * 0.15).clip(0, 1)
    
    frec_norm = (result['frecuencia_semanal'] / 7).clip(0, 1)
    part = df.get('participacion_sincronica', '').astype(str).str.lower()
    score_part = np.select([part.str.contains('siempre'), part.str.contains('regular'), 
                           part.str.contains('aveces|1-2')], [1.0, 0.7, 0.4], default=0.0)
    consulta = df.get('consulta_profesores', '').astype(str).str.lower()
    score_consulta = np.select([consulta.str.contains('siempre'), consulta.str.contains('regular')], 
                               [1.0, 0.7], default=0.4)
    claridad = df.get('claridad_proposito', '').astype(str).str.lower()
    score_claridad = np.select([claridad.str.contains('muy'), claridad.str.contains('algo')], 
                               [1.0, 0.5], default=0.2)
    
    result['indice_engagement'] = (result['acceso_plataforma'] * 0.25 + frec_norm * 0.25 +
                                   score_part * 0.20 + score_consulta * 0.20 + score_claridad * 0.10).clip(0, 1)
    
    bajo_engagement = 1 - result['indice_engagement']
    piensa_score = result['piensa_desertar_frecuente'] * 0.8 + result['piensa_desertar_alguna_vez'] * 0.4
    dif_econ = result['dificultad_pago'] * 0.8 + (result['trabaja'] * (result['horas_semanales'] > 30).astype(int) * 0.3)
    evento_estres = (result['evento_estresante'] != 'Ninguno').astype(int) * 0.5
    baja_satisf = (10 - result['satisfaccion_programa']) / 10
    
    result['probabilidad_desercion'] = (
        result['indice_riesgo_academico'] * 0.30 + bajo_engagement * 0.20 + 
        piensa_score * 0.25 + dif_econ * 0.15 + evento_estres * 0.05 + baja_satisf * 0.05
    ).clip(0, 1)
    
    mask_frec = result['piensa_desertar_frecuente'] == 1
    result.loc[mask_frec, 'probabilidad_desercion'] = result.loc[mask_frec, 'probabilidad_desercion'].clip(lower=0.7)
    
    result['riesgo_categoria'] = pd.cut(result['probabilidad_desercion'], 
                                        bins=[-0.1, 0.4, 0.7, 1.0], 
                                        labels=['BAJO', 'MEDIO', 'ALTO']).astype(str)
    
    result['recomendacion'] = "Monitoreo estándar."
    mask_alto_int = (result['riesgo_categoria'] == 'ALTO') & (result['piensa_desertar_frecuente'] == 1)
    mask_alto_acad = (result['riesgo_categoria'] == 'ALTO') & (result['indice_riesgo_academico'] > 0.6) & ~mask_alto_int
    mask_alto_econ = (result['riesgo_categoria'] == 'ALTO') & (result['dificultad_pago'] > 0.5) & ~mask_alto_int & ~mask_alto_acad
    mask_med_eng = (result['riesgo_categoria'] == 'MEDIO') & (result['indice_engagement'] < 0.4)
    mask_med_prom = (result['riesgo_categoria'] == 'MEDIO') & (result['promedio_ultimo'] < 3.0) & ~mask_med_eng
    
    result.loc[mask_alto_int, 'recomendacion'] = "Intervención psicológica inmediata."
    result.loc[mask_alto_acad, 'recomendacion'] = "Tutorías académicas urgentes."
    result.loc[mask_alto_econ, 'recomendacion'] = "Apoyo financiero/condonaciones."
    result.loc[mask_med_eng, 'recomendacion'] = "Acompañamiento virtual."
    result.loc[mask_med_prom, 'recomendacion'] = "Tutorías preventivas."
    
    result['fecha_prediccion'] = datetime.now()
    result['modelo_version'] = 'CUN_v1.0'
    result['target_desercion'] = ((result['probabilidad_desercion'] > 0.6) | 
                                  (result['piensa_desertar_frecuente'] == 1)).astype(int)
    
    return result

# ============================================================
# FILTROS AVANZADOS
# ============================================================

def render_filtros_avanzados(df):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtros Avanzados")
    
    if len(df) == 0:
        return df
    
    filtros_activos = []
    
    programas = sorted(df['programa'].unique().tolist())
    prog_seleccionados = st.sidebar.multiselect("📚 Programas", programas, default=[], 
                                                help="Vacío = todos")
    if prog_seleccionados:
        filtros_activos.append(f"Programas: {', '.join(prog_seleccionados)}")
    
    semestres = sorted(df['semestre'].unique().tolist())
    sem_seleccionados = st.sidebar.multiselect("📅 Semestres", semestres, default=[])
    if sem_seleccionados:
        filtros_activos.append(f"Semestres: {', '.join(map(str, sem_seleccionados))}")
    
    riesgos = ['ALTO', 'MEDIO', 'BAJO']
    riesgo_seleccionado = st.sidebar.multiselect("⚠️ Nivel de Riesgo", riesgos, default=[])
    if riesgo_seleccionado:
        filtros_activos.append(f"Riesgo: {', '.join(riesgo_seleccionado)}")
    
    jornadas = sorted(df['jornada'].unique().tolist())
    jornada_sel = st.sidebar.multiselect("🌅 Jornada", jornadas, default=[])
    if jornada_sel:
        filtros_activos.append(f"Jornada: {', '.join(jornada_sel)}")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        prom_min = st.number_input("Promedio Mín", 0.0, 5.0, 0.0, 0.5)
    with col2:
        prom_max = st.number_input("Promedio Máx", 0.0, 5.0, 5.0, 0.5)
    
    if prom_min > 0 or prom_max < 5:
        filtros_activos.append(f"Promedio: {prom_min}-{prom_max}")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        solo_desercion_frecuente = st.checkbox("🚨 Piensa desertar")
    with col2:
        solo_sin_acceso = st.checkbox("💻 Sin acceso")
    
    if solo_desercion_frecuente:
        filtros_activos.append("Solo intención frecuente")
    if solo_sin_acceso:
        filtros_activos.append("Solo sin acceso")
    
    df_filtrado = df.copy()
    
    if prog_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['programa'].isin(prog_seleccionados)]
    if sem_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['semestre'].isin(sem_seleccionados)]
    if riesgo_seleccionado:
        df_filtrado = df_filtrado[df_filtrado['riesgo_categoria'].isin(riesgo_seleccionado)]
    if jornada_sel:
        df_filtrado = df_filtrado[df_filtrado['jornada'].isin(jornada_sel)]
    
    df_filtrado = df_filtrado[(df_filtrado['promedio_ultimo'] >= prom_min) & 
                              (df_filtrado['promedio_ultimo'] <= prom_max)]
    
    if solo_desercion_frecuente:
        df_filtrado = df_filtrado[df_filtrado['piensa_desertar_frecuente'] == 1]
    if solo_sin_acceso:
        df_filtrado = df_filtrado[df_filtrado['acceso_plataforma'] == 0]
    
    if filtros_activos:
        st.sidebar.markdown("#### 🎯 Filtros Activos:")
        for filtro in filtros_activos:
            st.sidebar.caption(f"• {filtro}")
        st.sidebar.markdown(f"""
        <div class="filter-box filter-active">
            <strong>{len(df_filtrado)} de {len(df)} estudiantes</strong><br>
            <span style="font-size: 0.8rem;">({len(df_filtrado)/len(df)*100:.1f}%)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div class="filter-box">
            <strong>Sin filtros</strong><br>
            <span style="font-size: 0.8rem;">{len(df)} estudiantes</span>
        </div>
        """, unsafe_allow_html=True)
    
    if filtros_activos and st.sidebar.button("🧹 Limpiar Filtros", use_container_width=True):
        st.rerun()
    
    return df_filtrado

# ============================================================
# EXPORTACIÓN EXCEL
# ============================================================

def generar_excel_completo(df_original, df_filtrado):
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # 1. Resumen
        resumen_data = {
            'Métrica': [
                'Total Estudiantes',
                'Riesgo Alto', 'Riesgo Medio', 'Riesgo Bajo',
                'Promedio Riesgo Institucional',
                'Sin Acceso Plataforma',
                'Intención Frecuente Desertar',
                'Promedio Académico',
                'Fecha Análisis'
            ],
            'Valor': [
                len(df_original),
                (df_original['riesgo_categoria'] == 'ALTO').sum(),
                (df_original['riesgo_categoria'] == 'MEDIO').sum(),
                (df_original['riesgo_categoria'] == 'BAJO').sum(),
                f"{df_original['probabilidad_desercion'].mean():.2%}",
                (df_original['acceso_plataforma'] == 0).sum(),
                (df_original['piensa_desertar_frecuente'] == 1).sum(),
                f"{df_original['promedio_ultimo'].mean():.2f}",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ]
        }
        pd.DataFrame(resumen_data).to_excel(writer, sheet_name='1. Resumen', index=False)
        
        # 2. Alertas
        df_alertas = df_original[df_original['riesgo_categoria'] == 'ALTO'].sort_values(
            'probabilidad_desercion', ascending=False
        )
        if len(df_alertas) > 0:
            cols = ['id', 'programa', 'semestre', 'jornada', 'promedio_ultimo', 
                   'probabilidad_desercion', 'indice_riesgo_academico', 'indice_engagement',
                   'piensa_desertar_frecuente', 'recomendacion']
            df_alertas[cols].to_excel(writer, sheet_name='2. Alertas Alto Riesgo', index=False)
        else:
            pd.DataFrame({'Mensaje': ['No hay alertas']}).to_excel(
                writer, sheet_name='2. Alertas Alto Riesgo', index=False
            )
        
        # 3. Detalle
        df_original.to_excel(writer, sheet_name='3. Detalle Completo', index=False)
        
        # 4. Por Programa
        analisis_prog = df_original.groupby('programa').agg({
            'id': 'count',
            'probabilidad_desercion': ['mean', 'std'],
            'riesgo_categoria': lambda x: (x == 'ALTO').sum(),
            'promedio_ultimo': 'mean',
            'indice_engagement': 'mean'
        }).round(3)
        analisis_prog.columns = ['Total', 'Riesgo_Prom', 'Riesgo_Std', 'Alertas', 'Promedio', 'Engagement']
        analisis_prog.reset_index().sort_values('Riesgo_Prom', ascending=False).to_excel(
            writer, sheet_name='4. Por Programa', index=False
        )
        
        # 5. Por Semestre
        analisis_sem = df_original.groupby('semestre').agg({
            'id': 'count',
            'probabilidad_desercion': 'mean',
            'riesgo_categoria': lambda x: (x == 'ALTO').sum()
        }).round(3)
        analisis_sem.columns = ['Total', 'Riesgo_Prom', 'Alertas']
        analisis_sem.reset_index().to_excel(writer, sheet_name='5. Por Semestre', index=False)
        
        # 6. Filtrados si aplica
        if len(df_filtrado) != len(df_original):
            df_filtrado.to_excel(writer, sheet_name='6. Datos Filtrados', index=False)
    
    output.seek(0)
    return output

# ============================================================
# VISUALIZACIONES
# ============================================================

def render_kpis(df, df_filtrado):
    col1, col2, col3, col4 = st.columns(4)
    metricas = [
        (len(df_filtrado), "Estudiantes (Filtrados)" if len(df_filtrado) != len(df) else "Total", "blue"),
        ((df_filtrado['riesgo_categoria'] == 'ALTO').sum(), "🚨 Alto Riesgo", "red"),
        ((df_filtrado['riesgo_categoria'] == 'MEDIO').sum(), "⚠️ Medio", "orange"),
        ((df_filtrado['riesgo_categoria'] == 'BAJO').sum(), "✅ Bajo", "green")
    ]
    
    for col, (valor, label, color) in zip([col1, col2, col3, col4], metricas):
        with col:
            color_hex = '#3b82f6' if color=='blue' else '#ef4444' if color=='red' else '#f59e0b' if color=='orange' else '#10b981'
            st.markdown(f"""
            <div class="metric-container border-{color}">
                <div style="font-size: 2rem; font-weight: 700; color: {color_hex}">{valor}</div>
                <div style="font-size: 0.9rem; color: #666;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_dashboard(df, df_filtrado):
    render_kpis(df, df_filtrado)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        excel_file = generar_excel_completo(df, df_filtrado)
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_file,
            file_name=f"Analisis_CUN_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col1:
        if len(df_filtrado) != len(df):
            st.info(f"🔍 Vista filtrada: {len(df_filtrado)} de {len(df)} ({len(df_filtrado)/len(df)*100:.1f}%)")
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribución", "🚨 Alertas", "📚 Por Programa"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            riesgo_counts = df_filtrado['riesgo_categoria'].value_counts()
            colors = {'ALTO': '#ef4444', 'MEDIO': '#f59e0b', 'BAJO': '#10b981'}
            fig = px.pie(values=riesgo_counts.values, names=riesgo_counts.index, 
                        color=riesgo_counts.index, color_discrete_map=colors,
                        title=f"Distribución (n={len(df_filtrado)})")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(df_filtrado, x='probabilidad_desercion', nbins=20,
                             color='riesgo_categoria', color_discrete_map=colors,
                             title="Histograma de Probabilidades")
            fig.add_vline(x=0.7, line_dash="dash", line_color="red")
            fig.add_vline(x=0.4, line_dash="dash", line_color="orange")
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_filtrado[['id', 'programa', 'semestre', 'promedio_ultimo', 
                                'probabilidad_desercion', 'riesgo_categoria', 'recomendacion']]
                    .sort_values('probabilidad_desercion', ascending=False),
                    use_container_width=True, height=300)
    
    with tab2:
        alertas = df_filtrado[df_filtrado['riesgo_categoria'] == 'ALTO']
        if len(alertas) > 0:
            st.error(f"🚨 {len(alertas)} estudiantes en riesgo ALTO")
            st.dataframe(alertas[['id', 'programa', 'semestre', 'promedio_ultimo', 
                                'probabilidad_desercion', 'recomendacion']].sort_values('probabilidad_desercion', ascending=False),
                        use_container_width=True)
        else:
            st.success("No hay alertas de alto riesgo")
    
    with tab3:
        prog = df_filtrado.groupby('programa').agg({
            'id': 'count',
            'probabilidad_desercion': 'mean',
            'riesgo_categoria': lambda x: (x=='ALTO').sum()
        }).round(3)
        prog.columns = ['Total', 'Riesgo_Prom', 'Alertas']
        st.dataframe(prog.sort_values('Riesgo_Prom', ascending=False), use_container_width=True)

# ============================================================
# MAIN
# ============================================================

def main():
    # Header con logo
    render_header_with_logo()
    
    # Sidebar con logo pequeño
    render_sidebar_logo()
    
    # Resto del sidebar
    st.sidebar.markdown("## 📁 Carga de Datos")
    uploaded_file = st.sidebar.file_uploader("Seleccionar CSV de Google Forms", type=['csv'])
    
    df = st.session_state.get('datos_procesados', pd.DataFrame())
    
    if uploaded_file is not None and 'last_file' not in st.session_state:
        status = st.sidebar.empty()
        df = procesar_csv_optimizado(uploaded_file, status)
        if not df.empty:
            st.session_state['datos_procesados'] = df
            st.session_state['last_file'] = uploaded_file.name
            st.rerun()
    
    if len(df) == 0:
        st.info("👈 Carga un archivo CSV para comenzar el análisis")
        st.markdown("""
        ### 📝 Instrucciones:
        1. Descarga el CSV desde Google Forms (Respuestas → Descargar)
        2. Súbelo usando el panel lateral
        3. Aplica filtros avanzados según necesites
        4. Exporta los resultados a Excel
        
        **Desarrollado para:** Especialización en Ingeniería de Sistemas - CUN  
        **Docente:** Lida Alejandra Barbosa Amado
        """)
        return
    
    # Filtros y dashboard
    df_filtrado = render_filtros_avanzados(df)
    render_dashboard(df, df_filtrado)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #2e7d52; padding: 1rem; font-size: 0.9rem;">
        <strong>Corporación Unificada Nacional de Educación Superior</strong><br>
        <strong>TRABAJO DE GRADO 3 - MODELOS DE INNOVACION INGENIERIA DE SISTEMAS/51160/BLOQUE UNICO/26P01</strong><br>
        </strong>Victor Raul Gutierrez Sanabria<br>
         </strong>Ivonne Niño Valderrama<br>        
        Ingeniería de Sistemas - 2026
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()