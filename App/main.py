# Entry point

# Tasks for main.py 
# 1. Start the database 
# 2. Switch between the "Home" and "Stats" tab

import flet as ft 
from database import init_db
from views.home_view import HomeView
from views.stats_view import StatsView
from config import APP_TITLE, BG_MAIN, PRIMARY_COLOR 

def main(page: ft.Page):
    
    # App Configuration 
    page.title = APP_TITLE 
    page.bgcolor = BG_MAIN 
    page.padding = 0 

    # Simulating mobile dimensions for easy viewing on laptop 
    page.window_width = 400 
    page.window_height = 800 

    # initialising database and creating a table if one does'nt exist before
    init_db()

    # load_views 
    home = HomeView(page)
    stats = StatsView(page)

    # navigation logic 
    def change_tab(e):
        # clear current page 
        page.controls.clear()

        # add the selected view 
        if e.control.selected_index == 0:
            page.add(home)
        else:
            # If switching to stats, refresh the data first 
            stats.data()
            page.add(stats)

        # Always add the nav bar back to the bottom 
        page.add(nav_bar)
        page.update()

    # creating navigation bar 
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationDestination(icon=ft.Icons.PIE_CHART, label="Stats"),
        ],
        selected_index=0,
        on_change=change_tab,
        bgcolor=ft.Colors.WHITE,
        indicator_color=PRIMARY_COLOR,
    )

    # initial render (with home page being displayed first)
    page.add(home)
    page.add(nav_bar)

ft.app(target=main)
