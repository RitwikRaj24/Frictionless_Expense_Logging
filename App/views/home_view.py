# The Home Tab 

# Handles the inputs, category buttons and the transaction list 

import flet as ft 
import datetime 

from config import PRIMARY_COLOR
from database import add_to_db, get_recent_transactions, delete_transaction, set_budget, get_budget
from components.cards import create_card
from components.buttons import create_category_button, create_quick_chip

def HomeView(page):

    # Setting up a 
    # 1. User input(amount_field) 2. Placeholder for the List 3. Memory box for tracking what the user is doing 

    amount_field = ft.TextField(
        label = "Enter Amount", prefix_text="₹ ", text_style=ft.TextStyle(size=20, weight="bold"),
        border_color="transparent", bgcolor=ft.Colors.GREY_100, text_align=ft.TextAlign.CENTER, 
        keyboard_type=ft.KeyboardType.NUMBER, border_radius=10
    )

    # keyboard_type = ft.KeyboardType.NUMBER is critical for mobile apps for the numerical keyboard to pop up automatically 
    
    history_column = ft.Column(spacing=0)
    # For injecting the rows of "Recent Transactions" from the database DYNAMICALLY 

    # Using a dictionary to track state which will be mutable 
    state = {"current_amount": 0, "current_category": ""}

    def refresh_history():

        # What does this do ? 
        
        # Erases the old list of transactions on the screen and redraws it with the 
        # absolute latest data from the database 



        rows = get_recent_transactions()
        history_column.controls.clear()
        if not rows:
            history_column.controls.append(ft.Text("No transactions yet.", color="grey", size=12))

        for row in rows:
            trans_id, cat, amt, date_str = row
            dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            time_str = dt_obj.strftime("%d %b, %I:%M %p")
            
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE, 
                icon_color="red", 
                on_click=lambda e, x=trans_id: delete_item(x)
            )
            
            history_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=PRIMARY_COLOR),
                    title=ft.Text(cat, weight="bold"),
                    subtitle=ft.Text(time_str, size=12),
                    trailing=ft.Row([ft.Text(f"- ₹{amt:.0f}", weight="bold"), delete_btn], alignment=ft.MainAxisAlignment.END, width=100),
                    dense=True
                )
            )
            history_column.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_100))
        page.update()


    def delete_item(item_id):
        pass 
    def add_quick_amount(e):
        pass 
    def save_transaction(e):
        pass 
    def handle_payment(e):
        pass 
    def save_settings_action(e):
        pass 





