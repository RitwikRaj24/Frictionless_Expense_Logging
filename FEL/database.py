import sqlite3
import datetime 
import calendar 
from config import DB_NAME, DEFAULT_BUDGET

def init_db(): 
    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor() 
    # Transaction table 
    cursor.execute()

