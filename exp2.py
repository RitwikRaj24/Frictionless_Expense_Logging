import flet as ft
import sqlite3
import datetime

def main(page: ft.Page):
    # --- 1. APP SETTINGS ---
    page.title = "IIT Dhanbad Expense Tracker"
    page.window_width = 400
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 0  # Remove default padding to allow full-screen views

    # --- 2. BACKEND & LOGIC ---

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

    init_db()

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
    
    # --- 3. UI STATE MANAGEMENT ---
    
    # We will swap between these two main containers
    home_view = ft.Container(visible=True)
    payment_view = ft.Container(visible=False)

    # --- 4. VIEW 1: HOME DASHBOARD ---

    # Components for Home
    header_section = ft.Container(
        padding=20,
        content=ft.Row(
            [
                ft.Column([
                    ft.Text("Hello,", size=16, color=ft.Colors.GREY_400),
                    ft.Text("Harsh Suri", size=28, weight="bold", color="white")
                ], spacing=2),
                ft.CircleAvatar(
                    foreground_image_src="E:\App\WIN_20251104_13_13_29_Pro.jpg",
                    radius=25
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    overview_container = ft.Column(scroll=ft.ScrollMode.HIDDEN)
    history_container = ft.Column(scroll=ft.ScrollMode.AUTO, visible=False)

    def toggle_home_tabs(view_name):
        if view_name == "overview":
            overview_container.visible = True
            history_container.visible = False
            btn_overview.bgcolor = "blue"
            btn_history.bgcolor = None
        else:
            overview_container.visible = False
            history_container.visible = True
            btn_overview.bgcolor = None
            btn_history.bgcolor = "blue"
        page.update()

    btn_overview = ft.Container(
        content=ft.Text("Overview", weight="bold"),
        bgcolor="blue", padding=ft.padding.symmetric(10, 20), border_radius=20,
        on_click=lambda e: toggle_home_tabs("overview")
    )
    btn_history = ft.Container(
        content=ft.Text("Expense History", weight="bold"),
        bgcolor=None, padding=ft.padding.symmetric(10, 20), border_radius=20,
        on_click=lambda e: toggle_home_tabs("history")
    )
    
    # Assembly of Home View
    home_view.content = ft.Column([
        header_section,
        ft.Container(height=10),
        ft.Row([btn_overview, btn_history], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=20),
        ft.Container(
            padding=20,
            expand=True,
            content=ft.Column([overview_container, history_container], expand=True)
        )
    ], expand=True)


    # --- 5. VIEW 2: PAYMENT SCREEN (The New UI) ---

    # Input Fields for Payment Screen
    pay_amount_field = ft.TextField(
        label="Amount", 
        bgcolor="#2C2C2C", 
        border_color="#2C2C2C",
        color="white",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=10,
        height=60
    )
    
    pay_account_dropdown = ft.Dropdown(
        label="Account",
        bgcolor="#2C2C2C",
        border_color="#2C2C2C",
        color="white",
        border_radius=10,
        
    )

    def close_payment_view(e):
        # Clear fields and go back
        pay_amount_field.value = ""
        payment_view.visible = False
        home_view.visible = True
        page.update()

    def submit_payment(e):
        if not pay_amount_field.value:
            pay_amount_field.error_text = "Enter amount"
            page.update()
            return
        
        category = pay_account_dropdown.value
        amount = pay_amount_field.value
        
        add_to_db(amount, category)
        
        # Success and Return
        page.show_snack_bar(ft.SnackBar(content=ft.Text(f"Paid ₹{amount} for {category}")))
        refresh_home_data()
        close_payment_view(None)

    # The "Bahaut Bada QR Scanner" Box
    scanner_box = ft.Container(
        bgcolor=ft.Colors.GREY_400, # Light grey to match image
        height=300,
        width=300,
        border_radius=0, # Rectangle as per image
        alignment=ft.alignment.center,
        content=ft.Column([
            ft.Icon(ft.Icons.QR_CODE_SCANNER, size=50, color="black"),
            ft.Text("Scan QR Code", color="black", weight="bold")
        ], alignment="center", horizontal_alignment="center")
    )

    payment_view.content = ft.Container(
        bgcolor="#121212",
        padding=30,
        content=ft.Column([
            # Back Button
            ft.Row([
                ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color="white", on_click=close_payment_view),
                ft.Container(expand=True)
            ]),
            
            ft.Text("Make\nPayment", size=35, weight="bold", color="white", text_align="center"),
            
            ft.Container(height=30),
            
            # 1. The Scanner
            ft.Container(
                content=scanner_box,
                alignment=ft.alignment.center
            ),
            
            ft.Container(height=30),
            
            # 2. Account Selection
            ft.Text("Selected Account :", size=16, weight="bold", color="white"),
            ft.Container(height=5),
            pay_account_dropdown,
            
            ft.Container(height=15),
            
            # 3. Amount Entry
            ft.Text("Enter Amount :", size=16, weight="bold", color="white"),
            ft.Container(height=5),
            pay_amount_field,
            
            ft.Container(height=30),
            
            # 4. Pay Button
            ft.ElevatedButton(
                text="PAY",
                bgcolor="blue",
                color="white",
                width=300,
                height=55,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
                on_click=submit_payment
            )

        ], horizontal_alignment="center", scroll=ft.ScrollMode.AUTO)
    )

    # --- 6. NAVIGATION LOGIC ---

    def open_payment_view(category_name=None):
        # Refresh categories in dropdown
        cats = get_categories()
        pay_account_dropdown.options = [ft.dropdown.Option(c) for c in cats.keys()]
        
        # Pre-select the clicked category
        if category_name:
            pay_account_dropdown.value = category_name
        else:
            pay_account_dropdown.value = list(cats.keys())[0]

        # Switch Views
        home_view.visible = False
        payment_view.visible = True
        page.update()

    # --- 7. HOME COMPONENT BUILDERS ---

    def create_category_card(name, spent, limit, color, icon_name):
        pct = spent / limit if limit > 0 else 0
        return ft.Container(
            bgcolor="#1E1E1E", border_radius=15, padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(icon_name, color=color),
                        ft.Text(name, size=16, weight="bold")
                    ]),
                    # THE "+" BUTTON -> Opens Payment View
                    ft.IconButton(
                        icon=ft.Icons.ADD, bgcolor="blue", icon_color="white",
                        width=30, height=30, icon_size=16,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: open_payment_view(name) 
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=5),
                ft.Row([
                    ft.Text(f"₹{spent:,.0f}", size=22, weight="bold"),
                    ft.Text(f"/ ₹{limit:,.0f}", size=14, color=ft.Colors.GREY)
                ]),
                ft.ProgressBar(value=min(pct, 1), color=color, bgcolor="#333333", bar_height=5)
            ])
        )

    def refresh_home_data():
        categories = get_categories()
        total_spent, category_spent, history_list = get_data_for_ui()
        
        total_budget = sum(c['budget'] for c in categories.values())
        available = total_budget - total_spent
        available_pct = available / total_budget if total_budget > 0 else 0
        
        # Update Overview
        overview_container.controls = [
            ft.Container(
                bgcolor="#1E1E1E", padding=20, border_radius=15,
                content=ft.Column([
                    ft.Text("Available Balance", size=15),
                    ft.Row([
                        ft.Text(f"₹{available:,.0f}", size=30, weight="bold", color="white"),
                        ft.Text(f"/₹{total_budget:,.0f}", color="grey")
                    ]),
                    ft.ProgressBar(value=available_pct, color="orange", bgcolor="#333333", bar_height=6)
                ])
            ),
            ft.Container(height=10),
        ]
        
        for cat_name, data in categories.items():
            spent = category_spent.get(cat_name, 0)
            card = create_category_card(cat_name, spent, data['budget'], data['color'], data['icon'])
            overview_container.controls.append(card)
            overview_container.controls.append(ft.Container(height=10))

        # Update History
        history_container.controls = []
        for item in history_list:
            cat_name = item[0]
            amount = item[1]
            date = item[2]
            cat_data = categories.get(cat_name, {"color": "grey", "icon": ft.Icons.QUESTION_MARK})
            
            tile = ft.Container(
                bgcolor="#1E1E1E", padding=15, border_radius=15, margin=ft.margin.only(bottom=10),
                content=ft.Row([
                    ft.Row([
                        ft.Container(content=ft.Icon(cat_data['icon'], color=cat_data['color']), bgcolor="#2C2C2C", padding=10, border_radius=10),
                        ft.Column([ft.Text(cat_name, weight="bold", size=16), ft.Text(f"Date: {date}", size=12, color="grey")], spacing=2)
                    ]),
                    ft.Text(f"-₹{amount:,.0f}", size=18, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            history_container.controls.append(tile)
        
        page.update()

    # --- 8. INITIALIZATION ---
    
    # We use a Stack to layer the views (Home at back, Payment at front)
    page.add(
        ft.Stack(
            [
                home_view,
                payment_view
            ],
            expand=True
        )
    )

    refresh_home_data()

ft.app(target=main)