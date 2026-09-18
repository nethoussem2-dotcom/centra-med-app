import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import datetime
import database
import auth
import translations

def get_view(page: ft.Page):
    rtl = translations.is_rtl(page)
    
    def table_cell(text, width=None, expand=False, is_header=False, numeric=False, color=None, force_ltr=False):
        return ft.Container(
            content=ft.Text(
                str(text), 
                size=13 if not is_header else 12, 
                weight=ft.FontWeight.BOLD if is_header else ft.FontWeight.NORMAL, 
                color=color if color else (ft.colors.WHITE if is_header else ft.colors.ON_SURFACE),
                text_align=ft.TextAlign.RIGHT if numeric else ft.TextAlign.LEFT,
                rtl=False if force_ltr else rtl
            ),
            width=width,
            expand=expand,
            padding=ft.padding.symmetric(horizontal=10, vertical=12),
            alignment=ft.alignment.center_right if numeric else ft.alignment.center_left
        )

    header_row = ft.Container(
        content=ft.Row([
            table_cell(translations.t('suivi_date', page), width=90, is_header=True),
            table_cell(translations.t('suivi_machine', page), width=60, is_header=True),
            table_cell(translations.t('suivi_product', page), expand=True, is_header=True),
            table_cell(translations.t('suivi_batch', page), width=80, is_header=True),
            table_cell(translations.t('suivi_qty', page), width=60, is_header=True, numeric=True),
            table_cell(translations.t('suivi_theo_w', page), width=80, is_header=True, numeric=True),
            table_cell(translations.t('suivi_actual_w', page), width=80, is_header=True, numeric=True),
            table_cell("كمية الملون", width=80, is_header=True, numeric=True),
            table_cell(translations.t('suivi_waste', page), width=70, is_header=True, numeric=True),
            table_cell(translations.t('suivi_waste_rate', page), width=80, is_header=True, numeric=True),
            table_cell("مدة التوقف (د)" if rtl else "Arrêt (min)", width=90, is_header=True, numeric=True),
            table_cell("سبب التوقف / النقص" if rtl else "Cause Arrêt", width=140, is_header=True),
            table_cell(translations.t('suivi_operator', page), width=90, is_header=True),
        ], rtl=rtl),
        bgcolor=ft.colors.TEAL_700,
        border_radius=ft.border_radius.only(top_left=8, top_right=8),
        border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE))
    )
    
    body_column = ft.Column(
        scroll=ft.ScrollMode.ADAPTIVE,
        auto_scroll=True,
        expand=True,
        spacing=0
    )
    
    table_container = ft.Column(
        controls=[header_row, body_column],
        spacing=0,
        expand=True
    )
    
    def load_data():
        # Get today's records by default (or recent ones if none today)
        today = datetime.date.today()
        records = database.get_filtered_records(year=today.year, month=today.month, day=today.day)
        
        # If no records today, just fetch the most recent ones (limit 50)
        if not records:
            records = database.get_filtered_records()[:50]
            
        # Reverse the order so oldest is at the top, newest at the bottom (like Excel)
        records.reverse()
            
        body_column.controls.clear()
        
        for i, rec in enumerate(records):
            # Alternating row colors for Excel feel
            row_color = ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE) if i % 2 == 0 else ft.colors.TRANSPARENT
            
            # Format numbers
            qty = int(rec['qte_prod'])
            theo_w = f"{rec['poid_theo']:.2f}"
            actual_w = f"{rec['poid_reel']:.2f}" if rec['poid_reel'] > 0 else "-"
            colorant_val = f"{rec.get('colorant_kg', 0.0):.2f}"
            waste = f"{rec['dechet_kg']:.2f}"
            rate = f"{rec['taux_rebut'] * 100:.1f}%" if rec['taux_rebut'] else "0.0%"
            
            d_min = rec.get('downtime_min') or 0.0
            d_reason = rec.get('downtime_reason') or ""
            d_tooltip = None
            if d_min > 0 or d_reason:
                d_tooltip = f"توقف الإنتاج: {d_min:.0f} دقيقة | السبب: {d_reason}" if rtl else f"Arrêt: {d_min:.0f} min | Cause: {d_reason}"

            d_min_str = f"{d_min:.0f}" if d_min > 0 else "-"
            d_reason_str = d_reason if d_reason else "-"

            body_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        table_cell(rec['date'], width=90),
                        table_cell(rec['machine'], width=60, color=ft.colors.BLUE_400),
                        table_cell(f"{rec['code_article']} - {rec['designation']}", expand=True),
                        table_cell(rec['num_lot'], width=80, force_ltr=True),
                        table_cell(str(qty), width=60, numeric=True, color=ft.colors.GREEN_400),
                        table_cell(theo_w, width=80, numeric=True),
                        table_cell(actual_w, width=80, numeric=True, color=ft.colors.TEAL_400),
                        table_cell(colorant_val, width=80, numeric=True, color=ft.colors.ORANGE_300),
                        table_cell(waste, width=70, numeric=True, color=ft.colors.RED_400 if float(rec['dechet_kg'] or 0) > 0 else None),
                        table_cell(rate, width=80, numeric=True, color=ft.colors.RED_400 if (rec['taux_rebut'] and rec['taux_rebut'] > 0.05) else None),
                        table_cell(d_min_str, width=90, numeric=True, color=ft.colors.ORANGE_400 if d_min > 0 else None),
                        table_cell(d_reason_str, width=140, color=ft.colors.AMBER_300 if d_reason else None),
                        table_cell(rec['username'], width=90),
                    ], rtl=rtl),
                    bgcolor=row_color,
                    tooltip=d_tooltip,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)))
                )
            )
        
        if not records:
            body_column.controls = [
                ft.Container(
                    content=ft.Text(translations.t('suivi_empty', page), size=16, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)),
                    alignment=ft.alignment.center,
                    padding=50
                )
            ]
            
        page.update()

    # Load initial data
    load_data()
    
    # Title row with excel icon
    title_row = ft.Row(
        controls=[
            ft.Icon(ft.icons.TABLE_CHART, color=ft.colors.GREEN_500, size=28),
            ft.Text(translations.t('suivi_title', page), size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
        ] if not rtl else [
            ft.Text(translations.t('suivi_title', page), size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Icon(ft.icons.TABLE_CHART, color=ft.colors.GREEN_500, size=28),
        ],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END
    )

    # Calculate statistics
    today_dt = datetime.date.today()
    month_records = database.get_filtered_records(year=today_dt.year, month=today_dt.month)
    all_records = database.get_filtered_records(year=today_dt.year)
    
    month_total = sum(rec.get('qte_prod', 0) for rec in month_records)
    all_total = sum(rec.get('qte_prod', 0) for rec in all_records)
    
    month_title = "إنتاج شهر" if rtl else "Production du mois"
    all_title = "إنتاج سنة" if rtl else "Production de l'année"
    
    month_dropdown = ft.Dropdown(
        value=str(today_dt.month),
        options=[ft.dropdown.Option(str(i), f"{i}") for i in range(1, 13)],
        width=70,
        height=35,
        content_padding=5,
        text_size=13,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        dense=True
    )
    
    year_dropdown = ft.Dropdown(
        value=str(today_dt.year),
        options=[ft.dropdown.Option(str(y), f"{y}") for y in range(today_dt.year - 5, today_dt.year + 2)],
        width=80,
        height=35,
        content_padding=5,
        text_size=13,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        dense=True
    )
    
    month_val_text = ft.Text(f"{month_total:,}", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE)
    year_val_text = ft.Text(f"{all_total:,}", size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE)
    
    def on_month_change(e):
        m = int(month_dropdown.value)
        m_recs = database.get_filtered_records(year=today_dt.year, month=m)
        m_tot = sum(r.get('qte_prod', 0) for r in m_recs)
        month_val_text.value = f"{m_tot:,}"
        page.update()
        
    def on_year_change(e):
        y = int(year_dropdown.value)
        y_recs = database.get_filtered_records(year=y)
        y_tot = sum(r.get('qte_prod', 0) for r in y_recs)
        year_val_text.value = f"{y_tot:,}"
        page.update()
        
    month_dropdown.on_change = on_month_change
    year_dropdown.on_change = on_year_change
    
    def create_stat_card(icon, title, val_text_ctrl, color, dropdown):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=color, size=45),
                    padding=18,
                    bgcolor=ft.colors.with_opacity(0.15, color),
                    border_radius=50,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.with_opacity(0.25, color),
                        offset=ft.Offset(0, 4),
                    )
                ),
                ft.Column([
                    ft.Row([ft.Text(title, size=13, weight=ft.FontWeight.W_500, color=ft.colors.with_opacity(0.8, ft.colors.ON_SURFACE), rtl=rtl), dropdown], spacing=10, alignment=ft.MainAxisAlignment.START),
                    val_text_ctrl
                ], spacing=5, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START if not rtl else ft.CrossAxisAlignment.END)
            ], alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END, spacing=20, rtl=rtl),
            bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
            border=ft.border.all(1, ft.colors.with_opacity(0.15, color)),
            border_radius=16,
            padding=20,
            expand=True
        )

    stats_row = ft.Row(
        controls=[
            create_stat_card(ft.icons.CONVEYOR_BELT, month_title, month_val_text, ft.colors.BLUE_400, month_dropdown),
            create_stat_card(ft.icons.FACTORY, all_title, year_val_text, ft.colors.GREEN_400, year_dropdown),
        ],
        spacing=25,
        rtl=rtl
    )

    return ft.Column(
        controls=[
            title_row,
            ft.Container(height=10),
            stats_row,
            ft.Container(height=10),
            ft.Container(
                content=table_container,
                bgcolor=ft.colors.with_opacity(0.02, ft.colors.SURFACE),
                padding=10,
                border_radius=8,
                expand=True
            )
        ],
        spacing=0,
        expand=True
    )
