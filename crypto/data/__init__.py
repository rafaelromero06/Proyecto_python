# data/__init__.py
# Convierte /data en un paquete Python para importación modular desde app.py

from .fetch_data import (
    TOP_10,
    fetch_histoday,
    fetch_multi,
    fetch_global_stats,
    get_cached,
)

__all__ = [
    "TOP_10",
    "fetch_histoday",
    "fetch_multi",
    "fetch_global_stats",
    "get_cached",
]
