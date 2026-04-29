"""
app.py — Crypto Dashboard v3 (Menú con Desplazamiento Lateral)
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
from pages import marco_teorico
from pages import mercado
from pages import historico
from pages import eda
from pages import prediccion

# ── Inicializar app ───────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Crypto Dashboard",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# ── Definición del menú ───────────────────────────────────────────────────────
NAV = [
    ("inicio",     "🏠", "Inicio"),
    ("marco_teorico", "Marco teorico"),
    ("mercado",    "📊", "Mercado en vivo"),
    ("historico",  "⏳", "Histórico 3 años"),
    ("eda",        "🔍", "Análisis exploratorio"),
    ("prediccion", "📈", "Predicción ARIMA"),
]

def _sidebar(active: str, is_open: bool) -> html.Div:
    """Genera el sidebar con efecto de desplazamiento lateral (0px a 260px)."""
    
    # Estilo dinámico para el contenedor del sidebar
    sidebar_style = {
        "width": "260px" if is_open else "0px",
        "transition": "all 0.4s ease-in-out",
        "overflowX": "hidden",
        "borderRight": "1px solid var(--border)" if is_open else "none",
        "backgroundColor": "rgba(255,255,255,0.05)", # Ajustable según el tema
        "height": "calc(100vh - 52px)",
        "position": "sticky",
        "top": "52px"
    }

    menu_items = []
    for tab_id, icon, label in NAV:
        cls = "nav-item active" if tab_id == active else "nav-item"
        menu_items.append(html.Div(
            [html.Span(icon, className="nav-icon", style={"marginRight": "12px"}), label],
            className=cls,
            id={"type": "nav", "index": tab_id},
            n_clicks=0,
            style={"whiteSpace": "nowrap", "padding": "12px 20px", "cursor": "pointer"}
        ))

    return html.Div([
        # El contenedor interno mantiene un ancho fijo de 260px para que el contenido
        # no se "aplaste" mientras el sidebar se cierra.
        html.Div([
            html.Div([
                html.Span("MÓDULOS", className="nav-group-label", style={"flex": "1"}),
                html.Span("◀" if is_open else "", style={"fontSize": "0.7rem", "opacity": "0.5"})
            ], style={"display": "flex", "alignItems": "center", "padding": "15px 20px"}),
            
            html.Div(menu_items)
        ], style={"width": "260px"})
    ], className="sidebar", style=sidebar_style)


# ── Layout raíz ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="root",
    **{"data-theme": "light"},
    children=[
        # ── Almacenamiento de estado ─────────────────────────────────────
        dcc.Store(id="theme-store", storage_type="session", data="light"),
        dcc.Store(id="page-store",  storage_type="session", data="inicio"),
        dcc.Store(id="sidebar-status", storage_type="session", data=True), # Controla si está abierto
        dcc.Interval(id="iv-global", interval=300_000, n_intervals=0),

        # ── Topbar ───────────────────────────────────────────────────────
        html.Div([
            html.Div([
                # Botón de hamburguesa/toggle al lado del logo
                html.Button(
                    "☰", 
                    id="btn-toggle-sidebar", 
                    className="toggle-btn",
                    style={"background": "none", "border": "none", "fontSize": "1.5rem", "marginRight": "15px", "cursor": "pointer"}
                ),
                html.Div(className="brand-dot"),
                html.Span("Crypto Dashboard"),
            ], className="brand", style={"display": "flex", "alignItems": "center"}),

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

        # ── Contenedor Principal (Sidebar + Contenido) ───────────────────
        html.Div([
            html.Div(id="sidebar-slot"),
            html.Div(
                id="content-slot",
                style={
                    "flex": "1", 
                    "overflowY": "auto", 
                    "padding": "20px",
                    "transition": "margin-left 0.4s" # El contenido se ajusta suavemente
                }
            ),
        ], style={"display": "flex", "marginTop": "52px", "minHeight": "calc(100vh - 52px)"}),
    ],
)


# ── Callbacks ─────────────────────────────────────────────────────────────────

# 1. Toggle Sidebar (Desplazamiento Lateral)
@app.callback(
    Output("sidebar-status", "data"),
    Input("btn-toggle-sidebar", "n_clicks"),
    State("sidebar-status", "data"),
    prevent_initial_call=True
)
def toggle_sidebar(n, is_open):
    return not is_open


# 2. Toggle de Tema
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


# 3. Navegación entre páginas
@app.callback(
    Output("page-store", "data"),
    Input({"type": "nav", "index": "inicio"},      "n_clicks"),
    Input({"type":"nav","index":"marco_teorico"},"n_clicks"),
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
    return "inicio"


# 4. Renderizado de Componentes dinámicos
@app.callback(
    Output("sidebar-slot", "children"),
    Output("content-slot", "children"),
    Input("page-store",    "data"),
    Input("theme-store",   "data"),
    Input("sidebar-status", "data"),
)
def render(page, theme, is_open):
    # Generar Sidebar con estado de apertura
    sidebar_content = _sidebar(page, is_open)

    # Cargar Layout de la página
    mapping = {
        "inicio"   : inicio.layout,
        "marco_teorico": inicio.layout,
        "mercado"   : mercado.layout,
        "historico" : historico.layout,
        "eda"       : eda.layout,
        "prediccion": prediccion.layout,
    }
    
    layout_fn = mapping.get(page, inicio.layout)
    content = layout_fn()

    return sidebar_content, content


server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)
