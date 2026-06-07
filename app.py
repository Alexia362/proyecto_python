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
    "El objetivo de esta aplicación es explorar y comparar precios relevados "
    "en distintas cadenas de supermercados de Uruguay durante 2025. "
    "La app permite filtrar por supermercado, grupo de producto, rango de precios "
    "y productos básicos seleccionados para ver diferencias comerciales de forma más clara."
)


# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    ruta = "data/processed/p4ds_cadenas_limpio._2025.csv"
    datos = pd.read_csv(ruta)

    datos["Precio"] = pd.to_numeric(datos["Precio"], errors="coerce")
    datos = datos.dropna(subset=["Precio"])

    datos["Grupo"] = datos["Grupo"].astype(str).str.strip().str.title()
    datos["Super"] = datos["Super"].astype(str).str.strip().str.title()
    datos["Producto"] = datos["Producto"].astype(str).str.strip()

    return datos


datos_cadena = cargar_datos()


# CLASIFICACIÓN DE PRODUCTOS BÁSICOS
def es_producto_basico(nombre_producto):
    producto = str(nombre_producto).lower()

    palabras_clave = [
        "arroz",
        "aceite",
        "azúcar",
        "azucar",
        "harina",
        "fideos",
        "pan",
        "leche",
        "huevos",
        "pollo",
        "carne",
        "pescado",
        "agua",
        "yerba",
        "manteca",
        "margarina",
        "papa",
        "boniato",
        "cebolla",
        "tomate",
        "zanahoria",
        "banana",
        "manzana",
        "naranja",
        "lechuga"
    ]

    return any(palabra in producto for palabra in palabras_clave)


if "Producto_basico" not in datos_cadena.columns:
    datos_cadena["Producto_basico"] = datos_cadena["Producto"].apply(es_producto_basico)
else:
    datos_cadena["Producto_basico"] = datos_cadena["Producto_basico"].astype(str).str.lower()
    datos_cadena["Producto_basico"] = datos_cadena["Producto_basico"].isin(["true", "1", "sí", "si"])


# FILTROS LATERALES
st.sidebar.header("Filtros del análisis")

supermercados = sorted(datos_cadena["Super"].dropna().unique())
grupos = sorted(datos_cadena["Grupo"].dropna().unique())

super_seleccionados = st.sidebar.multiselect(
    "Supermercados",
    options=supermercados,
    default=supermercados
)

grupos_seleccionados = st.sidebar.multiselect(
    "Grupos de productos",
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

busqueda_producto = st.sidebar.text_input(
    "Buscar producto",
    placeholder="Ejemplo: arroz, leche, aceite"
)

metrica_seleccionada = st.sidebar.radio(
    "Métrica para comparar precios",
    options=["Media", "Mediana"]
)

top_n = st.sidebar.slider(
    "Cantidad de grupos a mostrar",
    min_value=5,
    max_value=20,
    value=10
)

mostrar_p95 = st.sidebar.checkbox(
    "Limitar gráficos al percentil 95",
    value=True
)

solo_basicos = st.sidebar.checkbox(
    "Mostrar solo productos básicos seleccionados",
    value=False
)


# APLICACIÓN DE FILTROS
datos_filtrados = datos_cadena[
    (datos_cadena["Super"].isin(super_seleccionados)) &
    (datos_cadena["Grupo"].isin(grupos_seleccionados)) &
    (datos_cadena["Precio"] >= rango_precio[0]) &
    (datos_cadena["Precio"] <= rango_precio[1])
]

if busqueda_producto.strip() != "":
    datos_filtrados = datos_filtrados[
        datos_filtrados["Producto"]
        .astype(str)
        .str.contains(busqueda_producto, case=False, na=False)
    ]

if solo_basicos:
    datos_filtrados = datos_filtrados[datos_filtrados["Producto_basico"]]


# VALIDACIÓN DE DATOS FILTRADOS
if datos_filtrados.empty:
    st.warning("No hay datos disponibles con los filtros seleccionados.")
    st.stop()


# INDICADORES PRINCIPALES
st.subheader("Indicadores principales")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Registros", f"{datos_filtrados.shape[0]:,}")
col2.metric("Supermercados", datos_filtrados["Super"].nunique())
col3.metric("Grupos", datos_filtrados["Grupo"].nunique())
col4.metric("Precio promedio", f"${datos_filtrados['Precio'].mean():.2f}")
col5.metric("Precio mediano", f"${datos_filtrados['Precio'].median():.2f}")
col6.metric("Productos básicos", f"{datos_filtrados['Producto_basico'].sum():,}")


# PESTAÑAS PRINCIPALES
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Resumen general",
        "Comparaciones",
        "Mapa comercial",
        "Productos básicos",
        "Datos"
    ]
)


# TAB 1: RESUMEN GENERAL
with tab1:
    st.subheader("Distribución de precios")

    if mostrar_p95:
        limite_visual = datos_filtrados["Precio"].quantile(0.95)
        datos_histograma = datos_filtrados[datos_filtrados["Precio"] <= limite_visual]
        st.caption(
            f"El histograma muestra precios hasta el percentil 95: ${limite_visual:.2f}. "
            "Esto es solo para que el gráfico se vea mejor; la base completa no se modifica."
        )
    else:
        datos_histograma = datos_filtrados

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.histplot(
        data=datos_histograma,
        x="Precio",
        bins=40,
        kde=True,
        ax=ax
    )

    ax.set_title("Distribución de precios")
    ax.set_xlabel("Precio")
    ax.set_ylabel("Frecuencia")

    st.pyplot(fig)

    st.subheader("Diagrama de caja de precios")

    fig, ax = plt.subplots(figsize=(10, 4))

    sns.boxplot(
        data=datos_filtrados,
        x="Precio",
        ax=ax
    )

    ax.set_title("Diagrama de caja de precios")
    ax.set_xlabel("Precio")

    st.pyplot(fig)

    if mostrar_p95:
        st.subheader("Diagrama de caja hasta el percentil 95")

        fig, ax = plt.subplots(figsize=(10, 4))

        sns.boxplot(
            data=datos_histograma,
            x="Precio",
            ax=ax
        )

        ax.set_title("Diagrama de caja de precios hasta el percentil 95")
        ax.set_xlabel("Precio")

        st.pyplot(fig)

    st.info(
        "Estos gráficos sirven para ver cómo se distribuyen los precios y detectar valores altos. "
        "El gráfico limitado al percentil 95 no borra datos, solo ayuda a ver mejor la parte donde "
        "se concentra la mayoría de los precios."
    )

    st.subheader("Resumen estadístico")

    resumen_precio = datos_filtrados["Precio"].describe().round(2)
    st.dataframe(resumen_precio)

    with st.expander("Ver registros con precios más altos"):
        productos_mas_caros = (
            datos_filtrados
            .sort_values("Precio", ascending=False)
            [["Periodo", "Super", "Grupo", "Producto", "Precio"]]
            .head(20)
        )

        st.dataframe(productos_mas_caros, width="stretch")


# TAB 2: COMPARACIONES
with tab2:
    st.subheader("Precio por supermercado")

    if metrica_seleccionada == "Media":
        precio_por_super = (
            datos_filtrados
            .groupby("Super")["Precio"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        nombre_metrica = "Precio promedio"
    else:
        precio_por_super = (
            datos_filtrados
            .groupby("Super")["Precio"]
            .median()
            .sort_values(ascending=False)
            .reset_index()
        )
        nombre_metrica = "Precio mediano"

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(
        data=precio_por_super,
        y="Super",
        x="Precio",
        hue="Super",
        palette="Blues_r",
        legend=False,
        ax=ax
    )

    ax.set_title(f"{nombre_metrica} por supermercado")
    ax.set_xlabel(nombre_metrica)
    ax.set_ylabel("Supermercado")

    st.pyplot(fig)

    st.info(
        "Esta comparación muestra diferencias generales entre supermercados. "
        "De todos modos, hay que leerla junto con los grupos de productos seleccionados, "
        "porque no todos los supermercados tienen la misma composición de registros."
    )

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

    st.subheader(f"Top {top_n} grupos con mayor precio")

    if metrica_seleccionada == "Media":
        precio_por_grupo = (
            datos_filtrados
            .groupby("Grupo")["Precio"]
            .mean()
            .sort_values(ascending=False)
            .head(top_n)
            .reset_index()
        )
    else:
        precio_por_grupo = (
            datos_filtrados
            .groupby("Grupo")["Precio"]
            .median()
            .sort_values(ascending=False)
            .head(top_n)
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

    ax.set_title(f"Top {top_n} grupos según {nombre_metrica.lower()}")
    ax.set_xlabel(nombre_metrica)
    ax.set_ylabel("Grupo de producto")

    st.pyplot(fig)


# TAB 3: MAPA COMERCIAL
with tab3:
    st.subheader("Mapa de calor: supermercado y grupo de producto")

    top_grupos_heatmap = (
        datos_filtrados["Grupo"]
        .value_counts()
        .head(top_n)
        .index
    )

    datos_heatmap = datos_filtrados[
        datos_filtrados["Grupo"].isin(top_grupos_heatmap)
    ]

    if metrica_seleccionada == "Media":
        funcion_agregacion = "mean"
        nombre_metrica = "Precio promedio"
    else:
        funcion_agregacion = "median"
        nombre_metrica = "Precio mediano"

    matriz_precios = datos_heatmap.pivot_table(
        values="Precio",
        index="Super",
        columns="Grupo",
        aggfunc=funcion_agregacion
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

    ax.set_title(f"{nombre_metrica} por supermercado y grupo de producto")
    ax.set_xlabel("Grupo de producto")
    ax.set_ylabel("Supermercado")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig)

    st.info(
        "El mapa de calor permite ver diferencias más específicas, cruzando supermercado "
        "y grupo de producto. Esto ayuda más que mirar solo el promedio general de cada cadena."
    )

    st.subheader("Insights automáticos")

    matriz_larga = matriz_precios.stack()

    if not matriz_larga.empty:
        combinacion_maxima = matriz_larga.idxmax()
        valor_maximo = matriz_larga.max()

        combinacion_minima = matriz_larga.idxmin()
        valor_minimo = matriz_larga.min()

        col1, col2 = st.columns(2)

        col1.info(
            f"Mayor valor: {combinacion_maxima[0]} - {combinacion_maxima[1]} "
            f"con ${valor_maximo:.2f}"
        )

        col2.success(
            f"Menor valor: {combinacion_minima[0]} - {combinacion_minima[1]} "
            f"con ${valor_minimo:.2f}"
        )

    with st.expander("Ver tabla dinámica"):
        st.dataframe(matriz_precios, width="stretch")


# TAB 4: PRODUCTOS BÁSICOS
with tab4:
    st.subheader("Análisis de productos básicos seleccionados")

    st.caption(
        "Esta selección no representa una canasta básica oficial. "
        "Es una aproximación hecha con palabras clave en el nombre del producto."
    )

    datos_basicos = datos_filtrados[datos_filtrados["Producto_basico"]]
    datos_no_basicos = datos_filtrados[~datos_filtrados["Producto_basico"]]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Registros básicos", f"{datos_basicos.shape[0]:,}")
    col2.metric("Resto de registros", f"{datos_no_basicos.shape[0]:,}")

    if not datos_basicos.empty:
        col3.metric("Promedio básicos", f"${datos_basicos['Precio'].mean():.2f}")
        col4.metric("Mediana básicos", f"${datos_basicos['Precio'].median():.2f}")
    else:
        col3.metric("Promedio básicos", "$0.00")
        col4.metric("Mediana básicos", "$0.00")

    if datos_basicos.empty:
        st.warning("No hay productos básicos seleccionados con los filtros actuales.")
    else:
        st.info(
            "Este apartado sirve para mirar una parte más cotidiana del consumo. "
            "No es una canasta básica oficial, sino una selección aproximada de productos comunes."
        )

        st.subheader("Comparación: productos básicos vs resto")

        datos_comparacion_basicos = datos_filtrados.copy()

        datos_comparacion_basicos["Tipo_producto"] = datos_comparacion_basicos[
            "Producto_basico"
        ].map({
            True: "Productos básicos",
            False: "Resto de productos"
        })

        resumen_tipo = (
            datos_comparacion_basicos
            .groupby("Tipo_producto")["Precio"]
            .agg(["count", "mean", "median"])
            .round(2)
            .reset_index()
        )

        st.dataframe(resumen_tipo, width="stretch")

        fig, ax = plt.subplots(figsize=(8, 5))

        sns.barplot(
            data=datos_comparacion_basicos,
            x="Tipo_producto",
            y="Precio",
            estimator="mean",
            errorbar=None,
            hue="Tipo_producto",
            palette="Set2",
            legend=False,
            ax=ax
        )

        ax.set_title("Precio promedio: productos básicos vs resto")
        ax.set_xlabel("Tipo de producto")
        ax.set_ylabel("Precio promedio")

        st.pyplot(fig)

        st.subheader("Top 10 productos básicos con mayor precio promedio")

        top_basicos = (
            datos_basicos
            .groupby("Producto")["Precio"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=top_basicos,
            y="Producto",
            x="Precio",
            hue="Producto",
            palette="Greens_r",
            legend=False,
            ax=ax
        )

        ax.set_title("Top 10 productos básicos con mayor precio promedio")
        ax.set_xlabel("Precio promedio")
        ax.set_ylabel("Producto")

        st.pyplot(fig)

        st.subheader("Precio de productos básicos por supermercado")

        if metrica_seleccionada == "Media":
            basicos_por_super = (
                datos_basicos
                .groupby("Super")["Precio"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            titulo_basicos_super = "Precio promedio de productos básicos por supermercado"
            etiqueta_basicos_super = "Precio promedio"
        else:
            basicos_por_super = (
                datos_basicos
                .groupby("Super")["Precio"]
                .median()
                .sort_values(ascending=False)
                .reset_index()
            )
            titulo_basicos_super = "Precio mediano de productos básicos por supermercado"
            etiqueta_basicos_super = "Precio mediano"

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=basicos_por_super,
            y="Super",
            x="Precio",
            hue="Super",
            palette="Blues_r",
            legend=False,
            ax=ax
        )

        ax.set_title(titulo_basicos_super)
        ax.set_xlabel(etiqueta_basicos_super)
        ax.set_ylabel("Supermercado")

        st.pyplot(fig)

        with st.expander("Ver registros de productos básicos"):
            st.dataframe(
                datos_basicos[["Periodo", "Super", "Grupo", "Producto", "Precio"]],
                width="stretch"
            )


# TAB 5: DATOS
with tab5:
    st.subheader("Datos filtrados")

    columnas_disponibles = datos_filtrados.columns.tolist()

    columnas_seleccionadas = st.multiselect(
        "Columnas a mostrar",
        options=columnas_disponibles,
        default=columnas_disponibles
    )

    st.dataframe(
        datos_filtrados[columnas_seleccionadas],
        width="stretch"
    )

    st.subheader("Descarga de datos")

    csv = datos_filtrados.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Descargar datos filtrados en CSV",
        data=csv,
        file_name="datos_filtrados_supermercados.csv",
        mime="text/csv"
    )
