"""
pages/marco_teorico.py
Marco teórico: conceptos clave del mercado cripto, series temporales
y modelos estadísticos. Incluye tabla de operacionalización de variables.
"""
 
import sys
import os
from dash import html
import dash_bootstrap_components as dbc
 
MONO = "JetBrains Mono, monospace"
 
# Tabla de operacionalización de variables
VARIABLES = [
    ("price",           "Cuantitativa continua",  "Precio de la cripto en el momento actual",          "USD",          "Descriptiva"),
    ("market_cap",      "Cuantitativa continua",  "Precio × unidades en circulación",                  "USD",          "Descriptiva"),
    ("volume_24h",      "Cuantitativa continua",  "Valor total transaccionado en 24 horas",             "USD",          "Predictora"),
    ("change_pct_24h",  "Cuantitativa continua",  "Variación porcentual del precio en 24h",             "%",            "Predictora"),
    ("high_24h",        "Cuantitativa continua",  "Precio máximo alcanzado en 24 horas",                "USD",          "Indicador técnico"),
    ("low_24h",         "Cuantitativa continua",  "Precio mínimo alcanzado en 24 horas",                "USD",          "Indicador técnico"),
    ("open_24h",        "Cuantitativa continua",  "Precio al inicio del período de 24 horas",           "USD",          "Indicador técnico"),
    ("close",           "Cuantitativa continua",  "Precio al cierre del período diario",                "USD",          "Target ARIMA"),
    ("retorno_diario",  "Cuantitativa continua",  "(close_t / close_{t-1} - 1) × 100",                 "%",            "Feature derivada"),
    ("sma_7",           "Cuantitativa continua",  "Media móvil simple de los últimos 7 días",           "USD",          "Indicador técnico"),
    ("sma_30",          "Cuantitativa continua",  "Media móvil simple de los últimos 30 días",          "USD",          "Indicador técnico"),
    ("volatilidad_30d", "Cuantitativa continua",  "Desv. estándar retornos × √365 (ventana 30d)",      "% anual",      "Feature derivada"),
    ("hl_range_pct",    "Cuantitativa continua",  "(high - low) / low × 100",                          "%",            "Proxy volatilidad"),
    ("liq_ratio",       "Cuantitativa continua",  "volume_24h / market_cap × 100",                     "%",            "Liquidez relativa"),
    ("señal_arima",     "Cuantitativa continua",  "Precio pronosticado por ARIMA(p,d,q)",               "USD",          "Variable objetivo"),
]
 
 
def layout():
    return html.Div([
 
        html.Div([
            html.H1("Marco Teórico", className="page-title"),
            html.P(
                "Conceptos fundamentales del mercado cripto, series temporales "
                "y modelos estadísticos utilizados en este proyecto.",
                className="page-sub"
            ),
        ], className="page-head"),
 
        # ── Nota introductoria ────────────────────────────────────────────
        html.Div(
            "Esta sección define los conceptos clave que fundamentan el análisis. "
            "No se requiere conocimiento previo avanzado: cada término se explica "
            "de forma clara y con su relevancia práctica para el proyecto.",
            className="info mb-3",
            style={"fontSize": ".88rem"}
        ),
 
        # ── Bloque 1: Mercado Cripto ──────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("₿ Conceptos del Mercado Cripto"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(_concepto(
                        "Blockchain",
                        "Red descentralizada de registros encadenados (bloques) que garantiza "
                        "la integridad e inmutabilidad de las transacciones sin necesidad de "
                        "intermediarios como bancos. Cada bloque contiene un hash del anterior, "
                        "haciendo prácticamente imposible alterar el historial.",
                        "₿"
                    ), md=4),
                    dbc.Col(_concepto(
                        "Market Cap (Capitalización)",
                        "Valor total de una criptomoneda en el mercado. Se calcula como: "
                        "Market Cap = Precio × Unidades en circulación. "
                        "Es la métrica principal para clasificar el tamaño de una cripto. "
                        "BTC tiene el mayor market cap del ecosistema.",
                        "📊"
                    ), md=4),
                    dbc.Col(_concepto(
                        "Dominancia de BTC",
                        "Porcentaje del market cap total del mercado cripto que corresponde "
                        "a Bitcoin. Si la dominancia es alta (>50%), Bitcoin lidera. "
                        "Si baja, las altcoins están ganando terreno. "
                        "Es un indicador del ciclo de mercado (bull vs bear).",
                        "👑"
                    ), md=4),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(_concepto(
                        "Volatilidad",
                        "Medida de la dispersión de los retornos respecto a su media. "
                        "En criptomonedas es estructuralmente alta (30-80% anual) "
                        "comparado con acciones (~15-20%) o divisas (~5-10%). "
                        "Se calcula como la desviación estándar de retornos × √252 (días hábiles).",
                        "📉"
                    ), md=4),
                    dbc.Col(_concepto(
                        "OHLCV",
                        "Open, High, Low, Close, Volume. Estructura estándar de datos de precio: "
                        "Open = precio de apertura, High = máximo del período, "
                        "Low = mínimo, Close = precio de cierre, Volume = total transaccionado. "
                        "Son la base de todo análisis técnico.",
                        "🕯️"
                    ), md=4),
                    dbc.Col(_concepto(
                        "Liquidez",
                        "Facilidad con la que un activo puede comprarse o venderse "
                        "sin afectar significativamente su precio. "
                        "Se mide como Volumen/Market Cap. Alta liquidez significa "
                        "que puedes vender grandes cantidades sin hundir el precio.",
                        "💧"
                    ), md=4),
                ]),
            ])
        ], className="mb-3"),
 
        # ── Bloque 2: Series Temporales ───────────────────────────────────
        dbc.Card([
            dbc.CardHeader("📈 Series Temporales y Estacionariedad"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        _concepto(
                            "Serie de tiempo",
                            "Secuencia de observaciones de una variable registradas "
                            "en intervalos regulares de tiempo. En este proyecto: "
                            "precio diario de cierre de cada criptomoneda. "
                            "El análisis de series temporales busca identificar patrones, "
                            "tendencias y ciclos para hacer predicciones.",
                            "📅"
                        ),
                        _concepto(
                            "Retornos logarítmicos",
                            "Cambio porcentual del precio entre dos períodos: "
                            "r_t = (P_t / P_{t-1} - 1) × 100. "
                            "Los retornos eliminan la tendencia de los precios y "
                            "son más adecuados para el análisis estadístico ya que "
                            "tienden a ser estacionarios.",
                            "↩️"
                        ),
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H6("⚖️ Estacionariedad — Concepto clave",
                                    style={"color": "var(--accent)", "marginBottom": "10px"}),
                            html.P(
                                "Una serie temporal es estacionaria si su media, varianza "
                                "y autocovarianza no cambian con el tiempo. "
                                "Es un requisito fundamental para modelos como ARIMA.",
                                style={"fontSize": ".87rem", "color": "var(--ink-mid)",
                                       "lineHeight": "1.65", "marginBottom": "10px"}
                            ),
                            html.Div([
                                html.Div([
                                    html.Strong("❌ Precios → NO estacionarios",
                                                style={"color": "var(--down)", "fontSize": ".85rem"}),
                                    html.P(
                                        "Los precios tienen tendencia creciente a largo plazo. "
                                        "La media cambia con el tiempo (hoy BTC vale más que hace 3 años). "
                                        "No se puede modelar directamente con ARIMA.",
                                        style={"fontSize": ".82rem", "color": "var(--ink-mid)",
                                               "lineHeight": "1.5", "marginBottom": "0"}
                                    )
                                ], style={
                                    "background": "var(--down-bg)", "borderRadius": "6px",
                                    "padding": "10px 14px", "marginBottom": "8px",
                                    "border": "1px solid var(--down-b)"
                                }),
                                html.Div([
                                    html.Strong("✅ Retornos → SÍ estacionarios",
                                                style={"color": "var(--up)", "fontSize": ".85rem"}),
                                    html.P(
                                        "Los retornos diarios fluctúan alrededor de una media "
                                        "constante cercana a 0% con varianza relativamente estable. "
                                        "ARIMA se aplica sobre los precios diferenciados (d=1).",
                                        style={"fontSize": ".82rem", "color": "var(--ink-mid)",
                                               "lineHeight": "1.5", "marginBottom": "0"}
                                    )
                                ], style={
                                    "background": "var(--up-bg)", "borderRadius": "6px",
                                    "padding": "10px 14px",
                                    "border": "1px solid var(--up-b)"
                                }),
                            ])
                        ], style={
                            "background": "var(--bg-subtle)", "borderRadius": "8px",
                            "padding": "16px", "border": "1px solid var(--rule)"
                        })
                    ], md=6),
                ], className="mb-3"),
 
                # Indicadores técnicos
                dbc.Row([
                    dbc.Col(_indicador(
                        "SMA — Media Móvil Simple",
                        "SMA_n = (P₁ + P₂ + ... + Pₙ) / n",
                        "Promedio del precio en los últimos n días. Suaviza fluctuaciones "
                        "y revela la tendencia subyacente. Cuando SMA7 cruza SMA30 hacia "
                        "arriba → señal alcista (golden cross). Al revés → señal bajista."
                    ), md=4),
                    dbc.Col(_indicador(
                        "Rango H-L (Volatilidad intradiaria)",
                        "hl_pct = (High - Low) / Low × 100",
                        "Mide qué tan amplia fue la oscilación de precio en un día. "
                        "Un rango alto indica alta volatilidad ese día. "
                        "Proxy simple de riesgo intradiario."
                    ), md=4),
                    dbc.Col(_indicador(
                        "Volatilidad Anualizada",
                        "σ_anual = σ_diaria × √365",
                        "Desviación estándar de retornos diarios escalada a un año. "
                        "Permite comparar la volatilidad de distintos activos "
                        "en la misma unidad temporal. BTC ≈ 60-80% anual."
                    ), md=4),
                ]),
            ])
        ], className="mb-3"),
 
        # ── Bloque 3: Pruebas Estadísticas ───────────────────────────────
        dbc.Card([
            dbc.CardHeader("🧪 Pruebas Estadísticas Utilizadas"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(_prueba(
                        "ADF — Augmented Dickey-Fuller",
                        "H₀: La serie tiene raíz unitaria (NO estacionaria)",
                        [
                            "Si p-valor > 0.05 → No rechazamos H₀ → Serie NO estacionaria (típico en precios).",
                            "Si p-valor ≤ 0.05 → Rechazamos H₀ → Serie SÍ estacionaria (típico en retornos).",
                            "El parámetro d de ARIMA indica cuántas veces hay que diferenciar para lograr estacionariedad.",
                        ]
                    ), md=6),
                    dbc.Col(_prueba(
                        "Jarque-Bera — Prueba de Normalidad",
                        "H₀: Los retornos siguen una distribución normal",
                        [
                            "Si p-valor < 0.05 → Los retornos NO son normales (casi siempre en cripto).",
                            "Los retornos cripto son leptocúrticos: más datos en las colas que la normal.",
                            "Curtosis > 3 confirma colas pesadas (eventos extremos más frecuentes de lo esperado).",
                        ]
                    ), md=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(_prueba(
                        "Ljung-Box — Independencia de Residuos",
                        "H₀: Los residuos del modelo ARIMA son independientes (no hay autocorrelación)",
                        [
                            "Si p-valor > 0.05 → Residuos independientes → El modelo es adecuado.",
                            "Si p-valor ≤ 0.05 → Hay estructura residual → El modelo puede mejorarse.",
                            "Se aplica como diagnóstico post-estimación del modelo ARIMA.",
                        ]
                    ), md=6),
                    dbc.Col(_prueba(
                        "Correlación de Pearson (r)",
                        "Mide la relación lineal entre dos series de precios",
                        [
                            "r = 1.0 → Correlación positiva perfecta (se mueven igual).",
                            "r = -1.0 → Correlación negativa perfecta (se mueven al revés).",
                            "r ≈ 0 → Sin relación lineal. En cripto, la mayoría de monedas "
                            "correlacionan positivamente (r 0.6-0.9) porque siguen el ciclo de BTC.",
                        ]
                    ), md=6),
                ]),
            ])
        ], className="mb-3"),
 
        # ── Bloque 4: ARIMA ───────────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("🔮 Modelo ARIMA — Fundamentos"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        _concepto(
                            "ARIMA(p, d, q)",
                            "AutoRegressive Integrated Moving Average. Modelo estadístico "
                            "para predecir series temporales univariadas: "
                            "p = orden autoregresivo (cuántos valores pasados usa), "
                            "d = grado de diferenciación para lograr estacionariedad, "
                            "q = orden de media móvil (errores pasados).",
                            "📐"
                        )
                    ], md=4),
                    dbc.Col([
                        _concepto(
                            "ACF y PACF",
                            "Autocorrelation Function y Partial ACF. "
                            "La ACF mide la correlación de la serie con sus propios valores "
                            "en rezagos pasados. La PACF controla los efectos indirectos. "
                            "Se usan para determinar el orden q (ACF) y p (PACF) del modelo.",
                            "📊"
                        )
                    ], md=4),
                    dbc.Col([
                        _concepto(
                            "Criterios AIC y BIC",
                            "Akaike Information Criterion y Bayesian IC. "
                            "Miden la calidad del modelo penalizando la complejidad. "
                            "Menor valor = mejor balance entre ajuste y parsimonia. "
                            "Se usan para comparar modelos ARIMA con diferentes órdenes (p,d,q).",
                            "🎯"
                        )
                    ], md=4),
                ])
            ])
        ], className="mb-3"),
 
        # ── Tabla de operacionalización ───────────────────────────────────
        dbc.Card([
            dbc.CardHeader("📋 Tabla de Operacionalización de Variables"),
            dbc.CardBody([
                html.P(
                    "Definición formal de cada variable utilizada en el análisis, "
                    "su tipo, cómo se calcula y su rol en el proyecto.",
                    style={"fontSize": ".87rem", "color": "var(--ink-mid)",
                           "marginBottom": "14px"}
                ),
                html.Div([
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Variable"),
                            html.Th("Tipo"),
                            html.Th("Definición operacional"),
                            html.Th("Unidad"),
                            html.Th("Rol"),
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(html.Code(var,
                                    style={"color": "var(--accent)", "fontSize": ".78rem"})),
                                html.Td(tipo, style={"color": "var(--ink-mid)", "fontSize": ".80rem"}),
                                html.Td(defn, style={"color": "var(--ink-mid)", "fontSize": ".80rem"}),
                                html.Td(html.Code(unidad, style={"fontSize": ".78rem"})),
                                html.Td(
                                    html.Span(rol, className=_pill_cls(rol)),
                                    style={"whiteSpace": "nowrap"}
                                ),
                            ])
                            for var, tipo, defn, unidad, rol in VARIABLES
                        ])
                    ], className="tbl"),
                ], style={"overflowX": "auto"}),
            ])
        ]),
 
    ], className="main", style={"paddingTop": "80px"})
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def _concepto(titulo, texto, emoji):
    return html.Div([
        html.Div([
            html.Span(emoji, style={"fontSize": "1.3rem", "marginRight": "8px"}),
            html.Strong(titulo, style={"color": "var(--ink)", "fontSize": ".90rem"}),
        ], style={"marginBottom": "8px"}),
        html.P(texto, style={
            "color": "var(--ink-mid)", "fontSize": ".84rem",
            "lineHeight": "1.65", "marginBottom": "0",
        }),
    ], style={
        "background": "var(--bg-subtle)", "borderRadius": "8px",
        "padding": "14px", "marginBottom": "12px",
        "border": "1px solid var(--rule)",
    })
 
 
def _indicador(titulo, formula, desc):
    return html.Div([
        html.Strong(titulo, style={"color": "var(--accent)", "fontSize": ".88rem",
                                    "display": "block", "marginBottom": "6px"}),
        html.Code(formula, style={
            "display": "block", "padding": "6px 10px",
            "background": "var(--bg-hover)", "borderRadius": "5px",
            "fontSize": ".78rem", "color": "var(--accent)",
            "fontFamily": MONO, "marginBottom": "8px",
        }),
        html.P(desc, style={
            "color": "var(--ink-mid)", "fontSize": ".82rem",
            "lineHeight": "1.6", "marginBottom": "0",
        }),
    ], style={
        "background": "var(--bg-subtle)", "borderRadius": "8px",
        "padding": "14px", "border": "1px solid var(--rule)",
    })
 
 
def _prueba(titulo, hipotesis, puntos):
    return html.Div([
        html.Strong(titulo, style={"color": "var(--ink)", "fontSize": ".90rem",
                                    "display": "block", "marginBottom": "6px"}),
        html.Em(hipotesis, style={"color": "var(--ink-mid)", "fontSize": ".82rem",
                                    "display": "block", "marginBottom": "8px"}),
        html.Ul([
            html.Li(p, style={"color": "var(--ink-mid)", "fontSize": ".82rem",
                               "lineHeight": "1.6", "marginBottom": "4px"})
            for p in puntos
        ], style={"paddingLeft": "18px", "marginBottom": "0"}),
    ], style={
        "background": "var(--bg-subtle)", "borderRadius": "8px",
        "padding": "14px", "border": "1px solid var(--rule)",
        "height": "100%",
    })
 
 
def _pill_cls(rol):
    rol_l = rol.lower()
    if "target" in rol_l or "objetivo" in rol_l:
        return "pill pill-d"
    if "descriptiva" in rol_l:
        return "pill pill-n"
    return "pill pill-a"