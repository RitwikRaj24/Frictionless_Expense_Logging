import flet as ft
from config import APP_TITLE, BG_MAIN
from database import init_db
from views.home_view import HomeView
from views.stats_view import StatsView

def main(page: ft.Page):
    
    # --- 1. SETUP ---
    page.title = APP_TITLE
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = BG_MAIN
    page.padding = 0 
    
    init_db()

    # --- 2. LOAD VIEWS ---
    home_view = HomeView(page)
    stats_view = StatsView(page)
    stats_view.visible = False

    # --- 3. NAVIGATION LOGIC ---
    def change_tab(e):
        index = e.control.selected_index
        if index == 0:
            home_view.visible = True
            stats_view.visible = False
        elif index == 1:
            home_view.visible = False
            stats_view.visible = True
            if hasattr(stats_view, 'data'):
                stats_view.data() 
        page.update()

    # --- 4. UI ASSEMBLY ---
    nav_bar = ft.NavigationBar(
        destinations=[
            # FIX: The correct class for Flet 0.80+ is NavigationBarDestination
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.PIE_CHART, label="Stats"),
        ],
        selected_index=0,
        on_change=change_tab,
        bgcolor="white",
        indicator_color=ft.Colors.BLUE_50
    )

    page.add(
        ft.Column([home_view, stats_view], expand=True), 
        nav_bar
    )

if __name__ == "__main__":
    # FIX: Use run() instead of app() to stop the DeprecationWarning
    # ft.app(target=main)
    ft.run(main=main)