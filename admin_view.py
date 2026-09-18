import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import database
import auth
import translations

def get_view(page: ft.Page):
    current_user = auth.get_current_user()
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    # 1. Security Check: Only Admins are authorized
    if current_user['role'] != 'admin':
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=ft.icons.LOCK, size=80, color=ft.colors.RED_400),
                    ft.Text(translations.t('admin_unauthorized_title', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.RED_400, rtl=rtl),
                    ft.Text(translations.t('admin_unauthorized_desc', page), size=14, color=ft.colors.with_opacity(0.7, ft.colors.ON_SURFACE), rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            alignment=ft.alignment.center,
            expand=True
        )

    # 2. Main Containers
    user_list_container = ft.Container(expand=True)
    product_list_container = ft.Container(expand=True)

    # Notification Snackbar helper
    def show_toast(text, is_error=False):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(text, size=14, rtl=rtl),
            bgcolor=ft.colors.RED_600 if is_error else ft.colors.GREEN_600
        )
        page.snack_bar.open = True
        page.update()

    # ==========================================
    # USER MANAGEMENT SUBPANEL
    # ==========================================
    u_username = ft.TextField(label=translations.t('field_username_unique', page), width=170, rtl=rtl, height=45, text_size=13, text_align=align)
    u_fullname = ft.TextField(label=translations.t('field_fullname_employee', page), width=170, rtl=rtl, height=45, text_size=13, text_align=align)
    u_password = ft.TextField(label=translations.t('field_password', page), width=170, password=True, can_reveal_password=True, rtl=rtl, height=45, text_size=13, text_align=align)
    u_role = ft.Dropdown(
        label=translations.t('field_role', page),
        options=[
            ft.dropdown.Option("admin", translations.t('opt_role_admin', page)),
            ft.dropdown.Option("user", translations.t('opt_role_user', page)),
            ft.dropdown.Option("visitor", translations.t('opt_role_visitor', page)),
        ],
        width=150,
        height=45,
    )

    def refresh_user_list():
        users = database.get_all_users()
        user_rows = []
        for u in users:
            def delete_u(username=u['username']):
                if username == current_user['username']:
                    show_toast(translations.t('toast_delete_self_err', page), is_error=True)
                    return
                database.delete_user(username)
                show_toast(translations.t('toast_delete_user_succ', page).format(username))
                refresh_user_list()

            role_label = translations.t('opt_role_admin', page) if u['role'] == 'admin' else (translations.t('opt_role_user', page) if u['role'] == 'user' else translations.t('opt_role_visitor', page))
            
            row_cells = [
                ft.DataCell(ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_400, on_click=lambda e, uname=u['username']: delete_u(uname))),
                ft.DataCell(ft.Text(role_label)),
                ft.DataCell(ft.Text(u['full_name'], rtl=rtl)),
                ft.DataCell(ft.Text(u['username'], color=ft.colors.TEAL_300)),
            ]

            user_rows.append(
                ft.DataRow(
                    cells=row_cells if rtl else list(reversed(row_cells))
                )
            )
            
        columns_list = [
            ft.DataColumn(ft.Text(translations.t('col_actions', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('field_role', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_fullname', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_username', page), rtl=rtl)),
        ]
        
        user_list_container.content = ft.DataTable(
            columns=columns_list if rtl else list(reversed(columns_list)),
            rows=user_rows,
            heading_row_color=ft.colors.with_opacity(0.06, ft.colors.ON_SURFACE),
            column_spacing=25,
            horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE))
        )
        page.update()

    def submit_user(e):
        uname = u_username.value.strip()
        fname = u_fullname.value.strip()
        pwd = u_password.value
        role = u_role.value
        
        if not uname or not fname or not pwd or not role:
            show_toast(translations.t('toast_fill_all_fields', page), is_error=True)
            return
            
        hashed = auth.hash_password(pwd)
        if database.add_user(uname, hashed, fname, role):
            show_toast(translations.t('toast_user_added', page).format(uname))
            u_username.value = ""
            u_fullname.value = ""
            u_password.value = ""
            u_role.value = None
            refresh_user_list()
        else:
            show_toast(translations.t('toast_username_taken', page), is_error=True)

    user_add_btn = ft.ElevatedButton(
        text=translations.t('btn_add_user', page),
        icon=ft.icons.PERSON_ADD,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.TEAL_600),
        on_click=submit_user
    )

    user_form_row = ft.Row(
        controls=[user_add_btn, u_role, u_password, u_fullname, u_username] if rtl else [u_username, u_fullname, u_password, u_role, user_add_btn],
        alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START,
        spacing=10
    )

    # ==========================================
    # ART_PF PRODUCT REFERENCE EDITOR SUBPANEL
    # ==========================================
    p_code = ft.TextField(label=translations.t('field_prod_code', page), width=130, rtl=rtl, height=45, text_size=13, text_align=align)
    p_desig = ft.TextField(label=translations.t('field_prod_desig', page), width=150, rtl=rtl, height=45, text_size=13, text_align=align)
    p_weight = ft.TextField(label=translations.t('field_prod_weight', page), width=120, rtl=rtl, height=45, text_size=13, keyboard_type=ft.KeyboardType.NUMBER, text_align=align)
    p_waste = ft.TextField(label=translations.t('field_prod_waste', page), width=130, rtl=rtl, height=45, text_size=13, keyboard_type=ft.KeyboardType.NUMBER, text_align=align)
    p_cadence = ft.TextField(label=translations.t('field_prod_cadence', page), width=130, rtl=rtl, height=45, text_size=13, keyboard_type=ft.KeyboardType.NUMBER, text_align=align)
    p_material = ft.TextField(label=translations.t('field_prod_material', page), width=120, rtl=rtl, height=45, text_size=13, text_align=align)

    def refresh_product_list():
        products = database.get_all_products()
        prod_rows = []
        for p in products:
            def delete_p(code=p['code_article']):
                database.delete_product(code)
                show_toast(translations.t('toast_delete_prod_succ', page).format(code))
                refresh_product_list()
                
            def edit_p(prod=p):
                p_code.value = prod['code_article']
                p_desig.value = prod['designation']
                p_weight.value = str(prod['poids_theorique_gr'])
                p_waste.value = str(prod['standard_dechet'])
                p_cadence.value = str(prod['cadence_theo']) if prod['cadence_theo'] else ""
                p_material.value = prod['matiere_premiere'] if prod['matiere_premiere'] else ""
                page.update()
                show_toast(translations.t('toast_edit_prod', page).format(prod['code_article']))

            row_cells = [
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(ft.icons.EDIT, icon_color=ft.colors.BLUE_400, on_click=lambda e, prod=p: edit_p(prod)),
                        ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color=ft.colors.RED_400, on_click=lambda e, code=p['code_article']: delete_p(code)),
                    ])
                ),
                ft.DataCell(ft.Text(p['matiere_premiere'] or "—")),
                ft.DataCell(ft.Text(f"{p['standard_dechet'] * 100:.1f}%" if p['standard_dechet'] else "0%")),
                ft.DataCell(ft.Text(f"{p['poids_theorique_gr']} " + translations.t('gram_unit', page))),
                ft.DataCell(ft.Text(p['designation'], rtl=rtl)),
                ft.DataCell(ft.Text(p['code_article'], color=ft.colors.TEAL_300)),
            ]

            prod_rows.append(
                ft.DataRow(
                    cells=row_cells if rtl else list(reversed(row_cells))
                )
            )
            
        columns_list = [
            ft.DataColumn(ft.Text(translations.t('col_actions', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_material', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_std_waste', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_theo_weight', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_prod_name', page), rtl=rtl)),
            ft.DataColumn(ft.Text(translations.t('col_prod_code', page), rtl=rtl)),
        ]
        
        product_list_container.content = ft.DataTable(
            columns=columns_list if rtl else list(reversed(columns_list)),
            rows=prod_rows,
            heading_row_color=ft.colors.with_opacity(0.06, ft.colors.ON_SURFACE),
            column_spacing=20,
            horizontal_lines=ft.border.BorderSide(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE))
        )
        page.update()

    def submit_product(e):
        code = p_code.value.strip()
        desig = p_desig.value.strip()
        
        if not code or not desig:
            show_toast(translations.t('toast_prod_fields_required', page), is_error=True)
            return
            
        try:
            weight = float(p_weight.value.strip()) if p_weight.value else 0.0
            waste = float(p_waste.value.strip()) if p_waste.value else 0.0
            cadence = float(p_cadence.value.strip()) if p_cadence.value else None
        except ValueError:
            show_toast(translations.t('toast_prod_numeric_required', page), is_error=True)
            return
            
        material = p_material.value.strip() if p_material.value else None
        
        database.add_or_update_product(
            code_article=code,
            designation=desig,
            poids_theorique_gr=weight,
            standard_dechet=waste,
            cadence_theo=cadence,
            matiere_premiere=material
        )
        
        show_toast(translations.t('toast_prod_saved', page).format(code))
        p_code.value = ""
        p_desig.value = ""
        p_weight.value = ""
        p_waste.value = ""
        p_cadence.value = ""
        p_material.value = ""
        refresh_product_list()

    prod_save_btn = ft.ElevatedButton(
        text=translations.t('btn_save_prod', page),
        icon=ft.icons.SAVE,
        style=ft.ButtonStyle(color=ft.colors.WHITE, bgcolor=ft.colors.TEAL_600),
        on_click=submit_product
    )

    product_form_row = ft.Row(
        controls=[prod_save_btn, p_material, p_cadence, p_waste, p_weight, p_desig, p_code] if rtl else [p_code, p_desig, p_weight, p_waste, p_cadence, p_material, prod_save_btn],
        alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START,
        spacing=8
    )

    # Initial Data Loading
    refresh_user_list()
    refresh_product_list()

    # Layout structuring (Tabs)
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text=translations.t('tab_product_mgmt', page),
                icon=ft.icons.CATEGORY,
                content=ft.Column(
                    controls=[
                        ft.Container(height=10),
                        product_form_row,
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Row([product_list_container], scroll=ft.ScrollMode.ALWAYS, vertical_alignment=ft.CrossAxisAlignment.START),
                            expand=True
                        )
                    ],
                    expand=True
                )
            ),
            ft.Tab(
                text=translations.t('tab_user_mgmt', page),
                icon=ft.icons.PEOPLE,
                content=ft.Column(
                    controls=[
                        ft.Container(height=10),
                        user_form_row,
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Row([user_list_container], scroll=ft.ScrollMode.ALWAYS, vertical_alignment=ft.CrossAxisAlignment.START),
                            expand=True
                        )
                    ],
                    expand=True
                )
            ),
        ],
        expand=True,
    )

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(translations.t('admin_header', page), size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                ],
                alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START
            ),
            ft.Container(height=15),
            tabs
        ],
        spacing=0,
        expand=True
    )
