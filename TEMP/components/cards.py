import flet as ft
from config import BG_CARD

def create_card(content, padding=15):
    return ft.Container(
        content=content,
        bgcolor=BG_CARD,
        padding=padding,
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        ),
        margin=ft.margin.symmetric(horizontal=20)
    )
