# # Entry point

# # Tasks for main.py 
# # 1. Start the database 
# # 2. Switch between the "Home" and "Stats" tab

import sys 
print("Python Path: ", sys.executable)

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

    # nav_bar = ft.Container(
    #         content=ft.Row(
    #             [
    #                 ft.IconButton(icon=ft.Icons.HOME, icon_size=30, on_click=switch_to_home, icon_color=PRIMARY_COLOR),
    #                 ft.IconButton(icon=ft.Icons.PIE_CHART, icon_size=30, on_click=switch_to_stats, icon_color=PRIMARY_COLOR),
    #             ],
    #             alignment=ft.MainAxisAlignment.SPACE_EVENLY
    #         ),
    #         bgcolor=ft.Colors.WHITE,
    #         height=60,
    #         border_radius=ft.border_radius.only(top_left=15, top_right=15),
    #         shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12)
    #     )    

    # initial render (with home page being displayed first)
    page.add(home)
    page.add(nav_bar)

# ft.app(target=main)
ft.run(main=main)

# import flet as ft 
# from database import init_db
# from views.home_view import HomeView
# from views.stats_view import StatsView
# from config import APP_TITLE, BG_MAIN, PRIMARY_COLOR 

# def main(page: ft.Page):
    
#     # 1. App Configuration 
#     page.title = APP_TITLE 
#     page.bgcolor = BG_MAIN 
#     page.padding = 0 

#     # Simulating mobile dimensions (Comment out if causing issues on Mac)
#     page.window_width = 400 
#     page.window_height = 800 

#     # 2. Initialise Database
#     init_db()

#     # 3. Load Views 
#     home = HomeView(page)
#     stats = StatsView(page)

#     # 4. Navigation Logic 
#     # We define specific functions for the specific buttons below
#     def switch_to_home(e):
#         page.controls.clear()
#         page.add(home)
#         page.add(nav_bar)
#         page.update()

#     def switch_to_stats(e):
#         page.controls.clear()
#         stats.data() # Refresh the stats data
#         page.add(stats)
#         page.add(nav_bar)
#         page.update()

#     # 5. Create Navigation Bar 
#     nav_bar = ft.Container(
#         content=ft.Row(
#             [
#                 ft.IconButton(icon=ft.Icons.HOME, icon_size=30, on_click=switch_to_home, icon_color=PRIMARY_COLOR),
#                 ft.IconButton(icon=ft.Icons.PIE_CHART, icon_size=30, on_click=switch_to_stats, icon_color=PRIMARY_COLOR),
#             ],
#             alignment=ft.MainAxisAlignment.SPACE_EVENLY
#         ),
#         bgcolor=ft.Colors.WHITE,
#         height=60,
#         border_radius=ft.border_radius.only(top_left=15, top_right=15),
#         shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.BLACK12)
#     )    

#     # 6. Initial Render
#     page.add(home)
#     page.add(nav_bar)

# ft.app(target=main)
