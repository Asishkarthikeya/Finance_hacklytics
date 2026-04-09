"""Portfolio Management API — handles user portfolios and trade execution."""

import os
import sqlite3
import pickle
import requests
import hashlib

# ==================== SECURITY BUGS ====================

# 🔴 BLOCKER: Hardcoded API keys
ALPHA_VANTAGE_KEY = "PKAJ82NZLX9W5Q3Y"
DB_PASSWORD = "admin123!"
SECRET_KEY = "sk-proj-8xKmN2vQ5tRwYs7uBcDf"

# 🔴 BLOCKER: Weak password hashing
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


# ==================== SQL INJECTION ====================

def get_user_portfolio(user_id):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    # 🔴 BLOCKER: SQL injection — user_id is not sanitized
    query = f"SELECT * FROM portfolios WHERE user_id = '{user_id}'"
    cursor.execute(query)
    results = cursor.fetchall()
    return results


def search_transactions(keyword):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    # 🔴 BLOCKER: Another SQL injection
    cursor.execute("SELECT * FROM transactions WHERE description LIKE '%" + keyword + "%'")
    return cursor.fetchall()


# ==================== PERFORMANCE ISSUES ====================

def get_all_portfolio_values():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    results = []
    for user in users:
        # 🟡 WARNING: N+1 query — DB call inside a loop
        cursor.execute(f"SELECT SUM(value) FROM holdings WHERE user_id = '{user[0]}'")
        total = cursor.fetchone()[0]
        
        # 🟡 WARNING: HTTP call without timeout
        response = requests.get(f"https://api.example.com/rates?key={ALPHA_VANTAGE_KEY}")
        rate = response.json().get("rate", 1.0)
        
        results.append({"user": user[0], "total": total * rate})
    
    return results


def calculate_risk_score(prices):
    # 🟡 WARNING: Unbounded loop — no exit condition if data is bad
    i = 0
    score = 0
    while prices[i] > 0:
        score += prices[i] * 0.01
        i += 1
    return score


# ==================== DANGEROUS APIs ====================

def load_user_settings(data):
    # 🔴 BLOCKER: Unsafe deserialization — arbitrary code execution
    return pickle.loads(data)


def execute_custom_formula(formula):
    # 🔴 BLOCKER: eval() — arbitrary code execution
    return eval(formula)


def run_analysis_script(script_name):
    # 🔴 BLOCKER: os.system() — command injection
    os.system(f"python scripts/{script_name}")


# ==================== MISSING ERROR HANDLING ====================

def fetch_stock_price(symbol):
    # 🟡 WARNING: No error handling, no timeout, no retry
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
    response = requests.get(url)
    data = response.json()
    return float(data["Global Quote"]["05. price"])


def calculate_returns(buy_price, sell_price):
    # 🟡 WARNING: Division by zero not handled
    return (sell_price - buy_price) / buy_price * 100
