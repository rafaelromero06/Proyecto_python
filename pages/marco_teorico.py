"""
tabs/marco_teorico.py
Marco teórico: conceptos de mercado cripto y operacionalización de variables.
"""

from dash import html
import dash_bootstrap_components as dbc


VARIABLES = [
    ("price",          "Cuantitativa continua",  "Precio actual en USD",                       "USD",               "Predictora / Target"),
    ("market_cap",     "Cuantitativa continua",  "Capitalización de mercado (precio × supply)", "USD",               "Predictora"),
    ("volume_24h",     "Cuantitativa continua",  "Volumen de transacciones en 24 horas",        "USD",               "Predictora"),
    ("change_pct_24h", "Cuantitativa continua",  "Variación porcentual del precio en 24h",      "%",                 "Predictora"),
    ("high_24h",       "Cuantitativa continua",  "Precio máximo en las últimas 24 horas",       "USD",               "Indicador técnico"),
    ("low_24h",        "Cuantitativa continua",  "Precio mínimo en las últimas 24 horas",       "USD",               "Indicador técnico"),
    ("open_24h",       "Cuantitativa continua",  "Precio de apertura hace 24 horas",            "USD",               "Indicador técnico"),
    ("supply",         "Cuantitativa discreta",  "Unidades de la cripto en circulación",        "Unidades",          "Contextual"),
    ("rango_hl_pct",   "Cuantitativa continua",  "(High-Low)/Low × 100: proxy de volatilidad",  "%",                 "Feature derivada"),
    ("liq_ratio",      "Cuantitativa continua",  "Volume/MarketCap × 100: liquidez relativa",   "%",                 "Feature derivada"),
    ("señal",          "Cualitativa binaria",    "Precio cierre > precio apertura",             "0=Baja, 1=Sube",    "Variable objetivo (ML)"),
]


def layout():
    return dbc.Container([

        html.H2("📚 Marco Teórico", className="section-title"),
        html.Div([
            html.P("Esta sección define los conceptos clave que necesitas conocer para entender "
                   "el análisis del mercado cripto. No es necesario ser experto: "
                   "explicamos cada término de manera simple y directa.",
                   style={"color": "var(--text-mid)", "fontSize": "0.90rem",
                          "lineHeight": "1.6", "padding": "10px 14px",
                          "background": "var(--bg-card2)", "borderRadius": "8px",
                          "borderLeft": "3px solid var(--accent-teal)", "marginBottom": "20px"})
        ]),
        html.P(
            "Conceptos fundamentales del mercado cripto y operacionalización "
            "de las variables del modelo.",
            className="section-subtitle"
        ),

        # ── Conceptos ────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(_concepto("₿", "Blockchain",
                "Red descentralizada de registros inmutables (bloques) que "
                "garantiza la trazabilidad de transacciones sin intermediarios.",
                "var(--accent-orange)"), md=4),
            dbc.Col(_concepto("📊", "Market Cap",
                "Valoración total de una cripto: precio × oferta circulante. "
                "Métrica principal para clasificar criptoactivos.",
                "var(--accent-blue)"), md=4),
            dbc.Col(_concepto("📉", "Volatilidad",
                "Medida de la dispersión de retornos. En cripto es estructuralmente "
                "alta (10-30% anual vs 1-2% en divisas fiat).",
                "var(--accent-red)"), md=4),
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(_concepto("🕯️", "OHLCV",
                "Open, High, Low, Close, Volume. Estructura estándar de datos "
                "de precio para análisis técnico e indicadores.",
                "var(--accent-teal)"), md=4),
            dbc.Col(_concepto("🔗", "Dominancia BTC",
                "Porcentaje del market cap total perteneciente a Bitcoin. "
                "Indicador del ciclo de mercado: alta dominancia = bear altcoins.",
                "var(--accent-orange)"), md=4),
            dbc.Col(_concepto("🎯", "Señal técnica",
                "Variable binaria derivada: price_close > price_open → señal alcista (1). "
                "Base del target de clasificación supervisada.",
                "var(--accent-green)"), md=4),
        ], className="mb-3"),

        # ── Indicadores técnicos ─────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("📐 Indicadores Técnicos Utilizados en el Modelo"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("SMA (Simple Moving Average)",
                                style={"color": "var(--accent-blue)"}),
                        html.Code("SMA_n = mean(close[-n:])",
                                  style=_code_style()),
                        html.P("Suaviza tendencia. SMA7 vs SMA30 genera señales de cruce.",
                               className="small mt-1", style={"color": "var(--text-mid)"})
                    ], md=4),
                    dbc.Col([
                        html.H6("Rango H-L %",
                                style={"color": "var(--accent-orange)"}),
                        html.Code("hl_pct = (high - low) / low × 100",
                                  style=_code_style()),
                        html.P("Proxy de volatilidad intradiaria del activo.",
                               className="small mt-1", style={"color": "var(--text-mid)"})
                    ], md=4),
                    dbc.Col([
                        html.H6("Ratio de Liquidez",
                                style={"color": "var(--accent-teal)"}),
                        html.Code("liq = volume_24h / market_cap × 100",
                                  style=_code_style()),
                        html.P("Activos con liq > 5% son más susceptibles a movimientos.",
                               className="small mt-1", style={"color": "var(--text-mid)"})
                    ], md=4),
                ])
            ])
        ], className="mb-3"),

        # ── Tabla de operacionalización ──────────────────────────────────
        dbc.Card([
            dbc.CardHeader("📋 Tabla de Operacionalización de Variables"),
            dbc.CardBody([
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Variable"),
                        html.Th("Tipo"),
                        html.Th("Definición"),
                        html.Th("Unidad"),
                        html.Th("Rol"),
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Code(var, style={"color": "var(--accent-blue)"})),
                            html.Td(tipo, style={"color": "var(--text-mid)"}),
                            html.Td(defn, style={"color": "var(--text-mid)"}),
                            html.Td(unidad, className="mono"),
                            html.Td(html.Span(
                                rol,
                                className="pill " + (
                                    "pill-green" if "objetivo" in rol.lower() else
                                    "pill-blue" if "Predictora" in rol else
                                    "pill-purple"
                                )
                            )),
                        ])
                        for var, tipo, defn, unidad, rol in VARIABLES
                    ])
                ], className="crypto-table")
            ])
        ]),

    ], fluid=True, className="py-3")


def _concepto(emoji, titulo, texto, color):
    return html.Div([
        html.Div([
            html.Span(emoji, style={"fontSize": "1.4rem"}),
            html.Strong(f"  {titulo}", style={"color": color}),
        ], style={"marginBottom": "6px"}),
        html.P(texto, className="small mb-0", style={"color": "var(--text-mid)"})
    ], style={
        "background": "var(--bg-card2)", "borderRadius": "10px",
        "padding": "16px", "marginBottom": "12px",
        "border": "1px solid var(--border)"
    })


def _code_style():
    return {
        "display": "block", "padding": "8px 12px",
        "background": "#0d1117", "borderRadius": "6px",
        "fontSize": "0.78rem", "color": "var(--accent-teal)",
        "fontFamily": "JetBrains Mono, monospace"
    }
