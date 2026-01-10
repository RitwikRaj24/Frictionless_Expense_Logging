import flet as ft
import sqlite3
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
APP_TITLE = "Frictionless Expense"
BG_MAIN = "#F5F7FA"  # Light Grey-Blue
PRIMARY_COLOR = "#4E48C8"  # Indigo/Purple

# ==========================================
# 2. DATABASE LAYER
# ==========================================
def get_db_connection():
    conn = sqlite3.connect("expenses.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                date TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY,
                limit_amount REAL
    )""")
    c.execute("SELECT count(*) FROM budget")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO budget (id, limit_amount) VALUES (1, 5000)")
    conn.commit()
    conn.close()

def save_transaction(category, amount):
    conn = get_db_connection()
    c = conn.cursor()
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)", 
              (category, amount, date))
    conn.commit()
    conn.close()

def get_recent_transactions():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 5")
    data = c.fetchall()
    conn.close()
    return data

def get_category_totals():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = c.fetchall()
    conn.close()
    return data 

def get_budget():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT limit_amount FROM budget WHERE id=1")
    res = c.fetchone()
    conn.close()
    return res[0] if res else 5000

def set_budget(new_limit):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE budget SET limit_amount = ? WHERE id=1", (new_limit,))
    conn.commit()
    conn.close()

# ==========================================
# 3. UI COMPONENTS
# ==========================================
def create_card(content):
    return ft.Container(
        content=content,
        bgcolor="white",
        padding=20,
        border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12)
    )

def create_category_button(text, icon, color, on_click_func):
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(icon, color="white", size=24),
                bgcolor=color,
                padding=15,
                border_radius=15,
                shape=ft.BoxShape.RECTANGLE,
            ),
            ft.Text(text, size=12, weight="bold", color=ft.Colors.BLACK54)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        on_click=on_click_func,
        data=text,
        ink=True,
        padding=5,
        border_radius=10
    )

# ==========================================
# 4. HOME VIEW
# ==========================================
def HomeView(page):
    state = {"current_amount": 0, "current_category": ""}
    
    amount_field = ft.TextField(
        label="Enter Amount",
        prefix=ft.Text("₹ "), # Universal syntax
        text_style=ft.TextStyle(size=20, weight="bold"),
        border_color="transparent",
        bgcolor=ft.Colors.GREY_100,
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10
    )

    history_column = ft.Column(spacing=10)

    def refresh_history():
        history_column.controls.clear()
        transactions = get_recent_transactions()
        if not transactions:
            history_column.controls.append(ft.Text("No transactions yet.", color="grey"))
        
        for t in transactions:
            history_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.RECEIPT_LONG, size=16, color="grey"),
                            ft.Text(t[1], weight="bold", color="black") 
                        ]),
                        ft.Text(f"-₹{t[2]}", color="red", weight="bold")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    bgcolor="white",
                    border_radius=10,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=2, color=ft.Colors.BLACK12)
                )
            )
        page.update()

    def quick_fill(e):
        amount_field.value = e.control.data
        amount_field.update()

    def save_transaction_action(e):
        save_transaction(state["current_category"], float(state["current_amount"]))
        amount_field.value = ""
        amount_field.update()
        confirm_dialog.open = False
        page.update()
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Saved!")))
        refresh_history()

    def handle_payment(e):
        user_amount = amount_field.value
        if not user_amount:
            amount_field.error_text = "Required"
            amount_field.update()
            return
        
        state["current_amount"] = user_amount
        state["current_category"] = e.control.data
        
        try: page.set_clipboard(user_amount)
        except: pass

        try: page.launch_url(f"upi://pay?am={user_amount}&cu=INR")
        except: pass
        
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()

    def open_settings(e):
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()

    def save_settings_action(e):
        try:
            set_budget(float(budget_input.value))
            settings_dialog.open = False
            page.update()
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Budget Updated!")))
        except: pass

    confirm_dialog = ft.AlertDialog(
        title=ft.Text("Payment Confirmation"),
        content=ft.Text("Did the payment complete successfully?"),
        actions=[
            ft.TextButton("Yes", on_click=save_transaction_action),
            ft.TextButton("No", on_click=lambda e: setattr(confirm_dialog, 'open', False) or page.update())
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    budget_input = ft.TextField(label="Monthly Budget", value=str(get_budget()), keyboard_type=ft.KeyboardType.NUMBER)
    settings_dialog = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Column([ft.Text("Set your monthly limit:"), budget_input], height=100),
        actions=[ft.TextButton("Save", on_click=save_settings_action)]
    )

    refresh_history()

    return ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Column([ft.Text("Good Evening,", color=ft.Colors.WHITE70, size=14), ft.Text("Student", color=ft.Colors.WHITE, size=24, weight="bold")]),
                ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=open_settings)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=400, height=120, bgcolor=PRIMARY_COLOR, padding=ft.padding.only(left=20, right=10, top=40, bottom=20),
            border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30)
        ),
        ft.Container(height=20),
        create_card(ft.Column([
            ft.Text("How much?", color="grey", size=12),
            amount_field,
            ft.Container(height=10),
            ft.Row([
                ft.Chip(label=ft.Text("+50"), on_click=quick_fill, data="50"),
                ft.Chip(label=ft.Text("+100"), on_click=quick_fill, data="100"),
                ft.Chip(label=ft.Text("+200"), on_click=quick_fill, data="200"),
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.MainAxisAlignment.CENTER)),
        ft.Container(height=20),
        ft.Row([
            create_category_button("Food", ft.Icons.FASTFOOD, ft.Colors.BLUE, handle_payment),
            create_category_button("Stationary", ft.Icons.EDIT, ft.Colors.ORANGE, handle_payment),
            create_category_button("Dorm", ft.Icons.BED, ft.Colors.PURPLE, handle_payment),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        ft.Container(height=30),
        ft.Container(content=ft.Column([ft.Text("Recent Transactions", weight="bold", size=16, color=PRIMARY_COLOR), history_column]), padding=20)
    ], scroll=ft.ScrollMode.AUTO)

# ==========================================
# 5. STATS VIEW (UNIVERSAL COMPATIBLE)
# ==========================================
class StatsView(ft.Container):
    def __init__(self):
        super().__init__()
        self.chart_container = ft.Column()
        self.content = ft.Column([
            ft.Text("Spending Analysis", size=24, weight="bold", color=PRIMARY_COLOR),
            ft.Container(height=20),
            self.chart_container,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.padding = 20
    
    def data(self):
        totals = get_category_totals()
        self.chart_container.controls.clear()
        
        if not totals:
            self.chart_container.controls.append(ft.Text("No data yet"))
            self.update()
            return

        # Find max for scaling bars
        max_val = max([x[1] for x in totals]) if totals else 1
        colors = [ft.Colors.BLUE, ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.GREEN]

        for i, (cat, amount) in enumerate(totals):
            bar_width = (amount / max_val) * 250 # Scale width relative to 250px
            if bar_width < 10: bar_width = 10 

            self.chart_container.controls.append(
                ft.Column([
                    ft.Row([ft.Text(cat, weight="bold"), ft.Text(f"₹{amount}")] , alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(
                        width=bar_width, 
                        height=20, 
                        bgcolor=colors[i % len(colors)], 
                        border_radius=5
                    ),
                    ft.Container(height=10)
                ])
            )
        self.update()

# ==========================================
# 6. MAIN APP LOGIC
# ==========================================
def main(page: ft.Page):
    page.title = APP_TITLE
    page.bgcolor = BG_MAIN
    page.padding = 0
    # page.window_width = 400 # Commented out for max compatibility
    # page.window_height = 800
    
    init_db()
    
    home_view = HomeView(page)
    stats_view = StatsView()
    
    def change_tab(e):
        page.controls.clear()
        if e.control.selected_index == 0:
            page.add(home_view)
        else:
            stats_view.data()
            page.add(stats_view)
        page.add(nav_bar)
        page.update()

    # Universal Nav Bar (Works on all versions)
    # If standard NavigationBar fails, we use this simple Row instead
    try:
        nav_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationDestination(icon=ft.Icons.PIE_CHART, label="Stats"),
            ],
            selected_index=0,
            on_change=change_tab,
            bgcolor=ft.Colors.WHITE,
            indicator_color=PRIMARY_COLOR,
        )
    except:
        # FALLBACK for really old versions
        nav_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.HOME, on_click=lambda e: change_tab(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 0})()})())),
                ft.IconButton(ft.Icons.PIE_CHART, on_click=lambda e: change_tab(type('obj', (object,), {'control': type('obj', (object,), {'selected_index': 1})()})()))
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            bgcolor="white", height=60
        )

    page.add(home_view)
    page.add(nav_bar)

if __name__ == "__main__":
    ft.app(target=main)