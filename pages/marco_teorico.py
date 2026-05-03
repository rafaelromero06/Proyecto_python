import os, sys
from dash import html
import dash_bootstrap_components as dbc

MONO = "JetBrains Mono, monospace"

VARIABLES = [
    ("price",          "Cuantitativa continua", "Precio actual en USD",                        "USD",     "Descriptiva"),
    ("market_cap",     "Cuantitativa continua", "Precio × unidades en circulación",            "USD",     "Descriptiva"),
    ("volume_24h",     "Cuantitativa continua", "Valor total transaccionado en 24 h",          "USD",     "Predictora"),
    ("change_pct_24h", "Cuantitativa continua", "Variación % del precio en 24 h",             "%",       "Predictora"),
    ("high_24h",       "Cuantitativa continua", "Precio máximo en las últimas 24 h",           "USD",     "Indicador técnico"),
    ("low_24h",        "Cuantitativa continua", "Precio mínimo en las últimas 24 h",           "USD",     "Indicador técnico"),
    ("close",          "Cuantitativa continua", "Precio de cierre diario",                     "USD",     "Target ARIMA"),
    ("retorno_diario", "Cuantitativa continua", "(P_t/P_{t-1} − 1) × 100",                    "%",       "Feature derivada"),
    ("sma_7",          "Cuantitativa continua", "Media simple de los últimos 7 cierres",       "USD",     "Indicador técnico"),
    ("sma_30",         "Cuantitativa continua", "Media simple de los últimos 30 cierres",      "USD",     "Indicador técnico"),
    ("vol_anual_30d",  "Cuantitativa continua", "σ_diaria × √365 con ventana 30 días",        "% anual", "Feature derivada"),
    ("tendencia",      "Cuantitativa continua", "Componente de largo plazo (STL)",             "USD",     "Descomposición"),
    ("estacionalidad", "Cuantitativa continua", "Componente periódico (STL)",                  "USD / %", "Descomposición"),
    ("residuo",        "Cuantitativa continua", "Componente irregular tras T y S",             "USD / %", "Descomposición"),
    ("fc_arima",       "Cuantitativa continua", "Precio pronosticado por ARIMA(p,d,q)",       "USD",     "Variable objetivo"),
]


def layout():
    return html.Div([

        html.Div([
            html.H1("Marco Teórico", className="page-title"),
            html.P("Conceptos fundamentales que sustentan el análisis de criptomonedas "
                   "como serie temporal.", className="page-sub"),
        ], className="page-head"),

        html.Div(
            "Cada concepto se explica de forma simple y directa, mostrando "
            "cómo aplica específicamente a este proyecto.",
            className="info mb-3", style={"fontSize": ".88rem"}
        ),

        # ── § 1 Mercado Cripto ────────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("₿  Conceptos del Mercado Cripto"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(_c("Blockchain", "₿",
                        "Red descentralizada de bloques encadenados que garantiza la integridad "
                        "de las transacciones sin intermediarios. Cada bloque contiene el hash del "
                        "anterior, haciendo imposible alterar el historial sin rehacerlo todo."), md=4),
                    dbc.Col(_c("Market Cap", "📊",
                        "Market Cap = Precio × Unidades en circulación. "
                        "Es el 'tamaño' total de una criptomoneda. "
                        "BTC tiene el mayor market cap y su movimiento arrastra al resto del mercado."), md=4),
                    dbc.Col(_c("Dominancia BTC", "👑",
                        "Porcentaje del mercado total que corresponde a Bitcoin. "
                        "Dominancia alta (>50 %) → mercado conservador. "
                        "Dominancia baja → las altcoins están ganando terreno (alt-season)."), md=4),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(_c("OHLCV", "🕯️",
                        "Open, High, Low, Close, Volume: los cinco datos que describen "
                        "el comportamiento de un activo en un período. Base de todo análisis técnico "
                        "y de las velas japonesas que se usan en este dashboard."), md=4),
                    dbc.Col(_c("Volatilidad", "📉",
                        "Dispersión de los retornos respecto a su media. "
                        "Fórmula: σ_anual = σ_diaria × √365. "
                        "BTC ≈ 60–80 % anual frente al 15–20 % de acciones tradicionales."), md=4),
                    dbc.Col(_c("Liquidez", "💧",
                        "Facilidad de comprar/vender sin mover el precio. "
                        "Se mide como Volumen / Market Cap. "
                        "Alta liquidez = puedes vender grandes cantidades sin hundir el precio."), md=4),
                ]),
            ])
        ], className="mb-3"),

        # ── § 2 Series Temporales y Estacionariedad ───────────────────────
        dbc.Card([
            dbc.CardHeader("📈  Series Temporales y Estacionariedad"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        _c("Serie de tiempo", "📅",
                           "Secuencia de observaciones de una variable en intervalos regulares. "
                           "En este proyecto: precio de cierre diario de cada criptomoneda. "
                           "El análisis busca tendencias, ciclos y patrones repetitivos."),
                        _c("Retornos diarios", "↩️",
                           "r_t = (P_t / P_{t-1} − 1) × 100. "
                           "Transforman los precios en cambios porcentuales, "
                           "eliminan la tendencia y acercan la serie a la estacionariedad."),
                    ], md=6),
                    dbc.Col([
                        html.Div([
                            html.H6("⚖️ Estacionariedad — concepto clave",
                                    style={"color":"var(--accent)","marginBottom":"10px"}),
                            html.P("Una serie es estacionaria si su media, varianza y "
                                   "autocovarianza NO cambian con el tiempo. "
                                   "Requisito fundamental para ARIMA.",
                                   style={"fontSize":".86rem","color":"var(--ink-mid)",
                                          "lineHeight":"1.6","marginBottom":"10px"}),
                            html.Div([
                                html.Div([
                                    html.Strong("❌  PRECIOS → NO estacionarios",
                                                style={"color":"var(--down)","fontSize":".84rem"}),
                                    html.P("La media cambia con el tiempo (tendencia alcista de largo plazo). "
                                           "El nivel de precios de BTC hoy es muy distinto al de hace 3 años. "
                                           "No se puede modelar con ARIMA sin diferenciar.",
                                           style={"fontSize":".81rem","color":"var(--ink-mid)",
                                                  "marginBottom":"0","marginTop":"4px"}),
                                ], style={"background":"var(--down-bg)","borderRadius":"6px",
                                           "padding":"10px 13px","marginBottom":"8px",
                                           "border":"1px solid var(--down-b)"}),
                                html.Div([
                                    html.Strong("✅  RETORNOS → SÍ estacionarios",
                                                style={"color":"var(--up)","fontSize":".84rem"}),
                                    html.P("Los retornos diarios fluctúan alrededor de ≈ 0 % "
                                           "con varianza relativamente estable. "
                                           "Por eso ARIMA usa d=1 (diferencia los precios una vez).",
                                           style={"fontSize":".81rem","color":"var(--ink-mid)",
                                                  "marginBottom":"0","marginTop":"4px"}),
                                ], style={"background":"var(--up-bg)","borderRadius":"6px",
                                           "padding":"10px 13px",
                                           "border":"1px solid var(--up-b)"}),
                            ])
                        ], style={"background":"var(--bg-subtle)","borderRadius":"8px",
                                   "padding":"15px","border":"1px solid var(--rule)"})
                    ], md=6),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(_ind("SMA — Media Móvil Simple",
                                 "SMA_n = (P₁ + P₂ + … + Pₙ) / n",
                                 "Promedio del precio en n días. SMA7 reacciona rápido a cambios; "
                                 "SMA30 muestra la tendencia de medio plazo. "
                                 "Cruce SMA7 > SMA30 → señal alcista (golden cross)."), md=4),
                    dbc.Col(_ind("Volatilidad anualizada",
                                 "σ_anual = σ_diaria × √365",
                                 "Desviación estándar de retornos diarios escalada al año. "
                                 "Permite comparar el riesgo entre activos distintos "
                                 "en la misma unidad. BTC ≈ 60–80 % anual."), md=4),
                    dbc.Col(_ind("Rango H-L (volatilidad intradiaria)",
                                 "hl_pct = (High − Low) / Low × 100",
                                 "Amplitud de la oscilación de precio en un día. "
                                 "Un rango alto indica alta volatilidad ese día. "
                                 "Proxy simple y visual del riesgo diario."), md=4),
                ]),
            ])
        ], className="mb-3"),

        # ── § 3 Descomposición Aditiva vs Multiplicativa ──────────────────
        dbc.Card([
            dbc.CardHeader("🔀  Descomposición de Series: Aditiva vs Multiplicativa"),
            dbc.CardBody([
                html.P(
                    "Toda serie temporal puede separarse en tres componentes: "
                    "Tendencia (T), Estacionalidad (S) y Residuo (R). "
                    "La diferencia entre los modelos está en cómo interactúan estos componentes.",
                    style={"fontSize":".90rem","color":"var(--ink-mid)","lineHeight":"1.7",
                           "marginBottom":"16px"}
                ),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("➕ Modelo ADITIVO",
                                    style={"color":"var(--accent)","marginBottom":"10px",
                                           "fontFamily":"Syne,sans-serif"}),
                            html.Code("Y_t  =  T_t  +  S_t  +  R_t",
                                      style=_code_style()),
                            html.Div([
                                html.P("📌 ¿Cuándo usarlo?",
                                       style={"fontWeight":"600","color":"var(--ink)",
                                              "fontSize":".88rem","marginBottom":"6px"}),
                                html.Ul([html.Li(x) for x in [
                                    "La amplitud de la estacionalidad es CONSTANTE con el tiempo.",
                                    "Los picos y valles del ciclo siempre tienen un tamaño similar.",
                                    "El nivel de la serie no cambia drásticamente.",
                                    "Ejemplo: temperatura mensual de una ciudad.",
                                ]], style={"color":"var(--ink-mid)","fontSize":".84rem",
                                           "lineHeight":"1.7","marginBottom":"10px"}),
                                html.P("🔢 Interpretación:",
                                       style={"fontWeight":"600","color":"var(--ink)",
                                              "fontSize":".88rem","marginBottom":"6px"}),
                                html.P("Cada componente se suma directamente. "
                                       "Si la tendencia es $40 000, la estacionalidad +$2 000 "
                                       "y el residuo -$500, el precio es $41 500.",
                                       style={"color":"var(--ink-mid)","fontSize":".84rem",
                                              "lineHeight":"1.6","marginBottom":"0"}),
                            ], style={"marginTop":"12px"}),
                        ], style={"background":"var(--accent-lt)","borderRadius":"8px",
                                   "padding":"18px","border":"1px solid var(--rule)",
                                   "height":"100%"}),
                    ], md=6),

                    dbc.Col([
                        html.Div([
                            html.H5("✖️ Modelo MULTIPLICATIVO",
                                    style={"color":"var(--down)","marginBottom":"10px",
                                           "fontFamily":"Syne,sans-serif"}),
                            html.Code("Y_t  =  T_t  ×  S_t  ×  R_t",
                                      style=_code_style("#3a0808")),
                            html.Div([
                                html.P("📌 ¿Cuándo usarlo?",
                                       style={"fontWeight":"600","color":"var(--ink)",
                                              "fontSize":".88rem","marginBottom":"6px"}),
                                html.Ul([html.Li(x) for x in [
                                    "La amplitud de la estacionalidad CRECE con el nivel de la serie.",
                                    "Cuando el precio sube, los picos son proporcionalmente mayores.",
                                    "La serie tiene crecimiento exponencial.",
                                    "Ejemplo: precios de Bitcoin (oscilaciones % constantes).",
                                ]], style={"color":"var(--ink-mid)","fontSize":".84rem",
                                           "lineHeight":"1.7","marginBottom":"10px"}),
                                html.P("🔢 Interpretación:",
                                       style={"fontWeight":"600","color":"var(--ink)",
                                              "fontSize":".88rem","marginBottom":"6px"}),
                                html.P("Los componentes se multiplican. Si la tendencia es 1.0, "
                                       "la estacionalidad 1.05 y el residuo 0.98, "
                                       "el factor total es 1.029 (el precio sube ~2.9 % respecto a T).",
                                       style={"color":"var(--ink-mid)","fontSize":".84rem",
                                              "lineHeight":"1.6","marginBottom":"0"}),
                            ], style={"marginTop":"12px"}),
                        ], style={"background":"var(--down-bg)","borderRadius":"8px",
                                   "padding":"18px","border":"1px solid var(--down-b)",
                                   "height":"100%"}),
                    ], md=6),
                ], className="mb-3"),

                # Cuadro de decisión
                dbc.Card([
                    dbc.CardHeader("🤔 ¿Cuál aplicar a las criptomonedas?"),
                    dbc.CardBody([
                        html.P(
                            "En general, los precios de criptomonedas se comportan de forma "
                            "MULTIPLICATIVA porque sus variaciones se expresan naturalmente "
                            "en porcentajes (%, no en USD absolutos). "
                            "Cuando BTC pasa de $1 000 a $50 000, un ciclo del +5 % representa "
                            "$50 en el primer caso pero $2 500 en el segundo: la amplitud crece "
                            "con el nivel de la serie.",
                            style={"fontSize":".90rem","color":"var(--ink-mid)","lineHeight":"1.7",
                                   "marginBottom":"10px"}
                        ),
                        html.P(
                            "Sin embargo, si trabajamos con los RETORNOS LOGARÍTMICOS "
                            "(log(P_t / P_{t-1})), la serie se vuelve aditiva porque "
                            "log(T × S × R) = log(T) + log(S) + log(R). "
                            "Esto justifica aplicar modelos aditivos a los retornos y "
                            "multiplicativos a los precios originales.",
                            style={"fontSize":".90rem","color":"var(--ink-mid)",
                                   "lineHeight":"1.7","marginBottom":"0"}
                        ),
                    ])
                ]),
            ])
        ], className="mb-3"),

        # ── § 4 Pruebas estadísticas ──────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("🧪  Pruebas Estadísticas"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(_prueba("ADF — Augmented Dickey-Fuller",
                        "H₀: la serie tiene raíz unitaria (NO estacionaria)",
                        ["p > 0.05 → No rechazamos H₀ → NO estacionaria (típico en precios).",
                         "p ≤ 0.05 → Rechazamos H₀ → SÍ estacionaria (típico en retornos).",
                         "El parámetro d de ARIMA = veces que hay que diferenciar."]), md=6),
                    dbc.Col(_prueba("Jarque-Bera — Normalidad",
                        "H₀: los retornos siguen una distribución normal",
                        ["p < 0.05 → Retornos NO son normales (casi siempre en cripto).",
                         "Curtosis > 3 → colas gruesas (leptocurtosis).",
                         "Eventos extremos (+20%, -30%) ocurren más de lo que predice la normal."]), md=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col(_prueba("Ljung-Box — Independencia de residuos",
                        "H₀: los residuos del modelo ARIMA son ruido blanco",
                        ["p > 0.05 → Residuos independientes → modelo adecuado.",
                         "p ≤ 0.05 → Hay estructura residual → el modelo se puede mejorar.",
                         "Se aplica post-estimación como diagnóstico de calidad del ajuste."]), md=6),
                    dbc.Col(_prueba("Correlación de Pearson (r)",
                        "Mide la relación lineal entre dos series de retornos",
                        ["r = 1.0 → se mueven perfectamente juntas.",
                         "r = -1.0 → se mueven perfectamente al revés.",
                         "r ≈ 0 → sin relación. En cripto: mayoría tiene r 0.6–0.9 (siguen ciclo BTC)."]), md=6),
                ]),
            ])
        ], className="mb-3"),

        # ── § 5 ARIMA ─────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("🔮  Modelo ARIMA — Fundamentos"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col(_c("ARIMA(p, d, q)", "📐",
                        "AutoRegressive Integrated Moving Average. "
                        "p = lags autoregresivos (cuántos precios pasados usa). "
                        "d = diferenciaciones para lograr estacionariedad. "
                        "q = lags de media móvil (errores pasados). "
                        "En cripto típicamente d=1 porque los precios son I(1)."), md=4),
                    dbc.Col(_c("ACF y PACF", "📊",
                        "Autocorrelation Function y Partial ACF. "
                        "La ACF mide correlación con rezagos pasados. "
                        "La PACF controla los efectos indirectos. "
                        "Se usan para determinar q (ACF) y p (PACF) del modelo."), md=4),
                    dbc.Col(_c("AIC y BIC", "🎯",
                        "Criterios de información que miden calidad del modelo "
                        "penalizando la complejidad. "
                        "Menor valor = mejor balance ajuste/parsimonia. "
                        "Se comparan entre modelos ARIMA con distintos órdenes."), md=4),
                ])
            ])
        ], className="mb-3"),

        # ── § 6 Tabla de variables ────────────────────────────────────────
        dbc.Card([
            dbc.CardHeader("📋  Tabla de Operacionalización de Variables"),
            dbc.CardBody([
                html.P("Definición formal de cada variable: cómo se mide y su rol en el proyecto.",
                       style={"fontSize":".87rem","color":"var(--ink-mid)","marginBottom":"14px"}),
                html.Div([
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Variable"), html.Th("Tipo"),
                            html.Th("Definición operacional"),
                            html.Th("Unidad"), html.Th("Rol"),
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(html.Code(var, style={"color":"var(--accent)","fontSize":".77rem"})),
                                html.Td(tipo, style={"color":"var(--ink-mid)","fontSize":".79rem"}),
                                html.Td(defn, style={"color":"var(--ink-mid)","fontSize":".79rem"}),
                                html.Td(html.Code(unidad, style={"fontSize":".77rem"})),
                                html.Td(html.Span(rol, className=_pill(rol)),
                                        style={"whiteSpace":"nowrap"}),
                            ])
                            for var, tipo, defn, unidad, rol in VARIABLES
                        ])
                    ], className="tbl"),
                ], style={"overflowX":"auto"}),
            ])
        ]),

    ], className="main", style={"paddingTop":"80px"})


# ── helpers ───────────────────────────────────────────────────────────────────

def _c(titulo, emoji, texto):
    return html.Div([
        html.Div([html.Span(emoji, style={"fontSize":"1.2rem","marginRight":"7px"}),
                  html.Strong(titulo, style={"color":"var(--ink)","fontSize":".89rem"})],
                 style={"marginBottom":"7px"}),
        html.P(texto, style={"color":"var(--ink-mid)","fontSize":".83rem",
                              "lineHeight":"1.65","marginBottom":"0"}),
    ], style={"background":"var(--bg-subtle)","borderRadius":"8px","padding":"13px",
               "marginBottom":"11px","border":"1px solid var(--rule)"})


def _ind(titulo, formula, desc):
    return html.Div([
        html.Strong(titulo, style={"color":"var(--accent)","fontSize":".88rem",
                                    "display":"block","marginBottom":"6px"}),
        html.Code(formula, style={"display":"block","padding":"6px 10px",
                                   "background":"var(--bg-hover)","borderRadius":"5px",
                                   "fontSize":".77rem","color":"var(--accent)",
                                   "fontFamily":MONO,"marginBottom":"8px"}),
        html.P(desc, style={"color":"var(--ink-mid)","fontSize":".82rem",
                             "lineHeight":"1.6","marginBottom":"0"}),
    ], style={"background":"var(--bg-subtle)","borderRadius":"8px",
               "padding":"13px","border":"1px solid var(--rule)"})


def _prueba(titulo, hipotesis, puntos):
    return html.Div([
        html.Strong(titulo, style={"color":"var(--ink)","fontSize":".89rem",
                                    "display":"block","marginBottom":"5px"}),
        html.Em(hipotesis, style={"color":"var(--ink-mid)","fontSize":".81rem",
                                    "display":"block","marginBottom":"8px"}),
        html.Ul([html.Li(p, style={"color":"var(--ink-mid)","fontSize":".81rem",
                                    "lineHeight":"1.6","marginBottom":"3px"})
                 for p in puntos], style={"paddingLeft":"17px","marginBottom":"0"}),
    ], style={"background":"var(--bg-subtle)","borderRadius":"8px",
               "padding":"13px","border":"1px solid var(--rule)","height":"100%"})


def _code_style(bg="#1a2040"):
    return {"display":"block","padding":"8px 12px","background":bg,
            "borderRadius":"6px","fontSize":".82rem","color":"#93c8f0",
            "fontFamily":MONO,"marginBottom":"0","letterSpacing":".04em",
            "fontWeight":"600"}


def _pill(rol):
    rl = rol.lower()
    if "target" in rl: return "pill pill-d"
    if "descriptiva" in rl: return "pill pill-n"
    if "descomposición" in rl: return "pill pill-u"
    return "pill pill-a"