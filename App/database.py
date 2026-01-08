# Database logic (No UI)  

# The Foundation Files. These don't depend on anything else.

import sqlite3 
import datetime 
import calendar 
from config import DB_NAME, DEFAULT_BUDGET 

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS transactions (
                   id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   amount REAL,
                   category TEXT, 
                   date TEXT)
    """)

    # (self): PRIMARY KEY : unique identifier for every row 
    # (self): AUTOINCREMENT : database automatically assigns 1,2,3... 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
                   key TEXT PRIMARY KEY, 
                   value TEXT)
                   """)
    
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('budget', ?)", (DEFAULT_BUDGET,))
    # INSERT OR IGNORE : To stop the database from crashing if the row with "budget" already exists 
    
    conn.commit()
    conn.close() 

def get_budget():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key='budget'")
    # 
    val = cursor.fetchone()[0]
    conn.close() 
    return float(val)

def set_budget(new_budget):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()    
    cursor.execute("UPDATE settings SET value=? WHERE key='budget'", (str(new_budget),))
    conn.commit()
    conn.close() 

def add_to_db(amount, category):
    # Captures the exact moment the transaction is recorded 

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", (amount, category, current_date))
    # VALUES (?, ?, ?) acts as a Security Guard, instead of pasting the variables directly into the text 
    # which is dangerous and prone to being hacked, put '?' as placeholders
    # (amount, category, current_date) is the actual package of data, python safely hands this package 
    # to the database, carefully placing each item into their respective slots 
    conn.commit()
    conn.close()

def delete_transaction(id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()    

def get_recent_transactions():
    # For getting the recent history dashboard 

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount, date FROM transactions ORDER BY id DESC LIMIT 5")
    # ORDER BY id DESC LIMIT 5 will sort by id in descending order and limit results to 5
    rows = cursor.fetchall()
    conn.commit()
    conn.close() 
    return rows 

def get_dashboard_data(): 
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Total Spent 
    cursor.execute("SELECT SUM(amount) FROM transactions")
    result = cursor.fetchone()[0]
    total_spent = result if result else 0 

    # 2. Category Breakdown 
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    breakdown = cursor.fetchall()
    conn.close()

    # 3. Pacing Logic 
    current_budget = get_budget()
    today = datetime.date.today() 
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    time_passed_pct = today.day / days_in_month 
    budget_spent_pct = total_spent / current_budget

    # adding code for avoiding division by zero (for when the code refreshes at the start of the month)
    pacing_score = budget_spent_pct / time_passed_pct if time_passed_pct > 0 else 0 

    return total_spent, breakdown, pacing_score, budget_spent_pct, current_budget

