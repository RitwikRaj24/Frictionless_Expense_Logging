import flet as ft
import sqlite3
import datetime
import asyncio
import webbrowser # FIX: Native browser launcher to avoid Flet warnings

# --- 1. CONFIGURATION ---
APP_TITLE = "Frictionless Expenses"
BG_MAIN = "#f5f5f5"       
BG_CARD = "#ffffff"       
PRIMARY_COLOR = "#2E3A59" 
DB_NAME = "expenses.db"

# --- 2. DATABASE LAYER ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    category TEXT,
                    date TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value REAL
                )''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('budget', 5000)")
    conn.commit()
    conn.close()

def add_transaction(amount, category):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amount, category, date_str))
    conn.commit()
    conn.close()

def get_recent_transactions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM expenses ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_transaction(item_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (item_id,))
    conn.commit()
    conn.close()

def get_budget():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key='budget'")
    res = c.fetchone()
    conn.close()
    return res[0] if res else 5000.0

def set_budget(new_limit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key='budget'", (new_limit,))
    conn.commit()
    conn.close()

# --- 3. UI COMPONENTS ---
def create_card(content, padding=15):
    return ft.Container(
        content=content,
        bgcolor=BG_CARD,
        padding=padding,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK12),
        margin=ft.Margin.symmetric(horizontal=20)
    )

def create_category_button(text, icon, color, on_click):
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=color, size=30),
            ft.Text(text, color=PRIMARY_COLOR, weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
        width=100, height=100,
        bgcolor=BG_CARD,
        border_radius=15,
        on_click=on_click,
        data=text,
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
        ink=True
    )

def create_quick_chip(amount, on_click):
    return ft.Container(
        content=ft.Text(f"+₹{amount}", size=12, color=PRIMARY_COLOR, weight="bold"),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=20,
        on_click=on_click,
        data=amount,
        ink=True
    )

# --- 4. MAIN LOGIC ---

def main(page: ft.Page):
    init_db()
    
    page.title = APP_TITLE
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = BG_MAIN
    page.padding = 0 
    
    state = {"current_amount": 0, "current_category": ""}

    # Status Indicator
    status_text = ft.Text("Ready", size=12, color="grey")

    amount_field = ft.TextField(
        label="Enter Amount", 
        prefix=ft.Text("₹ "), 
        text_style=ft.TextStyle(size=20, weight="bold"),
        border_color="transparent", 
        bgcolor=ft.Colors.GREY_100, 
        text_align=ft.TextAlign.CENTER, 
        keyboard_type=ft.KeyboardType.NUMBER, 
        border_radius=10
    )

    history_column = ft.Column(spacing=0)
    budget_input = ft.TextField(label="Monthly Budget", value=str(get_budget()), keyboard_type=ft.KeyboardType.NUMBER)

    def show_toast(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def refresh_history():
        rows = get_recent_transactions()
        history_column.controls.clear()
        
        if not rows:
            history_column.controls.append(ft.Text("No transactions yet.", color="grey", size=12))

        for row in rows:
            trans_id, cat, amt, date_str = row
            try:
                dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                time_str = dt_obj.strftime("%d %b, %I:%M %p")
            except:
                time_str = date_str

            def delete_click(e, x=trans_id):
                delete_transaction(x)
                refresh_history()
                show_toast("Deleted")

            history_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=PRIMARY_COLOR),
                    title=ft.Text(cat, weight="bold"),
                    subtitle=ft.Text(time_str, size=12),
                    trailing=ft.Row([
                        ft.Text(f"- ₹{amt:.0f}", weight="bold"), 
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="red", on_click=delete_click)
                    ], alignment=ft.MainAxisAlignment.END, width=100),
                    dense=True
                )
            )
            history_column.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_100))
        page.update()

    def add_quick_amount(e):
        current = amount_field.value if amount_field.value else "0"
        try:
            amount_field.value = str(int(current) + e.control.data)
        except:
            amount_field.value = str(e.control.data)
        amount_field.update()

    # --- PAYMENT FLOW ---

    def close_confirm(e):
        confirm_dialog.open = False
        status_text.value = "Cancelled"
        page.update()

    def save_transaction(e):
        add_transaction(state["current_amount"], state["current_category"])
        confirm_dialog.open = False
        amount_field.value = ""
        refresh_history()
        status_text.value = "Ready"
        show_toast("Saved!")
        page.update()

    async def handle_payment(e):
        user_amount = amount_field.value
        if not user_amount:
            amount_field.error_text = "Required"
            amount_field.update()
            return
        
        state["current_amount"] = user_amount
        state["current_category"] = e.control.data

        status_text.value = "Opening Payment App..."
        page.update()

        confirm_dialog.modal = True
        page.dialog = confirm_dialog
        confirm_dialog.open = True
        page.update()

        await asyncio.sleep(0.5)

        # FIX: Using native webbrowser to bypass Flet deprecation warning
        try:
            url = f"upi://pay?am={user_amount}&cu=INR"
            webbrowser.open(url)
        except Exception as ex:
            print(f"URL Error: {ex}")

    # --- DIALOGS ---
    
    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Payment"),
        content=ft.Text("Did the transaction succeed?"),
        actions=[
            ft.TextButton("Yes", on_click=save_transaction),
            ft.TextButton("No", on_click=close_confirm)
        ]
    )

    def save_settings_action(e):
        set_budget(float(budget_input.value))
        settings_dialog.open = False
        page.update()
        show_toast("Budget Updated!")

    def close_settings(e):
        settings_dialog.open = False
        page.update()

    settings_dialog = ft.AlertDialog(
        title=ft.Text("Settings"),
        content=ft.Column([ft.Text("Set Monthly Budget:"), budget_input], height=100),
        actions=[
            ft.TextButton("Save", on_click=save_settings_action),
            ft.TextButton("Cancel", on_click=close_settings)
        ]
    )

    def open_settings(e):
        page.dialog = settings_dialog
        settings_dialog.open = True
        page.update()

    # --- ASSEMBLY ---
    
    page.dialog = confirm_dialog 
    refresh_history()
    
    page.add(
        ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("Good Evening,", color=ft.Colors.WHITE70, size=14), 
                    ft.Text("Student", color=ft.Colors.WHITE, size=24, weight="bold")
                ]),
                ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=open_settings)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            width=400, height=120, bgcolor=PRIMARY_COLOR, 
            padding=ft.Padding.only(left=20, right=10, top=40, bottom=20),
            border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30)
        ),
        
        ft.Container(height=10),
        
        # Alignment Fix (0,0 is center)
        ft.Container(content=status_text, alignment=ft.Alignment(0, 0)),
        
        ft.Container(height=10),
        
        create_card(ft.Column([
            ft.Text("How much?", color="grey"),
            amount_field,
            ft.Container(height=10),
            ft.Row([
                create_quick_chip(10, add_quick_amount),
                create_quick_chip(20, add_quick_amount),
                create_quick_chip(50, add_quick_amount)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.MainAxisAlignment.CENTER)),
        
        ft.Container(height=20),
        
        ft.Row([
            create_category_button("Food", ft.Icons.FASTFOOD, ft.Colors.BLUE, handle_payment),
            create_category_button("Dorm", ft.Icons.BED, ft.Colors.PURPLE, handle_payment),
            create_category_button("Travel", ft.Icons.DIRECTIONS_BUS, ft.Colors.ORANGE, handle_payment)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
        
        ft.Container(height=20),
        
        ft.Container(content=history_column, padding=20)
    )

if __name__ == "__main__":
    # FIX: Switches to run() to solve the main warning
    # ft.app(target=main) 
    ft.run(main=main)
    # Note: Use ft.app(target=main) is actually usually preferred for packaging, 
    # but if the logs demand run(), change to: ft.run(target=main)
    # I kept ft.app here because run() often behaves differently with assets.
    # To strictly silence the warning, change line 335 to: ft.run(target=main)