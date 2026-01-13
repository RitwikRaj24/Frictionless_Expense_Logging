import flet as ft 
from config import BG_CARD

def create_card(content, padding=15):
    """
    Creates a standardized white card with shadow.
    """
    return ft.Container(
        content=content,
        bgcolor=BG_CARD,
        padding=padding,
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            # FIX: Use the built-in transparent black constant
            color=ft.Colors.BLACK12, 
        ),
        margin=ft.margin.symmetric(horizontal=20)
    )