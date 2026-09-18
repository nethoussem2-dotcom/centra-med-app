import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import datetime
import database
import auth
import translations

def get_view(page: ft.Page, on_save_success=None):
    current_user = auth.get_current_user()
    is_visitor = current_user['role'] == 'visitor'
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    # Load products from ART_PF database
    products = database.get_all_products()
    product_options = [ft.dropdown.Option(p['code_article']) for p in products]
    product_map = {p['code_article']: p for p in products}

    # Form Fields
    date_field = ft.TextField(
        label=translations.t('field_date', page),
        value=datetime.date.today().strftime("%Y-%m-%d"),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.CALENDAR_MONTH,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    product_dropdown = ft.Dropdown(
        label=translations.t('field_product', page),
        options=product_options,
        width=340,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    machine_dropdown = ft.Dropdown(
        label=translations.t('field_machine', page),
        options=[
            ft.dropdown.Option("I01"),
            ft.dropdown.Option("I02"),
            ft.dropdown.Option("I03"),
            ft.dropdown.Option("I04"),
            ft.dropdown.Option("I05"),
            ft.dropdown.Option("I06"),
            ft.dropdown.Option("S1"),
            ft.dropdown.Option("R1"),
            ft.dropdown.Option("R2"),
            ft.dropdown.Option("R3"),
            ft.dropdown.Option("IM1"),
        ],
        width=340,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    batch_field = ft.TextField(
        label=translations.t('field_batch', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.NUMBERS,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    qty_field = ft.TextField(
        label=translations.t('field_qty', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.INVENTORY_2,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    actual_weight_field = ft.TextField(
        label=translations.t('field_actual_weight', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.SCALE,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    waste_weight_field = ft.TextField(
        label=translations.t('field_waste_weight', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.DELETE_SWEEP,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    colorant_field = ft.TextField(
        label="كمية الملون (كغ)" if rtl else "Qté Colorant (kg)",
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.COLORIZE,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    low_prod_reason_field = ft.TextField(
        label=translations.t('field_low_prod_reason', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.WARNING_AMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ORANGE_400),
        focused_border_color=ft.colors.ORANGE_400,
        visible=False,
    )
    
    high_waste_reason_field = ft.TextField(
        label=translations.t('field_high_waste_reason', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.ERROR_OUTLINE,
        border_color=ft.colors.with_opacity(0.3, ft.colors.RED_400),
        focused_border_color=ft.colors.RED_400,
        visible=False,
    )

    downtime_min_field = ft.TextField(
        label=translations.t('field_downtime_min', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.TIMER,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    downtime_reason_field = ft.TextField(
        label=translations.t('field_downtime_reason', page),
        width=340,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.NOTE_ALT_OUTLINED,
        multiline=True,
        min_lines=1,
        max_lines=3,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )

    # Real-time Indicators (Glassmorphic panel on the left)
    name_indicator = ft.Text("—", size=15, color=ft.colors.ON_SURFACE, weight=ft.FontWeight.BOLD)
    unit_weight_indicator = ft.Text("—", size=15, color=ft.colors.ON_SURFACE, weight=ft.FontWeight.BOLD)
    theo_weight_indicator = ft.Text("—", size=15, color=ft.colors.ON_SURFACE, weight=ft.FontWeight.BOLD)
    waste_rate_indicator = ft.Text("—", size=15, color=ft.colors.ON_SURFACE, weight=ft.FontWeight.BOLD)
    alert_box = ft.Container(
        content=ft.Text(translations.t('realtime_default_msg', page), size=13, color=ft.colors.with_opacity(0.6, ft.colors.ON_SURFACE), rtl=rtl, text_align=ft.TextAlign.CENTER),
        padding=15,
        border_radius=10,
        bgcolor=ft.colors.with_opacity(0.03, ft.colors.ON_SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
        alignment=ft.alignment.center,
        width=340
    )

    def calculate_realtime_metrics(e):
        # 1. Product selections
        selected_code = product_dropdown.value
        p_data = product_map.get(selected_code)
        
        if p_data:
            name_indicator.value = p_data['designation']
            unit_weight_indicator.value = f"{p_data['poids_theorique_gr']} " + translations.t('gram_unit', page)
        else:
            name_indicator.value = "—"
            unit_weight_indicator.value = "—"
            
        # 2. Quantities
        try:
            qty = float(qty_field.value) if qty_field.value else 0.0
        except ValueError:
            qty = 0.0
            
        # 3. Theo weight calculations
        if p_data and qty > 0:
            theo_w = qty * (p_data['poids_theorique_gr'] / 1000.0)
            theo_weight_indicator.value = f"{theo_w:.3f} " + translations.t('unit_kg', page)
        else:
            theo_w = 0.0
            theo_weight_indicator.value = "—"
            
        # Check machine dependencies
        selected_machine = machine_dropdown.value
        is_no_actual_weight = selected_machine in ["R1", "R2", "R3", "S1"]
        
        actual_weight_field.disabled = is_no_actual_weight
        if is_no_actual_weight:
            actual_weight_field.value = ""
            actual_weight_field.label = translations.t('field_actual_weight_disabled', page)
        else:
            actual_weight_field.label = translations.t('field_actual_weight', page)
            
        # 4. Waste rate calculations
        try:
            waste_w = float(waste_weight_field.value) if waste_weight_field.value else 0.0
            if is_no_actual_weight:
                actual_w = theo_w
            else:
                actual_w = float(actual_weight_field.value) if actual_weight_field.value else 0.0
        except ValueError:
            actual_w = theo_w if is_no_actual_weight else 0.0
            waste_w = 0.0
            
        total_input_w = actual_w + waste_w
        if total_input_w > 0:
            rate = (waste_w / total_input_w) * 100.0
            waste_rate_indicator.value = f"{rate:.2f}%"
        else:
            rate = 0.0
            waste_rate_indicator.value = "—"
            
        is_high_waste = False
        is_low_prod = False
        
        # 5. Threshold warning evaluations
        if p_data and (qty > 0 or actual_w > 0 or waste_w > 0):
            # Check waste deviation
            limit_dechet = p_data['standard_dechet'] * 100.0  # e.g., 0.07 * 100 = 7%
            
            # Check weight deviation (actual vs theoretical)
            weight_dev_pct = 0.0
            if theo_w > 0 and actual_w > 0 and not is_no_actual_weight:
                weight_dev_pct = abs(actual_w - theo_w) / theo_w * 100.0
                
            cadence_theo = p_data.get('cadence_theo') or 0.0
            cadence_theo_8h = cadence_theo * 8
                
            if rate > limit_dechet:
                is_high_waste = True
            if cadence_theo_8h > 0 and qty > 0 and qty < 0.9 * cadence_theo_8h:
                is_low_prod = True
                
            if is_high_waste:
                alert_box.content = ft.Text(translations.t('realtime_high_waste_msg', page).format(f"{rate:.2f}", f"{limit_dechet:.1f}"), size=13, color=ft.colors.RED_400, weight=ft.FontWeight.W_500, rtl=rtl, text_align=ft.TextAlign.CENTER)
                alert_box.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
                alert_box.border = ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.RED_400))
            elif is_low_prod:
                alert_box.content = ft.Text(translations.t('realtime_low_prod_msg', page).format(int(qty), int(cadence_theo_8h)), size=13, color=ft.colors.ORANGE_400, weight=ft.FontWeight.W_500, rtl=rtl, text_align=ft.TextAlign.CENTER)
                alert_box.bgcolor = ft.colors.with_opacity(0.05, ft.colors.ORANGE_900)
                alert_box.border = ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ORANGE_400))
            elif weight_dev_pct > 10.0 and not is_no_actual_weight:
                alert_box.content = ft.Text(translations.t('realtime_dev_msg', page).format(f"{weight_dev_pct:.1f}"), size=13, color=ft.colors.ORANGE_400, weight=ft.FontWeight.W_500, rtl=rtl, text_align=ft.TextAlign.CENTER)
                alert_box.bgcolor = ft.colors.with_opacity(0.05, ft.colors.ORANGE_900)
                alert_box.border = ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ORANGE_400))
            else:
                alert_box.content = ft.Text(translations.t('realtime_ok_msg', page), size=13, color=ft.colors.GREEN_400, weight=ft.FontWeight.W_500, rtl=rtl, text_align=ft.TextAlign.CENTER)
                alert_box.bgcolor = ft.colors.with_opacity(0.05, ft.colors.GREEN_900)
                alert_box.border = ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.GREEN_400))
        else:
            alert_box.content = ft.Text(translations.t('realtime_default_msg', page), size=13, color=ft.colors.with_opacity(0.6, ft.colors.ON_SURFACE), rtl=rtl, text_align=ft.TextAlign.CENTER)
            alert_box.bgcolor = ft.colors.with_opacity(0.03, ft.colors.ON_SURFACE)
            alert_box.border = ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE))
            
        low_prod_reason_field.visible = is_low_prod
        high_waste_reason_field.visible = is_high_waste
            
        page.update()

    # Bind calculations to inputs
    product_dropdown.on_change = calculate_realtime_metrics
    qty_field.on_change = calculate_realtime_metrics
    actual_weight_field.on_change = calculate_realtime_metrics
    waste_weight_field.on_change = calculate_realtime_metrics
    machine_dropdown.on_change = calculate_realtime_metrics

    # Success / Error Message banner
    status_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, rtl=rtl)
    status_container = ft.Container(content=status_text, visible=False, padding=10, border_radius=8, width=340)

    def submit_form(e):
        status_container.visible = False
        page.update()
        
        # Validation checks
        if not date_field.value or not product_dropdown.value or not machine_dropdown.value or not batch_field.value:
            status_text.value = translations.t('form_err_req_fields', page)
            status_text.color = ft.colors.RED_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
            status_container.visible = True
            page.update()
            return
            
        try:
            date_str = date_field.value.strip()
            datetime.datetime.strptime(date_str, "%Y-%m-%d")  # Verify date format
        except ValueError:
            status_text.value = translations.t('form_err_date_format', page)
            status_text.color = ft.colors.RED_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
            status_container.visible = True
            page.update()
            return
            
        try:
            qte = float(qty_field.value) if qty_field.value else 0.0
            waste_w = float(waste_weight_field.value) if waste_weight_field.value else 0.0
            colorant_w = float(colorant_field.value) if colorant_field.value else 0.0
            downtime_m = float(downtime_min_field.value) if downtime_min_field.value else 0.0
            
            p_data = product_map[product_dropdown.value]
            unit_w_gr = p_data['poids_theorique_gr']
            theo_w_kg = qte * (unit_w_gr / 1000.0)
            
            is_no_actual_weight = machine_dropdown.value in ["R1", "R2", "R3", "S1"]
            if is_no_actual_weight:
                act_w = theo_w_kg
            else:
                act_w = float(actual_weight_field.value) if actual_weight_field.value else 0.0
                
            if qte <= 0 or act_w < 0 or waste_w < 0 or colorant_w < 0 or downtime_m < 0:
                raise ValueError()
        except ValueError:
            status_text.value = translations.t('form_err_positive', page)
            status_text.color = ft.colors.RED_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
            status_container.visible = True
            page.update()
            return
            
        if low_prod_reason_field.visible and not low_prod_reason_field.value.strip():
            status_text.value = translations.t('form_err_low_prod', page)
            status_text.color = ft.colors.ORANGE_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.ORANGE_900)
            status_container.visible = True
            page.update()
            return
            
        if high_waste_reason_field.visible and not high_waste_reason_field.value.strip():
            status_text.value = translations.t('form_err_high_waste', page)
            status_text.color = ft.colors.RED_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
            status_container.visible = True
            page.update()
            return

        # Fetch product reference
        p_data = product_map[product_dropdown.value]
        code_art = p_data['code_article']
        designation = p_data['designation']
        unit_w_gr = p_data['poids_theorique_gr']
        
        # Calculate derived fields
        theo_w_kg = qte * (unit_w_gr / 1000.0)
        dechet_pce = waste_w / (unit_w_gr / 1000.0)
        
        # Adjust weight for non-standard machines
        total_w = act_w + waste_w
        taux_rebut = waste_w / total_w if total_w > 0 else 0.0
        
        # Submit to DB
        record_id = database.add_production_record(
            date=date_str,
            username=current_user['username'],
            code_article=code_art,
            designation=designation,
            machine=machine_dropdown.value,
            num_lot=batch_field.value.strip(),
            qte_prod=qte,
            poid_theo=theo_w_kg,
            poid_reel=act_w,
            dechet_pce=dechet_pce,
            dechet_kg=waste_w,
            taux_rebut=taux_rebut,
            low_prod_reason=low_prod_reason_field.value.strip() if low_prod_reason_field.visible else "",
            high_waste_reason=high_waste_reason_field.value.strip() if high_waste_reason_field.visible else "",
            colorant_kg=colorant_w,
            downtime_min=downtime_m,
            downtime_reason=downtime_reason_field.value.strip() if downtime_reason_field.value else ""
        )
        
        if record_id:
            status_text.value = translations.t('status_succ_db', page)
            status_text.color = ft.colors.GREEN_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.GREEN_900)
            status_container.visible = True
            
            # Reset entry inputs (keep date/machine/batch for quicker consecutive logs)
            qty_field.value = ""
            actual_weight_field.value = ""
            waste_weight_field.value = ""
            colorant_field.value = ""
            downtime_min_field.value = ""
            downtime_reason_field.value = ""
            low_prod_reason_field.value = ""
            high_waste_reason_field.value = ""
            calculate_realtime_metrics(None)
            page.update()
            
            if on_save_success:
                on_save_success()
        else:
            status_text.value = translations.t('status_err_db', page)
            status_text.color = ft.colors.RED_400
            status_container.bgcolor = ft.colors.with_opacity(0.05, ft.colors.RED_900)
            status_container.visible = True
            page.update()

    # Submit Button
    submit_btn = ft.ElevatedButton(
        text=translations.t('save_record', page),
        icon=ft.icons.SAVE,
        width=340,
        height=48,
        disabled=is_visitor,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.TEAL_600 if not is_visitor else ft.colors.GREY_600,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=submit_form
    )

    visitor_warning = ft.Container(
        content=ft.Text(translations.t('visitor_warn', page), size=13, color=ft.colors.AMBER_400, weight=ft.FontWeight.BOLD, rtl=rtl, text_align=ft.TextAlign.CENTER),
        padding=10,
        border_radius=8,
        bgcolor=ft.colors.with_opacity(0.05, ft.colors.AMBER_900),
        border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.AMBER_400)),
        width=340,
        visible=is_visitor
    )

    # UI Design Layout Split
    left_indicator_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(translations.t('indicator_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400, rtl=rtl),
                ft.Container(height=10),
                
                # Indicators Table Rows
                ft.Row([name_indicator, ft.Text(translations.t('ind_product', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True)] if rtl else [ft.Text(translations.t('ind_product', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True), name_indicator], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START),
                ft.Row([unit_weight_indicator, ft.Text(translations.t('ind_theo_w_unit', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True)] if rtl else [ft.Text(translations.t('ind_theo_w_unit', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True), unit_weight_indicator], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START),
                ft.Row([theo_weight_indicator, ft.Text(translations.t('ind_theo_w_total', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True)] if rtl else [ft.Text(translations.t('ind_theo_w_total', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True), theo_weight_indicator], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START),
                ft.Row([waste_rate_indicator, ft.Text(translations.t('ind_waste_rate', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True)] if rtl else [ft.Text(translations.t('ind_waste_rate', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl, expand=True), waste_rate_indicator], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START),
                
                ft.Container(height=15),
                alert_box,
                ft.Container(height=10),
                visitor_warning,
                status_container
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START
        ),
        padding=25,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        width=380,
    )

    right_form_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(translations.t('form_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400, rtl=rtl),
                ft.Container(height=10),
                date_field,
                product_dropdown,
                machine_dropdown,
                batch_field,
                qty_field,
                actual_weight_field,
                waste_weight_field,
                colorant_field,
                downtime_min_field,
                downtime_reason_field,
                low_prod_reason_field,
                high_waste_reason_field,
                ft.Container(height=15),
                submit_btn
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START
        ),
        padding=25,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        width=380,
    )

    form_row_layout = ft.Row(
        controls=[left_indicator_panel, right_form_panel] if rtl else [right_form_panel, left_indicator_panel],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=40
    )

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(translations.t('entry_header', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START
            ),
            ft.Container(height=20),
            ft.Container(content=form_row_layout, alignment=ft.alignment.center, expand=True)
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
