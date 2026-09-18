import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import datetime
import database
import translations

def get_view(page: ft.Page):
    rtl = translations.is_rtl(page)
    
    # ------------------- Logic ------------------- #
    def analyze_data(records, rtl):
        if not records:
            return None
            
        total_qty = sum(r.get('qte_prod', 0) for r in records)
        total_waste = sum(r.get('dechet_kg', 0) for r in records)
        total_actual_w = sum(r.get('poid_reel', 0) for r in records)
        
        # Dynamically extract and sort machines to ensure consistent ordering
        all_machines = sorted(list(set(r['machine'] for r in records)))
        machine_stats = {m: {'qty': 0, 'waste': 0} for m in all_machines}
        
        product_stats = {}
        operator_stats = {}
        
        for r in records:
            m = r['machine']
            p = r['code_article']
            op = r['username']
            
            if m not in machine_stats: machine_stats[m] = {'qty': 0, 'waste': 0}
            if p not in product_stats: product_stats[p] = {'qty': 0, 'waste': 0}
            if op not in operator_stats: operator_stats[op] = {'qty': 0, 'waste': 0}
            
            qty = r.get('qte_prod', 0)
            waste = r.get('dechet_kg', 0)
            
            machine_stats[m]['qty'] += qty
            machine_stats[m]['waste'] += waste
            product_stats[p]['qty'] += qty
            product_stats[p]['waste'] += waste
            operator_stats[op]['qty'] += qty
            operator_stats[op]['waste'] += waste
            
        strengths = []
        weaknesses = []
        solutions = []
        
        # 1. Global Waste
        global_rate = (total_waste / (total_actual_w + total_waste)) * 100 if (total_actual_w + total_waste) > 0 else 0
        if global_rate < 3:
            strengths.append("معدل الهدر العام ممتاز وأقل من 3%." if rtl else "Le taux de rebut global est excellent (< 3%).")
        elif global_rate > 5:
            weaknesses.append(f"معدل الهدر العام مرتفع جداً ({global_rate:.1f}%)." if rtl else f"Le taux de rebut global est trop élevé ({global_rate:.1f}%).")
            solutions.append("مراجعة عامة لإعدادات جميع الآلات وجودة المواد الخام." if rtl else "Révision générale des paramètres machines et qualité matière.")
            
        # 2. Machine Performance
        active_machines = {k: v for k, v in machine_stats.items() if v['qty'] > 0 or v['waste'] > 0}
        if active_machines:
            best_machine = max(active_machines.items(), key=lambda x: x[1]['qty'])[0]
            strengths.append(f"الآلة '{best_machine}' تحقق أعلى إنتاجية." if rtl else f"La machine '{best_machine}' a la meilleure productivité.")
            
            worst_machines = sorted(active_machines.items(), key=lambda x: x[1]['waste'], reverse=True)
            if worst_machines and worst_machines[0][1]['waste'] > 10:
                wm = worst_machines[0][0]
                weaknesses.append(f"الآلة '{wm}' تسجل أعلى كمية نفايات." if rtl else f"La machine '{wm}' enregistre le plus de déchets.")
                solutions.append(f"إجراء صيانة وقائية ومعايرة عاجلة للآلة '{wm}'." if rtl else f"Faire une maintenance préventive pour la machine '{wm}'.")
                
        # 3. Operator Performance
        if operator_stats:
            best_op = max(operator_stats.items(), key=lambda x: x[1]['qty'])[0]
            strengths.append(f"المشغل '{best_op}' يتميز بأعلى كمية إنتاج." if rtl else f"L'opérateur '{best_op}' a la plus grande production.")
            
        # 4. Product Issues
        if product_stats:
            worst_products = sorted(product_stats.items(), key=lambda x: x[1]['waste'], reverse=True)
            if worst_products and worst_products[0][1]['waste'] > 5:
                wp = worst_products[0][0]
                weaknesses.append(f"المنتج '{wp}' يعاني من هدر كبير." if rtl else f"Le produit '{wp}' souffre d'un grand taux de rebut.")
                solutions.append(f"التحقق من قوالب ومعايير الإنتاج للمنتج '{wp}'." if rtl else f"Vérifier les moules du produit '{wp}'.")
                
        # Fallbacks
        if not strengths: strengths.append("الإنتاج مستقر بشكل عام." if rtl else "Production globalement stable.")
        if not weaknesses: weaknesses.append("لا توجد نقاط ضعف بارزة مسجلة." if rtl else "Aucun point faible majeur détecté.")
        if not solutions: solutions.append("الاستمرار على نفس وتيرة الإنتاج الحالية." if rtl else "Continuer sur le même rythme.")
        
        return {
            'qty': total_qty,
            'waste': total_waste,
            'global_rate': global_rate,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'solutions': solutions,
            'machine_stats': machine_stats
        }

    # ------------------- UI Components ------------------- #
    today_dt = datetime.date.today()
    
    view_type = ft.Dropdown(
        value="month",
        options=[
            ft.dropdown.Option("month", translations.t('analysis_month', page)),
            ft.dropdown.Option("year", translations.t('analysis_overall', page)),
        ],
        width=200,
        height=40,
        text_size=13,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        dense=True
    )
    
    month_dd = ft.Dropdown(
        value=str(today_dt.month),
        options=[ft.dropdown.Option(str(i), f"{i}") for i in range(1, 13)],
        width=70, height=40, text_size=13, dense=True
    )
    
    year_dd = ft.Dropdown(
        value=str(today_dt.year),
        options=[ft.dropdown.Option(str(y), f"{y}") for y in range(today_dt.year - 5, today_dt.year + 2)],
        width=80, height=40, text_size=13, dense=True
    )
    
    report_container = ft.Container(expand=True)
    
    def generate_report(e=None):
        v_type = view_type.value
        m = int(month_dd.value)
        y = int(year_dd.value)
        
        if v_type == "month":
            records = database.get_filtered_records(year=y, month=m)
            month_dd.visible = True
        else:
            records = database.get_filtered_records(year=y)
            month_dd.visible = False
            
        page.update()
            
        analysis = analyze_data(records, rtl)
        
        if not analysis:
            report_container.content = ft.Container(
                content=ft.Text(translations.t('analysis_empty', page), size=16, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                alignment=ft.alignment.center,
                padding=50
            )
        else:
            # Build AI Cards
            def build_bullet_list(items, icon, color):
                return ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=16),
                        ft.Text(item, size=14, color=ft.colors.with_opacity(0.9, ft.colors.ON_SURFACE), rtl=rtl)
                    ], rtl=rtl, vertical_alignment=ft.CrossAxisAlignment.START) for item in items
                ], spacing=10)
                
            def build_card(title, icon, color, items):
                return ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon, color=color, size=28),
                            ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=color, rtl=rtl)
                        ], rtl=rtl),
                        ft.Divider(color=ft.colors.with_opacity(0.1, color)),
                        build_bullet_list(items, ft.icons.ARROW_RIGHT if not rtl else ft.icons.ARROW_LEFT, color)
                    ], spacing=15),
                    bgcolor=ft.colors.with_opacity(0.05, color),
                    border=ft.border.all(1, ft.colors.with_opacity(0.1, color)),
                    border_radius=12,
                    padding=25,
                    expand=True
                )
                
            # Chart building
            chart_data = []
            max_qty = max((v['qty'] for v in analysis['machine_stats'].values()), default=1)
            for i, (m_name, m_data) in enumerate(analysis['machine_stats'].items()):
                chart_data.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=m_data['qty'],
                                width=40,
                                color=ft.colors.TEAL_400,
                                tooltip=f"{m_name}\nQty: {m_data['qty']:,}\nWaste: {m_data['waste']:,.2f}Kg",
                                border_radius=0,
                            ),
                        ],
                    )
                )
            
            machine_labels = list(analysis['machine_stats'].keys())
            chart = ft.BarChart(
                bar_groups=chart_data,
                border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Qty (Pcs)")),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=i, 
                            label=ft.Container(ft.Text(m, size=10), padding=10)
                        ) for i, m in enumerate(machine_labels)
                    ],
                    labels_size=40,
                ),
                horizontal_grid_lines=ft.ChartGridLines(
                    color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1, dash_pattern=[3, 3]
                ),
                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY_900),
                max_y=max_qty * 1.2,
                interactive=True,
                expand=True,
            )

            report_container.content = ft.Column([
                # KPI Row
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.SMART_TOY, color=ft.colors.PURPLE_400, size=40),
                            ft.Column([
                                ft.Text(translations.t('analysis_kpi', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl),
                                ft.Row([
                                    ft.Text(f"Total Qty: {analysis['qty']:,}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.GREEN_400),
                                    ft.Text(" | ", size=16, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                                    ft.Text(f"Total Waste: {analysis['waste']:,.2f} Kg", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.RED_400),
                                    ft.Text(" | ", size=16, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                                    ft.Text(f"Global Waste Rate: {analysis['global_rate']:.1f}%", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_400),
                                ], rtl=rtl)
                            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
                        ], rtl=rtl),
                        padding=20,
                        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                        border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
                        border_radius=12,
                        expand=True
                    )
                ]),
                
                # Charts
                ft.Container(
                    content=ft.Column([
                        ft.Text("Production by Machine (Qty)" if not rtl else "الإنتاج حسب الآلة (كمية)", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                        ft.Container(content=chart, height=300, padding=10)
                    ]),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                    border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
                    border_radius=12,
                ) if chart_data else ft.Container(),
                
                # Insights
                ft.Row([
                    build_card(translations.t('analysis_strengths', page), ft.icons.TRENDING_UP, ft.colors.GREEN_400, analysis['strengths']),
                    build_card(translations.t('analysis_weaknesses', page), ft.icons.TRENDING_DOWN, ft.colors.RED_400, analysis['weaknesses']),
                ], spacing=20, rtl=rtl),
                
                ft.Row([
                    build_card(translations.t('analysis_solutions', page), ft.icons.LIGHTBULB, ft.colors.AMBER_400, analysis['solutions']),
                ])
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            
        page.update()

    # Title row
    title_row = ft.Row(
        controls=[
            ft.Icon(ft.icons.INSIGHTS, color=ft.colors.PURPLE_400, size=35),
            ft.Text(translations.t('analysis_title', page), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Container(expand=True),
            year_dd,
            month_dd,
            view_type
        ] if not rtl else [
            view_type,
            month_dd,
            year_dd,
            ft.Container(expand=True),
            ft.Text(translations.t('analysis_title', page), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Icon(ft.icons.INSIGHTS, color=ft.colors.PURPLE_400, size=35),
        ],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END
    )

    view_type.on_change = generate_report
    month_dd.on_change = generate_report
    year_dd.on_change = generate_report
    
    generate_report()

    return ft.Column(
        controls=[
            title_row,
            ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            report_container
        ],
        spacing=20,
        expand=True
    )
