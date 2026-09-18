import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import database
import translations

def get_view(page: ft.Page):
    rtl = translations.is_rtl(page)
    
    # UI Elements
    product_dd = ft.Dropdown(
        label=translations.t('batch_select_prod', page),
        width=250,
        height=50,
        text_size=14,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        dense=True
    )
    
    batch_dd = ft.Dropdown(
        label=translations.t('batch_select_lot', page),
        width=250,
        height=50,
        text_size=14,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        dense=True,
        disabled=True
    )
    
    report_container = ft.Container(expand=True)
    
    # State
    all_records = []
    
    def load_initial_data():
        nonlocal all_records
        all_records = database.get_filtered_records()
        
        # Get unique products
        products = set()
        for r in all_records:
            if r['code_article']:
                products.add(r['code_article'])
                
        product_options = sorted(list(products))
        product_dd.options = [ft.dropdown.Option(p) for p in product_options]
        
        if product_options:
            product_dd.value = product_options[0]
            # trigger product change logic to populate batches and render chart
            selected_prod = product_options[0]
            batches = set()
            for r in all_records:
                if r['code_article'] == selected_prod and r['num_lot']:
                    batches.add(r['num_lot'])
            
            batch_opts = [ft.dropdown.Option("ALL", translations.t('batch_all_lots', page))]
            batch_opts.extend([ft.dropdown.Option(b) for b in sorted(list(batches))])
            batch_dd.options = batch_opts
            batch_dd.value = "ALL"
            batch_dd.disabled = False
    
    def on_product_change(e):
        selected_prod = product_dd.value
        if not selected_prod:
            return
            
        # Get unique batches for this product
        batches = set()
        for r in all_records:
            if r['code_article'] == selected_prod and r['num_lot']:
                batches.add(r['num_lot'])
                
        batch_opts = [ft.dropdown.Option("ALL", translations.t('batch_all_lots', page))]
        batch_opts.extend([ft.dropdown.Option(b) for b in sorted(list(batches))])
        
        batch_dd.options = batch_opts
        batch_dd.value = "ALL"
        batch_dd.disabled = False
        
        generate_report()
        page.update()
        
    def on_batch_change(e):
        generate_report()
        page.update()
        
    def generate_report():
        selected_prod = product_dd.value
        selected_batch = batch_dd.value
        
        if not selected_prod:
            report_container.content = ft.Container(
                content=ft.Text(translations.t('batch_empty', page), size=16, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                alignment=ft.alignment.center,
                padding=50
            )
            return
            
        prod_records = [r for r in all_records if r['code_article'] == selected_prod]
        
        if selected_batch == "ALL" or not selected_batch:
            # Show Bar Chart comparing all batches
            batch_stats = {}
            grand_total_qty = 0
            grand_total_waste = 0
            
            for r in prod_records:
                b = r['num_lot'] or "Unknown"
                if b not in batch_stats:
                    batch_stats[b] = {'qty': 0, 'waste': 0}
                q = r.get('qte_prod', 0)
                w = r.get('dechet_kg', 0)
                batch_stats[b]['qty'] += q
                batch_stats[b]['waste'] += w
                grand_total_qty += q
                grand_total_waste += w
                
            chart_data = []
            max_qty = max((v['qty'] for v in batch_stats.values()), default=1)
            
            for i, (b_name, b_data) in enumerate(batch_stats.items()):
                chart_data.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=[
                            ft.BarChartRod(
                                from_y=0,
                                to_y=b_data['qty'],
                                width=40,
                                color=ft.colors.TEAL_400,
                                tooltip=f"Lot: {b_name}\nQty: {b_data['qty']:,}\nWaste: {b_data['waste']:,.2f}Kg",
                                border_radius=0,
                            ),
                        ],
                    )
                )
                
            batch_labels = list(batch_stats.keys())
            chart = ft.BarChart(
                bar_groups=chart_data,
                border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Qty (Pcs)")),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=i, 
                            label=ft.Container(ft.Text(str(m), size=10), padding=10)
                        ) for i, m in enumerate(batch_labels)
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
            
            report_container.content = ft.Container(
                content=ft.Column([
                    ft.Row([
                        # Grand Total Quantity Card
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.icons.INVENTORY_2, color=ft.colors.TEAL_400, size=35),
                                    padding=15,
                                    bgcolor=ft.colors.with_opacity(0.15, ft.colors.TEAL_400),
                                    border_radius=50,
                                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.with_opacity(0.2, ft.colors.TEAL_400), offset=ft.Offset(0, 2))
                                ),
                                ft.Column([
                                    ft.Text("إجمالي الإنتاج (جميع الدفعات)" if rtl else "Production Totale (Tous les lots)", size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl),
                                    ft.Text(f"{grand_total_qty:,} Pcs", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
                            ], rtl=rtl, spacing=15, alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END),
                            padding=20,
                            bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
                            border=ft.border.all(1, ft.colors.with_opacity(0.15, ft.colors.TEAL_400)),
                            border_radius=12,
                            expand=True
                        ),
                        # Grand Total Waste Card
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.icons.DELETE_SWEEP, color=ft.colors.RED_400, size=35),
                                    padding=15,
                                    bgcolor=ft.colors.with_opacity(0.15, ft.colors.RED_400),
                                    border_radius=50,
                                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.colors.with_opacity(0.2, ft.colors.RED_400), offset=ft.Offset(0, 2))
                                ),
                                ft.Column([
                                    ft.Text("إجمالي الهدر (جميع الدفعات)" if rtl else "Déchets Totaux (Tous les lots)", size=12, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl),
                                    ft.Text(f"{grand_total_waste:,.2f} Kg", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
                            ], rtl=rtl, spacing=15, alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END),
                            padding=20,
                            bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
                            border=ft.border.all(1, ft.colors.with_opacity(0.15, ft.colors.RED_400)),
                            border_radius=12,
                            expand=True
                        )
                    ], spacing=20, rtl=rtl),
                    ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
                    ft.Text(translations.t('batch_chart_title', page), size=18, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400, rtl=rtl),
                    ft.Container(content=chart, height=400, padding=20)
                ], scroll=ft.ScrollMode.ADAPTIVE),
                padding=20,
                bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
                border_radius=12,
                expand=True
            )
            
        else:
            # Show specific batch details
            batch_records = [r for r in prod_records if r['num_lot'] == selected_batch]
            total_qty = sum(r.get('qte_prod', 0) for r in batch_records)
            total_waste = sum(r.get('dechet_kg', 0) for r in batch_records)
            
            report_container.content = ft.Column([
                ft.Row([
                    # Quantity Card
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.icons.INVENTORY_2_OUTLINED, color=ft.colors.TEAL_400, size=45),
                                padding=18,
                                bgcolor=ft.colors.with_opacity(0.15, ft.colors.TEAL_400),
                                border_radius=50,
                                shadow=ft.BoxShadow(
                                    spread_radius=1, blur_radius=15, color=ft.colors.with_opacity(0.25, ft.colors.TEAL_400), offset=ft.Offset(0, 4)
                                )
                            ),
                            ft.Column([
                                ft.Text(translations.t('batch_qty', page) + f" ({selected_batch})", size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl),
                                ft.Text(f"{total_qty:,} Pcs", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                            ], spacing=5, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
                        ], rtl=rtl, spacing=20, alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END),
                        padding=30,
                        bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
                        border=ft.border.all(1, ft.colors.with_opacity(0.15, ft.colors.TEAL_400)),
                        border_radius=16,
                        expand=True
                    ),
                    # Waste Card
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.icons.DELETE_SWEEP_OUTLINED, color=ft.colors.RED_400, size=45),
                                padding=18,
                                bgcolor=ft.colors.with_opacity(0.15, ft.colors.RED_400),
                                border_radius=50,
                                shadow=ft.BoxShadow(
                                    spread_radius=1, blur_radius=15, color=ft.colors.with_opacity(0.25, ft.colors.RED_400), offset=ft.Offset(0, 4)
                                )
                            ),
                            ft.Column([
                                ft.Text(translations.t('batch_waste', page) + f" ({selected_batch})", size=14, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl),
                                ft.Text(f"{total_waste:,.2f} Kg", size=26, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE),
                            ], spacing=5, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
                        ], rtl=rtl, spacing=20, alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END),
                        padding=30,
                        bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
                        border=ft.border.all(1, ft.colors.with_opacity(0.15, ft.colors.RED_400)),
                        border_radius=16,
                        expand=True
                    )
                ], spacing=20, rtl=rtl)
            ])

    product_dd.on_change = on_product_change
    batch_dd.on_change = on_batch_change
    
    load_initial_data()
    generate_report()

    # Title row
    title_row = ft.Row(
        controls=[
            ft.Icon(ft.icons.CATEGORY, color=ft.colors.PURPLE_400, size=35),
            ft.Text(translations.t('batch_title', page), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
        ] if not rtl else [
            ft.Text(translations.t('batch_title', page), size=24, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Icon(ft.icons.CATEGORY, color=ft.colors.PURPLE_400, size=35),
        ],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END
    )

    controls_row = ft.Row(
        controls=[product_dd, batch_dd] if not rtl else [batch_dd, product_dd],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END,
        spacing=20
    )

    return ft.Column(
        controls=[
            title_row,
            ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            controls_row,
            ft.Container(height=10),
            report_container
        ],
        spacing=20,
        expand=True
    )
