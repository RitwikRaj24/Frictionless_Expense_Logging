import  sqlite3
import datetime
 
 
def init_db():
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        
        # Table 1: Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                date TEXT
            )
        """)

        # Table 2: Categories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                budget REAL,
                color TEXT,
                icon TEXT
            )
        """)

        # Check for defaults
        cursor.execute("SELECT count(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            defaults = [
                ("Work", 28000, "purpleAccent", "home_work"),
                ("Food", 15000, "orangeAccent", "fastfood"),
                ("Other", 5000, "greenAccent", "category"),
            ]
            cursor.executemany("INSERT INTO categories (name, budget, color, icon) VALUES (?, ?, ?, ?)", defaults)
            conn.commit()

        conn.commit()
        conn.close()
def get_categories():
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, budget, color, icon FROM categories")
        rows = cursor.fetchall()
        conn.close()
        cats = {}
        for r in rows:
            cats[r[0]] = {"budget": r[1], "color": r[2], "icon": r[3]}
        return cats

def add_to_db(amount, category):
            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
            current_date = datetime.datetime.now().strftime("%d/%m/%Y")
            cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", 
                       (amount, category, current_date))
            conn.commit()
            conn.close()
        
def get_data_for_ui():
            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
        
            cursor.execute("SELECT SUM(amount) FROM transactions")
            res = cursor.fetchone()[0]
            total_spent = res if res else 0

            cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
            raw_breakdown = cursor.fetchall()
            category_spent = {item[0]: item[1] for item in raw_breakdown}

            cursor.execute("SELECT category, amount, date FROM transactions ORDER BY id DESC")
            history_list = cursor.fetchall()

            conn.close()
            return total_spent, category_spent, history_list   
        