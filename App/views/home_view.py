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
        # label = "Enter Amount", prefix_text="₹ ", text_style=ft.TextStyle(size=20, weight="bold"),
        label = "Enter Amount", prefix=ft.Text("₹ "), text_style=ft.TextStyle(size=20, weight="bold"),
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

        rows = get_recent_transactions() # query to get the raw data
        history_column.controls.clear() # IMP : Clears everything currently shown before adding new items 

        if not rows:
            history_column.controls.append(ft.Text("No transactions yet.", color="grey", size=12))

        for row in rows:
            trans_id, cat, amt, date_str = row
            dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") # converts into python date object
            time_str = dt_obj.strftime("%d %b, %I:%M %p") # converts python date into pretty string like "27 Oct, 10:30 AM"
            
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE, 
                icon_color="red", 
                on_click=lambda e, x=trans_id: delete_item(x)
            ) # rather than on_click = delete_item(trans_id) which would run the delete func immediately upon startup, 
            # wrapping it into a lambda function, essentially meaning "Wait until the user actually clicks, then call delete_item
            # specifically with one particular row's ID (x=trans_id)
            
            history_column.controls.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=PRIMARY_COLOR),
                    title=ft.Text(cat, weight="bold"),
                    subtitle=ft.Text(time_str, size=12),
                    trailing=ft.Row([ft.Text(f"- ₹{amt:.0f}", weight="bold"), delete_btn], alignment=ft.MainAxisAlignment.END, width=100),
                    dense=True
                ) # building the actual UI row seen on the screen
            )
            history_column.controls.append(ft.Divider(height=1, color=ft.Colors.GREY_100))
        page.update() # forcing the page to redraw with the new list 


    def delete_item(item_id): # action handler for the delete button

        # Finds the specific ID in the database, and permanently erases it 
        delete_transaction(item_id)
        refresh_history() # for UI update, imp for redrawing screen
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Transaction Deleted"))) # triggers a disappearing pop-up message 

    def add_quick_amount(e):
        
        current_val = amount_field.value if amount_field.value else "0" # grabs the value from the text box
        try:
            new_val = int(current_val) + e.control.data # e.control.data = value entered + quick-chip value 
            amount_field.value = str(new_val)
            amount_field.update() # command to redraw text box with new number
        except:
            amount_field.value = str(e.control.data) # safety net, incase of incompatible value takes only the quick-chip value 
            amount_field.update()

    def save_transaction(e):

        # The "Commit Action" function, runs only after the user clicks "Yes" 
        # on the pop-up dialog, confirming that their UPI payment went through.

        # Performs the final cleanup and storage operations 
        
        add_to_db(state["current_amount"], state["current_category"]) # sends amount and category values to the database 
        page.close(confirm_dialog) # removes the payment confirmation box for the app to be visible again
        amount_field.value = "" # Resetting the user-input form
        refresh_history() # re-fetches the list from the database 
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Saved!")))
        page.update()

        # Without this function (state dictionary) acting as a bridge, the data would be lost during the gap (i.e. redirecting to UPI app and coming back)

    def handle_payment(e):
        
        # IMP : Handles the transition for the app to the payment app 

        user_amount = amount_field.value 
        if not user_amount:
            amount_field.error_text = "Required" # turns the text box "red" if it's empty
            amount_field.update()
            return 
        
        # when handle_payment finishes running, local variables are lost
        # therefore, storing the user input values while the user is away in the UPI app
        state["current_amount"] = user_amount 
        state["current_category"] = e.control.data 

        # page.set_clipboard(user_amount)
        try:
            page.launch_url(f"upi://pay?am={user_amount}&cu=INR")
            # (IMP) USP : Copies the user amount to the clipboard, if the app does'nt auto-fill
            # the amount, the user can just hit "Paste"

            # page.launch_url() tells the phone's OS to open any app that can handle UPI payments 
            # am={user_amount} Auto-fills the amount 
            # cu=Sets currency to Indian Rupees 
    
        except: # to prevent the app from crashing (FOR DESKTOP TESTING PROCESS)
            pass 
        page.open(confirm_dialog) # banks dont tell local apps easily if the payment succeeded,
                                  #  therefore need a manual prompt for confirmation


    # -- Dialogs -- 

    # sets up the confirmation logic 

    confirm_dialog = ft.AlertDialog(
        title = ft.Text("Payment Confirmation"),
        content = ft.Text("Did the payment complete successfully?"), 
        actions = [
            ft.TextButton("Yes", on_click=save_transaction),
            ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog))
        ],
        actions_alignment = ft.MainAxisAlignment.END
    )

    # Settings logic 

    # settings popup that will allow users to change their monthly budget limit 
    # will consist of 
    # - input field - action logic - dialog container 

    budget_input = ft.TextField(label="Monthly Budget", value=str(get_budget()), keyboard_type=ft.KeyboardType.NUMBER)
    # value=str(get_budget()) -> instead of an empty box, shows the current budget from the database, pre-fills the box, 
    # shows the current_limit before changing it 

    def save_settings_action(e):
        try: 
            set_budget(float(budget_input.value)) # Updates database
            page.close(settings_dialog) # Close popup 
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Budget Updated!"))) # Confirmation message 
        except:
            pass # Ignore errors 

    settings_dialog = ft.AlertDialog(
        title = ft.Text("Settings"), 
        content = ft.Column([ft.Text("Set your monthly limit:"), budget_input], height=100), 
        actions = [ft.TextButton("Save", on_click=save_settings_action)] # opens only on pressing the "gear" icon
    )

    # --- Layout Assembly ---
    quick_chips_row = ft.Row(
        [
            create_quick_chip(10, add_quick_amount), 
            create_quick_chip(20, add_quick_amount), 
            create_quick_chip(50, add_quick_amount), 
            create_quick_chip(100, add_quick_amount)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )    

    # Initial load 
    refresh_history()

    # Architect Code 
    # No maths or database connections, just aligning all the buttons, inputs and lists 
    # vertically on the screen

    # returns a single ft.Column (i.e. a vertical stack) containing 4 distinct visual sections
    return ft.Column(
        [
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Column([ft.Text("Good Evening,", color=ft.Colors.WHITE70, size=14), ft.Text("Student", color=ft.Colors.WHITE, size=24, weight="bold")]),
                    ft.IconButton(ft.Icons.SETTINGS, icon_color="white", on_click=lambda e: page.open(settings_dialog))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                width=400, height=120, bgcolor=PRIMARY_COLOR, padding=ft.padding.only(left=20, right=10, top=40, bottom=20),
                border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30)
            ),
            ft.Container(height=20),
            
            # Input
            create_card(ft.Column([
                ft.Text("How much?", color="grey", size=12),
                amount_field,
                ft.Container(height=10),
                quick_chips_row
            ], horizontal_alignment=ft.MainAxisAlignment.CENTER)),

            ft.Container(height=20),
            
            # Categories
            ft.Row([
                create_category_button("Food", ft.Icons.FASTFOOD, ft.Colors.BLUE, handle_payment),
                create_category_button("Stationary", ft.Icons.EDIT, ft.Colors.ORANGE, handle_payment),
                create_category_button("Dorm", ft.Icons.BED, ft.Colors.PURPLE, handle_payment),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15),
            
            ft.Container(height=30),
            
            # History
            ft.Container(content=ft.Column([ft.Text("Recent Transactions", weight="bold", size=16, color=PRIMARY_COLOR), history_column]), padding=20)
        ],
        scroll=ft.ScrollMode.AUTO, spacing=0
    )




