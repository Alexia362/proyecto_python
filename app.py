# FASE 2: DESARROLLO DE LA APLICACIÓN INTERACTIVA (STREAMLIT)

# Importo librerias
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# Configuracion de la web (Título de la pestaña y vista ancha)
st.set_page_config(
    page_title="Portal de Precios - Cadenas de Supermercados",
    layout="wide"
)

# Carga del dataset limpio usando ruta relativa para que funcione en internet
ruta_limpia = "data/processed/p4ds_cadenas_limpio_2025.csv"
datos_cadena = pd.read_csv(ruta_limpia)

# Chequeo columna precios sea numerica flotante
datos_cadena['Precio'] = pd.to_numeric(datos_cadena['Precio'], errors='coerce')
datos_cadena = datos_cadena.dropna(subset=['Precio'])

# SIDEBAR DE CONTROL (ST.SIDEBAR) Y FILTROS INTERACTIVOS

# Titulo y descripcion posicion barra lateral para el usuario
st.sidebar.markdown("# Panel de Control")
st.sidebar.markdown("Utilizá el control deslizante para filtrar los registros por el rango de precios deseado.")

# Configuración del Slider dinámico basado en el Mínimo y Máximo real del dataset
precio_minimo = float(datos_cadena['Precio'].min())
precio_maximo = float(datos_cadena['Precio'].max())

rango_seleccionado = st.sidebar.slider(
    label="Seleccioná el rango de Precios ($):",
    min_value=precio_minimo,
    max_value=precio_maximo,
    value=(precio_minimo, precio_maximo),
)

# Le pongo el filtro al DataFrame original
# Creo máscara para quedarme solo con los datos dentro del rango del slider
datos_filtrados = datos_cadena[
    (datos_cadena['Precio'] >= rango_seleccionado[0]) &
    (datos_cadena['Precio'] <= rango_seleccionado[1])
]

# PASO 5: ANÁLISIS DE VARIABLES (UNIVARIANTE CATEGÓRICAS)

# Título de la sección en la interfaz principal
st.header("Análisis de Variables")
st.subheader(" Análisis de Variables Univariante Categóricas")

st.markdown("""
Una **variable categórica** es un tipo de variable que puede tomar uno de un número limitado de categorías o grupos. 
Para representar este tipo de variables utilizaremos gráficos de barras/frecuencias. 
En nuestro caso, las variables categóricas principales que analizaremos son `Super` y `Grupo`, las cuales se actualizan automáticamente según el rango de precios seleccionado.
""")

# Creo dos columnas en la pantalla de la web para poner los gráficos al lado
col_cat1, col_cat2 = st.columns(2)

with col_cat1:
    st.markdown("#### Distribución por Cadena de Supermercado (`Super`)")

    # Creacion del grafico Matplotlib/Seaborn alimentado por los DATOS FILTRADOS
    fig_super, ax_super = plt.subplots(figsize=(6, 4))
    sns.countplot(
        data=datos_filtrados,
        y="Super",
        order=datos_filtrados['Super'].value_counts().index,
        palette="Blues_r",
        ax=ax_super
    )
    ax_super.set_xlabel("Cantidad de Registros")
    ax_super.set_ylabel("Establecimiento")

    # Usamos Streamlit para que renderice el gráfico en la web
    st.pyplot(fig_super)

with col_cat2:
    st.markdown("#### Top 10 Categorías de Productos (`Grupo`)")

    # Buscamos el top 10 de grupos según el filtro actual
    top_grupos = datos_filtrados['Grupo'].value_counts().head(10).index
    datos_top_grupos = datos_filtrados[datos_filtrados['Grupo'].isin(top_grupos)]

    fig_grupo, ax_grupo = plt.subplots(figsize=(6, 4))
    sns.countplot(
        data=datos_top_grupos,
        y="Grupo",
        order=top_grupos,
        palette="Greens_r",
        ax=ax_grupo
    )
    ax_grupo.set_xlabel("Cantidad de Registros")
    ax_grupo.set_ylabel("Grupo")

    st.pyplot(fig_grupo)

st.markdown("---")

# PASO 5 (CONTINUACIÓN): ANÁLISIS DE VARIABLES UNIVARIANTE NUMÉRICAS

st.subheader("Análisis de Variables Univariante Numéricas")

st.markdown("""
Una **variable numérica** es un tipo de variable que puede tomar valores numéricos (enteros, fracciones, decimales, negativos, etc.) en un rango infinito. 
En nuestro dataset, la variable numérica principal es `Precio` (nuestro target). 
La representaremos utilizando un histograma y un diagrama de caja (boxplot) expuestos juntos para analizar su distribución y detectar valores atípicos.
""")

# --- CÁLCULO DEL RESUMEN ESTADÍSTICO INTERACTIVO ---
if not datos_filtrados.empty:
    media = datos_filtrados['Precio'].mean()
    mediana = datos_filtrados['Precio'].median()
    desviacion_estandar = datos_filtrados['Precio'].std()
    min_f = datos_filtrados['Precio'].min()
    max_f = datos_filtrados['Precio'].max()
    rango_f = max_f - min_f

    # Cuartiles
    q1 = datos_filtrados['Precio'].quantile(0.25)
    q3 = datos_filtrados['Precio'].quantile(0.75)

    # Muestro el resumen descriptivo en tarjetas visuales
    st.markdown("##### Resumen Descriptivo del Precio (Datos Filtrados)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Media (Promedio)", value=f"${media:.2f}")
        st.metric(label="Mediana (Q2)", value=f"${mediana:.2f}")
    with col2:
        st.metric(label="Desviación Estándar", value=f"${desviacion_estandar:.2f}")
        st.metric(label="Rango (Máx - Mín)", value=f"${rango_f:.2f}")
    with col3:
        st.metric(label="Mínimo Seleccionado", value=f"${min_f:.2f}")
        st.metric(label="Máximo Seleccionado", value=f"${max_f:.2f}")
    with col4:
        st.metric(label="Primer Cuartil (Q1)", value=f"${q1:.2f}")
        st.metric(label="Tercer Cuartil (Q3)", value=f"${q3:.2f}")
else:
    st.warning("No hay registros en el rango seleccionado.")

st.markdown("---")

# --- VISUALIZACIÓN GRÁFICA COMBINADA (Histograma + Boxplot) ---
st.markdown("##### Distribución y Caja del Target (`Precio`)")

# Creo estructura de dos filas de gráficos compartiendo el mismo eje X (igual que en clase)
fig_num, axis_num = plt.subplots(2, 1, figsize=(8, 5), gridspec_kw={'height_ratios': [4, 1]}, sharex=True)

# Histograma dinámico en la parte superior
sns.histplot(ax=axis_num[0], data=datos_filtrados, x="Precio", bins=30, kde=True, color="purple")
axis_num[0].set_title("Distribución Estadística del Precio")
axis_num[0].set_ylabel("Frecuencia")

# Diagrama de caja (Boxplot) en la parte inferior para visualizar y detectar outliers
sns.boxplot(ax=axis_num[1], data=datos_filtrados, x="Precio", color="orchid")
axis_num[1].set_xlabel("Precio ($)")

plt.tight_layout()
st.pyplot(fig_num)

st.markdown("---")

# ANÁLISIS MULTIVARIANTE: GRÁFICO DE DISPERSIÓN

st.subheader("Análisis Multivariante: Relación entre Variables")

st.markdown("""
Para analizar la relación entre dos características del dataset, realizaremos un **Gráfico de Dispersión**. 
En este caso, cruzamos nuestra variable objetivo `Precio` contra las cadenas de supermercados (`Super`). 
Este gráfico nos permite evaluar visualmente la dispersión y los rangos de precios competitivos que maneja cada establecimiento en tiempo real.
""")

# Creo Matplotlib para la dispersión por categorías
fig_disp, ax_disp = plt.subplots(figsize=(10, 5))

# Uso stripplot que es el gráfico de dispersión ideal cuando cruzás número vs texto
sns.stripplot(
    data=datos_filtrados,
    x="Precio",
    y="Super",
    palette="Set2",
    alpha=0.5,
    size=5,
    ax=ax_disp
)

# Configuracion de títulos y etiquetas informativas como pide el profe
ax_disp.set_title("Dispersión de Precios por Cadena de Supermercado (Datos Filtrados)")
ax_disp.set_xlabel("Precio del Producto ($)")
ax_disp.set_ylabel("Cadena de Supermercado / Establecimiento")

# Renderizamos el gráfico en la aplicación web
st.pyplot(fig_disp)

st.markdown("---")

# PASO 6: RELACIÓN ENTRE VARIABLES (MATRIZ DE CORRELACIÓN COMERCIAL)


st.header("Relación entre Variables")
st.subheader("Matriz de Precios Promedio por Cadena y Categoría")

st.markdown("""
La matriz de correlación numérica de Pearson. Adaptada a el dataset comercial (donde contamos con una única variable numérica objetivo: `Precio`), 
construimos una **matriz de relación cruzada**. 

Este mapa de calor (*heatmap*) representa el **precio promedio** para cada combinación de Cadena de Supermercado (`Super`) 
y Categoría (`Grupo`) en base a los datos filtrados, permitiendo identificar los posicionamientos de precios en el mercado.
""")

# Verificamos que tengamos datos suficientes para pivotar la matriz
if not datos_filtrados.empty:

    top_grupos_6 = datos_filtrados['Grupo'].value_counts().head(10).index
    df_pivot = datos_filtrados[datos_filtrados['Grupo'].isin(top_grupos_6)]

    matriz_comercial = df_pivot.pivot_table(
        values='Precio',
        index='Super',
        columns='Grupo',
        aggfunc='mean'
    )

    fig_heat, ax_heat = plt.subplots(figsize=(12, 6))

    sns.heatmap(
        matriz_comercial,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        ax=ax_heat
    )

    ax_heat.set_title("Mapa de Calor: Precios Promedio ($) por Establecimiento y Categoría")
    ax_heat.set_xlabel("Grupo de Producto")
    ax_heat.set_ylabel("Cadena de Supermercado")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    st.pyplot(fig_heat)

    # INSIGHTS AUTOMÁTICOS
    st.markdown("##### Conclusiones Automáticas de la Matriz:")

    promedio_por_super = df_pivot.groupby('Super')['Precio'].mean()

    super_mas_caro = promedio_por_super.idxmax()
    super_mas_barato = promedio_por_super.idxmin()

    val_max = promedio_por_super.max()
    val_min = promedio_por_super.min()

    categoria_mas_cara = df_pivot.groupby('Grupo')['Precio'].mean().idxmax()

    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        st.info(
            f"**Posicionamiento de Cadenas:**\n\n"
            f"• El establecimiento con el promedio más alto es **{super_mas_caro}** (${val_max:.2f}).\n\n"
            f"• El establecimiento más accesible es **{super_mas_barato}** (${val_min:.2f})."
        )

    with col_ins2:
        st.success(
            f"**Comportamiento de Categorías:**\n\n"
            f"• La categoría más cara es **{categoria_mas_cara}**."
        )

else:
    st.warning("No hay datos disponibles para generar la matriz con el filtro seleccionado.")

# PASO 7: INSPECCIÓN Y EXPORTACIÓN DE LOS DATOS FILTRADOS

st.header("Inspección de Registros Filtrados")
st.markdown("""
Para finalizar el análisis exploratorio interactivo, se presenta la tabla con los registros detallados 
que cumplen con los criterios del filtro de precios. Podés ordenar las columnas o explorar las filas de forma manual.
""")

# chqueo que hay datos para mostrar la tabla interactiva
if not datos_filtrados.empty:
    # Se muestran las primeras 100 filas del dataframe filtrado en un componente nativo y estético
    st.dataframe(datos_filtrados.head(100), use_container_width=True)

    # Extra: Permitir que el usuario descargue su filtro actual en un nuevo CSV directo desde la web
    csv_descarga = datos_filtrados.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar porción filtrada como CSV",
        data=csv_descarga,
        file_name="consulta_cadenas_filtrado.csv",
        mime="text/csv",
    )
else:
    st.info("No hay registros para mostrar en la tabla.")

st.markdown("---")