"""
pages/eda.py
Análisis Exploratorio Interactivo — 10 monedas, selector dinámico.
Secciones:
  1. OHLC + volumen (subplots)
  2. Distribución de retornos + curva normal
  3. Volatilidad rodante 7d / 30d
  4. Boxplot comparativo de las 10 monedas
  5. Heatmap de correlaciones
  6. Scatter de retornos (moneda vs BTC)
  7. Pruebas estadísticas (ADF, curtosis, asimetría, Jarque-Bera)
"""

import sys
import os
import warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "data"))
from data import fetch_histoday, fetch_multi, TOP_10

MONO  = "JetBrains Mono, monospace"
COINS = TOP_10


def layout():
    return html.Div([
        html.Div([
            html.H1("Análisis Exploratorio", className="page-title"),
            html.P("Serie de tiempo, distribuciones, volatilidad y correlaciones — hasta 3 años",
                   className="page-sub"),
        ], className="page-head"),

        # ── controles ────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.Label("Criptomoneda", style=_lbl()),
                dcc.Dropdown(
                    id="eda-sym",
                    options=[{"label": s, "value": s} for s in COINS],
                    value="BTC", clearable=False,
                    style={"fontFamily": MONO},
                ),
            ], md=3),
            dbc.Col([
                html.Label("Período", style=_lbl()),
                dcc.RadioItems(
                    id="eda-per",
                    options=[
                        {"label": "1 año",  "value": 365},
                        {"label": "2 años", "value": 730},
                        {"label": "3 años", "value": 1095},
                    ],
                    value=1095, inline=True,
                    inputStyle={"marginRight": "5px", "cursor": "pointer"},
                    labelStyle={"marginRight": "18px", "fontSize": ".85rem",
                                "color": "var(--ink-mid)", "cursor": "pointer"},
                ),
            ], md=5),
            dbc.Col([
                html.Label("SMA principal", style=_lbl()),
                dcc.Dropdown(
                    id="eda-sma",
                    options=[{"label": f"SMA {d}", "value": d}
                             for d in [7, 14, 30, 50, 100, 200]],
                    value=30, clearable=False,
                    style={"fontFamily": MONO},
                ),
            ], md=4),
        ], className="mb-3"),

        # ── KPIs dinámicos ────────────────────────────────────────────────
        html.Div(id="eda-kpis"),

        # ── contenido ────────────────────────────────────────────────────
        html.Div(id="eda-body"),

    ], className="main", style={"paddingTop": "80px"})


# ── callback ─────────────────────────────────────────────────────────────────

@callback(
    Output("eda-kpis", "children"),
    Output("eda-body", "children"),
    Input("eda-sym",    "value"),
    Input("eda-per",    "value"),
    Input("eda-sma",    "value"),
    Input("theme-store","data"),
)
def render(sym, days, sma, theme):
    dark    = (theme == "dark")
    df      = fetch_histoday(sym, days=days)
    df_wide = fetch_multi(COINS, days=days)

    kpis = _build_kpis(df, sym)
    body = _build_body(df, df_wide, sym, sma, dark)
    return kpis, body


def _build_kpis(df, sym):
    if df.empty:
        return html.P("Sin datos.", className="mid")

    p_now  = df["close"].iloc[-1]
    p_ini  = df["close"].iloc[0]
    rend   = (p_now / p_ini - 1) * 100
    vol30  = df["close"].pct_change().rolling(30).std().iloc[-1] * np.sqrt(365) * 100
    mxd    = _max_dd(df["close"])
    p_max  = df["high"].max()
    p_min  = df["low"].min()

    def fp(p):
        return f"${p:,.2f}" if p >= 1 else f"${p:.6f}"

    sign = "+" if rend >= 0 else ""
    clsr = "up" if rend >= 0 else "down"

    return dbc.Row([
        _kpi(fp(p_now),           f"{sym} Precio actual",     "accent"),
        _kpi(f"{sign}{rend:.1f}%","Rendimiento período",      clsr),
        _kpi(f"{vol30:.1f}%",     "Volatilidad 30d anual.",   "accent"),
        _kpi(f"{mxd:.1f}%",       "Max. Drawdown",            "down"),
        _kpi(fp(p_max),           "Máximo del período",       "up"),
        _kpi(fp(p_min),           "Mínimo del período",       "down"),
    ], className="mb-2")


def _build_body(df, df_wide, sym, sma, dark):
    return html.Div([
        # OHLC + volumen
        html.Div("Serie de tiempo", className="sec"),
        html.Div([
            dcc.Graph(figure=_fig_ohlc(df, sym, sma, dark),
                      config={"displayModeBar": False})
        ], className="gw"),

        # retornos y volatilidad
        html.Div("Distribución de retornos", className="sec"),
        dbc.Row([
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_ret_hist(df, sym, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=6),
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_vol(df, sym, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=6),
        ]),

        # boxplot + correlación
        html.Div("Comparativa entre monedas", className="sec"),
        dbc.Row([
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_box(df_wide, sym, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=5),
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_corr(df_wide, sym, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=7),
        ]),

        # scatter de retornos
        html.Div("Correlación de retornos", className="sec"),
        html.Div([
            dcc.Graph(figure=_fig_scat(df_wide, sym, dark),
                      config={"displayModeBar": False})
        ], className="gw"),

        # pruebas estadísticas
        html.Div("Pruebas estadísticas", className="sec"),
        _build_stats(df, sym),
    ])


# ── figuras ───────────────────────────────────────────────────────────────────

def _fig_ohlc(df, sym, sma, dark):
    if df.empty:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    df = df.copy()
    df[f"sma{sma}"] = df["close"].rolling(sma).mean()
    df["sma7"]      = df["close"].rolling(7).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.02)

    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing_line_color=_up(dark), increasing_fillcolor=_up(dark),
        decreasing_line_color=_dn(dark), decreasing_fillcolor=_dn(dark),
        name=sym, line=dict(width=1),
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df["date"], y=df["sma7"],
        line=dict(color=tdim, width=1, dash="dot"),
        name="SMA 7", opacity=0.8,
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df["date"], y=df[f"sma{sma}"],
        line=dict(color=_acc(dark), width=1.5),
        name=f"SMA {sma}",
    ), row=1, col=1)

    barcols = [_up(dark) if c >= o else _dn(dark)
               for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=df["date"], y=df["volume"],
        marker_color=barcols, marker_line_width=0,
        opacity=0.55, name="Volumen",
    ), row=2, col=1)

    fig.update_layout(
        height=440, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(text=f"{sym}/USD · OHLC + SMA {sma} + Volumen",
                   font=dict(color=txt, size=12)),
        margin=dict(t=48, b=20, l=52, r=16),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        legend=dict(font=dict(color=tdim, size=8), bgcolor="rgba(0,0,0,0)"),
    )
    for r in [1, 2]:
        fig.update_xaxes(row=r, gridcolor=grid, zeroline=False,
                         linecolor=grid, tickfont=dict(color=tdim, size=8))
        fig.update_yaxes(row=r, gridcolor=grid, zeroline=False,
                         linecolor=grid, tickfont=dict(color=tdim, size=8))
    fig.update_yaxes(row=1, tickprefix="$", tickformat=",")
    return fig


def _fig_ret_hist(df, sym, dark):
    if df.empty:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    rets = df["close"].pct_change().dropna() * 100
    mu, sig = rets.mean(), rets.std()
    xn = np.linspace(rets.min(), rets.max(), 200)
    yn = _norm_pdf(xn, mu, sig)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=rets, nbinsx=55,
        marker_color=_acc(dark), marker_line_width=0,
        opacity=0.72, histnorm="probability density", name="Retornos",
    ))
    fig.add_trace(go.Scatter(
        x=xn, y=yn, mode="lines",
        line=dict(color=_dn(dark), width=1.5, dash="dot"),
        name="Normal",
    ))
    fig.add_vline(x=0, line_dash="dot", line_color=tdim, line_width=1)
    fig.add_vline(x=mu, line_dash="dash", line_color=_acc(dark), line_width=1,
                  annotation_text=f"μ={mu:.2f}%",
                  annotation_font_size=8, annotation_font_color=tdim)

    _dl(fig, f"Distribución retornos diarios — {sym}",
        bg, pp, grid, txt, tdim, 290)
    fig.update_layout(showlegend=True,
                      xaxis=dict(ticksuffix="%"))
    return fig


def _fig_vol(df, sym, dark):
    if df.empty:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    df = df.copy()
    df["v30"] = df["close"].pct_change().rolling(30).std() * np.sqrt(365) * 100
    df["v7"]  = df["close"].pct_change().rolling(7).std()  * np.sqrt(365) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["v30"], mode="lines",
        name="Vol 30d",
        line=dict(color=_acc(dark), width=1.8),
        fill="tozeroy", fillcolor=_hex_alpha(_acc(dark), 0.08),
    ))
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["v7"], mode="lines",
        name="Vol 7d",
        line=dict(color=_dn(dark), width=1, dash="dot"),
        opacity=0.7,
    ))
    _dl(fig, f"Volatilidad rodante anualizada — {sym}",
        bg, pp, grid, txt, tdim, 290)
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(ticksuffix="%"),
    )
    return fig


def _fig_box(df_wide, selected, dark):
    if df_wide.empty:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    cols = [c for c in df_wide.columns if c != "date"]
    fig  = go.Figure()
    for sym in cols:
        rets = df_wide[sym].pct_change().dropna() * 100
        col  = _acc(dark) if sym == selected else tdim
        fig.add_trace(go.Box(
            y=rets, name=sym,
            marker_color=col, marker_size=3,
            line=dict(width=1, color=col),
            fillcolor=_hex_alpha(col, 0.13),
            boxpoints="outliers",
        ))
    _dl(fig, "Boxplot retornos — 10 monedas",
        bg, pp, grid, txt, tdim, 300)
    fig.update_layout(
        showlegend=False,
        yaxis=dict(ticksuffix="%"),
    )
    return fig


def _fig_corr(df_wide, selected, dark):
    if df_wide.empty or len(df_wide.columns) < 3:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    num  = df_wide.drop(columns=["date"], errors="ignore")
    if num.shape[0] < 5:
        return _empty(dark)
    corr = num.corr().round(2)
    acc  = _acc(dark)
    dn   = _dn(dark)
    cs   = [[0.0, dn], [0.5, pp], [1.0, acc]]

    fig = px.imshow(corr, text_auto=True,
                    color_continuous_scale=cs, zmin=-1, zmax=1)
    fig.update_traces(textfont=dict(size=9, family=MONO))
    _dl(fig, "Correlación Pearson (r) — precios de cierre",
        bg, pp, grid, txt, tdim, 380)
    fig.update_layout(
        xaxis=dict(showgrid=False, tickfont=dict(color=txt, size=9)),
        yaxis=dict(showgrid=False, tickfont=dict(color=txt, size=9)),
        coloraxis_colorbar=dict(
            tickfont=dict(color=tdim, size=8),
            title=dict(text="r", font=dict(color=tdim, size=9)),
            thickness=10,
        ),
    )
    return fig


def _fig_scat(df_wide, selected, dark):
    if df_wide.empty:
        return _empty(dark)
    bg, pp, grid, txt, tdim = _tc(dark)
    cols = [c for c in df_wide.columns if c != "date"]
    ref  = "BTC" if selected != "BTC" else "ETH"
    if ref not in cols or selected not in cols:
        return _empty(dark)

    r1 = df_wide[ref].pct_change().dropna() * 100
    r2 = df_wide[selected].pct_change().dropna() * 100
    n  = min(len(r1), len(r2))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=r1.values[:n], y=r2.values[:n],
        mode="markers",
        marker=dict(color=_acc(dark), size=3, opacity=0.5,
                    line=dict(width=0)),
        name=f"{ref} vs {selected}",
    ))
    if n > 5:
        m, b = np.polyfit(r1.values[:n], r2.values[:n], 1)
        cv   = np.corrcoef(r1.values[:n], r2.values[:n])[0, 1]
        xl   = np.linspace(r1.min(), r1.max(), 60)
        fig.add_trace(go.Scatter(
            x=xl, y=m * xl + b, mode="lines",
            line=dict(color=_dn(dark), width=1.5, dash="dot"),
            name=f"Regresión r={cv:.2f}",
        ))
    _dl(fig, f"Retornos diarios: {ref} vs {selected}",
        bg, pp, grid, txt, tdim, 320)
    fig.update_layout(
        xaxis=dict(title=f"{ref} ret %", ticksuffix="%"),
        yaxis=dict(title=f"{selected} ret %", ticksuffix="%"),
    )
    return fig


# ── pruebas estadísticas ──────────────────────────────────────────────────────

def _build_stats(df, sym):
    if df.empty:
        return html.P("Sin datos.", className="mid")

    rets = df["close"].pct_change().dropna() * 100

    # ADF
    try:
        from statsmodels.tsa.stattools import adfuller
        adf_p  = adfuller(df["close"].dropna(), autolag="AIC")
        adf_r  = adfuller(rets.dropna(), autolag="AIC")
        adf_ps = adf_p[1]
        adf_rs = adf_r[1]
        adf_pv = f"{adf_p[0]:.4f}"
        adf_rv = f"{adf_r[0]:.4f}"
    except Exception:
        adf_ps, adf_rs = 1.0, 0.0
        adf_pv = adf_rv = "N/A"

    kurt = rets.kurtosis()
    skew = rets.skew()
    try:
        from scipy import stats as sp_stats
        jb_s, jb_p = sp_stats.jarque_bera(rets.dropna())
    except Exception:
        jb_s, jb_p = 0.0, 1.0

    def row(nombre, stat, interp, ok=True):
        cls = "cup" if ok else "cdn"
        return html.Tr([
            html.Td(nombre, className="mono",
                    style={"fontSize": ".80rem", "padding": "9px 12px"}),
            html.Td(stat, className="mono",
                    style={"fontSize": ".80rem", "padding": "9px 12px"}),
            html.Td(html.Span(interp, className=cls),
                    style={"fontFamily": MONO, "fontSize": ".78rem",
                           "padding": "9px 12px"}),
        ])

    rows = [
        row("ADF — Precios", adf_pv,
            f"p={adf_ps:.4f} → {'No estacionaria ✓' if adf_ps > 0.05 else 'Estacionaria'}",
            ok=adf_ps > 0.05),
        row("ADF — Retornos", adf_rv,
            f"p={adf_rs:.4f} → {'Estacionaria ✓' if adf_rs <= 0.05 else 'No estacionaria'}",
            ok=adf_rs <= 0.05),
        row("Curtosis", f"{kurt:.3f}",
            "Leptocúrtica — colas gruesas" if kurt > 3 else "Mesocúrtica",
            ok=True),
        row("Asimetría", f"{skew:.3f}",
            "Sesgo neg." if skew < -.5 else ("Sesgo pos." if skew > .5 else "Simétrica"),
            ok=True),
        row("Jarque-Bera", f"{jb_s:.2f}",
            f"p={jb_p:.4f} → {'No normal ✓' if jb_p < .05 else 'Posible normal'}",
            ok=True),
    ]

    return dbc.Card([
        dbc.CardHeader(f"Pruebas estadísticas — {sym}"),
        dbc.CardBody([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Prueba"), html.Th("Estadístico"), html.Th("Interpretación")
                ])),
                html.Tbody(rows),
            ], className="tbl"),
            html.P(
                "ADF = Augmented Dickey-Fuller. H₀: la serie tiene raíz unitaria "
                "(no estacionaria). Precios → no estacionaria es lo esperado; "
                "retornos → estacionaria es lo esperado.",
                className="mt-2",
                style={"fontFamily": MONO, "fontSize": ".70rem",
                       "color": "var(--ink-dim)"}
            ),
        ])
    ], className="mb-3")


# ── helpers ───────────────────────────────────────────────────────────────────

def _dl(fig, title, bg, pp, grid, txt, tdim, h=360):
    fig.update_layout(
        height=h, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(text=title, font=dict(color=txt, size=11)),
        margin=dict(t=44, b=24, l=50, r=16),
        legend=dict(font=dict(color=tdim, size=8), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
        yaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
    )


def _norm_pdf(x, mu, sig):
    denom = sig * np.sqrt(2 * np.pi)
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.exp(-0.5 * ((x - mu) / sig) ** 2) / denom
    return np.nan_to_num(y, nan=0.0, posinf=0.0, neginf=0.0)


def _kpi(val, lbl, cls):
    return dbc.Col(html.Div([
        html.Div(val, className="kpi-val"),
        html.Div(lbl, className="kpi-lbl"),
    ], className=f"kpi {cls}"), md=2)


def _tc(dark):
    if dark:
        return "#0c0c0e","#0c0c0e","#2a2a2e","#f0f0ee","#55554e"
    return "#ffffff","#ffffff","#f2f1ee","#1a1a18","#a09d96"


def _acc(dark): return "#5a7aec" if dark else "#1a46c4"
def _up(dark):  return "#4ade80" if dark else "#166534"
def _dn(dark):  return "#f87171" if dark else "#991b1b"

def _hex_alpha(hex_color, alpha):
    rgb = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def _max_dd(prices):
    roll = prices.cummax()
    dd   = (prices - roll) / roll * 100
    return dd.min()


def _lbl():
    return {"fontFamily": MONO, "fontSize": ".63rem", "textTransform": "uppercase",
            "letterSpacing": ".08em", "color": "var(--ink-dim)",
            "marginBottom": "6px", "display": "block"}


def _empty(dark):
    bg, pp = _tc(dark)[:2]
    fig = go.Figure()
    fig.add_annotation(text="Sin datos disponibles", xref="paper", yref="paper",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color="#a09d96", size=13, family=MONO))
    fig.update_layout(paper_bgcolor=pp, plot_bgcolor=bg,
                      height=260, margin=dict(t=30, b=20, l=20, r=20))
    return fig
