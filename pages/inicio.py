"""
tabs/inicio.py
Página de inicio: imagen hero, descripción del proyecto y objetivos.
"""

from dash import html
import dash_bootstrap_components as dbc
from dash import html, dcc


def layout():
    return html.Div([

        # ── Hero con imagen de fondo ──────────────────────────────────────
        html.Div([
            # Overlay oscuro encima de la imagen
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("", style={
                            "display": "inline-block",
                            "width": "10px", "height": "10px",
                            "borderRadius": "50%", "background": "#88e0b4",
                            "marginRight": "8px", "animation": "pulse 1.5s infinite",
                            "marginLeft": "260px"  
                        }),
                        html.Span("LIVE · CryptoCompare API", style={
                            "fontFamily": "monospace", "fontSize": "0.75rem",
                            "color": "#88e0b4", "letterSpacing": "0.1em",
                            "textTransform": "uppercase",
                        }),
                    ], style={"marginBottom": "20px"}),

                    html.H1("Crypto Market Dashboard", style={
                        "fontFamily": "'Space Grotesk', sans-serif",
                        "fontSize": "clamp(2rem, 5vw, 3.5rem)",
                        "fontWeight": "800",
                        "color": "#ffffff",
                        "letterSpacing": "-1px",
                        "lineHeight": "1.1",
                        "marginBottom": "16px",
                        "textShadow": "0 2px 20px rgba(0,0,0,0.5)",
                    }),

                    html.P(
                        "Análisis en tiempo real del mercado de criptomonedas. "
                        "Explora precios, tendencias, correlaciones y métricas "
                        "de las principales monedas digitales del mundo.",
                        style={
                            "color": "rgba(255,255,255,0.85)",
                            "fontSize": "1.1rem",
                            "maxWidth": "600px",
                            "lineHeight": "1.7",
                            "marginBottom": "28px",
                        }
                    ),

                    # Badges de tecnologías
                    html.Div([
                        _badge("₿ Bitcoin"),
                        _badge("Ξ Ethereum"),
                        _badge("📊 Dash + Python"),
                        _badge("🔄 Datos en vivo"),
                        _badge("📈 Análisis técnico"),
                    ], style={"display": "flex", "flexWrap": "wrap", "gap": "8px"}),

                ], style={
                    "maxWidth": "700px",
                    "padding": "60px 48px",
                }),
            ], style={
                "background": "linear-gradient(135deg, rgba(13,17,23,0.92) 0%, rgba(22,27,34,0.75) 100%)",
                "minHeight": "480px",
                "display": "flex",
                "alignItems": "center",
            }),
        ], style={
            "backgroundImage": "url('https://images.unsplash.com/photo-1642790551116-18e4f68b5253?w=1600&q=80')",
            "backgroundSize": "cover",
            "backgroundPosition": "center",
            "backgroundRepeat": "no-repeat",
            "borderRadius": "0 0 20px 20px",
            "overflow": "hidden",
            "marginBottom": "36px",
        }),

        # ── Contenido principal ───────────────────────────────────────────
        dbc.Container([

            # ── ¿Qué es este proyecto? ────────────────────────────────────
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🧭 ¿Qué es este proyecto?"),
                        dbc.CardBody([
                            html.P(
                                "Este dashboard es una herramienta de análisis financiero "
                                "construida con Python y Dash que consume datos en tiempo real "
                                "de la API de CryptoCompare, una de las fuentes más confiables "
                                "de datos de criptomonedas del mundo.",
                                style={"color": "var(--text-bright)", "fontSize": "0.95rem",
                                       "lineHeight": "1.7"}
                            ),
                            html.P(
                                "La herramienta permite explorar el mercado cripto de forma "
                                "visual e interactiva, entender las relaciones entre monedas "
                                "y analizar tendencias de precios, todo sin necesidad de "
                                "conocimientos técnicos avanzados.",
                                style={"color": "var(--text-mid)", "fontSize": "0.92rem",
                                       "lineHeight": "1.7", "marginBottom": "0"}
                            ),
                        ])
                    ])
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("❓ ¿Por qué es importante?"),
                        dbc.CardBody([
                            html.P(
                                "El mercado de criptomonedas mueve más de 2 billones de dólares "
                                "en capitalización global. Sin embargo, su alta volatilidad "
                                "hace muy difícil tomar decisiones de inversión sin datos claros.",
                                style={"color": "var(--text-bright)", "fontSize": "0.95rem",
                                       "lineHeight": "1.7"}
                            ),
                            html.P(
                                "Este proyecto demuestra cómo la ciencia de datos puede "
                                "transformar datos crudos de API en visualizaciones útiles "
                                "que cualquier persona pueda interpretar.",
                                style={"color": "var(--text-mid)", "fontSize": "0.92rem",
                                       "lineHeight": "1.7", "marginBottom": "0"}
                            ),
                        ])
                    ])
                ], md=6),
            ], className="mb-4"),

            # ── Objetivos ─────────────────────────────────────────────────
            html.H3("🎯 Objetivos del Proyecto", style={
                "color": "var(--text-bright)", "fontFamily": "'Space Grotesk', sans-serif",
                "fontWeight": "700", "marginBottom": "20px",
                "borderBottom": "2px solid var(--accent-blue)",
                "paddingBottom": "10px",
            }),

            dbc.Row([
                dbc.Col(_objetivo(
                    "01", "Monitorear el mercado en tiempo real",
                    "Conectar con la API de CryptoCompare para obtener precios actualizados, "
                    "capitalización de mercado y volumen de las 20 principales criptomonedas "
                    "cada 5 minutos automáticamente.",
                    "#7eb8f7"
                ), md=6),
                dbc.Col(_objetivo(
                    "02", "Visualizar datos de forma clara",
                    "Transformar números complejos en gráficas interactivas que permitan "
                    "identificar tendencias, comparar monedas y detectar patrones "
                    "de comportamiento del mercado fácilmente.",
                    "#c5b8f0"
                ), md=6),
            ], className="mb-3"),

            dbc.Row([
                dbc.Col(_objetivo(
                    "03", "Analizar correlaciones entre monedas",
                    "Estudiar cómo se relacionan los movimientos de precio entre "
                    "las distintas criptomonedas. ¿Se mueven juntas? ¿Cuáles son "
                    "independientes entre sí? Esto es clave para diversificar.",
                    "#7ed4c5"
                ), md=6),
                dbc.Col(_objetivo(
                    "04", "Identificar patrones de volatilidad",
                    "Determinar qué monedas son más estables y cuáles más riesgosas, "
                    "midiendo el rango de variación de precios y comparando por "
                    "tamaño de capitalización de mercado.",
                    "#f7c87e"
                ), md=6),
            ], className="mb-4"),

            # ── Cómo navegar ──────────────────────────────────────────────
            html.H3("🗺️ Cómo navegar este dashboard", style={
                "color": "var(--text-bright)", "fontFamily": "'Space Grotesk', sans-serif",
                "fontWeight": "700", "marginBottom": "20px",
                "borderBottom": "2px solid var(--accent-blue)",
                "paddingBottom": "10px",
            }),

            dbc.Row([
                dbc.Col(_nav_card("", "Mercado",
                    "Estado actual del mercado: precios, capitalización y tabla de las top 20 monedas.",
                    "/contexto"), md=3),

                dbc.Col(_nav_card("", "Histórico",
                    "Comportamiento pasado del mercado: tendencias, patrones y análisis de datos históricos.",
                    "/metodologia"), md=3),

                dbc.Col(_nav_card("", "Análisis Exploratorio",
                    "Estudio de las características y relaciones de los datos del mercado.",
                    "/resultados"), md=3),

                dbc.Col(_nav_card("", "Prediccion ARIMA",
                    "Modelos de predicción para estimar movimientos futuros del mercado.",
                    "/conclusiones"), md=3),
            ], className="mb-3"),



            # ── Datos del proyecto ────────────────────────────────────────
            dbc.Row([
                dbc.Col(_stat("20",    "Monedas monitoreadas"),  md=3),
                dbc.Col(_stat("5 min", "Frecuencia de actualización"), md=3),
                dbc.Col(_stat("4",     "Secciones de análisis"),  md=3),
                dbc.Col(_stat("100%",  "Open source · Python"),  md=3),
            ], className="mb-4"),

            # ── Nota final ────────────────────────────────────────────────
            html.Div([
                html.P(
                    "⚠️ Este dashboard es una herramienta de análisis educativo. "
                    "La información presentada no constituye asesoramiento financiero. "
                    "Las criptomonedas son activos de alto riesgo.",
                    style={
                        "color": "var(--text-dim)", "fontSize": "0.80rem",
                        "textAlign": "center", "fontStyle": "italic",
                        "padding": "12px", "borderTop": "1px solid var(--border)",
                    }
                )
            ]),

        ], fluid=True),
    ])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(texto):
    return html.Span(texto, style={
        "background": "rgba(255,255,255,0.12)",
        "backdropFilter": "blur(8px)",
        "border": "1px solid rgba(255,255,255,0.25)",
        "color": "rgba(255,255,255,0.9)",
        "padding": "5px 14px",
        "borderRadius": "999px",
        "fontSize": "0.78rem",
        "fontWeight": "500",
        "letterSpacing": "0.02em",
    })


def _objetivo(num, titulo, desc, color):
    return html.Div([
        html.Div([
            html.Span(num, style={
                "fontFamily": "'Space Grotesk', sans-serif",
                "fontSize": "2rem", "fontWeight": "800",
                "color": color, "lineHeight": "1",
            }),
            html.Strong(titulo, style={
                "color": "var(--text-bright)", "fontSize": "0.95rem",
                "display": "block", "marginTop": "6px",
            }),
        ], style={"marginBottom": "10px"}),
        html.P(desc, style={
            "color": "var(--text-mid)", "fontSize": "0.87rem",
            "lineHeight": "1.65", "marginBottom": "0",
        }),
    ], style={
        "background": "var(--bg-card2)", "borderRadius": "12px",
        "padding": "20px", "marginBottom": "14px",
        "border": "1px solid var(--border)",
        "borderLeft": f"3px solid {color}",
    })


def _nav_card(emoji, titulo, desc, ruta):
    return dcc.Link(
        html.Div([
            html.Div(emoji, style={
                "fontSize": "1.8rem",
                "marginBottom": "8px"
            }),

            html.Strong(titulo, style={
                "color": "var(--accent-blue)",
                "fontSize": "0.9rem",
                "display": "block",
                "marginBottom": "6px"
            }),

            html.P(desc, style={
                "color": "var(--text-dim)",
                "fontSize": "0.80rem",
                "lineHeight": "1.5",
                "marginBottom": "0"
            }),

        ], style={
            "background": "var(--bg-card2)",
            "borderRadius": "10px",
            "padding": "16px",
            "marginBottom": "12px",
            "border": "1px solid var(--border)",
            "height": "calc(100% - 12px)",
            "cursor": "pointer",
            "transition": "all 0.25s ease",
        }),
        href=ruta,
        refresh=False,  # 🔥 IMPORTANTE (no recarga la app)
        style={"textDecoration": "none"}
    )


def _stat(valor, label):
    return html.Div([
        html.Div(valor, style={
            "fontFamily": "'Space Grotesk', monospace",
            "fontSize": "2rem", "fontWeight": "700",
            "color": "var(--accent-blue)", "lineHeight": "1",
        }),
        html.Div(label, style={
            "color": "var(--text-dim)", "fontSize": "0.78rem",
            "marginTop": "4px", "textTransform": "uppercase",
            "letterSpacing": "0.06em",
        }),
    ], style={
        "background": "var(--bg-card2)", "borderRadius": "10px",
        "padding": "18px 20px", "marginBottom": "12px",
        "border": "1px solid var(--border)",
        "textAlign": "center",
    })