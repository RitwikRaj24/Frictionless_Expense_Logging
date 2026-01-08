# def create_category():
#     pass

# def create_preset_amount():
#     pass
import flet as ft
from config import BG_CARD, PRIMARY_COLOR

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
        data=text, # We store the category name here
        shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        ink=True
    )

def create_quick_chip(amount, on_click):
    return ft.Container(
        content=ft.Text(f"+₹{amount}", size=12, color=PRIMARY_COLOR, weight="bold"),
        padding=10,
        bgcolor=ft.Colors.BLUE_50,
        border_radius=20,
        on_click=on_click,
        data=amount, # Store the integer value here
        ink=True
    )
