"""
pages/historico.py
Histórico 3 años: comparativa, drawdown, rendimiento anual,
heatmap mensual.
"""

import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "data"))
from data import fetch_multi, fetch_histoday, TOP_10

MONO   = "JetBrains Mono, monospace"
PAL_LT = ["#1a46c4","#991b1b","#166534","#78350f","#5b21b6",
           "#0e7490","#9f1239","#1e3a5f","#3d6b27","#5c2d8a"]
PAL_DK = ["#5a7aec","#f87171","#4ade80","#fbbf24","#a78bfa",
           "#34d399","#fb7185","#38bdf8","#a3e635","#c084fc"]


def layout():
    return html.Div([
        html.Div([
            html.H1("Histórico 3 años", className="page-title"),
            html.P("Comparativa de rendimientos, drawdown y retornos anuales",
                   className="page-sub"),
        ], className="page-head"),

        dbc.Row([
            dbc.Col([
                html.Label("Monedas (máx. 5)", style=_lbl()),
                dcc.Dropdown(
                    id="h-syms",
                    options=[{"label": s, "value": s} for s in TOP_10],
                    value=["BTC", "ETH", "SOL"],
                    multi=True,
                    style={"fontFamily": MONO, "fontSize": ".84rem"},
                ),
            ], md=6),
            dbc.Col([
                html.Label("Escala", style=_lbl()),
                dcc.RadioItems(
                    id="h-scale",
                    options=[
                        {"label": "Precio USD",    "value": "precio"},
                        {"label": "Base 100 (%)",  "value": "b100"},
                    ],
                    value="b100", inline=True,
                    inputStyle={"marginRight":"5px","cursor":"pointer"},
                    labelStyle={"marginRight":"18px","fontSize":".85rem",
                                "color":"var(--ink-mid)","cursor":"pointer"},
                ),
            ], md=6),
        ], className="mb-3"),

        html.Div(id="h-body"),
    ], className="main", style={"paddingTop": "80px"})


@callback(
    Output("h-body", "children"),
    Input("h-syms",     "value"),
    Input("h-scale",    "value"),
    Input("theme-store","data"),
)
def render(syms, scale, theme):
    if not syms:
        return html.P("Selecciona al menos una moneda.", className="mid")
    syms    = syms[:5]
    dark    = (theme == "dark")
    df_wide = fetch_multi(syms, days=1095)

    return html.Div([
        html.Div([
            dcc.Graph(figure=_fig_lines(df_wide, syms, scale, dark),
                      config={"displayModeBar": False})
        ], className="gw"),

        html.Div("Drawdown desde máximo", className="sec"),

        html.Div([
            dcc.Graph(figure=_fig_drawdown(df_wide, syms, dark),
                      config={"displayModeBar": False})
        ], className="gw"),

        html.Div("Rendimiento anual por moneda", className="sec"),

        _tabla_anual(df_wide, syms),

        html.Div(f"Retornos mensuales — {syms[0]}", className="sec"),

        html.Div([
            dcc.Graph(figure=_fig_monthly(syms[0], dark),
                      config={"displayModeBar": False})
        ], className="gw"),
    ])


# ── figuras ───────────────────────────────────────────────────────────────────

def _fig_lines(df_wide, syms, scale, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    pal  = PAL_DK if dark else PAL_LT
    fig  = go.Figure()
    for i, sym in enumerate(syms):
        if sym not in df_wide.columns:
            continue
        s = df_wide[sym].dropna()
        if s.empty:
            continue
        y = s / s.iloc[0] * 100 if scale == "b100" else s
        fig.add_trace(go.Scatter(
            x=df_wide["date"].iloc[:len(y)], y=y.values,
            mode="lines", name=sym,
            line=dict(color=pal[i % len(pal)], width=1.8),
        ))
    if scale == "b100":
        fig.add_hline(y=100, line_dash="dot",
                      line_color=tdim, line_width=1)
    ytitle = "Retorno acumulado (%)" if scale == "b100" else "Precio USD"
    ysuf   = "%" if scale == "b100" else ""
    ttl    = "Retorno acumulado (base 100)" if scale == "b100" else "Precio histórico USD"
    _dl(fig, ttl, bg, pp, grid, txt, tdim, 360)
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(ticksuffix=ysuf, gridcolor=grid,
                   tickfont=dict(color=tdim, size=8)),
    )
    return fig


def _fig_drawdown(df_wide, syms, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    pal = PAL_DK if dark else PAL_LT
    fig = go.Figure()
    for i, sym in enumerate(syms):
        if sym not in df_wide.columns:
            continue
        s  = df_wide[sym].dropna()
        dd = (s - s.cummax()) / s.cummax() * 100
        fig.add_trace(go.Scatter(
            x=df_wide["date"].iloc[:len(dd)], y=dd.values,
            mode="lines", name=sym,
            line=dict(color=pal[i % len(pal)], width=1.5),
            fill="tozeroy",
            fillcolor=_hex_alpha(pal[i % len(pal)], 0.13),
        ))
    _dl(fig, "Drawdown desde máximo (%)", bg, pp, grid, txt, tdim, 260)
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(ticksuffix="%", gridcolor=grid,
                   tickfont=dict(color=tdim, size=8)),
    )
    return fig


def _tabla_anual(df_wide, syms):
    if df_wide.empty:
        return html.P("Sin datos.", className="mid")
    años = sorted(df_wide["date"].dt.year.unique())

    def ret_año(col, año):
        s = col[df_wide["date"].dt.year == año].dropna()
        return (s.iloc[-1] / s.iloc[0] - 1) * 100 if len(s) >= 2 else None

    cabeceras = [html.Th("Año")] + [html.Th(s) for s in syms]
    filas = []
    for año in años:
        celdas = [html.Td(str(año), className="dim mono")]
        for sym in syms:
            if sym not in df_wide.columns:
                celdas.append(html.Td("—", className="mono"))
                continue
            r = ret_año(df_wide[sym], año)
            if r is None:
                celdas.append(html.Td("—", className="mono"))
            else:
                cls  = "cup" if r >= 0 else "cdn"
                sign = "+" if r >= 0 else ""
                celdas.append(html.Td(
                    html.Span(f"{sign}{r:.1f}%", className=cls),
                    style={"fontFamily": MONO, "fontSize": ".80rem"},
                ))
        filas.append(html.Tr(celdas))

    return html.Table([
        html.Thead(html.Tr(cabeceras)),
        html.Tbody(filas),
    ], className="tbl mb-3")


def _fig_monthly(symbol, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    df = fetch_histoday(symbol, days=1095)
    if df.empty:
        return go.Figure()

    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month

    monthly = df.groupby(["year", "month"])["close"].last().reset_index()
    monthly["ret"] = monthly.groupby("year")["close"].pct_change() * 100
    monthly = monthly.dropna()

    pivot = monthly.pivot(index="year", columns="month", values="ret")
    mnames = ["Ene","Feb","Mar","Abr","May","Jun",
              "Jul","Ago","Sep","Oct","Nov","Dic"]
    pivot.columns = [mnames[m - 1] for m in pivot.columns]
    acc = "#5a7aec" if dark else "#1a46c4"
    dn  = "#f87171" if dark else "#991b1b"

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=list(pivot.columns),
        y=[str(y) for y in pivot.index],
        text=[[f"{v:+.1f}%" if not np.isnan(v) else ""
               for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=9, color="white", family=MONO),
        colorscale=[[0, dn], [0.5, pp], [1, acc]],
        zmid=0, showscale=True,
        colorbar=dict(tickfont=dict(color=tdim, size=8), thickness=10),
    ))
    _dl(fig, f"Retornos mensuales — {symbol}", bg, pp, grid, txt, tdim, 260)
    fig.update_layout(
        xaxis=dict(showgrid=False, tickfont=dict(color=txt, size=9)),
        yaxis=dict(showgrid=False, tickfont=dict(color=txt, size=9)),
    )
    return fig


# ── helpers ───────────────────────────────────────────────────────────────────

def _dl(fig, title, bg, pp, grid, txt, tdim, h=360):
    fig.update_layout(
        height=h, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(text=title, font=dict(color=txt, size=11)),
        margin=dict(t=44, b=24, l=52, r=16),
        hovermode="x unified",
        legend=dict(font=dict(color=tdim, size=8), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=grid, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
        yaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
    )


def _tc(dark):
    if dark:
        return "#0c0c0e","#0c0c0e","#2a2a2e","#f0f0ee","#55554e"
    return "#ffffff","#ffffff","#f2f1ee","#1a1a18","#a09d96"


def _hex_alpha(hex_color, alpha):
    rgb = tuple(int(hex_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def _lbl():
    return {"fontFamily": MONO, "fontSize": ".63rem", "textTransform": "uppercase",
            "letterSpacing": ".08em", "color": "var(--ink-dim)",
            "marginBottom": "6px", "display": "block"}
