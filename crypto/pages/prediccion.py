"""
pages/prediccion.py
Predicción ARIMA:
  - Selector de moneda y horizonte
  - Pronóstico con IC 80% y 95%
  - Validación hold-out con MAE / RMSE / MAPE
  - Diagnósticos: residuos, ACF, PACF, QQ-plot
  - Interpretación en lenguaje natural
"""

import sys
import os
import warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "data"))
from data import fetch_histoday, TOP_10

MONO  = "JetBrains Mono, monospace"
COINS = TOP_10

# Órdenes (p,d,q) preoptimizados para agilizar el cómputo
_ORDERS = {
    "BTC": (2,1,2), "ETH": (1,1,1), "BNB": (1,1,1),
    "SOL": (2,1,1), "XRP": (1,1,2), "ADA": (1,1,1),
    "AVAX":(1,1,1), "DOGE":(2,1,2), "LTC": (1,1,1),
    "LINK":(1,1,1),
}


def layout():
    return html.Div([
        html.Div([
            html.H1("Predicción ARIMA", className="page-title"),
            html.P("Modelo ARIMA con intervalos de confianza, "
                   "diagnósticos y métricas de error en validación",
                   className="page-sub"),
        ], className="page-head"),

        # controles
        dbc.Row([
            dbc.Col([
                html.Label("Criptomoneda", style=_lbl()),
                dcc.Dropdown(
                    id="ar-sym",
                    options=[{"label": s, "value": s} for s in COINS],
                    value="BTC", clearable=False,
                    style={"fontFamily": MONO},
                ),
            ], md=3),
            dbc.Col([
                html.Label("Días de entrenamiento", style=_lbl()),
                dcc.Slider(id="ar-train", min=90, max=730, step=30, value=365,
                           marks={90:"90d", 365:"1a", 730:"2a"},
                           tooltip={"placement":"bottom","always_visible":True}),
            ], md=5),
            dbc.Col([
                html.Label("Horizonte (días)", style=_lbl()),
                dcc.Slider(id="ar-hor", min=7, max=60, step=7, value=14,
                           marks={7:"7d", 14:"14d", 30:"30d", 60:"60d"},
                           tooltip={"placement":"bottom","always_visible":True}),
            ], md=4),
        ], className="mb-4"),

        # resultados (se llenan via callback)
        html.Div(id="ar-summary"),

        html.Div("Pronóstico con intervalos de confianza", className="sec"),
        html.Div(id="ar-fgraph", className="gw"),

        html.Div("Métricas de validación (hold-out)", className="sec"),
        html.Div(id="ar-metrics"),

        html.Div("Diagnósticos del modelo", className="sec"),
        html.Div(id="ar-diag", className="gw"),

        html.Div("Interpretación", className="sec"),
        html.Div(id="ar-interp"),

    ], className="main", style={"paddingTop": "80px"})


# ── callback ─────────────────────────────────────────────────────────────────

@callback(
    Output("ar-summary", "children"),
    Output("ar-fgraph",  "children"),
    Output("ar-metrics", "children"),
    Output("ar-diag",    "children"),
    Output("ar-interp",  "children"),
    Input("ar-sym",     "value"),
    Input("ar-train",   "value"),
    Input("ar-hor",     "value"),
    Input("theme-store","data"),
)
def run(sym, train_days, horizon, theme):
    dark = (theme == "dark")
    df   = fetch_histoday(sym, days=train_days + 30)

    if df.empty or len(df) < 60:
        msg = dbc.Alert("Datos insuficientes para entrenar ARIMA.", color="warning")
        return msg, msg, msg, msg, msg

    try:
        res = _fit(df, sym, train_days, horizon)
    except Exception as exc:
        msg = dbc.Alert(f"Error en ARIMA: {exc}", color="danger")
        return msg, msg, msg, msg, msg

    summary  = _build_summary(res, sym)
    fgraph   = dcc.Graph(figure=_fig_forecast(res, sym, dark),
                         config={"displayModeBar": False})
    metrics  = _build_metrics(res)
    diag     = dcc.Graph(figure=_fig_diag(res, dark),
                         config={"displayModeBar": False})
    interp   = _build_interp(res, sym)

    return summary, fgraph, metrics, diag, interp


# ── núcleo ARIMA ──────────────────────────────────────────────────────────────

def _fit(df, sym, train_days, horizon):
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.stats.diagnostic import acorr_ljungbox

    prices = df["close"].values.astype(float)
    dates  = df["date"].values

    val_size  = min(30, max(10, len(prices) // 10))
    te        = len(prices) - val_size
    tr_p      = prices[:te]
    vl_p      = prices[te:]
    vl_d      = dates[te:]

    order  = _ORDERS.get(sym, (1, 1, 1))
    model  = ARIMA(tr_p, order=order)
    fitted = model.fit()

    # validación
    vl_fc = fitted.forecast(steps=val_size)
    mae   = float(np.mean(np.abs(vl_fc - vl_p)))
    rmse  = float(np.sqrt(np.mean((vl_fc - vl_p) ** 2)))
    denom = np.abs(vl_p)
    denom[denom < 1e-9] = 1e-9
    mape  = float(np.mean(np.abs((vl_fc - vl_p) / denom)) * 100)

    # pronóstico futuro
    fc   = fitted.get_forecast(steps=horizon)
    fc_m = fc.predicted_mean
    ci95 = np.asarray(fc.conf_int(alpha=0.05))
    ci80 = np.asarray(fc.conf_int(alpha=0.20))

    last_date = pd.to_datetime(dates[-1])
    fc_dates  = pd.date_range(last_date + pd.Timedelta(days=1),
                               periods=horizon, freq="D")

    # residuos
    resid = fitted.resid

    # Ljung-Box
    try:
        lb   = acorr_ljungbox(resid, lags=[10], return_df=True)
        lb_p = float(lb["lb_pvalue"].iloc[0])
    except Exception:
        lb_p = float("nan")

    return {
        "order"      : order,
        "aic"        : float(fitted.aic),
        "bic"        : float(fitted.bic),
        "tr_dates"   : dates[:te],
        "tr_prices"  : tr_p,
        "vl_dates"   : vl_d,
        "vl_prices"  : vl_p,
        "vl_fc"      : vl_fc,
        "fc_dates"   : fc_dates,
        "fc_mean"    : fc_m,
        "fc_lo95"    : ci95[:, 0],
        "fc_hi95"    : ci95[:, 1],
        "fc_lo80"    : ci80[:, 0],
        "fc_hi80"    : ci80[:, 1],
        "resid"      : resid,
        "fitted_vals": fitted.fittedvalues,
        "mae"        : mae,
        "rmse"       : rmse,
        "mape"       : mape,
        "lb_p"       : lb_p,
        "cur_price"  : float(prices[-1]),
        "fc_end"     : float(fc_m[-1]),
        "horizon"    : horizon,
    }


# ── figuras ───────────────────────────────────────────────────────────────────

def _fig_forecast(r, sym, dark):
    bg, pp, grid, txt, tdim = _tc(dark)
    acc = _acc(dark)
    up  = _up(dark)
    dn  = _dn(dark)
    fc_color = up if r["fc_end"] >= r["cur_price"] else dn

    n_show = min(180, len(r["tr_dates"]))
    fig = go.Figure()

    # histórico reciente
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(r["tr_dates"][-n_show:]),
        y=r["tr_prices"][-n_show:],
        mode="lines", name="Histórico",
        line=dict(color=tdim, width=1.2),
    ))

    # validación real vs ARIMA
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(r["vl_dates"]),
        y=r["vl_prices"],
        mode="lines", name="Real (validación)",
        line=dict(color=txt, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(r["vl_dates"]),
        y=r["vl_fc"],
        mode="lines", name="ARIMA (validación)",
        line=dict(color=acc, width=1.5, dash="dot"),
    ))

    # IC 95%
    fig.add_trace(go.Scatter(
        x=list(r["fc_dates"]) + list(reversed(list(r["fc_dates"]))),
        y=list(r["fc_hi95"])  + list(reversed(list(r["fc_lo95"]))),
        fill="toself", fillcolor=_hex_alpha(acc, 0.1),
        line=dict(color="rgba(0,0,0,0)"),
        name="IC 95%", hoverinfo="skip",
    ))

    # IC 80%
    fig.add_trace(go.Scatter(
        x=list(r["fc_dates"]) + list(reversed(list(r["fc_dates"]))),
        y=list(r["fc_hi80"])  + list(reversed(list(r["fc_lo80"]))),
        fill="toself", fillcolor=_hex_alpha(acc, 0.18),
        line=dict(color="rgba(0,0,0,0)"),
        name="IC 80%", hoverinfo="skip",
    ))

    # pronóstico central
    fig.add_trace(go.Scatter(
        x=r["fc_dates"], y=r["fc_mean"],
        mode="lines+markers",
        name=f"Pronóstico {r['horizon']}d",
        line=dict(color=fc_color, width=2),
        marker=dict(size=4, color=fc_color),
    ))

    # línea vertical de inicio del pronóstico
    fig.add_vline(x=str(r["fc_dates"][0]),
                  line_dash="dot", line_color=tdim, line_width=1)

    fig.update_layout(
        height=420, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=9),
        title=dict(
            text=f"{sym}/USD · ARIMA{r['order']} · Pronóstico {r['horizon']} días",
            font=dict(color=txt, size=12),
        ),
        margin=dict(t=48, b=24, l=60, r=20),
        hovermode="x unified",
        legend=dict(font=dict(color=tdim, size=8), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=grid, zeroline=False, linecolor=grid,
                   tickfont=dict(color=tdim, size=8)),
        yaxis=dict(gridcolor=grid, zeroline=False, tickprefix="$",
                   tickformat=",", tickfont=dict(color=tdim, size=8)),
    )
    return fig


def _fig_diag(r, dark):
    """4 paneles: residuos, ACF, PACF, QQ-plot."""
    bg, pp, grid, txt, tdim = _tc(dark)
    acc   = _acc(dark)
    resid = pd.Series(r["resid"]).dropna()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Residuos en el tiempo", "ACF",
                        "PACF", "QQ-Plot"],
    )

    # residuos
    fig.add_trace(go.Scatter(
        x=list(range(len(resid))), y=resid.values,
        mode="lines", line=dict(color=acc, width=0.8),
        name="Residuos",
    ), row=1, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color=tdim,
                  line_width=1, row=1, col=1)

    # ACF
    nlags = min(40, len(resid) // 3)
    cb    = 1.96 / np.sqrt(len(resid))
    acf_v = [float(resid.autocorr(lag=i)) for i in range(1, nlags + 1)]
    fig.add_trace(go.Bar(
        x=list(range(1, nlags + 1)), y=acf_v,
        marker_color=acc, marker_line_width=0, opacity=0.75, name="ACF",
    ), row=1, col=2)
    fig.add_hline(y=cb,  line_dash="dot", line_color=tdim,
                  line_width=1, row=1, col=2)
    fig.add_hline(y=-cb, line_dash="dot", line_color=tdim,
                  line_width=1, row=1, col=2)

    # PACF
    try:
        from statsmodels.tsa.stattools import pacf as _pacf
        pv = _pacf(resid, nlags=nlags, method="ywm")
        pacf_v = list(pv[1:])
    except Exception:
        pacf_v = [0.0] * nlags
    fig.add_trace(go.Bar(
        x=list(range(1, nlags + 1)), y=pacf_v,
        marker_color=_up(dark), marker_line_width=0,
        opacity=0.75, name="PACF",
    ), row=2, col=1)
    fig.add_hline(y=cb,  line_dash="dot", line_color=tdim,
                  line_width=1, row=2, col=1)
    fig.add_hline(y=-cb, line_dash="dot", line_color=tdim,
                  line_width=1, row=2, col=1)

    # QQ-plot manual (sin matplotlib)
    n = len(resid)
    empirical = np.sort(resid.values)
    theoric   = np.array([
        float(np.percentile(
            np.random.default_rng(42).standard_normal(10000),
            (i / (n + 1)) * 100
        ))
        for i in range(1, n + 1)
    ])
    # línea de referencia
    q25_e = np.percentile(empirical, 25)
    q75_e = np.percentile(empirical, 75)
    q25_t = np.percentile(theoric,  25)
    q75_t = np.percentile(theoric,  75)
    slope = (q75_e - q25_e) / max(q75_t - q25_t, 1e-9)
    inter = q25_e - slope * q25_t
    xr    = np.array([theoric.min(), theoric.max()])
    yr    = slope * xr + inter

    fig.add_trace(go.Scatter(
        x=theoric, y=empirical, mode="markers",
        marker=dict(color=acc, size=3, opacity=0.55),
        name="Quantiles",
    ), row=2, col=2)
    fig.add_trace(go.Scatter(
        x=xr, y=yr, mode="lines",
        line=dict(color=_dn(dark), width=1.5, dash="dot"),
        name="Referencia",
    ), row=2, col=2)

    fig.update_layout(
        height=440, paper_bgcolor=pp, plot_bgcolor=bg,
        font=dict(family=MONO, color=txt, size=8),
        title=dict(text="Diagnósticos ARIMA",
                   font=dict(color=txt, size=11)),
        margin=dict(t=60, b=20, l=42, r=16),
        showlegend=False,
    )
    for r2 in [1, 2]:
        for c in [1, 2]:
            fig.update_xaxes(row=r2, col=c,
                             gridcolor=grid, zeroline=False,
                             linecolor=grid,
                             tickfont=dict(color=tdim, size=7))
            fig.update_yaxes(row=r2, col=c,
                             gridcolor=grid, zeroline=False,
                             linecolor=grid,
                             tickfont=dict(color=tdim, size=7))
    for ann in fig.layout.annotations:
        ann.font.color = tdim
        ann.font.size  = 9
    return fig


# ── widgets de texto ──────────────────────────────────────────────────────────

def _build_summary(r, sym):
    cp  = r["cur_price"]
    fp2 = r["fc_end"]
    chg = (fp2 / cp - 1) * 100
    sgn = "+" if chg >= 0 else ""
    cls = "up" if chg >= 0 else "down"
    arr = "↑" if chg >= 0 else "↓"

    def fp(p):
        return f"${p:,.2f}" if p >= 1 else f"${p:.6f}"

    return dbc.Row([
        _kpi(fp(cp),                  f"{sym} Precio actual",    "accent"),
        _kpi(fp(fp2),                 f"Pronóstico +{r['horizon']}d", cls),
        _kpi(f"{arr} {sgn}{chg:.1f}%","Variación esperada",      cls),
        _kpi(f"ARIMA{r['order']}",    f"AIC={r['aic']:.1f}",     "accent"),
    ], className="mb-3")


def _build_metrics(r):
    def fmtp(p):
        return f"${p:,.2f}" if p >= 1 else f"${p:.6f}"

    lb_ok  = not np.isnan(r["lb_p"]) and r["lb_p"] > 0.05
    lb_txt = (f"p={r['lb_p']:.4f} → "
              f"{'Residuos independientes ✓' if lb_ok else 'Posible autocorrelación residual'}")

    def row(nombre, val, desc):
        return html.Tr([
            html.Td(nombre, className="mono",
                    style={"padding":"9px 12px","fontSize":".80rem"}),
            html.Td(val, className="mono",
                    style={"padding":"9px 12px","fontSize":".80rem",
                           "color":"var(--accent)","fontWeight":"600"}),
            html.Td(desc, style={"fontFamily":MONO,"fontSize":".78rem",
                                 "padding":"9px 12px","color":"var(--ink-mid)"}),
        ])

    return dbc.Card([
        dbc.CardHeader("Métricas de error — validación hold-out"),
        dbc.CardBody([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Métrica"), html.Th("Valor"), html.Th("Descripción")
                ])),
                html.Tbody([
                    row("MAE",       fmtp(r["mae"]),
                        "Error absoluto medio en USD"),
                    row("RMSE",      fmtp(r["rmse"]),
                        "Raíz del error cuadrático medio"),
                    row("MAPE",      f"{r['mape']:.2f}%",
                        "Error porcentual absoluto medio"),
                    row("Ljung-Box", f"{r['lb_p']:.4f}" if not np.isnan(r["lb_p"]) else "N/A",
                        lb_txt),
                    row("AIC",       f"{r['aic']:.2f}",
                        "Criterio Akaike — menor es mejor"),
                    row("BIC",       f"{r['bic']:.2f}",
                        "Criterio Bayesiano — menor es mejor"),
                ]),
            ], className="tbl"),
        ]),
    ], className="mb-3")


def _build_interp(r, sym):
    chg   = (r["fc_end"] / r["cur_price"] - 1) * 100
    sign  = "+" if chg >= 0 else ""
    cls   = "cup" if chg >= 0 else "cdn"
    dir_  = "alcista 📈" if chg >= 0 else "bajista 📉"
    mapeq = "buena" if r["mape"] < 5 else ("aceptable" if r["mape"] < 15 else "moderada")
    lb_ok = not np.isnan(r["lb_p"]) and r["lb_p"] > 0.05

    return dbc.Card([
        dbc.CardHeader("Interpretación"),
        dbc.CardBody([
            html.P([
                "El modelo ", html.Strong(f"ARIMA{r['order']}"),
                f" proyecta una tendencia ",
                html.Strong(dir_, className=cls),
                f" para {sym} en los próximos ",
                html.Strong(f"{r['horizon']} días"),
                ", con un cambio esperado de ",
                html.Strong(f"{sign}{chg:.1f}%", className=cls),
                " respecto al precio actual.",
            ], style={"fontSize":".92rem","lineHeight":"1.8"}),
            html.P([
                "La precisión en validación es ",
                html.Strong(mapeq),
                f" (MAPE = {r['mape']:.1f}%). Los residuos ",
                html.Strong(
                    "son estadísticamente independientes" if lb_ok
                    else "muestran estructura residual"
                ),
                f" según el test de Ljung-Box (p={r['lb_p']:.4f}).",
            ], style={"fontSize":".92rem","lineHeight":"1.8"}),
            html.Div(
                "⚠️ ARIMA modela la estructura temporal de la serie histórica. "
                "No incorpora noticias, eventos externos ni sentimiento de mercado. "
                "Este pronóstico es orientativo y no constituye asesoramiento financiero.",
                className="info mt-2",
                style={"fontSize":".82rem"}
            ),
        ]),
    ], className="mb-3")


# ── helpers ───────────────────────────────────────────────────────────────────

def _kpi(val, lbl, cls):
    return dbc.Col(html.Div([
        html.Div(val, className="kpi-val"),
        html.Div(lbl, className="kpi-lbl"),
    ], className=f"kpi {cls}"), md=3)


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


def _lbl():
    return {"fontFamily": MONO, "fontSize": ".63rem", "textTransform": "uppercase",
            "letterSpacing": ".08em", "color": "var(--ink-dim)",
            "marginBottom": "6px", "display": "block"}
