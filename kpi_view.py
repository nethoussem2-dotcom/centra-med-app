import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import datetime
import database
import translations

def get_view(page: ft.Page):
    rtl = translations.is_rtl(page)
    
    # ------------------- Calculation Core ------------------- #
    def compute_kpis(records):
        if not records:
            return None
            
        total_qty = sum(r.get('qte_prod', 0) for r in records)
        total_actual_w = sum(r.get('poid_reel', 0) for r in records)
        total_waste_w = sum(r.get('dechet_kg', 0) for r in records)
        total_theo_w = sum(r.get('poid_theo', 0) for r in records)
        total_downtime_min = sum(r.get('downtime_min', 0) or 0 for r in records)
        total_entries = len(records)
        
        # 1. TQ - Quality Rate
        total_input_w = total_actual_w + total_waste_w
        if total_input_w > 0:
            tq = (total_actual_w / total_input_w) * 100.0
        else:
            tq = 100.0
            
        # 2. T.Disp - Availability Rate
        # Assuming standard shift = 480 mins (8 hours) per entry
        planned_mins = max(480.0, total_entries * 480.0)
        operating_mins = max(0.0, planned_mins - total_downtime_min)
        tdisp = (operating_mins / planned_mins) * 100.0
        
        # 3. T.Perf - Performance Rate
        if total_theo_w > 0 and total_actual_w > 0:
            tperf = min(100.0, (total_actual_w / total_theo_w) * 100.0)
        else:
            tperf = 95.0  # default baseline
            
        # 4. TRS (OEE)
        trs = (tdisp / 100.0) * (tperf / 100.0) * (tq / 100.0) * 100.0
        
        # 5. TRG & TRE
        trg = trs * 0.92  # factoring planned stoppages/breaks (~92%)
        tre = trg * 0.85  # factoring calendar utilization (~85%)
        
        # Machine level breakdown
        machine_map = {}
        for r in records:
            m = r['machine']
            if m not in machine_map:
                machine_map[m] = {
                    'qty': 0, 'actual_w': 0, 'waste_w': 0, 'theo_w': 0, 'downtime': 0, 'entries': 0
                }
            machine_map[m]['qty'] += r.get('qte_prod', 0)
            machine_map[m]['actual_w'] += r.get('poid_reel', 0)
            machine_map[m]['waste_w'] += r.get('dechet_kg', 0)
            machine_map[m]['theo_w'] += r.get('poid_theo', 0)
            machine_map[m]['downtime'] += (r.get('downtime_min', 0) or 0)
            machine_map[m]['entries'] += 1
            
        machine_kpis = {}
        for m, d in machine_map.items():
            inp_w = d['actual_w'] + d['waste_w']
            m_tq = (d['actual_w'] / inp_w * 100.0) if inp_w > 0 else 100.0
            
            m_planned = max(480.0, d['entries'] * 480.0)
            m_operating = max(0.0, m_planned - d['downtime'])
            m_tdisp = (m_operating / m_planned) * 100.0
            
            m_tperf = min(100.0, (d['actual_w'] / d['theo_w'] * 100.0)) if d['theo_w'] > 0 else 95.0
            m_trs = (m_tdisp / 100.0) * (m_tperf / 100.0) * (m_tq / 100.0) * 100.0
            m_trg = m_trs * 0.92
            
            machine_kpis[m] = {
                'qty': d['qty'],
                'actual_w': d['actual_w'],
                'waste_w': d['waste_w'],
                'downtime': d['downtime'],
                'tq': m_tq,
                'tdisp': m_tdisp,
                'tperf': m_tperf,
                'trs': m_trs,
                'trg': m_trg
            }
            
        return {
            'total_qty': total_qty,
            'total_actual_w': total_actual_w,
            'total_waste_w': total_waste_w,
            'total_downtime_min': total_downtime_min,
            'tq': tq,
            'tdisp': tdisp,
            'tperf': tperf,
            'trs': trs,
            'trg': trg,
            'tre': tre,
            'machine_kpis': machine_kpis
        }

    # ------------------- UI Controls ------------------- #
    today_dt = datetime.date.today()
    
    view_type = ft.Dropdown(
        value="month",
        options=[
            ft.dropdown.Option("month", translations.t('analysis_month', page)),
            ft.dropdown.Option("year", translations.t('analysis_overall', page)),
        ],
        width=180,
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
    
    kpi_container = ft.Container(expand=True)
    
    def create_neon_kpi_card(title, value_pct, subtitle, icon, color, badge_text=""):
        val_color = color
        if value_pct >= 85:
            badge_color = ft.colors.GREEN_400
        elif value_pct >= 70:
            badge_color = ft.colors.AMBER_400
        else:
            badge_color = ft.colors.RED_400
            
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=28),
                        padding=10,
                        bgcolor=ft.colors.with_opacity(0.12, color),
                        border_radius=50
                    ),
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.colors.with_opacity(0.9, ft.colors.ON_SURFACE), rtl=rtl, expand=True),
                    ft.Container(
                        content=ft.Text(badge_text or (f"{value_pct:.1f}%"), size=11, color=badge_color, weight=ft.FontWeight.BOLD),
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor=ft.colors.with_opacity(0.12, badge_color),
                        border_radius=8
                    ) if badge_text or value_pct else ft.Container()
                ], rtl=rtl, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=5),
                
                ft.Row([
                    ft.Text(f"{value_pct:.1f}%", size=32, weight=ft.FontWeight.BOLD, color=val_color),
                ], alignment=ft.MainAxisAlignment.CENTER if not rtl else ft.MainAxisAlignment.CENTER),
                
                # Progress Bar
                ft.ProgressBar(
                    value=min(1.0, max(0.0, value_pct / 100.0)),
                    color=color,
                    bgcolor=ft.colors.with_opacity(0.1, color),
                    height=6,
                ),
                
                ft.Text(subtitle, size=11, color=ft.colors.with_opacity(0.6, ft.colors.ON_SURFACE), rtl=rtl, text_align=ft.TextAlign.CENTER)
            ], spacing=8),
            bgcolor=ft.colors.with_opacity(0.05, color),
            border=ft.border.all(1, ft.colors.with_opacity(0.2, color)),
            border_radius=16,
            padding=20,
            expand=True
        )

    def render_kpis(e=None):
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
            
        res = compute_kpis(records)
        
        if not res:
            kpi_container.content = ft.Container(
                content=ft.Text(translations.t('kpi_empty', page), size=16, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                alignment=ft.alignment.center,
                padding=50
            )
        else:
            # 1. Primary KPI Cards
            card_trs = create_neon_kpi_card(
                translations.t('kpi_trs', page),
                res['trs'],
                "Overall Equipment Effectiveness" if not rtl else "مؤشر الفاعلية الكلية للآلات والمعدات",
                ft.icons.SPEED,
                ft.colors.TEAL_400,
                "ممتاز" if res['trs'] >= 85 else ("مقبول" if res['trs'] >= 70 else "ضعيف")
            )
            
            card_trg = create_neon_kpi_card(
                translations.t('kpi_trg', page),
                res['trg'],
                "Taux de Rendement Global" if not rtl else "مؤشر المردودية الإجمالي للتشغيل",
                ft.icons.ANALYTICS,
                ft.colors.BLUE_400
            )
            
            card_tre = create_neon_kpi_card(
                translations.t('kpi_tre', page),
                res['tre'],
                "Taux de Rendement Économique" if not rtl else "مؤشر العائد الاقتصادي الفعلي",
                ft.icons.SAVINGS_OUTLINED,
                ft.colors.PURPLE_400
            )
            
            card_tq = create_neon_kpi_card(
                translations.t('kpi_tq', page),
                res['tq'],
                "Taux de Qualité (Conforme / Total)" if not rtl else "نسبة المنتجات الصالحة بدون تالف",
                ft.icons.CHECK_CIRCLE_OUTLINE,
                ft.colors.GREEN_400
            )
            
            card_tdisp = create_neon_kpi_card(
                translations.t('kpi_disp', page),
                res['tdisp'],
                f"التوقفات الكلية: {res['total_downtime_min']:.0f} دقيقة" if rtl else f"Temps d'arrêt total: {res['total_downtime_min']:.0f} min",
                ft.icons.TIMER_OUTLINED,
                ft.colors.AMBER_400
            )
            
            card_tperf = create_neon_kpi_card(
                translations.t('kpi_perf', page),
                res['tperf'],
                "معدل أداء السرعة والإنتاجية النظرية" if rtl else "Ratio de cadence réelle / théorique",
                ft.icons.ELECTRIC_BOLT,
                ft.colors.CYAN_400
            )
            
            # 2. Machine Bar Chart comparison
            chart_data = []
            m_keys = sorted(list(res['machine_kpis'].keys()))
            max_trs = 100.0
            
            for i, mk in enumerate(m_keys):
                m_val = res['machine_kpis'][mk]['trs']
                bar_color = ft.colors.GREEN_400 if m_val >= 85 else (ft.colors.AMBER_400 if m_val >= 70 else ft.colors.RED_400)
                
                chart_data.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=m_val,
                                width=32,
                                color=bar_color,
                                tooltip=f"Machine: {mk}\nTRS: {m_val:.1f}%\nTQ: {res['machine_kpis'][mk]['tq']:.1f}%\nT.Disp: {res['machine_kpis'][mk]['tdisp']:.1f}%",
                                border_radius=4,
                            ),
                        ],
                    )
                )
                
            machine_chart = ft.BarChart(
                bar_groups=chart_data,
                border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("TRS %")),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=i, 
                            label=ft.Container(ft.Text(mk, size=11, weight=ft.FontWeight.BOLD), padding=5)
                        ) for i, mk in enumerate(m_keys)
                    ],
                    labels_size=35,
                ),
                horizontal_grid_lines=ft.ChartGridLines(
                    color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1, dash_pattern=[3, 3]
                ),
                tooltip_bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLUE_GREY_900),
                max_y=105.0,
                interactive=True,
                expand=True,
            )
            
            # 3. Machine Table Details
            table_header = ft.Container(
                content=ft.Row([
                    ft.Container(ft.Text("الآلة" if rtl else "Machine", size=12, weight=ft.FontWeight.BOLD), width=70),
                    ft.Container(ft.Text("الإنتاج (قطع)" if rtl else "Production (Pcs)", size=12, weight=ft.FontWeight.BOLD), width=100),
                    ft.Container(ft.Text("التالف (كجم)" if rtl else "Déchets (Kg)", size=12, weight=ft.FontWeight.BOLD), width=90),
                    ft.Container(ft.Text("التوقف (دقيقة)" if rtl else "Arrêt (min)", size=12, weight=ft.FontWeight.BOLD), width=90),
                    ft.Container(ft.Text("TQ %", size=12, weight=ft.FontWeight.BOLD), width=70),
                    ft.Container(ft.Text("T.Disp %", size=12, weight=ft.FontWeight.BOLD), width=80),
                    ft.Container(ft.Text("T.Perf %", size=12, weight=ft.FontWeight.BOLD), width=80),
                    ft.Container(ft.Text("TRS %", size=12, weight=ft.FontWeight.BOLD), width=80),
                ], rtl=rtl),
                bgcolor=ft.colors.TEAL_700,
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                border_radius=8
            )
            
            table_rows = []
            for mk in m_keys:
                mv = res['machine_kpis'][mk]
                trs_col = ft.colors.GREEN_400 if mv['trs'] >= 85 else (ft.colors.AMBER_400 if mv['trs'] >= 70 else ft.colors.RED_400)
                
                table_rows.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(ft.Text(mk, size=13, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_300), width=70),
                            ft.Container(ft.Text(f"{mv['qty']:,}", size=13), width=100),
                            ft.Container(ft.Text(f"{mv['waste_w']:.2f}", size=13, color=ft.colors.RED_300 if mv['waste_w'] > 0 else None), width=90),
                            ft.Container(ft.Text(f"{mv['downtime']:.0f}", size=13, color=ft.colors.ORANGE_300 if mv['downtime'] > 0 else None), width=90),
                            ft.Container(ft.Text(f"{mv['tq']:.1f}%", size=13), width=70),
                            ft.Container(ft.Text(f"{mv['tdisp']:.1f}%", size=13), width=80),
                            ft.Container(ft.Text(f"{mv['tperf']:.1f}%", size=13), width=80),
                            ft.Container(ft.Text(f"{mv['trs']:.1f}%", size=13, weight=ft.FontWeight.BOLD, color=trs_col), width=80),
                        ], rtl=rtl),
                        padding=ft.padding.symmetric(horizontal=15, vertical=10),
                        border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)))
                    )
                )

            # Assembling UI
            kpi_container.content = ft.Column([
                # Primary Metrics (Row 1)
                ft.Row([card_trs, card_trg, card_tre], spacing=15, rtl=rtl),
                
                # Sub Metrics (Row 2)
                ft.Row([card_tq, card_tdisp, card_tperf], spacing=15, rtl=rtl),
                
                ft.Container(height=10),
                
                # Chart Container
                ft.Container(
                    content=ft.Column([
                        ft.Text(translations.t('kpi_mach_chart', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                        ft.Container(content=machine_chart, height=300, padding=10)
                    ]),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                    border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
                    border_radius=16,
                ) if chart_data else ft.Container(),
                
                ft.Container(height=10),
                
                # Machine Breakdown Table
                ft.Container(
                    content=ft.Column([
                        ft.Text("تفاصيل مؤشرات الأداء حسب الآلة" if rtl else "Détails des indicateurs par machine", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                        table_header,
                        ft.Column(table_rows, spacing=0)
                    ], spacing=10),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                    border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
                    border_radius=16,
                )
            ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            
        page.update()

    # Title row
    title_row = ft.Row(
        controls=[
            ft.Icon(ft.icons.SPEED, color=ft.colors.TEAL_400, size=35),
            ft.Text(translations.t('kpi_title', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Container(expand=True),
            year_dd,
            month_dd,
            view_type
        ] if not rtl else [
            view_type,
            month_dd,
            year_dd,
            ft.Container(expand=True),
            ft.Text(translations.t('kpi_title', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Icon(ft.icons.SPEED, color=ft.colors.TEAL_400, size=35),
        ],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END
    )

    view_type.on_change = render_kpis
    month_dd.on_change = render_kpis
    year_dd.on_change = render_kpis
    
    render_kpis()

    return ft.Column(
        controls=[
            title_row,
            ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            kpi_container
        ],
        spacing=15,
        expand=True
    )
