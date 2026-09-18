import flet as ft
from database import get_active_products, add_transfert_record, get_all_transfert_records
import translations
import datetime

def TransfertView(page: ft.Page):
    rtl = page.client_storage.get("rtl")
    
    # -----------------------------------------------------
    # PAGE TITLE (LOG-FO-016)
    # -----------------------------------------------------
    title_text = "وصل تحويل المنتج النهائي (LOG-FO-016)" if rtl else "Bon de Transfert Produit Fini (LOG-FO-016)"
    page_title = ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400)
    
    version_text = "الإصدار: 01" if rtl else "Version: 01"
    version_badge = ft.Container(
        content=ft.Text(version_text, size=12, color=ft.colors.ON_PRIMARY),
        bgcolor=ft.colors.TEAL_600,
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=4,
    )
    
    header_row = ft.Row([page_title, version_badge], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=rtl)
    
    # -----------------------------------------------------
    # FORM CONTROLS
    # -----------------------------------------------------
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    now_time_str = datetime.datetime.now().strftime("%H:%M")
    
    date_field = ft.TextField(
        label=translations.t('date_label', page),
        value=today_str,
        width=150,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT,
    )
    
    products = get_active_products()
    product_options = [ft.dropdown.Option(f"{p['code_article']} - {p['designation']}") for p in products]
    
    product_dropdown = ft.Dropdown(
        label="رمز المنتج (Code Article)",
        options=product_options,
        width=300,
        border_color=ft.colors.TEAL_400,
    )
    
    qte_field = ft.TextField(
        label="الكمية بالقطع (Quantité pcs)",
        width=180,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )
    
    lot_field = ft.TextField(
        label="رقم الدفعة (N° de Lot)",
        width=180,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.LEFT,
    )
    
    sacs_field = ft.TextField(
        label="عدد الأكياس / الترقيم (Nb Sacs)",
        width=200,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.LEFT,
    )
    
    heure_field = ft.TextField(
        label="ساعة التحويل (Heure)",
        value=now_time_str,
        width=120,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.LEFT,
    )
    
    operateur_field = ft.TextField(
        label="المُسلم / المشغل (Opérateur)",
        width=180,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT,
    )
    
    receptionnaire_field = ft.TextField(
        label="مستلم المخزن (Réceptionnaire)",
        width=180,
        border_color=ft.colors.TEAL_400,
        text_align=ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT,
    )
    
    def on_submit(e):
        if not date_field.value or not product_dropdown.value or not qte_field.value or not lot_field.value:
            page.snack_bar = ft.SnackBar(ft.Text("يرجى ملء جميع الحقول الإجبارية" if rtl else "Veuillez remplir les champs obligatoires"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return
            
        try:
            qte = float(qte_field.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("كمية غير صالحة" if rtl else "Quantité invalide"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()
            return
            
        code_art = product_dropdown.value.split(" - ")[0]
        
        add_transfert_record(
            date=date_field.value,
            code_article=code_art,
            qte_pcs=qte,
            num_lot=lot_field.value,
            nb_sacs=sacs_field.value,
            heure_transfert=heure_field.value,
            operateur=operateur_field.value,
            receptionnaire=receptionnaire_field.value
        )
        
        page.snack_bar = ft.SnackBar(ft.Text("تم تسجيل وصل التحويل بنجاح!" if rtl else "Bon de transfert enregistré avec succès!"), bgcolor=ft.colors.GREEN_700)
        page.snack_bar.open = True
        
        # Reset form fields
        qte_field.value = ""
        lot_field.value = ""
        sacs_field.value = ""
        heure_field.value = datetime.datetime.now().strftime("%H:%M")
        
        load_transfert_table()
        page.update()
        
    submit_btn = ft.ElevatedButton(
        text="تسجيل وصل التحويل (LOG-FO-016)" if rtl else "Enregistrer Bon (LOG-FO-016)",
        icon=ft.icons.SAVE,
        on_click=on_submit,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.TEAL_600,
            padding=15,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )
    
    form_container = ft.Container(
        content=ft.Column([
            ft.Text("إضافة وصل جديد" if rtl else "Nouveau Bon de Transfert", size=18, weight=ft.FontWeight.W_500),
            ft.Divider(),
            ft.Row([date_field, product_dropdown, qte_field, lot_field], wrap=True, rtl=rtl),
            ft.Row([sacs_field, heure_field, operateur_field, receptionnaire_field], wrap=True, rtl=rtl),
            ft.Row([submit_btn], alignment=ft.MainAxisAlignment.END, rtl=rtl)
        ]),
        padding=20,
        border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
        border_radius=10,
        bgcolor=ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE),
        margin=ft.margin.only(bottom=20)
    )
    
    # -----------------------------------------------------
    # HISTORY TABLE
    # -----------------------------------------------------
    table_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    
    def table_cell(text, width=None, expand=False, numeric=False, force_ltr=False):
        return ft.Container(
            content=ft.Text(
                str(text),
                text_align=ft.TextAlign.RIGHT if (rtl and not force_ltr and not numeric) else (ft.TextAlign.CENTER if numeric else ft.TextAlign.LEFT),
                size=13
            ),
            width=width,
            expand=expand,
            padding=ft.padding.symmetric(horizontal=8, vertical=12),
        )

    def load_transfert_table():
        records = get_all_transfert_records(limit=200)
        table_container.controls.clear()
        
        # Header Row
        header_row = ft.Container(
            content=ft.Row([
                table_cell("التاريخ" if rtl else "Date", width=100),
                table_cell("المنتج" if rtl else "Produit", expand=True),
                table_cell("الكمية" if rtl else "Quantité", width=100, numeric=True),
                table_cell("رقم الدفعة" if rtl else "Lot", width=100),
                table_cell("الأكياس" if rtl else "Sacs", width=100),
                table_cell("الساعة" if rtl else "Heure", width=80),
                table_cell("المُسلم" if rtl else "Opérateur", width=100),
                table_cell("المستلم" if rtl else "Réception", width=100),
            ], rtl=rtl),
            bgcolor=ft.colors.TEAL_700,
            border_radius=ft.border_radius.only(topLeft=8, topRight=8),
        )
        table_container.controls.append(header_row)
        
        # Body rows
        for i, rec in enumerate(records):
            row_color = ft.colors.with_opacity(0.02, ft.colors.ON_SURFACE) if i % 2 == 0 else ft.colors.TRANSPARENT
            
            table_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        table_cell(rec['date'], width=100),
                        table_cell(rec['code_article'], expand=True, force_ltr=True),
                        table_cell(f"{rec['qte_pcs']:.0f}", width=100, numeric=True),
                        table_cell(rec['num_lot'], width=100, force_ltr=True),
                        table_cell(rec['nb_sacs'], width=100, force_ltr=True),
                        table_cell(rec['heure_transfert'], width=80),
                        table_cell(rec['operateur'], width=100),
                        table_cell(rec['receptionnaire'], width=100),
                    ], rtl=rtl),
                    bgcolor=row_color,
                    border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)))
                )
            )
            
    load_transfert_table()
    
    return ft.Container(
        content=ft.Column([
            header_row,
            ft.Divider(),
            form_container,
            ft.Text("سجل تحويلات المنتجات (آخر 200 سجل)" if rtl else "Historique des transferts", size=18, weight=ft.FontWeight.W_500),
            table_container
        ], expand=True),
        padding=20,
        expand=True
    )
