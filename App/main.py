# # # Entry point

# # # Tasks for main.py 
# # # 1. Start the database 
# # # 2. Switch between the "Home" and "Stats" tab

# import sys 
# print("Python Path: ", sys.executable)

# import flet as ft 
# from database import init_db
# from views.home_view import HomeView
# from views.stats_view import StatsView
# from config import APP_TITLE, BG_MAIN, PRIMARY_COLOR 

# def main(page: ft.Page):
    
#     # App Configuration 
#     page.title = APP_TITLE 
#     page.bgcolor = BG_MAIN 
#     page.padding = 0 

#     # Simulating mobile dimensions for easy viewing on laptop 
#     page.window_width = 400 
#     page.window_height = 800 

#     # initialising database and creating a table if one does'nt exist before
#     init_db()

#     # load_views 
#     home = HomeView(page)
#     stats = StatsView(page)

#     # navigation logic 
#     def change_tab(e):
#         # clear current page 
#         page.controls.clear()

#         # add the selected view 
#         if e.control.selected_index == 0:
#             page.add(home)
#         else:
#             # If switching to stats, refresh the data first 
#             stats.data()
#             page.add(stats)

#         # Always add the nav bar back to the bottom 
#         page.add(nav_bar)
#         page.update()

#     # creating navigation bar 

#     nav_bar = ft.NavigationBar(
#         destinations=[
#             ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
#             ft.NavigationDestination(icon=ft.Icons.PIE_CHART, label="Stats"),
#         ],
#         selected_index=0,
#         on_change=change_tab,
#         bgcolor=ft.Colors.WHITE,
#         indicator_color=PRIMARY_COLOR,
#     )

#     # nav_bar = ft.Container(
#     #         content=ft.Row(
#     #             [
#     #                 ft.IconButton(icon=ft.Icons.HOME, icon_size=30, on_click=switch_to_home, icon_color=PRIMARY_COLOR),
#     #                 ft.IconButton(icon=ft.Icons.PIE_CHART, icon_size=30, on_click=switch_to_stats, icon_color=PRIMARY_COLOR),
#     #             ],
#     #             alignment=ft.MainAxisAlignment.SPACE_EVENLY
#     #         ),
#     #         bgcolor=ft.Colors.WHITE,
#     #         height=60,
#     #         border_radius=ft.border_radius.only(top_left=15, top_right=15),
#     #         shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12)
#     #     )    

#     # initial render (with home page being displayed first)
#     page.add(home)
#     page.add(nav_bar)

# ft.app(target=main)

import flet as ft
import sqlite3
import datetime

def main(page: ft.Page):
    # --- CONFIGURATION ---
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
        if not data:
            history_list.controls.append(ft.Text("No transactions yet", color="grey"))
            
        for cat, amt in data:
            history_list.controls.append(
                ft.Container(
                    content=ft.Row([ft.Text(cat), ft.Text(f"₹{amt}", color="red")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor="white", padding=10, border_radius=5
                )
            )
        
        total = get_total()
        stats_text.value = f"Total Spent: ₹{total}"
        page.update()

    def save_click(e):
        if not amount_box.value: return
        cat = e.control.data
        add_expense(float(amount_box.value), cat)
        amount_box.value = ""
        
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
            # --- FIX IS HERE: (0,0) is the universal code for "Center" ---
            alignment=ft.Alignment(0, 0), 
            on_click=save_click, data=txt
        )

    # --- LAYOUT ---
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
        ft.Container(content=stats_text, alignment=ft.Alignment(0, 0)),
    ], visible=False)

    def nav_click(e):
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

if __name__ == "__main__":
    ft.app(target=main)