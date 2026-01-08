# The Dashboard tab

# responsible for taking raw numbers from the database and turning them into 
# visual elements like a Progress Bar and a Pie Chart 

import flet as ft 
from config import PRIMARY_COLOR
from database import get_dashboard_data
from components.cards import create_card

def StatsView(page):
    txt_total_spent = ft.Text("₹0", size=30, weight="bold", color=PRIMARY_COLOR)
    txt_pacing_status = ft.Text("...", size=14)
    pacing_bar = ft.ProgressBar(width=300, height=15, color=ft.Colors.GREY, bgcolor=ft.Colors.GREY_100, border_radius=5)
    chart_container = ft.Column() # for pie charts 

    def refresh_stats(): # logic engine, runs every time the tab opens
        spent, breakdown, pacing, budget_pct, current_limit = get_dashboard_data() 
        
        # Update Top Cards
        txt_total_spent.value = f"₹{spent:.0f} / ₹{current_limit:.0f}"
        pacing_bar.value = min(budget_pct, 1.0)
        
        if pacing > 1.1: # If spending is 10% faster than time is passing, it turns the bar Red (eg. 50% budget spent by day 5)
            pacing_bar.color = ft.Colors.RED
            txt_pacing_status.value = "⚠️ Spending too fast!"
            txt_pacing_status.color = ft.Colors.RED
        else: # spending within control, bar stays Green 
            pacing_bar.color = ft.Colors.GREEN
            txt_pacing_status.value = "✅ Safe Zone"
            txt_pacing_status.color = ft.Colors.GREEN

        # Chart Logic 
        sections = []
        colors = [ft.Colors.BLUE, ft.Colors.ORANGE, ft.Colors.PURPLE, ft.Colors.TEAL, ft.Colors.PINK]

        if not breakdown:
            chart_container.controls = [ft.Text("No data yet", color="grey")]
        else: 
            # Create Slices
            for i, item in enumerate(breakdown):
                sections.append(
                    ft.PieChartSection(
                        value=item[1], 
                        title=f"{item[0][0]}", 
                        color=colors[i % len(colors)], 
                        radius=40, 
                        title_style=ft.TextStyle(size=14, color="white", weight="bold")
                    )
                )
            
            # Create Legend
            legend_items = []
            for i, item in enumerate(breakdown):
                legend_items.append(
                    ft.Row([
                        ft.Container(width=10, height=10, bgcolor=colors[i % len(colors)], border_radius=5), 
                        ft.Text(f"{item[0]}: ₹{item[1]:.0f}", size=12)
                    ])
                )
            
            # Add Chart to Container (OUTSIDE THE LOOP)
            chart_container.controls = [
                ft.Row(
                    [
                        ft.PieChart(sections=sections, sections_space=2, center_space_radius=30, height=150), 
                        ft.Column(legend_items)
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                )
            ]
        
        page.update()                    
        # We expose this function so the Main file can call it when the tab is clicked
        # We attach it to the Column object so it can be accessed externally
    view = ft.Column(
        [
            ft.Container(height=40),
            ft.Text("Analytics Dashboard", size=22, weight="bold", color=PRIMARY_COLOR),
            ft.Container(height=20),
            create_card(ft.Column([ft.Text("Total Spent", size=12, color="grey"), txt_total_spent], horizontal_alignment=ft.MainAxisAlignment.CENTER), padding=20),
            ft.Container(height=20),
            create_card(ft.Column([ft.Text("Budget Health", weight="bold"), ft.Container(height=10), pacing_bar, ft.Container(height=10), txt_pacing_status])),
            ft.Container(height=20),
            create_card(ft.Column([ft.Text("Breakdown", weight="bold"), ft.Container(height=20), chart_container], horizontal_alignment=ft.MainAxisAlignment.CENTER))
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO
    )
    
    view.data = refresh_stats 
    refresh_stats() 
    return view