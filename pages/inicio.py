
"""
tabs/inicio.py
Página de inicio: imagen hero, descripción del proyecto y objetivos.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc


def layout():
    return html.Div([

        # ── Hero con imagen de fondo ──────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("", style={
                            "display": "inline-block",
                            "width": "10px", "height": "10px",
                            "borderRadius": "50%", "background": "#88e0b4",
                            "marginRight": "8px", "animation": "pulse 1.5s infinite",
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

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🧭 ¿Qué es este proyecto?"),
                        dbc.CardBody([
                            html.P(
                                "Este dashboard es una herramienta de análisis financiero "
                                "construida con Python y Dash que consume datos en tiempo real "
                                "de la API de CryptoCompare.",
                            ),
                        ])
                    ])
                ], md=6),

                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("❓ ¿Por qué es importante?"),
                        dbc.CardBody([
                            html.P(
                                "El mercado de criptomonedas es altamente volátil, "
                                "por lo que el análisis visual facilita la toma de decisiones."
                            ),
                        ])
                    ])
                ], md=6),
            ], className="mb-4"),

            # ── Navegación ───────────────────────────────────────────────
            html.H3("🗺️ Navegación", className="mb-3"),

            dbc.Row([
                dbc.Col(_nav_card("📊", "Mercado",
                    "Precios y capitalización en tiempo real.",
                    "/contexto"), md=3),

                dbc.Col(_nav_card("📈", "Histórico",
                    "Análisis de tendencias pasadas.",
                    "/metodologia"), md=3),

                dbc.Col(_nav_card("🔍", "EDA",
                    "Relaciones y análisis exploratorio.",
                    "/resultados"), md=3),

                dbc.Col(_nav_card("🤖", "Predicción",
                    "Modelos ARIMA de predicción.",
                    "/conclusiones"), md=3),
            ]),

        ], fluid=True),
    ])


# ── Helpers ─────────────────────────────────────────────────────

def _badge(texto):
    return html.Span(texto, style={
        "background": "rgba(255,255,255,0.12)",
        "padding": "5px 14px",
        "borderRadius": "999px",
        "fontSize": "0.78rem",
    })


def _nav_card(icono, titulo, desc, ruta):
    return dcc.Link(
        html.Div([
            html.Div(icono, style={"fontSize": "1.8rem"}),
            html.Strong(titulo),
            html.P(desc),
        ], style={
            "padding": "16px",
            "border": "1px solid #333",
            "borderRadius": "10px",
            "cursor": "pointer",
            "transition": "all 0.2s",
        }),
        href=ruta,
        style={"textDecoration": "none"}
    )

