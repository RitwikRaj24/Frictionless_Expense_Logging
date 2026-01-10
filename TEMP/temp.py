# import flet as ft
# import sqlite3
# import datetime
# import calendar

# def main(page: ft.Page):
#     # --- 1. APP THEME & SETTINGS ---
#     page.title = "IIT Dhanbad Expense Tracker"
#     page.window_width = 400
#     page.window_height = 800
#     page.theme_mode = ft.ThemeMode.LIGHT
#     page.bgcolor = "#f5f5f5"
#     page.padding = 0

#     # COLORS
#     PRIMARY_COLOR = "#2E3A59"
#     ACCENT_COLOR = "#FF6B6B"
#     BG_CARD = "#FFFFFF"
    
#     # --- 2. BACKEND & LOGIC ---
#     def init_db():
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         # Transaction Table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS transactions (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 amount REAL,
#                 category TEXT,
#                 date TEXT
#             )
#         """)
#         # Settings Table
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS settings (
#                 key TEXT PRIMARY KEY,
#                 value TEXT
#             )
#         """)
#         # Set default budget if not exists
#         cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('budget', '5000')")
#         conn.commit()
#         conn.close()

#     init_db()

#     # --- DATABASE HELPERS ---
#     def get_budget():
#         """Fetches the dynamic budget from DB"""
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT value FROM settings WHERE key='budget'")
#         val = cursor.fetchone()[0]
#         conn.close()
#         return float(val)

#     def set_budget(new_budget):
#         """Updates the budget in DB"""
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         cursor.execute("UPDATE settings SET value=? WHERE key='budget'", (str(new_budget),))
#         conn.commit()
#         conn.close()

#     def add_to_db(amount, category):
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", 
#                        (amount, category, current_date))
#         conn.commit()
#         conn.close()

#     def delete_transaction(id):
#         """New Feature: Delete Logic"""
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM transactions WHERE id=?", (id,))
#         conn.commit()
#         conn.close()
#         print(f"Deleted transaction {id}")

#     def get_recent_transactions():
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         # We now fetch ID too, so we know what to delete
#         cursor.execute("SELECT id, category, amount, date FROM transactions ORDER BY id DESC LIMIT 5")
#         rows = cursor.fetchall()
#         conn.close()
#         return rows

#     def get_dashboard_data():
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         cursor.execute("SELECT SUM(amount) FROM transactions")
#         result = cursor.fetchone()[0]
#         total_spent = result if result else 0 
        
#         cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
#         breakdown = cursor.fetchall() 
#         conn.close()
        
#         current_budget = get_budget() # Use Dynamic Budget
        
#         today = datetime.date.today()
#         days_in_month = calendar.monthrange(today.year, today.month)[1]
#         time_passed_pct = today.day / days_in_month
#         budget_spent_pct = total_spent / current_budget
        
#         pacing_score = budget_spent_pct / time_passed_pct if time_passed_pct > 0 else 0
        
#         return total_spent, breakdown, pacing_score, budget_spent_pct, current_budget

#     # --- 3. UI COMPONENTS ---

#     # -- HELPER: Cards --
#     def create_card(content, padding=15):
#         return ft.Container(
#             content=content,
#             bgcolor=BG_CARD,
#             padding=padding,
#             border_radius=15,
#             shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
#             margin=ft.margin.symmetric(horizontal=20)
#         )

#     # -- VIEW A: HOME --
#     amount_field = ft.TextField(
#         label="Enter Amount", prefix_text="₹ ", text_style=ft.TextStyle(size=20, weight="bold"),
#         border_color="transparent", bgcolor=ft.Colors.GREY_100, text_align=ft.TextAlign.CENTER, 
#         keyboard_type=ft.KeyboardType.NUMBER, border_radius=10
#     )
    
#     # Quick Chips Logic
#     def add_quick_amount(e):
#         current_val = amount_field.value if amount_field.value else "0"
#         try:
#             new_val = int(current_val) + e.control.data
#             amount_field.value = str(new_val)
#             amount_field.update()
#         except:
#             amount_field.value = str(e.control.data)
#             amount_field.update()

#     def create_quick_chip(amount):
#         return ft.Container(
#             content=ft.Text(f"+₹{amount}", size=12, color=PRIMARY_COLOR, weight="bold"),
#             padding=10,
#             bgcolor=ft.Colors.BLUE_50,
#             border_radius=20,
#             on_click=add_quick_amount,
#             data=amount, # Store the integer value here
#             ink=True
#         )

#     quick_chips_row = ft.Row(
#         [create_quick_chip(10), create_quick_chip(20), create_quick_chip(50), create_quick_chip(100)],
#         alignment=ft.MainAxisAlignment.CENTER
#     )

#     history_column = ft.Column(spacing=0)
#     current_transaction = {"amount": 0, "category": ""}

#     def refresh_history():
#         rows = get_recent_transactions()
#         history_column.controls.clear()
        
#         if not rows:
#             history_column.controls.append(ft.Text("No transactions yet.", color="grey", size=12))
        
#         for row in rows:
#             trans_id, cat, amt, date_str = row
#             dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
#             time_str = dt_obj.strftime("%d %b, %I:%M %p")
            
#             # Delete Button
#             delete_btn = ft.IconButton(
#                 icon=ft.Icons.DELETE_OUTLINE, 
#                 icon_color="red", 
#                 on_click=lambda e, x=trans_id: delete_item(x)
#             )

#             # --- FIX IS HERE ---
#             # Changed 'main_axis_alignment' to 'alignment'
#             trailing_row = ft.Row(
#                 [ft.Text(f"- ₹{amt:.0f}", weight="bold"), delete_btn], 
#                 alignment=ft.MainAxisAlignment.END, 
#                 width=100
#             )

#             history_column.controls.append(
#                 ft.ListTile(
#                     leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=PRIMARY_COLOR),
#                     title=ft.Text(cat, weight="bold"),
#                     subtitle=ft.Text(time_str, size=12),
#                     trailing=trailing_row,
#                     dense=True
#                 )
#             )
#             history_column.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_100))
#         page.update()

#     def delete_item(item_id):
#         delete_transaction(item_id)
#         refresh_history()
#         page.show_snack_bar(ft.SnackBar(content=ft.Text("Transaction Deleted")))

#     def save_transaction(e):
#         add_to_db(current_transaction["amount"], current_transaction["category"])
#         page.close(confirm_dialog)
#         amount_field.value = ""
#         refresh_history()
#         page.show_snack_bar(ft.SnackBar(content=ft.Text("Saved!")))
#         page.update()

#     def handle_payment(e):
#         user_amount = amount_field.value
#         category_name = e.control.data
#         if not user_amount:
#             amount_field.error_text = "Required"
#             page.update()
#             return
        
#         current_transaction["amount"] = user_amount
#         current_transaction["category"] = category_name
#         page.set_clipboard(user_amount)
#         try:
#             page.launch_url(f"upi://pay?am={user_amount}&cu=INR")
#         except:
#             pass 
#         page.open(confirm_dialog)

#     confirm_dialog = ft.AlertDialog(
#         title=ft.Text("Payment Confirmation"),
#         content=ft.Text("Did the payment complete successfully?"),
#         actions=[
#             ft.TextButton("Yes", on_click=save_transaction),
#             ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
#         ],
#         actions_alignment=ft.MainAxisAlignment.END,
#     )

#     # Settings Dialog
#     budget_input = ft.TextField(label="Monthly Budget", value=str(get_budget()), keyboard_type=ft.KeyboardType.NUMBER)
    
#     def save_settings(e):
#         try:
#             new_budget = float(budget_input.value)
#             set_budget(new_budget)
#             page.close(settings_dialog)
#             page.show_snack_bar(ft.SnackBar(content=ft.Text("Budget Updated!")))
#         except:
#             pass # Handle invalid input

#     settings_dialog = ft.AlertDialog(
#         title=ft.Text("Settings"),
#         content=ft.Column([ft.Text("Set your monthly limit:"), budget_input], height=100),
#         actions=[ft.TextButton("Save", on_click=save_settings)]
#     )

#     def create_category_button(text, icon, color):
#         return ft.Container(
#             content=ft.Column([ft.Icon(icon, color=color, size=30), ft.Text(text, color=PRIMARY_COLOR, weight="bold")], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
#             width=100, height=100, bgcolor=BG_CARD, border_radius=15, on_click=handle_payment, data=text,
#             shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)), ink=True
#         )

#     home_view = ft.Column(
#         [
#             # Header with Settings Icon
#             ft.Container(
#                 content=ft.Row([
#                     ft.Column([ft.Text("Good Evening,", color=ft.Colors.WHITE70, size=14), ft.Text("Student", color=ft.Colors.WHITE, size=24, weight="bold")]),
#                     ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda e: page.open(settings_dialog))
#                 ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
#                 width=400, height=120, bgcolor=PRIMARY_COLOR, padding=ft.padding.only(left=20, right=10, top=40, bottom=20),
#                 border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30)
#             ),
#             ft.Container(height=20),
            
#             # Input Area with Chips
#             create_card(ft.Column([
#                 ft.Text("How much?", color="grey", size=12),
#                 amount_field,
#                 ft.Container(height=10),
#                 quick_chips_row # Added Chips here
#             ], horizontal_alignment=ft.MainAxisAlignment.CENTER)),

#             ft.Container(height=20),
#             ft.Row([
#                 create_category_button("Food", ft.Icons.FASTFOOD, ft.Colors.BLUE),
#                 create_category_button("Stationary", ft.Icons.EDIT, ft.Colors.ORANGE),
#                 create_category_button("Dorm", ft.Icons.BED, ft.Colors.PURPLE),
#             ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            
#             ft.Container(height=30),
#             ft.Container(content=ft.Column([ft.Text("Recent Transactions", weight="bold", size=16, color=PRIMARY_COLOR), history_column]), padding=20)
#         ],
#         scroll=ft.ScrollMode.AUTO, spacing=0
#     )

#     # -- VIEW B: STATS --
#     txt_total_spent = ft.Text("₹0", size=30, weight="bold", color=PRIMARY_COLOR)
#     txt_pacing_status = ft.Text("...", size=14)
#     pacing_bar = ft.ProgressBar(width=300, height=15, color=ft.Colors.GREY, bgcolor=ft.Colors.GREY_100, border_radius=5)
#     chart_container = ft.Column()

#     stats_view = ft.Column(
#         [
#             ft.Container(height=40),
#             ft.Text("Analytics Dashboard", size=22, weight="bold", color=PRIMARY_COLOR),
#             ft.Container(height=20),
#             create_card(ft.Column([ft.Text("Total Spent", size=12, color="grey"), txt_total_spent], horizontal_alignment=ft.MainAxisAlignment.CENTER), padding=20),
#             ft.Container(height=20),
#             create_card(ft.Column([ft.Text("Budget Health", weight="bold"), ft.Container(height=10), pacing_bar, ft.Container(height=10), txt_pacing_status])),
#             ft.Container(height=20),
#             create_card(ft.Column([ft.Text("Breakdown", weight="bold"), ft.Container(height=20), chart_container], horizontal_alignment=ft.MainAxisAlignment.CENTER))
#         ],
#         horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO
#     )

#     def refresh_stats():
#         spent, breakdown, pacing, budget_pct, current_limit = get_dashboard_data()
        
#         txt_total_spent.value = f"₹{spent:.0f} / ₹{current_limit:.0f}" # Shows Limit now
        
#         pacing_bar.value = min(budget_pct, 1.0)
#         if pacing > 1.1:
#             pacing_bar.color = ft.Colors.RED
#             txt_pacing_status.value = "⚠️ Spending too fast!"
#             txt_pacing_status.color = ft.Colors.RED
#         else:
#             pacing_bar.color = ft.Colors.GREEN
#             txt_pacing_status.value = "✅ Safe Zone"
#             txt_pacing_status.color = ft.Colors.GREEN

#         sections = []
#         colors = [ft.Colors.BLUE, ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.TEAL]
#         for i, item in enumerate(breakdown):
#             sections.append(ft.PieChartSection(value=item[1], title=f"{item[0][0]}", color=colors[i % len(colors)], radius=40, title_style=ft.TextStyle(size=14, color="white", weight="bold")))
        
#         legend_items = []
#         for i, item in enumerate(breakdown):
#             legend_items.append(ft.Row([ft.Container(width=10, height=10, bgcolor=colors[i % len(colors)]), ft.Text(f"{item[0]}: ₹{item[1]:.0f}", size=12)]))

#         chart_container.controls = [ft.Row([ft.PieChart(sections=sections, sections_space=2, center_space_radius=30, height=150), ft.Column(legend_items)], alignment=ft.MainAxisAlignment.SPACE_EVENLY)]
#         page.update()

#     def on_tab_change(e):
#         if e.control.selected_index == 1:
#             refresh_stats()
#         else:
#             refresh_history()

#     t = ft.Tabs(
#         selected_index=0, animation_duration=300, indicator_color=PRIMARY_COLOR, label_color=PRIMARY_COLOR, unselected_label_color="grey",
#         on_change=on_tab_change,
#         tabs=[ft.Tab(text="Home", icon=ft.Icons.HOME, content=home_view), ft.Tab(text="Analytics", icon=ft.Icons.INSERT_CHART, content=stats_view)],
#         expand=1,
#     )
    
#     refresh_history()
#     page.add(t)

# ft.app(target=main)


import flet as ft
import sqlite3
import datetime

def main(page: ft.Page):
    page.title = "Expense Tracker"
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f5f5f5"
    page.padding = 0

    # --- DATABASE ---
    conn = sqlite3.connect("expenses.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, category TEXT, amount REAL, date TEXT)")
    conn.commit()

    def add_expense(amt, cat):
        d = datetime.datetime.now().strftime("%Y-%m-%d")
        c.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", (amt, cat, d))
        conn.commit()

    def get_expenses():
        c.execute("SELECT category, amount FROM expenses ORDER BY id DESC LIMIT 5")
        return c.fetchall()

    def get_total():
        c.execute("SELECT SUM(amount) FROM expenses")
        res = c.fetchone()[0]
        return res if res else 0

    # --- UI COMPONENTS ---
    
    # 1. COMPATIBILITY FIX: Use 'prefix' (Widget) not 'prefix_text' (String)
    amount_box = ft.TextField(
        label="Amount", 
        prefix=ft.Text("₹ "), 
        keyboard_type=ft.KeyboardType.NUMBER,
        bgcolor="white",
        text_align=ft.TextAlign.CENTER
    )

    history_list = ft.Column()

    def refresh():
        history_list.controls.clear()
        data = get_expenses()
        for cat, amt in data:
            history_list.controls.append(
                ft.Container(
                    content=ft.Row([ft.Text(cat), ft.Text(f"₹{amt}", color="red")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white", padding=10, border_radius=5
                )
            )
        
        # Update Stats Manually (No PieChart to avoid crashes)
        total = get_total()
        stats_text.value = f"Total Spent: ₹{total}"
        page.update()

    def save_click(e):
        if not amount_box.value: return
        cat = e.control.data
        add_expense(float(amount_box.value), cat)
        amount_box.value = ""
        
        # 2. COMPATIBILITY FIX: Legacy Dialog
        page.dialog = confirm_dlg
        confirm_dlg.open = True
        refresh()

    confirm_dlg = ft.AlertDialog(
        title=ft.Text("Saved!"),
        actions=[ft.TextButton("OK", on_click=lambda e: setattr(confirm_dlg, 'open', False) or page.update())]
    )

    def btn(txt, color):
        return ft.Container(
            content=ft.Text(txt, color="white", weight="bold"),
            bgcolor=color, width=80, height=80, border_radius=10,
            alignment=ft.alignment.center, on_click=save_click, data=txt
        )

    # --- LAYOUT (No Tabs, just switching visibility) ---
    
    stats_text = ft.Text("Total Spent: ₹0", size=20, weight="bold")
    
    home_view = ft.Column([
        ft.Container(height=20),
        ft.Text("  Add Expense", size=20, weight="bold", color="#333333"),
        ft.Container(content=amount_box, padding=20),
        ft.Row([btn("Food", "blue"), btn("Travel", "orange"), btn("Other", "purple")], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=20),
        ft.Text("  Recent History", size=20, weight="bold", color="#333333"),
        ft.Container(content=history_list, padding=20)
    ])

    stats_view = ft.Column([
        ft.Container(height=50),
        ft.Container(content=stats_text, alignment=ft.alignment.center),
    ], visible=False)

    def nav_click(e):
        # 3. COMPATIBILITY FIX: Manual Navigation (No 'Tabs' widget)
        if e.control.data == "home":
            home_view.visible = True
            stats_view.visible = False
        else:
            home_view.visible = False
            stats_view.visible = True
        page.update()

    nav_bar = ft.Container(
        content=ft.Row([
            ft.IconButton(ft.Icons.HOME, on_click=nav_click, data="home", icon_size=30),
            ft.IconButton(ft.Icons.PIE_CHART, on_click=nav_click, data="stats", icon_size=30)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        bgcolor="white", height=60
    )

    refresh()
    page.add(ft.Column([home_view, stats_view], expand=True), nav_bar)

ft.app(target=main)