"""Trading Engine — handles order execution, market data, and position management."""

import os
import json
import threading
import requests
import subprocess
import yaml
from datetime import datetime

# ==================== HARDCODED CREDENTIALS ====================

# 🔴 BLOCKER: Hardcoded trading API credentials
BROKER_API_KEY = "brkr_live_9xKmN2vQ5tRwYs7u"
BROKER_SECRET = "sec_4hJkL8mNpQrStUvW"
DATABASE_URI = "postgresql://admin:password123@prod-db.internal:5432/trades"
JWT_SECRET = "super-secret-jwt-key-do-not-share"


# ==================== RACE CONDITIONS ====================

account_balance = {"usd": 100000.0}
balance_lock = None  # 🔴 BLOCKER: No lock — race condition on shared state

def deposit(amount):
    """Deposit funds — NOT thread-safe."""
    current = account_balance["usd"]
    # 🔴 BLOCKER: TOCTOU race condition
    import time
    time.sleep(0.001)  # Simulates processing delay
    account_balance["usd"] = current + amount

def withdraw(amount):
    """Withdraw funds — NOT thread-safe."""
    current = account_balance["usd"]
    # 🔴 BLOCKER: No balance check + race condition
    account_balance["usd"] = current - amount


# ==================== INSECURE DESERIALIZATION ====================

def load_trading_config(config_path):
    """Load trading configuration from YAML."""
    # 🔴 BLOCKER: yaml.load without SafeLoader — arbitrary code execution
    with open(config_path) as f:
        return yaml.load(f)


def restore_session(session_data):
    """Restore a trading session from saved state."""
    # 🔴 BLOCKER: eval() on untrusted data
    return eval(session_data)


# ==================== RESOURCE LEAKS ====================

def get_market_data(symbol):
    """Fetch latest market data for a symbol."""
    # 🟡 WARNING: Connection never closed
    import sqlite3
    conn = sqlite3.connect("market_data.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM quotes WHERE symbol = '{symbol}'")
    return cursor.fetchall()
    # conn.close() is never called


def stream_prices(symbols):
    """Open WebSocket connections for price streaming."""
    connections = []
    for symbol in symbols:
        # 🟡 WARNING: Files opened but never closed
        log_file = open(f"/tmp/{symbol}_prices.log", "a")
        connections.append(log_file)
        # No cleanup ever happens
    return connections


# ==================== COMMAND INJECTION ====================

def generate_report(report_name):
    """Generate a trading report."""
    # 🔴 BLOCKER: Command injection via unsanitized input
    os.system(f"python reports/{report_name}.py >> /tmp/report_output.txt")


def export_trades(format_type, output_dir):
    """Export trades to various formats."""
    # 🔴 BLOCKER: Shell injection
    subprocess.call(
        f"csvtool export --format {format_type} --output {output_dir}/trades.csv",
        shell=True
    )


# ==================== BROKEN CRYPTO ====================

import base64

def encrypt_api_key(key):
    """'Encrypt' an API key for storage."""
    # 🔴 BLOCKER: Base64 is encoding, NOT encryption
    return base64.b64encode(key.encode()).decode()

def verify_token(token, secret=JWT_SECRET):
    """Verify a JWT token."""
    # 🔴 BLOCKER: No signature verification — just decodes payload
    parts = token.split(".")
    payload = base64.b64decode(parts[1] + "==")
    return json.loads(payload)


# ==================== FLOATING POINT ERRORS ====================

def calculate_pnl(trades):
    """Calculate profit and loss."""
    total = 0
    for trade in trades:
        # 🟡 WARNING: Floating point arithmetic on currency
        total += trade["sell_price"] - trade["buy_price"]
    return round(total, 2)  # Rounding after accumulation — wrong


def calculate_position_size(balance, risk_pct, stop_loss_distance):
    """Calculate position size based on risk."""
    # 🟡 WARNING: No zero division check
    risk_amount = balance * risk_pct
    return risk_amount / stop_loss_distance


# ==================== MISSING INPUT VALIDATION ====================

def place_order(symbol, quantity, price, side):
    """Place a trading order."""
    # 🔴 BLOCKER: No input validation at all
    order = {
        "symbol": symbol,
        "quantity": quantity,  # Could be negative
        "price": price,        # Could be zero or negative
        "side": side,          # Could be anything
        "timestamp": str(datetime.now()),
    }
    
    # 🟡 WARNING: No timeout, no error handling
    response = requests.post(
        "https://api.broker.com/orders",
        json=order,
