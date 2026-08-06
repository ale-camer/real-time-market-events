from datetime import UTC, datetime


def normalize_symbol(symbol: str, asset_class: str) -> str:
    """
    Standardizes the format of a market symbol based on its asset class.

    Args:
        symbol: The raw symbol (e.g., 'btcusdt', 'AAPL', 'EURUSD')
        asset_class: The asset class ('crypto', 'stocks', 'forex')

    Returns:
        A standardized, uppercase symbol (e.g., 'BTC-USDT', 'AAPL', 'EUR-USD').
    """
    symbol = symbol.strip().upper()

    if asset_class == "crypto":
        # Basic heuristic to separate base and quote currencies if unseparated
        # e.g., BTCUSDT -> BTC-USDT
        for quote in ["USDT", "USD", "EUR", "BTC", "ETH"]:
            if symbol.endswith(quote) and len(symbol) > len(quote) and "-" not in symbol:
                base = symbol[: -len(quote)]
                return f"{base}-{quote}"
        return symbol

    elif asset_class == "forex":
        # Forex pairs are typically 6 characters (e.g., EURUSD)
        if len(symbol) == 6 and "-" not in symbol:
            return f"{symbol[:3]}-{symbol[3:]}"
        return symbol

    # Stocks and other defaults just return uppercase (already done at the start)
    return symbol


def normalize_timestamp(ts: float) -> str:
    """
    Converts a UNIX timestamp into a standardized ISO 8601 UTC string.

    Args:
        ts: UNIX timestamp (seconds since epoch)

    Returns:
        ISO 8601 formatted datetime string with UTC timezone indicator (Z).
    """
    dt = datetime.fromtimestamp(ts, tz=UTC)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
