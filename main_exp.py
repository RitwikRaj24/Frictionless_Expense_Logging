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
    page.padding = 20

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

        # Table 2: Categories (New! Stores names so we can edit them)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                budget REAL,
                color TEXT,
                icon TEXT
            )
        """)

        # Check if categories exist, if not, add defaults
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
        """Returns a list of dicts: [{'name': 'Work', 'budget': 28000...}, ...]"""
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

    def rename_category_in_db(old_name, new_name):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        try:
            # 1. Update the Category Name
            cursor.execute("UPDATE categories SET name = ? WHERE name = ?", (new_name, old_name))
            # 2. Update all historical transactions to the new name
            cursor.execute("UPDATE transactions SET category = ? WHERE category = ?", (new_name, old_name))
            conn.commit()
        except sqlite3.IntegrityError:
            # Handle case where name already exists
            pass
        conn.close()

    def get_data_for_ui():
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        
        # 1. Total spent
        cursor.execute("SELECT SUM(amount) FROM transactions")
        res = cursor.fetchone()[0]
        total_spent = res if res else 0

        # 2. Category Breakdown
        cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
        raw_breakdown = cursor.fetchall()
        category_spent = {item[0]: item[1] for item in raw_breakdown}

        # 3. Recent History
        cursor.execute("SELECT category, amount, date FROM transactions ORDER BY id DESC")
        history_list = cursor.fetchall()

        conn.close()
        return total_spent, category_spent, history_list

    # --- 3. UI COMPONENTS ---

    # A. HEADER
    header_section = ft.Row(
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

    # B. DIALOGS (Add Money & Rename)

    # 1. ADD MONEY DIALOG
    dlg_amount_field = ft.TextField(label="Amount", keyboard_type=ft.KeyboardType.NUMBER, text_align="center")
    dlg_category_store = ft.Text(visible=False) 

    def save_transaction(e):
        if not dlg_amount_field.value: return
        add_to_db(dlg_amount_field.value, dlg_category_store.value)
        dlg_amount_field.value = ""
        page.close(add_dialog)
        refresh_data()
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Transaction Added!")))

    add_dialog = ft.AlertDialog(
        title=ft.Text("Add Expense"),
        content=ft.Column([ft.Text("How much did you spend?"), dlg_amount_field], height=100, tight=True),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(add_dialog)),
            ft.ElevatedButton("Save", on_click=save_transaction, bgcolor="blue", color="white"),
        ]
    )

    # 2. RENAME DIALOG (NEW!)
    dlg_rename_field = ft.TextField(label="New Name", text_align="left")
    dlg_old_name_store = ft.Text(visible=False)

    def save_rename(e):
        if not dlg_rename_field.value: return
        rename_category_in_db(dlg_old_name_store.value, dlg_rename_field.value)
        dlg_rename_field.value = ""
        page.close(rename_dialog)
        refresh_data()
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Category Renamed!")))

    rename_dialog = ft.AlertDialog(
        title=ft.Text("Edit Category Name"),
        content=dlg_rename_field,
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.close(rename_dialog)),
            ft.ElevatedButton("Rename", on_click=save_rename, bgcolor="blue", color="white"),
        ]
    )

    def open_add_dialog(category_name):
        dlg_category_store.value = category_name
        page.open(add_dialog)

    def open_rename_dialog(current_name):
        dlg_old_name_store.value = current_name
        dlg_rename_field.value = current_name
        page.open(rename_dialog)

    # C. CARDS & LISTS
    
    def create_category_card(name, spent, limit, color, icon_name):
        pct = spent / limit if limit > 0 else 0
        
        return ft.Container(
            bgcolor="#1E1E1E",
            border_radius=15,
            padding=15,
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(icon_name, color=color),
                        ft.Text(name, size=16, weight="bold"),
                        # EDIT BUTTON (Pencil)
                        ft.IconButton(
                            icon=ft.Icons.EDIT, 
                            icon_color=ft.Colors.GREY_700, 
                            icon_size=14,
                            tooltip="Rename Account",
                            on_click=lambda e: open_rename_dialog(name)
                        )
                    ]),
                    # ADD BUTTON (Blue +)
                    ft.IconButton(
                        icon=ft.Icons.ADD, 
                        bgcolor="blue", 
                        icon_color="white", 
                        width=30, height=30,
                        icon_size=16,
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                        on_click=lambda e: open_add_dialog(name)
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

    overview_container = ft.Column(scroll=ft.ScrollMode.HIDDEN)
    history_container = ft.Column(scroll=ft.ScrollMode.AUTO, visible=False)

    def refresh_data():
        # Load fresh data
        categories = get_categories() # Dynamic from DB
        total_spent, category_spent, history_list = get_data_for_ui()
        
        total_budget = sum(c['budget'] for c in categories.values())
        available = total_budget - total_spent
        available_pct = available / total_budget if total_budget > 0 else 0
        
        # 1. Update Overview
        overview_container.controls = [
            # Main Balance
            ft.Container(
                bgcolor="#1E1E1E", padding=20, border_radius=15,
                content=ft.Column([
                    ft.Text("Available Balance", size=15),
                    ft.Row([
                        ft.Text(f"₹{available:,.0f}", size=30, weight="bold", color="white"),
                        ft.Text(f"/₹{total_budget:,.0f}", color="grey")
                    ]),
                    ft.Container(height=5),
                    ft.ProgressBar(value=available_pct, color="orange", bgcolor="#333333", bar_height=6)
                ])
            ),
            ft.Container(height=10),
        ]
        
        # 2. Dynamic Category Cards
        for cat_name, data in categories.items():
            spent = category_spent.get(cat_name, 0)
            card = create_category_card(cat_name, spent, data['budget'], data['color'], data['icon'])
            overview_container.controls.append(card)
            overview_container.controls.append(ft.Container(height=10))

        # 3. Update History
        history_container.controls = []
        for item in history_list:
            cat_name = item[0]
            amount = item[1]
            date = item[2]
            
            # Fallback for icon if category was deleted/missing (safety check)
            cat_data = categories.get(cat_name, {"color": "grey", "icon": ft.Icons.QUESTION_MARK})
            
            tile = ft.Container(
                bgcolor="#1E1E1E", padding=15, border_radius=15, margin=ft.margin.only(bottom=10),
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(cat_data['icon'], color=cat_data['color']),
                            bgcolor="#2C2C2C", padding=10, border_radius=10
                        ),
                        ft.Column([
                            ft.Text(cat_name, weight="bold", size=16),
                            ft.Text(f"Date: {date}", size=12, color="grey")
                        ], spacing=2)
                    ]),
                    ft.Text(f"-₹{amount:,.0f}", size=18, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
            history_container.controls.append(tile)
            
        page.update()

    # D. NAVIGATION
    btn_overview = ft.Container(
        content=ft.Text("Overview", weight="bold"),
        bgcolor="blue", padding=ft.padding.symmetric(10, 20), border_radius=20,
        on_click=lambda e: toggle_view("overview")
    )
    btn_history = ft.Container(
        content=ft.Text("Expense History", weight="bold"),
        bgcolor=None, padding=ft.padding.symmetric(10, 20), border_radius=20,
        on_click=lambda e: toggle_view("history")
    )

    def toggle_view(view_name):
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

    # --- 4. LAYOUT ASSEMBLY ---
    page.add(
        header_section,
        ft.Container(height=20),
        ft.Row([btn_overview, btn_history], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=20),
        ft.Column([overview_container, history_container], expand=True)
    )

    refresh_data()

ft.app(target=main)