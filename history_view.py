import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import database
import auth
import os
import csv
import datetime
import translations

def get_view(page: ft.Page):
    current_user = auth.get_current_user()
    is_visitor = current_user['role'] == 'visitor'
    is_admin = current_user['role'] == 'admin'
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    # Inputs for filtering
    product_input = ft.TextField(label=translations.t('filter_product', page), width=160, rtl=rtl, height=45, text_size=13, text_align=align)
    batch_input = ft.TextField(label=translations.t('filter_batch', page), width=140, rtl=rtl, height=45, text_size=13, text_align=align)
    qty_input = ft.TextField(label=translations.t('filter_min_qty', page), width=140, rtl=rtl, height=45, text_size=13, keyboard_type=ft.KeyboardType.NUMBER, text_align=align)
    operator_input = ft.TextField(label=translations.t('filter_operator', page), width=140, rtl=rtl, height=45, text_size=13, text_align=align)
    
    # Date Filtering Inputs
    year_filter = ft.Dropdown(label=translations.t('filter_year', page), width=100, options=[ft.dropdown.Option(str(y)) for y in range(2023, 2031)], height=45, text_size=13)
    month_filter = ft.Dropdown(label=translations.t('filter_month', page), width=90, options=[ft.dropdown.Option(f"{m:02d}") for m in range(1, 13)], height=45, text_size=13)
    day_filter = ft.Dropdown(label=translations.t('filter_day', page), width=90, options=[ft.dropdown.Option(f"{d:02d}") for d in range(1, 32)], height=45, text_size=13)
    
    # Operators can only view their own logs if they are not admin/visitor, so we lock their input
    if current_user['role'] == 'user':
        operator_input.value = current_user['username']
        operator_input.disabled = True

    # Data container
    records_table_container = ft.Container(expand=True)
    active_records = []  # Reference to holds currently filtered records

    def show_alert(text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, size=14, rtl=rtl, color=ft.colors.WHITE),
            bgcolor=ft.colors.RED_600 if is_error else ft.colors.GREEN_600
        )
        page.snack_bar.open = True
        page.update()

    def handleDelete(record_id):
        def confirm_delete(e):
            database.delete_production_record(record_id)
            dialog.open = False
            show_alert(translations.t('delete_success', page))
            refresh_data(None)
            
        def cancel_delete(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(translations.t('delete_confirm_title', page), rtl=rtl),
            content=ft.Text(translations.t('delete_confirm_msg', page), rtl=rtl),
            actions=[
                ft.TextButton(translations.t('cancel', page), on_click=cancel_delete),
                ft.ElevatedButton(translations.t('confirm_delete', page), bgcolor=ft.colors.RED_600, color=ft.colors.WHITE, on_click=confirm_delete),
            ] if rtl else [
                ft.ElevatedButton(translations.t('confirm_delete', page), bgcolor=ft.colors.RED_600, color=ft.colors.WHITE, on_click=confirm_delete),
                ft.TextButton(translations.t('cancel', page), on_click=cancel_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def refresh_data(e):
        nonlocal active_records
        
        # Parse filter parameters
        prod = product_input.value.strip() if product_input.value else None
        batch = batch_input.value.strip() if batch_input.value else None
        
        try:
            min_q = float(qty_input.value.strip()) if qty_input.value else None
        except ValueError:
            min_q = None
            
        op = operator_input.value.strip() if operator_input.value else None
        
        y = year_filter.value
        m = month_filter.value
        d = day_filter.value
        
        # Query database
        active_records = database.get_filtered_records(
            product_name=prod,
            min_qte=min_q,
            username=op,
            num_lot=batch,
            year=y,
            month=m,
            day=d
        )
        
        # Build DataTable (Limit UI rendering to top 200 for performance)
        display_records = active_records[:200]
        data_rows = []
        for r in display_records:
            # Color coding for waste rate
            w_rate = r['taux_rebut'] * 100.0
            w_color = ft.colors.GREEN_400 if w_rate <= 3.0 else (ft.colors.ORANGE_400 if w_rate <= 7.0 else ft.colors.RED_400)
            
            # Action button authorization check
            can_delete = is_admin or (current_user['username'] == r['username'] and not is_visitor)
            
            delete_btn = ft.IconButton(
                icon=ft.icons.DELETE_FOREVER,
                icon_color=ft.colors.RED_400 if can_delete else ft.colors.GREY_600,
                tooltip=translations.t('delete_tooltip', page) if can_delete else "",
                disabled=not can_delete,
                on_click=lambda e, rid=r['id']: handleDelete(rid)
            )
            
            hw_reason = r.get('high_waste_reason') or ''
            lp_reason = r.get('low_prod_reason') or ''
            
            row_cells_arabic = [
                ft.DataCell(delete_btn),
                ft.DataCell(ft.Text(f"{w_rate:.2f}%", color=w_color, weight=ft.FontWeight.BOLD)),
                ft.DataCell(ft.Text(hw_reason[:20] + ('...' if len(hw_reason)>20 else ''), color=ft.colors.RED_300, tooltip=hw_reason)),
                ft.DataCell(ft.Text(lp_reason[:20] + ('...' if len(lp_reason)>20 else ''), color=ft.colors.ORANGE_300, tooltip=lp_reason)),
                ft.DataCell(ft.Text(f"{round(r['dechet_kg'], 2)} " + translations.t('unit_kg', page))),
                ft.DataCell(ft.Text(f"{round(r.get('dechet_pce') or 0.0, 3)}")),
                ft.DataCell(ft.Text(f"{round(r['poid_reel'], 2)} " + translations.t('unit_kg', page))),
                ft.DataCell(ft.Text(f"{round(r['poid_theo'], 2)} " + translations.t('unit_kg', page))),
                ft.DataCell(ft.Text(f"{int(r['qte_prod']):,}")),
                ft.DataCell(ft.Text(r['num_lot'])),
                ft.DataCell(ft.Text(r['machine'], color=ft.colors.TEAL_400, weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(r['designation'], weight=ft.FontWeight.W_500, rtl=rtl)),
                ft.DataCell(ft.Text(r['code_article'])),
                ft.DataCell(ft.Text(r['username'], color=ft.colors.BLUE_300)),
                ft.DataCell(ft.Text(r['date'])),
            ]
            
            # If LTR, we reverse the cells array order to align with the LTR headers
            data_rows.append(
                ft.DataRow(
                    cells=row_cells_arabic if rtl else list(reversed(row_cells_arabic))
                )
            )
            
        # Headers matching the row cells
        headers_arabic = [
            ft.DataColumn(ft.Text(translations.t('col_actions', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_waste_rate', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_hw_reason', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_lp_reason', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_waste_kg', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_waste_pce', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_actual_w', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_theo_w', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_qty', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_batch', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_machine', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_product', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_code', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_operator', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_date', page), rtl=rtl)),
        ]
        
        data_table = ft.DataTable(
            columns=headers_arabic if rtl else list(reversed(headers_arabic)),
            rows=data_rows,
            column_spacing=18,
            heading_row_color=ft.colors.with_opacity(0.06, ft.colors.ON_SURFACE),
            divider_thickness=1,
            horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
        )
        
        # Update Table view scroll wrapper
        count_label = (
            translations.t('showing_first_200', page).format(len(active_records))
            if len(active_records) > 200 else 
            translations.t('showing_count', page).format(len(active_records))
        )
        
        records_table_container.content = ft.Column(
            controls=[
                ft.Row([ft.Text(count_label, size=12, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE), rtl=rtl)], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Row([
                        ft.Column([data_table], scroll=ft.ScrollMode.ALWAYS)
                    ], scroll=ft.ScrollMode.ALWAYS, vertical_alignment=ft.CrossAxisAlignment.START),
                    expand=True
                )
            ],
            expand=True
        )
        page.update()

    def export_csv(e):
        if not active_records:
            show_alert(translations.t('export_empty', page), is_error=True)
            return
            
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.getcwd()
            
        file_path = os.path.join(desktop_dir, f"CENTRA_MED_PROD_EXPORT_{datetime.date.today()}.csv")
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                # Header row
                writer.writerow([
                    translations.t('col_date', page),
                    translations.t('col_operator', page),
                    translations.t('col_product', page),
                    translations.t('col_code', page),
                    translations.t('col_machine', page),
                    translations.t('col_batch', page),
                    translations.t('col_qty', page),
                    translations.t('col_theo_w', page),
                    translations.t('col_actual_w', page),
                    translations.t('col_waste_kg', page),
                    translations.t('col_waste_pce', page),
                    translations.t('col_waste_rate', page),
                    translations.t('col_lp_reason', page),
                    translations.t('col_hw_reason', page),
                ])
                # Data rows
                for r in active_records:
                    writer.writerow([
                        r['date'], r['username'], r['designation'], r['code_article'], r['machine'], r['num_lot'],
                        r['qte_prod'], r['poid_theo'], r['poid_reel'], r['dechet_kg'], r['dechet_pce'],
                        f"{r['taux_rebut'] * 100.0:.2f}%", r.get('low_prod_reason', '') or '', r.get('high_waste_reason', '') or ''
                    ])
            show_alert(translations.t('export_success', page).format(os.path.basename(file_path)))
        except Exception as ex:
            show_alert(translations.t('export_fail', page).format(str(ex)), is_error=True)

    # Filter Action Buttons
    filter_btn = ft.IconButton(
        icon=ft.icons.FILTER_ALT,
        icon_color=ft.colors.TEAL_400,
        tooltip=translations.t('filter_apply_tooltip', page),
        icon_size=28,
        on_click=refresh_data
    )
    
    year_filter.on_change = refresh_data
    month_filter.on_change = refresh_data
    day_filter.on_change = refresh_data
    
    reset_btn = ft.IconButton(
        icon=ft.icons.REFRESH,
        icon_color=ft.colors.TEAL_300,
        tooltip=translations.t('filter_reset_tooltip', page),
        icon_size=28,
        on_click=lambda e: [
            setattr(product_input, 'value', ""),
            setattr(batch_input, 'value', ""),
            setattr(qty_input, 'value', ""),
            setattr(operator_input, 'value', current_user['username'] if current_user['role'] == 'user' else ""),
            setattr(year_filter, 'value', None),
            setattr(month_filter, 'value', None),
            setattr(day_filter, 'value', None),
            refresh_data(None)
        ]
    )
    
    export_btn = ft.ElevatedButton(
        text=translations.t('export_btn', page),
        icon=ft.icons.DOWNLOAD,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        on_click=export_csv
    )

    # Top Filters Bar
    filters_bar = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        operator_input,
                        qty_input,
                        batch_input,
                        product_input,
                    ] if rtl else [
                        product_input,
                        batch_input,
                        qty_input,
                        operator_input,
                    ],
                    alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Row(
                    controls=[
                        export_btn,
                        ft.Container(expand=True),
                        reset_btn,
                        filter_btn,
                        ft.Container(width=10),
                        day_filter,
                        month_filter,
                        year_filter,
                        ft.Text(translations.t('filter_date_label', page), rtl=rtl, weight=ft.FontWeight.W_500, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE))
                    ] if rtl else [
                        ft.Text(translations.t('filter_date_label', page), rtl=rtl, weight=ft.FontWeight.W_500, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE)),
                        year_filter,
                        month_filter,
                        day_filter,
                        ft.Container(width=10),
                        filter_btn,
                        reset_btn,
                        ft.Container(expand=True),
                        export_btn,
                    ],
                    alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            ],
            spacing=15
        ),
        padding=15,
        border_radius=12,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
    )

    # Initial load
    refresh_data(None)

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(translations.t('history_title', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START
            ),
            ft.Container(height=15),
            filters_bar,
            ft.Container(height=15),
            records_table_container
        ],
        spacing=0,
        expand=True
    )
