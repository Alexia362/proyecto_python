import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Portal de Precios - Supermercados Uruguay",
    layout="wide"
)

st.title("Portal de Precios de Supermercados en Uruguay")
st.markdown(
    "Aplicación interactiva para analizar precios relevados en distintas cadenas "
    "de supermercados de Uruguay durante 2025."
)


# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    ruta = "data/processed/p4ds_cadenas_limpio._2025.csv"
    datos = pd.read_csv(ruta)

    datos["Precio"] = pd.to_numeric(datos["Precio"], errors="coerce")
    datos = datos.dropna(subset=["Precio"])

    return datos


datos_cadena = cargar_datos()


# FILTROS LATERALES
st.sidebar.header("Filtros")

supermercados = sorted(datos_cadena["Super"].dropna().unique())
grupos = sorted(datos_cadena["Grupo"].dropna().unique())

super_seleccionados = st.sidebar.multiselect(
    "Seleccionar supermercado",
    options=supermercados,
    default=supermercados
)

grupos_seleccionados = st.sidebar.multiselect(
    "Seleccionar grupo de producto",
    options=grupos,
    default=grupos
)

precio_minimo = float(datos_cadena["Precio"].min())
precio_maximo = float(datos_cadena["Precio"].max())

rango_precio = st.sidebar.slider(
    "Rango de precios",
    min_value=precio_minimo,
    max_value=precio_maximo,
    value=(precio_minimo, precio_maximo)
)

datos_filtrados = datos_cadena[
    (datos_cadena["Super"].isin(super_seleccionados)) &
    (datos_cadena["Grupo"].isin(grupos_seleccionados)) &
    (datos_cadena["Precio"] >= rango_precio[0]) &
    (datos_cadena["Precio"] <= rango_precio[1])
]


# VALIDACIÓN DE DATOS FILTRADOS
if datos_filtrados.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()


# INDICADORES PRINCIPALES
st.subheader("Indicadores principales")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros", f"{datos_filtrados.shape[0]:,}")
col2.metric("Precio promedio", f"${datos_filtrados['Precio'].mean():.2f}")
col3.metric("Precio mediano", f"${datos_filtrados['Precio'].median():.2f}")
col4.metric("Precio máximo", f"${datos_filtrados['Precio'].max():.2f}")


# VISUALIZACIÓN 1: DISTRIBUCIÓN DE PRECIOS
st.subheader("Distribución de precios")

fig, ax = plt.subplots(figsize=(10, 5))

sns.histplot(
    data=datos_filtrados,
    x="Precio",
    bins=40,
    kde=True,
    ax=ax
)

ax.set_title("Distribución de precios")
ax.set_xlabel("Precio")
ax.set_ylabel("Frecuencia")

st.pyplot(fig)


# VISUALIZACIÓN 2: PRECIO PROMEDIO POR SUPERMERCADO
st.subheader("Precio promedio por supermercado")

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    data=datos_filtrados,
    y="Super",
    x="Precio",
    estimator="mean",
    errorbar=None,
    hue="Super",
    palette="Blues_r",
    legend=False,
    ax=ax
)

ax.set_title("Precio promedio por supermercado")
ax.set_xlabel("Precio promedio")
ax.set_ylabel("Supermercado")

st.pyplot(fig)


# VISUALIZACIÓN 3: DISPERSIÓN DE PRECIOS POR SUPERMERCADO
st.subheader("Dispersión de precios por supermercado")

fig, ax = plt.subplots(figsize=(10, 5))

sns.stripplot(
    data=datos_filtrados,
    y="Super",
    x="Precio",
    hue="Super",
    palette="Set2",
    legend=False,
    alpha=0.5,
    ax=ax
)

ax.set_title("Dispersión de precios por supermercado")
ax.set_xlabel("Precio")
ax.set_ylabel("Supermercado")

st.pyplot(fig)


# VISUALIZACIÓN 4: TOP 10 GRUPOS POR PRECIO PROMEDIO
st.subheader("Top 10 grupos con mayor precio promedio")

precio_por_grupo = (
    datos_filtrados
    .groupby("Grupo")["Precio"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(10, 5))

sns.barplot(
    data=precio_por_grupo,
    y="Grupo",
    x="Precio",
    hue="Grupo",
    palette="Oranges_r",
    legend=False,
    ax=ax
)

ax.set_title("Top 10 grupos con mayor precio promedio")
ax.set_xlabel("Precio promedio")
ax.set_ylabel("Grupo de producto")

st.pyplot(fig)


# VISUALIZACIÓN 5: MAPA DE CALOR COMERCIAL
st.subheader("Mapa de calor: precio promedio por supermercado y grupo")

top_grupos = (
    datos_filtrados["Grupo"]
    .value_counts()
    .head(10)
    .index
)

datos_heatmap = datos_filtrados[datos_filtrados["Grupo"].isin(top_grupos)]

matriz_precios = datos_heatmap.pivot_table(
    values="Precio",
    index="Super",
    columns="Grupo",
    aggfunc="mean"
).round(2)

fig, ax = plt.subplots(figsize=(14, 7))

sns.heatmap(
    matriz_precios,
    annot=True,
    fmt=".0f",
    cmap="YlOrRd",
    linewidths=0.5,
    ax=ax
)

ax.set_title("Precio promedio por supermercado y grupo de producto")
ax.set_xlabel("Grupo de producto")
ax.set_ylabel("Supermercado")

plt.xticks(rotation=45, ha="right")
plt.tight_layout()

st.pyplot(fig)


# INSIGHTS AUTOMÁTICOS
st.subheader("Insights automáticos")

matriz_larga = matriz_precios.stack()

if not matriz_larga.empty:
    combinacion_maxima = matriz_larga.idxmax()
    valor_maximo = matriz_larga.max()

    combinacion_minima = matriz_larga.idxmin()
    valor_minimo = matriz_larga.min()

    st.info(
        f"Mayor precio promedio: {combinacion_maxima[0]} - {combinacion_maxima[1]} "
        f"con un promedio de ${valor_maximo:.2f}"
    )

    st.success(
        f"Menor precio promedio: {combinacion_minima[0]} - {combinacion_minima[1]} "
        f"con un promedio de ${valor_minimo:.2f}"
    )


# TABLA DE DATOS
st.subheader("Datos filtrados")

st.dataframe(datos_filtrados)


# DESCARGA DE DATOS
csv = datos_filtrados.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Descargar datos filtrados en CSV",
    data=csv,
    file_name="datos_filtrados_supermercados.csv",
    mime="text/csv"
)