"""
pages/mercado.py
Snapshot del mercado en vivo: KPIs, barras, dona, heatmap y tabla.
"""

import sys
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# ── path al módulo de datos ──────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "data"))
from data import get_cached, fetch_global_stats

MONO = "JetBrains Mono, monospace"


# ── layout ───────────────────────────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div([
            html.H1("Mercado en vivo", className="page-title"),
            html.P("Top 30 criptomonedas · actualización automática cada 5 min",
                   className="page-sub"),
        ], className="page-head"),

        html.Div(id="mkt-body"),
    ], className="main", style={"paddingTop": "80px"})


# ── callback ─────────────────────────────────────────────────────────────────

@callback(
    Output("mkt-body", "children"),
    Input("theme-store",    "data"),
    Input("iv-global",      "n_intervals"),
)
def render(theme, _n):
    dark  = (theme == "dark")
    df    = get_cached(30)
    stats = fetch_global_stats()

    return html.Div([
        # KPIs
        dbc.Row([
            _kpi(_fmt(stats.get("total_market_cap", 0)), "Cap. total",       "accent"),
            _kpi(f"{stats.get('btc_dominance',0):.1f}%", "Dominancia BTC",  "accent"),
            _kpi(_fmt(stats.get("total_volume_24h", 0)), "Volumen 24h",      "accent"),
            _kpi(f"{stats.get('avg_change_pct_24h',0):+.2f}%",
                 "Cambio prom. 24h",
                 "up" if stats.get("avg_change_pct_24h", 0) >= 0 else "down"),
        ], className="mb-1"),

        html.Div("Distribución del mercado", className="sec"),

        dbc.Row([
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_bars(df, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=8),
            dbc.Col(html.Div([
                dcc.Graph(figure=_fig_dona(df, dark),
                          config={"displayModeBar": False})
            ], className="gw"), md=4),
        ]),

        html.Div("Mapa de calor — cambio 24h", className="sec"),

        html.Div([
            dcc.Graph(figure=_fig_heat(df, dark),
                      config={"displayModeBar": False})
        ], className="gw"),

        html.Div("Top 30 — tabla", className="sec"),
        _tabla(df),
    ])


# ── figuras ───────────────────────────────────────────────────────────────────

def _fig_bars(df, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    df2 = df.nlargest(15, "market_cap").sort_values("market_cap")
    colors = [_up(dark) if x >= 0 else _dn(dark)
              for x in df2["change_pct_24h"]]
    fig = go.Figure(go.Bar(
        x=df2["market_cap"], y=df2["symbol"],
        orientation="h",
        marker_color=colors, marker_line_width=0,
        text=df2["market_cap"].apply(_fmt),
        textposition="outside",
        textfont=dict(size=8, color=tdim, family=MONO),
    ))
    _dl(fig, "Market Cap — Top 15", bg, pp, grid, txt, tdim, 380)
    fig.update_layout(xaxis=dict(showticklabels=False))
    return fig


def _fig_dona(df, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    df2 = df.nlargest(8, "market_cap")
    pal = (["#5a7aec","#7a96f0","#93a8f0","#aabdf4","#c2d2f8","#3e3e44","#52525b","#27272a"]
           if dark else
           ["#1a46c4","#2d58d4","#4470e0","#6080e8","#8098f0","#a8a7a3","#6b6a67","#3a3a3a"])
    fig = px.pie(df2, names="symbol", values="market_cap",
                 hole=0.52, color_discrete_sequence=pal)
    fig.update_layout(
        height=380, paper_bgcolor=pp,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(text="Dominancia", font=dict(color=txt, size=11)),
        margin=dict(t=44, b=10, l=10, r=10),
        legend=dict(font=dict(color=tdim, size=8)),
    )
    return fig


def _fig_heat(df, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    df2    = df.head(30).copy()
    ncols  = 6
    nrows  = int(np.ceil(len(df2) / ncols))
    pad    = nrows * ncols - len(df2)
    if pad:
        df2 = pd.concat([df2, pd.DataFrame(
            [{"symbol": "", "change_pct_24h": np.nan}] * pad
        )], ignore_index=True)
    z    = df2["change_pct_24h"].values.reshape(nrows, ncols)
    text = df2["symbol"].values.reshape(nrows, ncols)
    chg  = df2["change_pct_24h"].values.reshape(nrows, ncols)
    cust = [[f"{text[r][c]}  {chg[r][c]:+.1f}%" if text[r][c] else ""
             for c in range(ncols)] for r in range(nrows)]
    fig = go.Figure(go.Heatmap(
        z=z, text=text, customdata=cust,
        hovertemplate="%{customdata}<extra></extra>",
        texttemplate="%{text}",
        textfont=dict(size=10, color="white", family=MONO),
        colorscale=[[0, _dn(dark)], [0.5, pp], [1, _up(dark)]],
        zmid=0, showscale=True,
        colorbar=dict(tickfont=dict(color=tdim, size=8), thickness=10),
    ))
    _dl(fig, "Cambio 24h — Top 30", bg, pp, grid, txt, tdim, 300)
    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
    )
    return fig


def _tabla(df):
    rows = []
    for i, (_, r) in enumerate(df.iterrows(), 1):
        chg = r["change_pct_24h"]
        cls = "cup" if chg >= 0 else "cdn"
        sgn = "▲" if chg >= 0 else "▼"
        p   = r["price"]
        fp  = f"${p:,.2f}" if p >= 1 else f"${p:.6f}"
        rows.append(html.Tr([
            html.Td(f"#{i}", className="dim mono"),
            html.Td(html.Strong(r["symbol"],
                    style={"color":"var(--accent)","fontFamily":MONO})),
            html.Td(r["name"], className="mid",
                    style={"fontSize":".80rem"}),
            html.Td(fp, className="mono"),
            html.Td(_fmt(r["market_cap"]),  className="mono"),
            html.Td(_fmt(r["volume_24h"]), className="mono"),
            html.Td(html.Span(f"{sgn} {abs(chg):.2f}%", className=cls,
                              style={"fontFamily":MONO})),
        ]))
    return html.Table([
        html.Thead(html.Tr([html.Th(h) for h in
            ["#","Symbol","Nombre","Precio","Mkt Cap","Vol 24h","Cambio 24h"]])),
        html.Tbody(rows),
    ], className="tbl")


# ── helpers ───────────────────────────────────────────────────────────────────

def _kpi(val, lbl, cls):
    return dbc.Col(html.Div([
        html.Div(val, className="kpi-val"),
        html.Div(lbl, className="kpi-lbl"),
    ], className=f"kpi {cls}"), md=3)


def _dl(fig, title, bg, pp, grid, txt, tdim, h=360):
    fig.update_layout(
        height=h, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(text=title, font=dict(color=txt, size=11)),
        margin=dict(t=44, b=20, l=20, r=16),
        xaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
        yaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
    )


def _tc(dark):
    if dark:
        return "#0c0c0e","#0c0c0e","#2a2a2e","#f0f0ee","#55554e"
    return "#ffffff","#ffffff","#f2f1ee","#1a1a18","#a09d96"


def _up(dark): return "#4ade80" if dark else "#166534"
def _dn(dark): return "#f87171" if dark else "#991b1b"


def _fmt(v):
    try:
        v = float(v)
    except Exception:
        return "—"
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.2f}B"
    if v >= 1e6:  return f"${v/1e6:.2f}M"
    return f"${v:,.4f}"
