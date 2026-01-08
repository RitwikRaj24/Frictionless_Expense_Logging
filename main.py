# # import flet as ft

# # def main(page: ft.Page):
# #     # --- 1. APP SETTINGS ---
# #     # We set the window size to look like a phone for testing
# #     page.title = "IIT Dhanbad Expense Tracker"
# #     page.window_width = 400
# #     page.window_height = 700
# #     page.vertical_alignment = ft.MainAxisAlignment.CENTER # Center everything vertically
# #     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # Center everything horizontally
    
# #     # --- 2. THE LOGIC (Brain) ---
    
# #     # This function runs when the user clicks "Yes" on the popup
# #     def save_transaction(e):
# #         # In Phase 2, we will write to the database here.
# #         # For now, we just print to the terminal to prove it works.
# #         print("SUCCESS: Transaction saved to database!")
# #         page.close(confirm_dialog) # Close the popup

# #     # This function runs when the user clicks a Category Button (Food/Stationary/Dorm)
# #     def handle_payment(e):
# #         user_amount = amount_field.value
# #         category_name = e.control.text # Gets the text of the button clicked
        
# #         if not user_amount:
# #             # Error handling: If box is empty, show a visual error
# #             amount_field.error_text = "Please enter amount"
# #             page.update()
# #             return

# #         # A. Mock the "Clipboard" action
# #         print(f"--- ACTION ---")
# #         print(f"1. Copied '₹{user_amount}' to Clipboard")
        
# #         # B. Mock the "Redirect" action
# #         print(f"2. Launching Google Pay for Category: {category_name}")
        
# #         # C. Open the Confirmation Dialog
# #         page.open(confirm_dialog)

# #     # --- 3. THE UI ELEMENTS (Body) ---
    
# #     # The Input Field
# #     amount_field = ft.TextField(
# #         label="Amount (₹)", 
# #         text_align=ft.TextAlign.CENTER, 
# #         width=200,
# #         keyboard_type=ft.KeyboardType.NUMBER
# #     )

# #     # The Buttons
# #     # We use a helper function to make them look identical
# #     def create_pay_button(text, color):
# #         return ft.ElevatedButton(
# #             text=text, 
# #             width=200, 
# #             height=50, 
# #             bgcolor=color, 
# #             color=ft.Colors.WHITE,
# #             on_click=handle_payment # Connects the button to the logic function above
# #         )

# #     btn_food = create_pay_button("Food", ft.Colors.BLUE_400)
# #     btn_stat = create_pay_button("Stationary", ft.Colors.ORANGE_400)
# #     btn_dorm = create_pay_button("Dorm", ft.Colors.PURPLE_400)

# #     # The Popup Dialog (Hidden by default)
# #     confirm_dialog = ft.AlertDialog(
# #         title=ft.Text("Payment Check"),
# #         content=ft.Text("Did the payment go through successfully?"),
# #         actions=[
# #             ft.TextButton("Yes", on_click=save_transaction),
# #             ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
# #         ],
# #     )

# #     # --- 4. ASSEMBLE THE PAGE ---
# #     page.add(
# #         ft.Text("Expense Tracker", size=30, weight="bold"),
# #         ft.Divider(height=20, color="transparent"), # Spacer
# #         amount_field,
# #         ft.Divider(height=20, color="transparent"), # Spacer
# #         btn_food,
# #         ft.Divider(height=10, color="transparent"), 
# #         btn_stat,
# #         ft.Divider(height=10, color="transparent"), 
# #         btn_dorm,
# #     )

# # # Run the app
# # ft.app(target=main)


# # TESTING DONE : Works OK 

# # Tasks at hand : 
# # 1. Creating a database : Expenses are actually saved to a file
# # 2. Activating the clipboard : Amount is copied automatically 
# # 3. Preparing the launcher : Code to open GPay 


# # # Rewriting code 
# # import flet as ft
# # import sqlite3
# # import datetime 

# # def main(page: ft.Page):
# #     # --- 1. APP SETTINGS ---
# #     # We set the window size to look like a phone for testing
# #     page.title = "IIT Dhanbad Expense Tracker"
# #     page.window_width = 400
# #     page.window_height = 700
# #     page.vertical_alignment = ft.MainAxisAlignment.CENTER # Center everything vertically
# #     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER # Center everything horizontally
    
# #     # --- 2. BACKEND SETUP (Database) ---
    
# #     # Creating a simple function to connect to a local file 'expenses.db' 
# #     def init_db(): # initialising database 
# #         conn = sqlite3.connect("expenses.db")
# #         cursor = conn.cursor()
# #         # Create table if it does not exist 
# #         cursor.execute("""
# #             CREATE TABLE IF NOT EXISTS transactions (
# #                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
# #                        amount REAL, 
# #                        category TEXT, 
# #                        date TEXT)
# #         """)
# #         conn.commit()
# #         conn.close()

# #     init_db() # initialising the DB immediately when the app starts
    
# #     # Function to save data to the DB 
# #     def add_to_db(amount, category):
# #         conn = sqlite3.connect("expenses.db")
# #         cursor = conn.cursor()
# #         current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# #         cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", 
# #                        (amount, category, current_date))
        
# #     # --- 3. STATE VARIABLES --- 
# #     # For remembering what the user clicks while the popup 
# #     # is open, create temporary memory slots

# #     current_transactions = {"amount":0, "category":""}

# #     # --- 4. THE LOGIC (Brain) --- 

# #     def save_transactions(e):
# #         # 1. Save to Database 
# #         add_to_db(current_transactions["amount"], current_transactions["category"])

# #         # 2. Close popup 
# #         page.close(confirm_dialog)

# #         # 3. Clear Input Field for the next time  
# #         amount_field.value = ""
# #         page.show_snack_bar(ft.SnackBar(content=ft.Text("Expense Saved!")))
# #         page.update()

# #     def handle_payment(e):
# #         user_amount = amount_field.value 
# #         category_name = e.control.text 

# #         if not user_amount:
# #             amount_field.error_text = "Please enter amount"
# #             page.update()
# #             return 
        
# #         current_transactions["amount"] = user_amount 
# #         current_transactions["category"] = category_name

# #         # --- REAL FEATURE 1 : CLIPBOARD --- 
# #         page.set_clipboard(user_amount)
# #         print(f"CLIPBOARD: Copied {user_amount}")

# #         # --- REAL FEATURE 2: LAUNCHER ---
# #         # Note: On a laptop, this might try to open a browser or do nothing.
# #         # On Android, it will ask which app to use.
# #         # We use a generic UPI string. Since we don't know the payee yet, 
# #         # we are just triggering the phone's "Pay" intent.
        
# #         try:
# #             # Trying to open the system's UPI handler
# #             page.launch_url(f"upi://pay?am={user_amount}&cu=INR") 
# #         except Exception as ex:
# #             print(f"LAUNCH ERROR (Expected on Laptop): {ex}")
        
# #         # Open the Confirmation Dialog
# #         page.open(confirm_dialog)

# #     # --- 5. THE UI ELEMENTS (Body) ---
    
# #     amount_field = ft.TextField(
# #         label="Amount (₹)", 
# #         text_align=ft.TextAlign.CENTER, 
# #         width=200,
# #         keyboard_type=ft.KeyboardType.NUMBER
# #     )

# #     def create_pay_button(text, color):
# #         return ft.ElevatedButton(
# #             text=text, 
# #             width=200, 
# #             height=50, 
# #             bgcolor=color, 
# #             color=ft.Colors.WHITE,
# #             on_click=handle_payment
# #         )

# #     btn_food = create_pay_button("Food", ft.Colors.BLUE_400)
# #     btn_stat = create_pay_button("Stationary", ft.Colors.ORANGE_400)
# #     btn_dorm = create_pay_button("Dorm", ft.Colors.PURPLE_400)

# #     confirm_dialog = ft.AlertDialog(
# #         title=ft.Text("Payment Check"),
# #         content=ft.Text("Did the payment go through successfully?"),
# #         actions=[
# #             ft.TextButton("Yes", on_click=save_transaction),
# #             ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
# #         ],
# #     )

# #     page.add(
# #         ft.Text("Expense Tracker", size=30, weight="bold"),
# #         ft.Divider(height=20, color="transparent"),
# #         amount_field,
# #         ft.Divider(height=20, color="transparent"),
# #         btn_food,
# #         ft.Divider(height=10, color="transparent"),
# #         btn_stat,
# #         ft.Divider(height=10, color="transparent"),
# #         btn_dorm,
# #     )

# # ft.app(target=main)    

# import flet as ft
# import sqlite3
# import datetime

# def main(page: ft.Page):
#     # --- 1. APP SETTINGS ---
#     page.title = "IIT Dhanbad Expense Tracker"
#     page.window_width = 400
#     page.window_height = 700
#     page.vertical_alignment = ft.MainAxisAlignment.CENTER
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

#     # --- 2. BACKEND SETUP (Database) ---
#     # We create a simple function to connect to a local file 'expenses.db'
#     def init_db():
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         # Create table if it doesn't exist
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS transactions (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 amount REAL,
#                 category TEXT,
#                 date TEXT
#             )
#         """)
#         conn.commit()
#         conn.close()

#     # Initialize the DB immediately when app starts
#     init_db()

#     # Function to save data to the DB
#     def add_to_db(amount, category):
#         conn = sqlite3.connect("expenses.db")
#         cursor = conn.cursor()
#         current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
#         cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", 
#                        (amount, category, current_date))
#         conn.commit()
#         conn.close()
#         print(f"DATABASE: Saved ₹{amount} for {category} at {current_date}")

#     # --- 3. STATE VARIABLES ---
#     # We need to remember "What did the user just click?" while the popup is open
#     # These are like temporary memory slots.
#     current_transaction = {"amount": 0, "category": ""}

#     # --- 4. THE LOGIC (Brain) ---
    
#     def save_transaction(e):
#         # 1. Save to Database
#         add_to_db(current_transaction["amount"], current_transaction["category"])
        
#         # 2. Close Popup
#         page.close(confirm_dialog)
        
#         # 3. Clear Input Field for next time
#         amount_field.value = ""
#         page.show_snack_bar(ft.SnackBar(content=ft.Text("Expense Saved!")))
#         page.update()

#     def handle_payment(e):
#         user_amount = amount_field.value
#         category_name = e.control.text 
        
#         if not user_amount:
#             amount_field.error_text = "Please enter amount"
#             page.update()
#             return

#         # Save to temporary memory so we can log it later if they say "Yes"
#         current_transaction["amount"] = user_amount
#         current_transaction["category"] = category_name

#         # --- REAL FEATURE 1: CLIPBOARD ---
#         page.set_clipboard(user_amount)
#         print(f"CLIPBOARD: Copied {user_amount}")

#         # --- REAL FEATURE 2: LAUNCHER ---
#         # Note: On a laptop, this might try to open a browser or do nothing.
#         # On Android, it will ask which app to use.
#         # We use a generic UPI string. Since we don't know the payee yet, 
#         # we are just triggering the phone's "Pay" intent.
        
#         try:
#             # Trying to open the system's UPI handler
#             page.launch_url(f"upi://pay?am={user_amount}&cu=INR") 
#         except Exception as ex:
#             print(f"LAUNCH ERROR (Expected on Laptop): {ex}")
        
#         # Open the Confirmation Dialog
#         page.open(confirm_dialog)

#     # --- 5. THE UI ELEMENTS (Body) ---
    
#     amount_field = ft.TextField(
#         label="Amount (₹)", 
#         text_align=ft.TextAlign.CENTER, 
#         width=200,
#         keyboard_type=ft.KeyboardType.NUMBER
#     )

#     def create_pay_button(text, color):
#         return ft.ElevatedButton(
#             text=text, 
#             width=200, 
#             height=50, 
#             bgcolor=color, 
#             color=ft.Colors.WHITE,
#             on_click=handle_payment
#         )

#     btn_food = create_pay_button("Food", ft.Colors.BLUE_400)
#     btn_stat = create_pay_button("Stationary", ft.Colors.ORANGE_400)
#     btn_dorm = create_pay_button("Dorm", ft.Colors.PURPLE_400)

#     confirm_dialog = ft.AlertDialog(
#         title=ft.Text("Payment Check"),
#         content=ft.Text("Did the payment go through successfully?"),
#         actions=[
#             ft.TextButton("Yes", on_click=save_transaction),
#             ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
#         ],
#     )

#     page.add(
#         ft.Text("Expense Tracker", size=30, weight="bold"),
#         ft.Divider(height=20, color="transparent"),
#         amount_field,
#         ft.Divider(height=20, color="transparent"),
#         btn_food,
#         ft.Divider(height=10, color="transparent"),
#         btn_stat,
#         ft.Divider(height=10, color="transparent"),
#         btn_dorm,
#     )

# ft.app(target=main)

## now have a working "Backend" (Database) and "Logic Layer" (Clipboard/Redirect).


import flet as ft
import sqlite3
import datetime
import calendar

def main(page: ft.Page):
    # --- 1. APP SETTINGS ---
    page.title = "IIT Dhanbad Expense Tracker"
    page.window_width = 400
    page.window_height = 750
    page.theme_mode = ft.ThemeMode.LIGHT # Force light mode for better colors

    # --- 2. BACKEND & LOGIC ---
    
    # HARDCODED BUDGETS (For the MVP)
    # In the future, we can let the user edit these
    TOTAL_BUDGET = 5000 
    
    def init_db():
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                category TEXT,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    init_db()

    def add_to_db(amount, category):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO transactions (amount, category, date) VALUES (?, ?, ?)", 
                       (amount, category, current_date))
        conn.commit()
        conn.close()

    # --- NEW: ANALYTICS ENGINE ---
    def get_dashboard_data():
        """Reads DB and calculates stats for the 'Power BI' Dashboard"""
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        
        # Query 1: Total Spent
        cursor.execute("SELECT SUM(amount) FROM transactions")
        result = cursor.fetchone()[0]
        total_spent = result if result else 0 # Handle case where DB is empty
        
        # Query 2: Category Breakdown
        cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
        breakdown = cursor.fetchall() # Returns list like [('Food', 150), ('Dorm', 500)]
        
        conn.close()
        
        # LOGIC: The Pacing Calculation
        # 1. How much time has passed?
        today = datetime.date.today()
        # Get total days in current month (e.g., 30 or 31)
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        time_passed_pct = today.day / days_in_month
        
        # 2. How much budget is spent?
        budget_spent_pct = total_spent / TOTAL_BUDGET
        
        # 3. The Pacing Score (The "Red/Green" Logic)
        # Avoid division by zero if it's the 1st of the month
        pacing_score = budget_spent_pct / time_passed_pct if time_passed_pct > 0 else 0
        
        return total_spent, breakdown, pacing_score, budget_spent_pct

    # --- 3. UI COMPONENTS (The Views) ---

    # -- VIEW A: HOME (Input) --
    amount_field = ft.TextField(label="Amount (₹)", text_align=ft.TextAlign.CENTER, width=200, keyboard_type=ft.KeyboardType.NUMBER)
    current_transaction = {"amount": 0, "category": ""}

    def save_transaction(e):
        add_to_db(current_transaction["amount"], current_transaction["category"])
        page.close(confirm_dialog)
        amount_field.value = ""
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Saved! Check Stats tab.")))
        page.update()

    def handle_payment(e):
        user_amount = amount_field.value
        category_name = e.control.text 
        if not user_amount:
            amount_field.error_text = "Required"
            page.update()
            return
        
        current_transaction["amount"] = user_amount
        current_transaction["category"] = category_name
        page.set_clipboard(user_amount)
        
        # Attempt Deep Link (Will fail gracefully on laptop)
        try:
            page.launch_url(f"upi://pay?am={user_amount}&cu=INR")
        except:
            pass # Ignore errors on laptop
            
        page.open(confirm_dialog)

    confirm_dialog = ft.AlertDialog(
        title=ft.Text("Confirm"),
        content=ft.Text("Payment successful?"),
        actions=[
            ft.TextButton("Yes", on_click=save_transaction),
            ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
        ],
    )

    def create_pay_button(text, color):
        return ft.ElevatedButton(text=text, width=200, height=50, bgcolor=color, color=ft.Colors.WHITE, on_click=handle_payment)

    home_view = ft.Column(
        [
            ft.Container(height=50), # Spacer
            ft.Text("Quick Pay", size=30, weight="bold"),
            ft.Divider(height=20, color="transparent"),
            amount_field,
            ft.Divider(height=20, color="transparent"),
            create_pay_button("Food", ft.Colors.BLUE_400),
            ft.Divider(height=10, color="transparent"),
            create_pay_button("Stationary", ft.Colors.ORANGE_400),
            ft.Divider(height=10, color="transparent"),
            create_pay_button("Dorm", ft.Colors.PURPLE_400),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # -- VIEW B: STATS (Dashboard) --
    # We define the dashboard elements here, but we will UPDATE them dynamically
    
    txt_total_spent = ft.Text("₹0", size=40, weight="bold")
    txt_pacing_status = ft.Text("Calculating...", size=16)
    
    # The "Red/Green" Bar
    pacing_bar = ft.ProgressBar(width=300, height=20, color=ft.Colors.GREY, bgcolor=ft.Colors.GREY_200)
    
    # The Pie Chart Container (Starts empty)
    chart_container = ft.Column()

    stats_view = ft.Column(
        [
            ft.Container(height=30),
            ft.Text("Monthly Dashboard", size=25, weight="bold"),
            ft.Divider(),
            ft.Text("Total Spent"),
            txt_total_spent,
            ft.Divider(height=20, color="transparent"),
            
            ft.Text("Budget Pacing (Health)"),
            pacing_bar,
            txt_pacing_status,
            
            ft.Divider(height=30, color="transparent"),
            ft.Text("Category Breakdown"),
            chart_container, 
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO # Allow scrolling if content is long
    )

    # --- 4. NAVIGATION LOGIC ---
    
    def refresh_stats():
        """Runs every time you click the 'Stats' tab"""
        spent, breakdown, pacing, budget_pct = get_dashboard_data()
        
        # 1. Update Total
        txt_total_spent.value = f"₹{spent:.0f} / ₹{TOTAL_BUDGET}"
        
        # 2. Update Pacing Bar
        # Logic: If Pacing > 1.0 (Spending too fast) -> RED. Else -> GREEN.
        pacing_bar.value = min(budget_pct, 1.0) # Bar maxes out at 100%
        if pacing > 1.1: # 10% buffer
            pacing_bar.color = ft.Colors.RED_400
            txt_pacing_status.value = f"⚠️ CRITICAL: You are spending {pacing:.1f}x faster than time!"
            txt_pacing_status.color = ft.Colors.RED_400
        else:
            pacing_bar.color = ft.Colors.GREEN_400
            txt_pacing_status.value = "✅ ON TRACK: Your spending is healthy."
            txt_pacing_status.color = ft.Colors.GREEN_700

        # 3. Update Pie Chart
        # We dynamically build the chart sections based on DB data
        sections = []
        colors = [ft.Colors.BLUE_400, ft.Colors.ORANGE_400, ft.Colors.PURPLE_400, ft.Colors.GREEN_400]
        
        for i, item in enumerate(breakdown):
            cat_name = item[0]
            cat_amount = item[1]
            sections.append(
                ft.PieChartSection(
                    value=cat_amount,
                    title=f"{cat_name}\n{cat_amount:.0f}",
                    color=colors[i % len(colors)], # Cycle through colors
                    radius=50,
                    title_style=ft.TextStyle(size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                )
            )
        
        # Replace the old chart with the new one
        chart_container.controls = [
            ft.PieChart(sections=sections, sections_space=2, center_space_radius=40, height=200)
        ]
        page.update()

    def on_tab_change(e):
        # If user clicked "Stats" (Index 1), refresh the data
        if e.control.selected_index == 1:
            refresh_stats()

    # The Tabs Layout
    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="Pay", icon=ft.Icons.PAYMENT, content=home_view),
            ft.Tab(text="Stats", icon=ft.Icons.BAR_CHART, content=stats_view),
        ],
        expand=1,
    )

    page.add(t)

ft.app(target=main)

# A "student budget" app doesn't have to look cheap. We will upgrade the UI to use Cards, Shadows, Icons, and a Modern Color Palette.

# We are also adding a highly requested feature: Recent History.
# You will now see a list of your last 5 transactions right on the Home 
# screen, so you know exactly what you just logged.
# The "Fintech" Upgrade (Code)
# Replace your main.py with this polished version.

# Key Visual Changes:

# Modern Header: A blue container with rounded corners at the top.
# Cards: The buttons are now "Action Cards" with icons.
# History List: A scrollable list showing your recent spending.
# Dashboard Polish: The stats are now enclosed in "Data Cards" with shadows.

