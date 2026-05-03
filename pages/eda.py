

import sys, os, warnings
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats as sp_stats
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "data"))
from fetch_data import fetch_histoday, fetch_multi, TOP_10

MONO  = "JetBrains Mono, monospace"
COINS = TOP_10


# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────

def layout():
    return html.Div([
        html.Div([
            html.H1("Análisis Exploratorio", className="page-title"),
            html.P("Selecciona una moneda y período para explorar su comportamiento: "
                   "precios, retornos, estacionariedad, descomposición y correlaciones.",
                   className="page-sub"),
        ], className="page-head"),

        # ── Controles ─────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Criptomoneda", style=_lbl()),
                        dcc.Dropdown(id="eda-sym",
                            options=[{"label": s, "value": s} for s in COINS],
                            value="BTC", clearable=False,
                            style={"fontFamily": MONO, "fontSize": ".85rem"}),
                    ], md=3),
                    dbc.Col([
                        html.Label("Período", style=_lbl()),
                        dcc.RadioItems(id="eda-per",
                            options=[{"label": "1 año", "value": 365},
                                     {"label": "2 años","value": 730},
                                     {"label": "3 años","value": 1095}],
                            value=1095, inline=True,
                            inputStyle={"marginRight":"5px","cursor":"pointer"},
                            labelStyle={"marginRight":"18px","fontSize":".85rem",
                                        "color":"var(--ink-mid)","cursor":"pointer"}),
                    ], md=4),
                    dbc.Col([
                        html.Label("SMA principal", style=_lbl()),
                        dcc.Dropdown(id="eda-sma",
                            options=[{"label": f"SMA {d}", "value": d}
                                     for d in [7,14,30,50,100,200]],
                            value=30, clearable=False,
                            style={"fontFamily": MONO, "fontSize": ".85rem"}),
                    ], md=3),
                    dbc.Col([
                        html.Label("Descomposición", style=_lbl()),
                        dcc.RadioItems(id="eda-decomp",
                            options=[{"label": "Aditiva",       "value": "additive"},
                                     {"label": "Multiplicativa", "value": "multiplicative"}],
                            value="multiplicative", inline=True,
                            inputStyle={"marginRight":"5px","cursor":"pointer"},
                            labelStyle={"marginRight":"14px","fontSize":".84rem",
                                        "color":"var(--ink-mid)","cursor":"pointer"}),
                    ], md=2),
                ], align="center"),
            ], style={"padding":"14px 16px"}),
        ], className="mb-3"),

        html.Div(id="eda-kpis"),
        html.Div(id="eda-body"),

    ], className="main", style={"paddingTop":"80px"})


# ─────────────────────────────────────────────────────────────────────────────
# CALLBACK
# ─────────────────────────────────────────────────────────────────────────────

@callback(
    Output("eda-kpis", "children"),
    Output("eda-body", "children"),
    Input("eda-sym",    "value"),
    Input("eda-per",    "value"),
    Input("eda-sma",    "value"),
    Input("eda-decomp", "value"),
    Input("theme-store","data"),
)
def render(sym, days, sma, decomp, theme):
    dark    = (theme == "dark")
    df      = fetch_histoday(sym, days=days)
    df_wide = fetch_multi(COINS, days=days)
    return _build_kpis(df, sym), _build_body(df, df_wide, sym, sma, decomp, dark)


# ─────────────────────────────────────────────────────────────────────────────
# KPIs — manejo robusto de NaN
# ─────────────────────────────────────────────────────────────────────────────

def _build_kpis(df, sym):
    if df.empty or len(df) < 2:
        return dbc.Alert("Sin datos disponibles.", color="warning")
    try:
        close  = df["close"].replace(0, np.nan).dropna()
        p_now  = float(close.iloc[-1])
        p_ini  = float(close.iloc[0])
        rend   = (p_now / p_ini - 1) * 100 if p_ini else 0.0

        rets   = close.pct_change().dropna()
        v_ser  = rets.rolling(min(30, len(rets))).std() * np.sqrt(365) * 100
        vol30  = float(v_ser.dropna().iloc[-1]) if not v_ser.dropna().empty else float(rets.std() * np.sqrt(365) * 100)
        vol30  = 0.0 if np.isnan(vol30) else vol30

        rm     = close.cummax()
        mxd    = float(((close - rm) / rm * 100).min())
        mxd    = 0.0 if np.isnan(mxd) else mxd

        p_max  = float(df["high"].replace(0, np.nan).max())  if "high" in df else p_now
        p_min  = float(df["low"].replace(0, np.nan).min())   if "low"  in df else p_now
        p_max  = p_now if np.isnan(p_max) else p_max
        p_min  = p_now if np.isnan(p_min) else p_min
    except Exception:
        return dbc.Alert("Error calculando métricas.", color="danger")

    fp   = lambda p: f"${float(p):,.2f}" if float(p) >= 1 else f"${float(p):.6f}"
    sign = "+" if rend >= 0 else ""
    cls  = "up" if rend >= 0 else "down"

    return dbc.Row([
        _kpi(fp(p_now),            f"{sym} — Precio actual",      "accent"),
        _kpi(f"{sign}{rend:.1f}%", "Rendimiento del período",     cls),
        _kpi(f"{vol30:.1f}%",      "Volatilidad anualizada 30d",  "accent"),
        _kpi(f"{mxd:.1f}%",        "Máx. Drawdown",               "down"),
        _kpi(fp(p_max),            "Precio máximo del período",   "up"),
        _kpi(fp(p_min),            "Precio mínimo del período",   "down"),
    ], className="mb-3")


# ─────────────────────────────────────────────────────────────────────────────
# CUERPO
# ─────────────────────────────────────────────────────────────────────────────

def _build_body(df, df_wide, sym, sma, decomp, dark):
    return html.Div([

        # § 1 Velas + volumen
        _sec("📈 Serie de tiempo — Velas japonesas OHLC"),
        _nota("Las velas muestran el comportamiento diario: verde = precio cerró más alto "
              "que al abrir (día positivo), rojo = cerró más bajo (negativo). "
              "La mecha delgada marca el máximo y mínimo del día. "
              f"La SMA {sma} suaviza la tendencia. El volumen (parte inferior) indica actividad."),
        html.Div([dcc.Graph(figure=_fig_ohlc(df, sym, sma, dark),
                            config={"displayModeBar":False})], className="gw"),

        # § 2 Retornos acumulados
        _sec("📊 Retorno acumulado normalizado (base 100)"),
        _nota("Divide el precio de cada día entre el precio inicial y multiplica por 100. "
              "Todas las monedas empiezan en 100, permitiendo comparar quién creció más "
              "independientemente de su precio en dólares. La moneda seleccionada aparece resaltada."),
        html.Div([dcc.Graph(figure=_fig_retornos_acum(df_wide, sym, dark),
                            config={"displayModeBar":False})], className="gw"),

        # § 3 Distribución de retornos
        _sec("📉 Distribución de retornos diarios"),
        _nota("Histograma de los cambios % diarios con la distribución normal como referencia (línea roja). "
              "En cripto los retornos tienen 'colas más gruesas' que la normal: "
              "hay más días con cambios extremos de lo esperado. "
              "Esto se llama leptocurtosis y es característica típica de activos volátiles."),
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=_fig_ret_hist(df, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=_fig_vol(df, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=6),
        ]),

        # § 4 Estacionariedad — BOXPLOT POR TRIMESTRE
        _sec("⚖️ Estacionariedad — Boxplot por trimestre"),
        _nota("La forma más visual de entender la estacionariedad es comparar los boxplots "
              "por trimestre. Si los precios tienen CAJAS A DISTINTOS NIVELES → la media cambia "
              "con el tiempo → NO estacionaria (requiere diferenciar). "
              "Si los retornos tienen CAJAS AL MISMO NIVEL → media constante ≈ 0% → SÍ estacionaria."),
        dbc.Row([
            dbc.Col([
                html.Div([dcc.Graph(figure=_fig_estac_precios(df, sym, dark),
                                    config={"displayModeBar":False})], className="gw"),
                _nota_s("❌ PRECIOS — NO estacionarios",
                    "Las cajas están a diferentes alturas porque el nivel de precios "
                    "cambia con el tiempo (tendencia). ARIMA no puede usarse directamente: "
                    "requiere diferenciar la serie (d=1 en ARIMA)."),
            ], md=6),
            dbc.Col([
                html.Div([dcc.Graph(figure=_fig_estac_retornos(df, sym, dark),
                                    config={"displayModeBar":False})], className="gw"),
                _nota_s("✅ RETORNOS — SÍ estacionarios",
                    "Las cajas están aproximadamente al mismo nivel (media ≈ 0%). "
                    "La varianza puede variar (heteroscedasticidad), pero la media es estable. "
                    "Los retornos son el input adecuado para modelos estadísticos como ARIMA."),
            ], md=6),
        ]),

        # § 5 Descomposición aditiva / multiplicativa
        _sec(f"🔀 Descomposición {'Aditiva' if decomp=='additive' else 'Multiplicativa'} de la serie"),
        _nota(
            f"Modelo {'ADITIVO: Y = T + S + R' if decomp=='additive' else 'MULTIPLICATIVO: Y = T × S × R'}. "
            "La serie se separa en Tendencia (movimiento de largo plazo), "
            "Estacionalidad (ciclos repetitivos periódicos) y "
            "Residuo (componente irregular que no explican T ni S). "
            + ("Aplica cuando la amplitud de los ciclos es CONSTANTE." if decomp=="additive"
               else "Aplica cuando la amplitud de los ciclos CRECE con el nivel de la serie — "
                    "típico en criptomonedas cuyas oscilaciones son proporcionales al precio.")
        ),
        html.Div([dcc.Graph(figure=_fig_decomp(df, sym, decomp, dark),
                            config={"displayModeBar":False})], className="gw"),

        # § 6 Boxplot comparativo + correlación
        _sec("📦 Comparativa entre las 10 monedas"),
        _nota("Boxplot de retornos diarios (izquierda): cajas más altas = más volátiles. "
              "Heatmap de correlaciones (derecha): verde = se mueven juntas, rojo = al revés. "
              "En cripto la mayoría tiene correlación alta porque siguen el ciclo de Bitcoin."),
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=_fig_box(df_wide, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=5),
            dbc.Col(html.Div([dcc.Graph(figure=_fig_corr(df_wide, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=7),
        ]),

        # § 7 Scatter + volumen
        _sec("🔗 Correlación de retornos y actividad de mercado"),
        _nota("Scatter (izquierda): cada punto es un día; si los puntos forman diagonal → alta correlación. "
              "La línea punteada es la regresión lineal y el valor r cuantifica la relación. "
              "Volumen (derecha): barras verdes = días alcistas, rojas = bajistas. "
              "La línea punteada es la media móvil de volumen (MA 20)."),
        dbc.Row([
            dbc.Col(html.Div([dcc.Graph(figure=_fig_scat(df_wide, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=6),
            dbc.Col(html.Div([dcc.Graph(figure=_fig_volumen(df, sym, dark),
                                        config={"displayModeBar":False})], className="gw"), md=6),
        ]),

        # § 8 Pruebas estadísticas
        _sec("🧪 Pruebas estadísticas formales"),
        _nota("Cuantifican formalmente lo que los gráficos muestran visualmente. "
              "Confirman si la serie es estacionaria, si los retornos son normales "
              "y si los residuos son ruido blanco (útil para validar ARIMA)."),
        _build_stats(df, sym),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# FIGURAS
# ─────────────────────────────────────────────────────────────────────────────

def _fig_ohlc(df, sym, sma, dark):
    if df.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    df = df.copy()
    df[f"sma{sma}"] = df["close"].rolling(sma).mean()
    df["sma7"]      = df["close"].rolling(7).mean()
    fig = make_subplots(rows=2,cols=1,shared_xaxes=True,
                        row_heights=[0.75,0.25],vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(
        x=df["date"],open=df["open"],high=df["high"],
        low=df["low"],close=df["close"],
        increasing_line_color=_up(dark),increasing_fillcolor=_up(dark),
        decreasing_line_color=_dn(dark),decreasing_fillcolor=_dn(dark),
        name=sym,line=dict(width=1)), row=1,col=1)
    fig.add_trace(go.Scatter(x=df["date"],y=df["sma7"],
        line=dict(color=tdim,width=1,dash="dot"),name="SMA 7",opacity=0.8),row=1,col=1)
    fig.add_trace(go.Scatter(x=df["date"],y=df[f"sma{sma}"],
        line=dict(color=_acc(dark),width=1.5),name=f"SMA {sma}"),row=1,col=1)
    bc = [_up(dark) if c>=o else _dn(dark) for c,o in zip(df["close"],df["open"])]
    fig.add_trace(go.Bar(x=df["date"],y=df["volume"],
        marker_color=bc,marker_line_width=0,opacity=0.55,name="Volumen"),row=2,col=1)
    fig.update_layout(height=440,paper_bgcolor=pp,plot_bgcolor=bg,
        font=dict(family=MONO,color=txt,size=9),
        title=dict(text=f"{sym}/USD · OHLC + SMA {sma} + Volumen",font=dict(color=txt,size=12)),
        margin=dict(t=48,b=20,l=52,r=16),xaxis_rangeslider_visible=False,
        hovermode="x unified",legend=dict(font=dict(color=tdim,size=8),bgcolor="rgba(0,0,0,0)"))
    for r in [1,2]:
        fig.update_xaxes(row=r,gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8))
        fig.update_yaxes(row=r,gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8))
    fig.update_yaxes(row=1,tickprefix="$",tickformat=",")
    return fig


def _fig_retornos_acum(df_wide, selected, dark):
    if df_wide.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    cols = [c for c in df_wide.columns if c != "date"]
    fig  = go.Figure()
    for sym in cols:
        s = df_wide[sym].replace(0,np.nan).dropna()
        if s.empty or float(s.iloc[0]) == 0: continue
        norm  = s / s.iloc[0] * 100
        color = _acc(dark) if sym==selected else tdim
        w     = 2.0  if sym==selected else 0.7
        op    = 1.0  if sym==selected else 0.35
        fig.add_trace(go.Scatter(x=df_wide["date"].iloc[:len(norm)],y=norm.values,
            mode="lines",name=sym,line=dict(color=color,width=w),opacity=op))
    fig.add_hline(y=100,line_dash="dot",line_color=tdim,line_width=1)
    _dl(fig,f"Retorno acumulado (base 100) — {selected} resaltado",bg,pp,grid,txt,tdim,320)
    fig.update_layout(hovermode="x unified",yaxis=dict(ticksuffix="%"))
    return fig


def _fig_ret_hist(df, sym, dark):
    if df.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    rets = df["close"].replace(0,np.nan).pct_change().dropna()*100
    if rets.empty: return _empty(dark)
    mu,sig = float(rets.mean()),float(rets.std())
    xn = np.linspace(float(rets.min()),float(rets.max()),200)
    yn = sp_stats.norm.pdf(xn,mu,sig)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=rets,nbinsx=55,marker_color=_acc(dark),
        marker_line_width=0,opacity=0.72,histnorm="probability density",name="Retornos"))
    fig.add_trace(go.Scatter(x=xn,y=yn,mode="lines",
        line=dict(color=_dn(dark),width=1.5,dash="dot"),name="Normal"))
    fig.add_vline(x=0,line_dash="dot",line_color=tdim,line_width=1)
    if not np.isnan(mu):
        fig.add_vline(x=mu,line_dash="dash",line_color=_acc(dark),line_width=1,
            annotation_text=f"μ={mu:.2f}%",annotation_font_size=8,annotation_font_color=tdim)
    _dl(fig,f"Distribución retornos diarios — {sym}",bg,pp,grid,txt,tdim,290)
    fig.update_layout(showlegend=True,xaxis=dict(ticksuffix="%"))
    return fig


def _fig_vol(df, sym, dark):
    if df.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    df2 = df.copy()
    df2["v30"] = df2["close"].pct_change().rolling(30).std()*np.sqrt(365)*100
    df2["v7"]  = df2["close"].pct_change().rolling(7).std() *np.sqrt(365)*100
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df2["date"],y=df2["v30"],mode="lines",name="Vol 30d",
        line=dict(color=_acc(dark),width=1.8),fill="tozeroy",fillcolor=_acc(dark)+"15"))
    fig.add_trace(go.Scatter(x=df2["date"],y=df2["v7"],mode="lines",name="Vol 7d",
        line=dict(color=_dn(dark),width=1,dash="dot"),opacity=0.7))
    _dl(fig,f"Volatilidad rodante anualizada — {sym}",bg,pp,grid,txt,tdim,290)
    fig.update_layout(hovermode="x unified",yaxis=dict(ticksuffix="%"))
    return fig


def _fig_estac_precios(df, sym, dark):
    """Boxplot PRECIOS por trimestre → muestra NO estacionariedad."""
    if df.empty or len(df) < 60: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    df2 = df.copy()
    df2["date"]     = pd.to_datetime(df2["date"])
    df2["trim"]     = df2["date"].dt.to_period("Q").astype(str)
    trims           = sorted(df2["trim"].unique())[-8:]
    df2             = df2[df2["trim"].isin(trims)]
    fig = go.Figure()
    for trim in trims:
        sub = df2[df2["trim"]==trim]["close"].replace(0,np.nan).dropna()
        if sub.empty: continue
        fig.add_trace(go.Box(y=sub.values,name=trim,
            marker_color=_acc(dark),line=dict(color=_acc(dark),width=1.2),
            fillcolor=_acc(dark)+"28",boxpoints=False))
    _dl(fig,f"PRECIOS por trimestre — {sym}  (❌ NO estacionario)",bg,pp,grid,txt,tdim,320)
    fig.update_layout(showlegend=False,
        yaxis=dict(tickprefix="$",tickformat=","),
        xaxis=dict(tickangle=-30,tickfont=dict(size=8,color=tdim)))
    fig.add_annotation(text="Cajas a distintas alturas → media cambia → NO estacionario",
        xref="paper",yref="paper",x=0.5,y=1.07,showarrow=False,
        font=dict(size=8,color=tdim,family=MONO))
    return fig


def _fig_estac_retornos(df, sym, dark):
    """Boxplot RETORNOS por trimestre → muestra estacionariedad."""
    if df.empty or len(df) < 60: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    df2 = df.copy()
    df2["date"]    = pd.to_datetime(df2["date"])
    df2["retorno"] = df2["close"].pct_change()*100
    df2["trim"]    = df2["date"].dt.to_period("Q").astype(str)
    trims          = sorted(df2["trim"].unique())[-8:]
    df2            = df2[df2["trim"].isin(trims)].dropna(subset=["retorno"])
    fig = go.Figure()
    for trim in trims:
        sub = df2[df2["trim"]==trim]["retorno"].dropna()
        if sub.empty: continue
        fig.add_trace(go.Box(y=sub.values,name=trim,
            marker_color=_up(dark),line=dict(color=_up(dark),width=1.2),
            fillcolor=_up(dark)+"28",boxpoints=False))
    _dl(fig,f"RETORNOS por trimestre — {sym}  (✅ SÍ estacionario)",bg,pp,grid,txt,tdim,320)
    fig.update_layout(showlegend=False,
        yaxis=dict(ticksuffix="%"),
        xaxis=dict(tickangle=-30,tickfont=dict(size=8,color=tdim)))
    fig.add_hline(y=0,line_dash="dot",line_color=tdim,line_width=1)
    fig.add_annotation(text="Cajas al mismo nivel → media ≈ 0 % → SÍ estacionario",
        xref="paper",yref="paper",x=0.5,y=1.07,showarrow=False,
        font=dict(size=8,color=tdim,family=MONO))
    return fig


def _fig_decomp(df, sym, decomp, dark):
    """Descomposición STL aditiva o multiplicativa en 4 subplots."""
    if df.empty or len(df) < 60: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        serie  = df.set_index("date")["close"].replace(0,np.nan).dropna()
        period = 30   # ciclo mensual aproximado
        if len(serie) < 2 * period:
            period = max(7, len(serie) // 4)
        result = seasonal_decompose(serie, model=decomp, period=period, extrapolate_trend="freq")
    except Exception as e:
        return _empty(dark)

    labels = ["Serie original","Tendencia","Estacionalidad","Residuo"]
    datos  = [serie, result.trend, result.seasonal, result.resid]
    colors = [_acc(dark), _up(dark), "#fbbf24", _dn(dark)]
    fills  = [None, None, None, "tozeroy"]

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=labels, vertical_spacing=0.06)
    for i,(dat,col,fill) in enumerate(zip(datos,colors,fills),1):
        kw = dict(fill=fill,fillcolor=col+"18") if fill else {}
        fig.add_trace(go.Scatter(x=dat.index,y=dat.values,mode="lines",
            line=dict(color=col,width=1.4),name=labels[i-1],**kw), row=i,col=1)

    fig.update_layout(height=560,paper_bgcolor=pp,plot_bgcolor=bg,
        font=dict(family=MONO,color=txt,size=9),
        title=dict(text=f"Descomposición {'Aditiva' if decomp=='additive' else 'Multiplicativa'} — {sym}  "
                        f"({'Y=T+S+R' if decomp=='additive' else 'Y=T×S×R'})",
                   font=dict(color=txt,size=12)),
        margin=dict(t=52,b=24,l=52,r=16),showlegend=False)
    for r in range(1,5):
        fig.update_xaxes(row=r,gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8))
        fig.update_yaxes(row=r,gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8))
    for ann in fig.layout.annotations:
        ann.font.color = tdim
        ann.font.size  = 9
    return fig


def _fig_box(df_wide, selected, dark):
    if df_wide.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    cols = [c for c in df_wide.columns if c != "date"]
    fig  = go.Figure()
    for sym in cols:
        rets  = df_wide[sym].pct_change().dropna()*100
        color = _acc(dark) if sym==selected else tdim
        fig.add_trace(go.Box(y=rets,name=sym,marker_color=color,marker_size=3,
            line=dict(width=1,color=color),fillcolor=color+"22",boxpoints="outliers"))
    _dl(fig,"Distribución retornos — 10 monedas",bg,pp,grid,txt,tdim,320)
    fig.update_layout(showlegend=False,yaxis=dict(ticksuffix="%"))
    return fig


def _fig_corr(df_wide, selected, dark):
    if df_wide.empty or len(df_wide.columns) < 3: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    num = df_wide.drop(columns=["date"],errors="ignore")
    if num.shape[0] < 5: return _empty(dark)
    corr = num.corr().round(2)
    cs   = [[0.0,_dn(dark)],[0.5,pp],[1.0,_acc(dark)]]
    fig  = px.imshow(corr,text_auto=True,color_continuous_scale=cs,zmin=-1,zmax=1)
    fig.update_traces(textfont=dict(size=9,family=MONO))
    _dl(fig,"Correlación Pearson (r) — precios de cierre",bg,pp,grid,txt,tdim,380)
    fig.update_layout(
        xaxis=dict(showgrid=False,tickfont=dict(color=txt,size=9)),
        yaxis=dict(showgrid=False,tickfont=dict(color=txt,size=9)),
        coloraxis_colorbar=dict(tickfont=dict(color=tdim,size=8),
            title=dict(text="r",font=dict(color=tdim,size=9)),thickness=10))
    return fig


def _fig_scat(df_wide, selected, dark):
    if df_wide.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    cols = [c for c in df_wide.columns if c != "date"]
    ref  = "BTC" if selected != "BTC" else "ETH"
    if ref not in cols or selected not in cols: return _empty(dark)
    r1 = df_wide[ref].pct_change().dropna()*100
    r2 = df_wide[selected].pct_change().dropna()*100
    n  = min(len(r1),len(r2))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r1.values[:n],y=r2.values[:n],mode="markers",
        marker=dict(color=_acc(dark),size=3,opacity=0.5,line=dict(width=0)),
        name=f"{ref} vs {selected}"))
    if n > 5:
        m,b  = np.polyfit(r1.values[:n],r2.values[:n],1)
        cv   = float(np.corrcoef(r1.values[:n],r2.values[:n])[0,1])
        xl   = np.linspace(float(r1.min()),float(r1.max()),60)
        fig.add_trace(go.Scatter(x=xl,y=m*xl+b,mode="lines",
            line=dict(color=_dn(dark),width=1.5,dash="dot"),name=f"r = {cv:.2f}"))
    _dl(fig,f"Retornos diarios: {ref} vs {selected}",bg,pp,grid,txt,tdim,300)
    fig.update_layout(xaxis=dict(title=f"{ref} ret %",ticksuffix="%"),
                      yaxis=dict(title=f"{selected} ret %",ticksuffix="%"))
    return fig


def _fig_volumen(df, sym, dark):
    if df.empty: return _empty(dark)
    bg,pp,grid,txt,tdim = _tc(dark)
    df2    = df.copy().tail(120)
    colors = [_up(dark) if c>=o else _dn(dark)
              for c,o in zip(df2["close"],df2["open"])]
    fig = go.Figure(go.Bar(x=df2["date"],y=df2["volume"],
        marker_color=colors,marker_line_width=0,opacity=0.72,name="Volumen"))
    df2["vol_ma"] = df2["volume"].rolling(20).mean()
    fig.add_trace(go.Scatter(x=df2["date"],y=df2["vol_ma"],mode="lines",
        line=dict(color=_acc(dark),width=1.5,dash="dot"),name="MA 20"))
    _dl(fig,f"Volumen diario — {sym} (últimos 120 días)",bg,pp,grid,txt,tdim,280)
    fig.update_layout(hovermode="x unified",
        legend=dict(font=dict(color=tdim,size=8),bgcolor="rgba(0,0,0,0)"))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# PRUEBAS ESTADÍSTICAS
# ─────────────────────────────────────────────────────────────────────────────

def _build_stats(df, sym):
    if df.empty or len(df) < 30:
        return dbc.Alert("Datos insuficientes para pruebas.", color="warning")
    rets = df["close"].replace(0,np.nan).pct_change().dropna()*100
    # ADF
    try:
        from statsmodels.tsa.stattools import adfuller
        ap  = adfuller(df["close"].dropna(),autolag="AIC")
        ar  = adfuller(rets.dropna(),autolag="AIC")
        aps,apv = float(ap[1]),f"{ap[0]:.4f}"
        ars,arv = float(ar[1]),f"{ar[0]:.4f}"
    except Exception:
        aps,ars = 1.0,0.0; apv=arv="N/A"
    # Curtosis y asimetría
    try:
        kurt = float(rets.kurtosis()); skew = float(rets.skew())
        kurt = 0.0 if np.isnan(kurt) else kurt
        skew = 0.0 if np.isnan(skew) else skew
    except Exception:
        kurt=skew=0.0
    # Jarque-Bera
    try:
        jb_s,jb_p = sp_stats.jarque_bera(rets.dropna())
        jb_s,jb_p = float(jb_s),float(jb_p)
    except Exception:
        jb_s,jb_p=0.0,1.0

    def row(nombre,stat,interp,ok=True):
        return html.Tr([
            html.Td(nombre,className="mono",style={"fontSize":".80rem","padding":"9px 12px","color":"var(--ink)"}),
            html.Td(stat,className="mono",style={"fontSize":".80rem","padding":"9px 12px","color":"var(--accent)","fontWeight":"600"}),
            html.Td(html.Span(interp,className="cup" if ok else "cdn"),
                    style={"fontFamily":MONO,"fontSize":".78rem","padding":"9px 12px"}),
        ])

    rows = [
        row("ADF — Precios",  apv,
            f"p={aps:.4f} → {'❌ NO estacionaria (esperado en precios)' if aps>0.05 else '✓ Estacionaria'}",
            ok=aps>0.05),
        row("ADF — Retornos", arv,
            f"p={ars:.4f} → {'✅ Estacionaria (esperado en retornos)' if ars<=0.05 else '⚠️ No estacionaria'}",
            ok=ars<=0.05),
        row("Curtosis",  f"{kurt:.3f}",
            "Leptocúrtica: colas gruesas → más eventos extremos que la normal" if kurt>3 else "Mesocúrtica",
            ok=True),
        row("Asimetría", f"{skew:.3f}",
            "Sesgo negativo: caídas extremas más frecuentes" if skew<-.5
            else ("Sesgo positivo: subidas extremas más frecuentes" if skew>.5 else "Aproximadamente simétrica"),
            ok=True),
        row("Jarque-Bera (normalidad)", f"{jb_s:.1f}",
            f"p={jb_p:.4f} → {'✅ Retornos NO normales — colas gruesas (esperado en cripto)' if jb_p<.05 else 'Posible normalidad'}",
            ok=True),
    ]

    return dbc.Card([
        dbc.CardHeader(f"Pruebas estadísticas formales — {sym}"),
        dbc.CardBody([
            html.Table([
                html.Thead(html.Tr([html.Th("Prueba"),html.Th("Estadístico"),html.Th("Interpretación")])),
                html.Tbody(rows),
            ], className="tbl"),
            html.P("ADF: p > 0.05 en precios confirma no estacionariedad (normal). "
                   "p ≤ 0.05 en retornos confirma estacionariedad (necesario para ARIMA). "
                   "Jarque-Bera p < 0.05 → colas más gruesas que la distribución normal.",
                   style={"fontFamily":MONO,"fontSize":".71rem","color":"var(--ink-dim)",
                          "lineHeight":"1.6","marginTop":"10px","marginBottom":"0"}),
        ])
    ], className="mb-3")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _sec(texto):
    return html.Div([
        html.H5(texto,style={"fontFamily":"Syne,sans-serif","fontWeight":"600",
                              "fontSize":".95rem","color":"var(--ink)",
                              "marginBottom":"6px","marginTop":"8px"}),
        html.Hr(style={"borderColor":"var(--rule)","margin":"0 0 10px 0"}),
    ])


def _nota(texto):
    return html.P(texto,style={"color":"var(--ink-mid)","fontSize":".87rem",
                                "lineHeight":"1.65","marginBottom":"10px",
                                "padding":"10px 14px","background":"var(--bg-subtle)",
                                "borderRadius":"6px","borderLeft":"3px solid var(--accent)"})


def _nota_s(titulo, texto):
    return html.Div([
        html.Strong(titulo+" — ",style={"color":"var(--accent)","fontSize":".80rem"}),
        html.Span(texto,style={"color":"var(--ink-dim)","fontSize":".80rem"}),
    ],style={"padding":"7px 12px","marginBottom":"14px","background":"var(--bg-subtle)",
              "borderRadius":"5px","border":"1px solid var(--rule)"})


def _dl(fig,title,bg,pp,grid,txt,tdim,h=360):
    fig.update_layout(height=h,paper_bgcolor=pp,plot_bgcolor=bg,
        font=dict(family=MONO,color=txt,size=9),
        title=dict(text=title,font=dict(color=txt,size=11)),
        margin=dict(t=44,b=24,l=50,r=16),
        legend=dict(font=dict(color=tdim,size=8),bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8)),
        yaxis=dict(gridcolor=grid,zeroline=False,linecolor=grid,tickfont=dict(color=tdim,size=8)))


def _kpi(val,lbl,cls):
    return dbc.Col(html.Div([
        html.Div(val,className="kpi-val"),
        html.Div(lbl,className="kpi-lbl"),
    ],className=f"kpi {cls}"),md=2)


def _tc(dark):
    if dark: return "#0c0c0e","#0c0c0e","#2a2a2e","#f0f0ee","#55554e"
    return "#ffffff","#ffffff","#f2f1ee","#1a1a18","#a09d96"


def _acc(dark): return "#5a7aec" if dark else "#1a46c4"
def _up(dark):  return "#4ade80" if dark else "#166534"
def _dn(dark):  return "#f87171" if dark else "#991b1b"

def _rgba(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return hex_color
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.2f})"


def _lbl():
    return {"fontFamily":MONO,"fontSize":".63rem","textTransform":"uppercase",
            "letterSpacing":".08em","color":"var(--ink-dim)","marginBottom":"6px","display":"block"}


def _empty(dark):
    bg,pp = _tc(dark)[:2]
    fig = go.Figure()
    fig.add_annotation(text="Sin datos disponibles",xref="paper",yref="paper",
        x=0.5,y=0.5,showarrow=False,font=dict(color="#a09d96",size=13,family=MONO))
    fig.update_layout(paper_bgcolor=pp,plot_bgcolor=bg,
        height=260,margin=dict(t=30,b=20,l=20,r=20))
    return fig