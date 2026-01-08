# Button styles 

# This file will primarily handle the "Category Buttons" 
# Food, Dorm, Stationary 

import flet as ft 
from config import BG_CARD, PRIMARY_COLOR

def create_category_button(text, icon, color, on_click):

    # ft.Container : Box, holds everything
    # ft.Column : For an icon on top and text below, use a column 

    return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=30),
                ft.Text(text, color=PRIMARY_COLOR, weight="bold")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            width=100, height=100,
            bgcolor=BG_CARD,
            border_radius=15,
            on_click=on_click, # ensures the function runs when clicked
            data=text, # IMP : after on_click, tells which category was clicked, stores the category name, later retrieved using "e.control.data"
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            ink=True # Enables the ripple effect
        )

def create_quick_chip(amount, on_click):
    """
    Creates the small '+10', '+50' chips.
    """
    return ft.Container(
        content=ft.Text(f"+₹{amount}", size=12, color=PRIMARY_COLOR, weight="bold"),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=20,
        on_click=on_click,
        data=amount, # Store the integer value here
        ink=True
    )