"""
app.py — Crypto Dashboard v3
Importa módulos desde /pages/ (evita conflicto con 'tabs' de site-packages).
Incluye:
  - Sidebar de navegación fija
  - Toggle claro / oscuro
  - dcc.Store para persistir el tema en la sesión
  - dcc.Interval para auto-refresh de datos de mercado
"""

import sys
import os

# ── asegurar que Python encuentre /pages y /data en este directorio ──────────
_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)

from dash import Dash, html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc

# ── importar layouts desde /pages ────────────────────────────────────────────
from pages import inicio
from pages import mercado
from pages import historico
from pages import eda
from pages import prediccion

# ── Inicializar app ───────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True,
    title="Crypto Dashboard",
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1",
    }],
)

# ── Definición del menú ───────────────────────────────────────────────────────
NAV = [
    ("inicio",      "", "Inicio"),
    ("mercado",    "", "Mercado en vivo"),
    ("historico",  "", "Histórico 3 años"),
    ("eda",        "", "Análisis exploratorio"),
    ("prediccion", "", "Predicción ARIMA"),
]


def _sidebar(active: str) -> html.Div:
    items = [html.Div("Módulos", className="nav-group-label")]
    for tab_id, icon, label in NAV:
        cls = "nav-item active" if tab_id == active else "nav-item"
        items.append(html.Div(
            [html.Span(icon, className="nav-icon"), label],
            className=cls,
            id={"type": "nav", "index": tab_id},
            n_clicks=0,
        ))
    return html.Div(items, className="sidebar")


# ── Layout raíz ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="root",
    **{"data-theme": "light"},
    children=[
        # ── Stores e Interval ────────────────────────────────────────────
        dcc.Store(id="theme-store", storage_type="session", data="light"),
        dcc.Store(id="page-store",  storage_type="session", data="mercado"),
        dcc.Interval(id="iv-global", interval=300_000, n_intervals=0),

        # ── Topbar ───────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div(className="brand-dot"),
                html.Span("Crypto Dashboard"),
            ], className="brand"),

            html.Div([
                html.Div([
                    html.Span("", className="live-dot"),
                    "LIVE",
                ], className="live-badge"),

                html.Button(
                    "🌙 Modo oscuro",
                    id="btn-theme",
                    className="theme-btn",
                    n_clicks=0,
                ),
            ], className="topbar-right"),
        ], className="topbar"),

        # ── Sidebar + contenido ──────────────────────────────────────────
        html.Div([
            html.Div(id="sidebar-slot"),
            html.Div(id="content-slot",
                     style={"flex": "1", "overflowY": "auto"}),
        ], style={"display": "flex", "marginTop": "52px",
                  "minHeight": "calc(100vh - 52px)"}),
    ],
)


# ── Callbacks ─────────────────────────────────────────────────────────────────

# Toggle de tema
@app.callback(
    Output("root",        "data-theme"),
    Output("theme-store", "data"),
    Output("btn-theme",   "children"),
    Input("btn-theme",    "n_clicks"),
    State("theme-store",  "data"),
    prevent_initial_call=False,
)
def toggle_theme(n, current):
    if n and n % 2 == 1:
        return "dark", "dark", "☀️ Modo claro"
    return "light", "light", "🌙 Modo oscuro"


# Actualizar pestaña activa al hacer clic en el sidebar
@app.callback(
    Output("page-store", "data"),
    Input({"type": "nav", "index": "inicio"},      "n_clicks"),
    Input({"type": "nav", "index": "mercado"},    "n_clicks"),
    Input({"type": "nav", "index": "historico"},  "n_clicks"),
    Input({"type": "nav", "index": "eda"},        "n_clicks"),
    Input({"type": "nav", "index": "prediccion"}, "n_clicks"),
    prevent_initial_call=True,
)
def set_page(*_):
    triggered = ctx.triggered_id
    if triggered and isinstance(triggered, dict):
        return triggered["index"]
    return "mercado"


# Renderizar sidebar y contenido
@app.callback(
    Output("sidebar-slot", "children"),
    Output("content-slot", "children"),
    Input("page-store",  "data"),
    Input("theme-store", "data"),
)
def render(page, theme):
    sidebar = _sidebar(page)

    mapping = {
        "inicio"   : inicio.layout,
        "mercado"   : mercado.layout,
        "historico" : historico.layout,
        "eda"       : eda.layout,
        "prediccion": prediccion.layout,
    }
    fn      = mapping.get(page, mercado.layout)
    content = fn()

    return sidebar, content

server = app.server
# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
