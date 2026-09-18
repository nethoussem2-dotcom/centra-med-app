import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import database
import auth
import translations

def get_view(page: ft.Page):
    current_user = auth.get_current_user()
    username_scope = None if current_user['role'] in ('admin', 'visitor') else current_user['username']
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    # Refresh metrics
    stats = database.get_overall_stats(username_scope)
    machine_stats = database.get_production_by_machine(username_scope)
    product_stats = database.get_production_by_product(username_scope, limit=5)
    trends = database.get_daily_production_trends(username_scope, limit=10)

    # 1. Helper function to create a gorgeous glassmorphic KPI card
    def create_kpi_card(title, value, unit, icon, icon_color, gradient_colors):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(title, size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), weight=ft.FontWeight.W_500, rtl=rtl),
                            ft.Row(
                                controls=[
                                    ft.Text(f"{value:,}" if isinstance(value, (int, float)) else str(value), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                                    ft.Text(unit, size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), weight=ft.FontWeight.W_500) if unit else ft.Container()
                                ],
                                spacing=5,
                                vertical_alignment=ft.CrossAxisAlignment.BASELINE
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START
                    ),
                    ft.Container(
                        content=ft.Icon(icon, size=30, color=icon_color),
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.colors.with_opacity(0.1, icon_color),
                    )
                ] if rtl else [
                    ft.Container(
                        content=ft.Icon(icon, size=30, color=icon_color),
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.colors.with_opacity(0.1, icon_color),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(title, size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), weight=ft.FontWeight.W_500, rtl=rtl),
                            ft.Row(
                                controls=[
                                    ft.Text(f"{value:,}" if isinstance(value, (int, float)) else str(value), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                                    ft.Text(unit, size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), weight=ft.FontWeight.W_500) if unit else ft.Container()
                                ],
                                spacing=5,
                                vertical_alignment=ft.CrossAxisAlignment.BASELINE
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        horizontal_alignment=ft.CrossAxisAlignment.START
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            border_radius=16,
            expand=True,
            bgcolor=ft.colors.with_opacity(0.08, ft.colors.SURFACE),
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=gradient_colors
            )
        )

    # Conditional color for waste rate KPI
    waste_rate = stats['waste_rate_pct']
    waste_color = ft.colors.GREEN_400 if waste_rate <= 3.0 else (ft.colors.ORANGE_400 if waste_rate <= 7.0 else ft.colors.RED_400)
    
    # KPI Grid Row
    kpis = ft.Row(
        controls=[
            create_kpi_card(translations.t('kpi_waste_rate', page), f"{waste_rate:.2f}", "%", ft.icons.PERCENT, waste_color, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.05, waste_color)]),
            create_kpi_card(translations.t('kpi_waste_kg', page), round(stats['total_waste_kg'], 1), translations.t('unit_kg', page), ft.icons.DELETE_OUTLINE, ft.colors.RED_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.RED_900)]),
            create_kpi_card(translations.t('kpi_weight_kg', page), round(stats['total_weight_kg'], 1), translations.t('unit_kg', page), ft.icons.SCALE, ft.colors.BLUE_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.BLUE_900)]),
            create_kpi_card(translations.t('kpi_qty', page), int(stats['total_qty']), translations.t('unit_pcs', page), ft.icons.SETTINGS, ft.colors.TEAL_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.TEAL_900)]),
        ] if rtl else [
            create_kpi_card(translations.t('kpi_qty', page), int(stats['total_qty']), translations.t('unit_pcs', page), ft.icons.SETTINGS, ft.colors.TEAL_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.TEAL_900)]),
            create_kpi_card(translations.t('kpi_weight_kg', page), round(stats['total_weight_kg'], 1), translations.t('unit_kg', page), ft.icons.SCALE, ft.colors.BLUE_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.BLUE_900)]),
            create_kpi_card(translations.t('kpi_waste_kg', page), round(stats['total_waste_kg'], 1), translations.t('unit_kg', page), ft.icons.DELETE_OUTLINE, ft.colors.RED_400, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.03, ft.colors.RED_900)]),
            create_kpi_card(translations.t('kpi_waste_rate', page), f"{waste_rate:.2f}", "%", ft.icons.PERCENT, waste_color, [ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE), ft.colors.with_opacity(0.05, waste_color)]),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 2. Daily Production & Waste Trends LineChart
    if len(trends) >= 2:
        trend_points_qty = []
        trend_points_waste = []
        x_labels = []
        
        max_qty = 1000
        max_waste = 100
        
        for idx, t in enumerate(trends):
            date_short = t['date'][5:]  # Extract MM-DD
            x_labels.append(date_short)
            trend_points_qty.append(ft.LineChartDataPoint(idx, t['total_qty']))
            trend_points_waste.append(ft.LineChartDataPoint(idx, t['total_waste_kg'] * 100))  # Scale up waste to see on same axis
            max_qty = max(max_qty, t['total_qty'])
            max_waste = max(max_waste, t['total_waste_kg'] * 100)
            
        line_chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=trend_points_qty,
                    stroke_width=3,
                    color=ft.colors.TEAL_400,
                    curved=True
                ),
                ft.LineChartData(
                    data_points=trend_points_waste,
                    stroke_width=2,
                    color=ft.colors.RED_400,
                    curved=True
                )
            ],
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max(1000, max_qty // 5),
                color=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE),
                width=1
            ),
            bottom_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(x_labels[i] if i < len(x_labels) else "", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))) for i in range(len(x_labels))],
                show_labels=True,
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))),
                    ft.ChartAxisLabel(value=max_qty//2, label=ft.Text(f"{int(max_qty//2):,}", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))),
                    ft.ChartAxisLabel(value=max_qty, label=ft.Text(f"{int(max_qty):,}", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))),
                ],
                show_labels=True,
            ),
            expand=True,
            interactive=True
        )
        line_chart_content = ft.Container(content=line_chart, expand=True, padding=10)
    else:
        line_chart_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.SHOW_CHART, size=40, color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE)),
                    ft.Text(translations.t('trend_empty', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE), rtl=rtl, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            expand=True
        )
        
    line_chart_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=ft.colors.RED_400, border_radius=5),
                                ft.Text(translations.t('trend_waste_scaled', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                                ft.Container(width=10, height=10, bgcolor=ft.colors.TEAL_400, border_radius=5),
                                ft.Text(translations.t('trend_qty', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                            ] if (len(trends) >= 2 and rtl) else (
                                [
                                    ft.Container(width=10, height=10, bgcolor=ft.colors.TEAL_400, border_radius=5),
                                    ft.Text(translations.t('trend_qty', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                                    ft.Container(width=10, height=10, bgcolor=ft.colors.RED_400, border_radius=5),
                                    ft.Text(translations.t('trend_waste_scaled', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                                ] if len(trends) >= 2 else []
                            ),
                            spacing=15
                        ),
                        ft.Text(translations.t('trend_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                    ] if rtl else [
                        ft.Text(translations.t('trend_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                        ft.Row(
                            controls=[
                                ft.Container(width=10, height=10, bgcolor=ft.colors.TEAL_400, border_radius=5),
                                ft.Text(translations.t('trend_qty', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                                ft.Container(width=10, height=10, bgcolor=ft.colors.RED_400, border_radius=5),
                                ft.Text(translations.t('trend_waste_scaled', page), size=12, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE)),
                            ] if len(trends) >= 2 else [],
                            spacing=15
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=10),
                line_chart_content
            ],
            expand=True
        ),
        padding=20,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        height=320,
        expand=2
    )

    # 3. BarChart: Machine Production Comparison
    if machine_stats:
        bar_groups = []
        machine_names = []
        max_m_qty = 1000
        
        for idx, m in enumerate(machine_stats[:5]):
            machine_names.append(m['machine'])
            bar_groups.append(
                ft.BarChartGroup(
                    x=idx,
                    bar_rods=[
                        ft.BarChartRod(
                            to_y=max(0.1, m['total_qty']),
                            color=ft.colors.TEAL_600 if idx % 2 == 0 else ft.colors.BLUE_600,
                            width=18,
                            border_radius=0,
                            tooltip=f"{m['machine']}: {int(m['total_qty']):,} " + (translations.t('unit_pcs', page)),
                        )
                    ]
                )
            )
            max_m_qty = max(max_m_qty, m['total_qty'])

        machine_chart = ft.BarChart(
            bar_groups=bar_groups,
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max(1000, max_m_qty // 4),
                color=ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)
            ),
            bottom_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(machine_names[i], size=10, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE))) for i in range(len(machine_names))],
                show_labels=True
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))),
                    ft.ChartAxisLabel(value=max_m_qty, label=ft.Text(f"{int(max_m_qty):,}", size=10, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)))
                ],
                show_labels=True
            ),
            expand=True,
            interactive=True
        )
        machine_chart_content = ft.Container(content=machine_chart, expand=True, padding=10)
    else:
        machine_chart_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.BAR_CHART_OUTLINED, size=40, color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE)),
                    ft.Text(translations.t('machine_empty', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE), rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            expand=True
        )
        
    machine_chart_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(translations.t('machine_compare_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                ft.Container(height=10),
                machine_chart_content
            ],
            expand=True
        ),
        padding=20,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        height=320,
        expand=1
    )

    # Charts Row
    charts_row = ft.Row(
        controls=[machine_chart_container, line_chart_container] if rtl else [line_chart_container, machine_chart_container],
        spacing=20,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # 4. Pie Chart: Top Products share & Machine efficiency list
    if product_stats:
        pie_sections = []
        colors_list = [ft.colors.TEAL_400, ft.colors.BLUE_400, ft.colors.ORANGE_400, ft.colors.PURPLE_400, ft.colors.PINK_400]
        legend_controls = []
        
        total_p_qty = sum(p['total_qty'] for p in product_stats)
        for idx, p in enumerate(product_stats):
            color = colors_list[idx % len(colors_list)]
            percentage = (p['total_qty'] / total_p_qty * 100) if total_p_qty > 0 else 0
            
            # Pie Section
            pie_sections.append(
                ft.PieChartSection(
                    value=p['total_qty'],
                    title=f"{percentage:.0f}%",
                    title_style=ft.TextStyle(size=11, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    color=color,
                    radius=50
                )
            )
            
            # Legend Item
            legend_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(f"{p['designation']} ({int(p['total_qty']):,})", size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl, expand=True),
                        ft.Container(width=12, height=12, bgcolor=color, border_radius=4),
                    ] if rtl else [
                        ft.Container(width=12, height=12, bgcolor=color, border_radius=4),
                        ft.Text(f"{p['designation']} ({int(p['total_qty']):,})", size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl, expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START,
                    spacing=8
                )
            )
            
        pie_chart = ft.PieChart(
            sections=pie_sections,
            sections_space=2,
            center_space_radius=40,
            expand=True
        )
        
        product_chart_content = ft.Row(
            controls=[
                ft.Column(
                    controls=legend_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START,
                    spacing=8,
                    expand=True
                ),
                ft.Container(content=pie_chart, width=200, height=200),
                ft.Column(
                    controls=[
                        ft.Text(translations.t('product_dist_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START
                )
            ] if rtl else [
                ft.Column(
                    controls=[
                        ft.Text(translations.t('product_dist_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START
                ),
                ft.Container(content=pie_chart, width=200, height=200),
                ft.Column(
                    controls=legend_controls,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=8,
                    expand=True
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    else:
        product_chart_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.icons.PIE_CHART_OUTLINE, size=40, color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE)),
                    ft.Text(translations.t('product_empty', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE), rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            expand=True
        )
        
    product_chart_container = ft.Container(
        content=product_chart_content,
        padding=20,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        height=220,
        expand=1
    )

    # 5. Machine waste details list
    machine_rows = []
    if machine_stats:
        for m in machine_stats:
            m_rate = m['waste_rate_pct']
            m_color = ft.colors.GREEN_400 if m_rate <= 3.0 else (ft.colors.ORANGE_400 if m_rate <= 7.0 else ft.colors.RED_400)
            machine_rows.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{m_rate:.2f}%", size=14, color=m_color, weight=ft.FontWeight.BOLD),
                            ft.Text(f"{round(m['total_waste_kg'], 1)} " + (translations.t('unit_kg', page)), size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)),
                            ft.Text(f"{int(m['total_qty']):,} " + (translations.t('unit_pcs', page)), size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)),
                            ft.Text(m['machine'], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400),
                        ] if rtl else [
                            ft.Text(m['machine'], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400),
                            ft.Text(f"{int(m['total_qty']):,} " + (translations.t('unit_pcs', page)), size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)),
                            ft.Text(f"{round(m['total_waste_kg'], 1)} " + (translations.t('unit_kg', page)), size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)),
                            ft.Text(f"{m_rate:.2f}%", size=14, color=m_color, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=ft.padding.symmetric(vertical=8, horizontal=15),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)))
                )
            )

    machine_list_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(translations.t('machine_list_col_rate', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_waste', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_good', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_mach', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                        ] if rtl else [
                            ft.Text(translations.t('machine_list_col_mach', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_good', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_waste', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                            ft.Text(translations.t('machine_list_col_rate', page), size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.symmetric(horizontal=15)
                ),
                ft.Column(
                    controls=machine_rows if machine_rows else [
                        ft.Container(
                            content=ft.Text(translations.t('machine_list_empty', page), size=14, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE), text_align=ft.TextAlign.CENTER),
                            alignment=ft.alignment.center,
                            expand=True
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO,
                    spacing=0,
                    expand=True
                )
            ],
            expand=True
        ),
        padding=15,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        height=220,
        expand=1
    )

    bottom_row = ft.Row(
        controls=[machine_list_container, product_chart_container] if rtl else [product_chart_container, machine_list_container],
        spacing=20,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Main dashboard column (scrollable)
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(translations.t('dashboard_header', page).format(current_user['full_name']), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START
            ),
            ft.Container(height=10),
            kpis,
            ft.Container(height=15),
            charts_row,
            ft.Container(height=15),
            bottom_row
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH
    )
