"""
data/fetch_data.py
Fuente única de datos para el dashboard.
- fetch_top_coins()       → top 30 por market cap
- fetch_histoday()        → OHLCV diario hasta 3 años
- fetch_multi()           → cierre diario de varias monedas (wide)
- fetch_global_stats()    → KPIs globales
- get_cached()            → versión cacheada de fetch_top_coins
Fallback sintético completamente independiente (no depende de red).
"""

import time
import hashlib
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

BASE_URL  = "https://min-api.cryptocompare.com/data"
HEADERS   = {"Accept": "application/json"}
CACHE_TTL = 300   # 5 minutos

_cache: dict = {}

TOP_10 = ["BTC", "ETH", "BNB", "SOL", "XRP",
          "ADA", "AVAX", "DOGE", "LTC", "LINK"]

_COINS_META = [
    ("BTC",  "Bitcoin",           95000, 1850e9),
    ("ETH",  "Ethereum",           3200,  385e9),
    ("USDT", "Tether",             1.00,  140e9),
    ("BNB",  "BNB",                 650,   95e9),
    ("SOL",  "Solana",              185,   87e9),
    ("XRP",  "XRP",                2.50,  143e9),
    ("USDC", "USD Coin",            1.00,   45e9),
    ("ADA",  "Cardano",             1.10,   39e9),
    ("AVAX", "Avalanche",            40,   17e9),
    ("DOGE", "Dogecoin",            0.38,   56e9),
    ("DOT",  "Polkadot",             10,    9e9),
    ("LINK", "Chainlink",            20,   12e9),
    ("MATIC","Polygon",             0.55,    5e9),
    ("LTC",  "Litecoin",             95,    7e9),
    ("SHIB", "Shiba Inu",       2.5e-5,   15e9),
    ("TRX",  "TRON",               0.24,   21e9),
    ("UNI",  "Uniswap",              12,    7e9),
    ("ATOM", "Cosmos",               10,    4e9),
    ("XMR",  "Monero",              165,    3e9),
    ("ETC",  "Ethereum Classic",     30,    4e9),
    ("FIL",  "Filecoin",              6,    3e9),
    ("HBAR", "Hedera",              0.12,    5e9),
    ("ICP",  "Internet Computer",    12,    5e9),
    ("VET",  "VeChain",            0.045,    4e9),
    ("ALGO", "Algorand",            0.22,    2e9),
    ("XLM",  "Stellar",             0.12,    3e9),
    ("NEAR", "NEAR Protocol",         6,    7e9),
    ("APT",  "Aptos",                12,    5e9),
    ("ARB",  "Arbitrum",            1.20,    5e9),
    ("OP",   "Optimism",            2.50,    3e9),
]

_BASE_PRICES = {s: p for s, _, p, _ in _COINS_META}


# ─────────────────────────────────────────────────────────────────────────────
# helpers internos
# ─────────────────────────────────────────────────────────────────────────────

def _sym_seed(symbol: str) -> int:
    """Semilla determinista única por símbolo via MD5."""
    return int(hashlib.md5(symbol.encode()).hexdigest(), 16) % (2 ** 31)


def _fmt_usd(v: float) -> str:
    if v >= 1e12: return f"${v / 1e12:.2f}T"
    if v >= 1e9:  return f"${v / 1e9:.2f}B"
    if v >= 1e6:  return f"${v / 1e6:.2f}M"
    return f"${v:,.4f}"


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot top coins
# ─────────────────────────────────────────────────────────────────────────────

def fetch_top_coins(limit: int = 30) -> pd.DataFrame:
    rows = []
    try:
        r = requests.get(
            f"{BASE_URL}/top/mktcapfull",
            params={"limit": min(limit, 100), "tsym": "USD", "page": 0},
            headers=HEADERS, timeout=10
        )
        r.raise_for_status()
        data = r.json()
        if data.get("Response") == "Success":
            for item in data.get("Data", []):
                coin = item.get("CoinInfo", {})
                raw  = item.get("RAW", {}).get("USD", {})
                if not raw:
                    continue
                rows.append({
                    "symbol"        : coin.get("Name", ""),
                    "name"          : coin.get("FullName", ""),
                    "price"         : float(raw.get("PRICE", 0)),
                    "market_cap"    : float(raw.get("MKTCAP", 0)),
                    "volume_24h"    : float(raw.get("VOLUME24HOURTO", 0)),
                    "change_pct_24h": float(raw.get("CHANGEPCT24HOUR", 0)),
                    "high_24h"      : float(raw.get("HIGH24HOUR", 0)),
                    "low_24h"       : float(raw.get("LOW24HOUR", 0)),
                    "open_24h"      : float(raw.get("OPEN24HOUR", 0)),
                    "supply"        : float(raw.get("SUPPLY", 0)),
                })
    except Exception:
        pass

    if rows:
        return pd.DataFrame(rows).head(limit)
    return _synth_top_coins(limit)


def get_cached(limit: int = 30) -> pd.DataFrame:
    key = f"snap_{limit}"
    now = time.time()
    if key in _cache and (now - _cache[key]["ts"]) < CACHE_TTL:
        return _cache[key]["data"]
    df = fetch_top_coins(limit)
    _cache[key] = {"ts": now, "data": df}
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Histórico diario OHLCV
# ─────────────────────────────────────────────────────────────────────────────

def fetch_histoday(symbol: str = "BTC", days: int = 365) -> pd.DataFrame:
    """
    Retorna DataFrame con columnas: date, open, high, low, close, volume
    Soporta hasta 2000 días (~5.5 años) en una sola petición.
    Fallback automático a datos sintéticos si la API falla.
    """
    key = f"hist_{symbol}_{days}"
    now = time.time()
    ttl = CACHE_TTL * 12  # caché de 1 hora para histórico
    if key in _cache and (now - _cache[key]["ts"]) < ttl:
        return _cache[key]["data"]

    df = None
    try:
        r = requests.get(
            f"{BASE_URL}/v2/histoday",
            params={"fsym": symbol, "tsym": "USD", "limit": min(days, 2000)},
            headers=HEADERS, timeout=15
        )
        r.raise_for_status()
        data = r.json()
        if data.get("Response") == "Success":
            entries = data.get("Data", {}).get("Data", [])
            if entries:
                tmp = pd.DataFrame(entries)
                tmp["date"] = pd.to_datetime(tmp["time"], unit="s")
                tmp = tmp.rename(columns={"volumeto": "volume"})
                cols = ["date", "open", "high", "low", "close", "volume"]
                tmp = tmp[[c for c in cols if c in tmp.columns]]
                tmp = tmp[tmp["close"] > 0].sort_values("date").reset_index(drop=True)
                if len(tmp) > 10:
                    df = tmp
    except Exception:
        pass

    if df is None:
        df = _synth_histoday(symbol, days)

    _cache[key] = {"ts": now, "data": df}
    return df


def fetch_multi(symbols: list = None, days: int = 1095) -> pd.DataFrame:
    """
    DataFrame wide: columnas = date + cada símbolo (precio cierre).
    Garantiza que no haya NaN usando interpolación lineal.
    """
    if symbols is None:
        symbols = TOP_10

    frames = {}
    for sym in symbols:
        df = fetch_histoday(sym, days=days)
        if not df.empty and "close" in df.columns:
            s = df.set_index("date")["close"].replace(0, np.nan)
            frames[sym] = s

    if not frames:
        return pd.DataFrame()

    combined = pd.DataFrame(frames)
    combined = combined.interpolate(method="linear").dropna()
    combined.index.name = "date"
    return combined.reset_index()


def fetch_global_stats() -> dict:
    df = get_cached(30)
    if df.empty:
        return {}
    total = df["market_cap"].sum()
    btc   = df.loc[df["symbol"] == "BTC", "market_cap"].sum()
    eth   = df.loc[df["symbol"] == "ETH", "market_cap"].sum()
    return {
        "total_market_cap"  : total,
        "btc_dominance"     : (btc / total * 100) if total else 0,
        "eth_dominance"     : (eth / total * 100) if total else 0,
        "total_volume_24h"  : df["volume_24h"].sum(),
        "avg_change_pct_24h": df["change_pct_24h"].mean(),
        "coins_tracked"     : len(df),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fallback sintético
# ─────────────────────────────────────────────────────────────────────────────

def _synth_top_coins(limit: int = 30) -> pd.DataFrame:
    rows = []
    for sym, name, base_price, base_mcap in _COINS_META[:limit]:
        rng   = np.random.default_rng(_sym_seed(sym) + int(time.time() // 300))
        noise = rng.uniform(0.93, 1.07)
        price = base_price * noise
        chg   = rng.uniform(-10, 10)
        rows.append({
            "symbol"        : sym,
            "name"          : name,
            "price"         : price,
            "market_cap"    : base_mcap * noise,
            "volume_24h"    : base_mcap * rng.uniform(0.02, 0.18),
            "change_pct_24h": chg,
            "high_24h"      : price * rng.uniform(1.01, 1.06),
            "low_24h"       : price * rng.uniform(0.94, 0.99),
            "open_24h"      : price * (1 - chg / 100),
            "supply"        : base_mcap / max(price, 1e-9),
        })
    return pd.DataFrame(rows)


def _synth_histoday(symbol: str, days: int) -> pd.DataFrame:
    """
    Caminata aleatoria realista. Cada símbolo tiene semilla única
    → series distintas → correlación no trivial.
    Incluye régimen bull/bear alternado cada ~180 días.
    """
    base  = _BASE_PRICES.get(symbol, 1.0)
    seed  = _sym_seed(symbol)
    rng   = np.random.default_rng(seed)
    drift = rng.uniform(-0.001, 0.0025)
    vol   = rng.uniform(0.018, 0.065)
    n     = days + 1

    # ciclos de mercado
    regime = np.sin(np.linspace(0, 4 * np.pi, n) +
                    rng.uniform(0, 2 * np.pi)) * 0.001

    returns = rng.normal(drift, vol, n) + regime

    # construir precios hacia atrás desde el precio actual
    prices = [base]
    for r in reversed(returns[1:]):
        prices.insert(0, max(prices[0] / (1 + r), base * 0.005))

    dates = [datetime.utcnow() - timedelta(days=days - i) for i in range(n)]

    opens  = [max(p * rng.uniform(0.985, 1.005),  1e-9) for p in prices]
    highs  = [max(p * rng.uniform(1.002, 1.055),  p)    for p in prices]
    lows   = [max(p * rng.uniform(0.945, 0.998),  1e-9) for p in prices]
    vols   = [abs(rng.normal(base * 8000, base * 2500))  for _  in prices]

    return pd.DataFrame({
        "date"  : dates,
        "open"  : opens,
        "high"  : highs,
        "low"   : lows,
        "close" : prices,
        "volume": vols,
    })
