import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import datetime
import database
import auth
import translations

def get_view(page: ft.Page):
    current_user = auth.get_current_user()
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    default_name = current_user['full_name'] if current_user else ("زائر" if rtl else "Visiteur")
    default_role = current_user['role'] if current_user else "visitor"

    # Form Controls
    name_field = ft.TextField(
        label=translations.t('feedback_name', page),
        value=default_name,
        width=400,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.PERSON_OUTLINE,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    category_dropdown = ft.Dropdown(
        label=translations.t('feedback_category', page),
        value=translations.t('cat_prod', page),
        options=[
            ft.dropdown.Option(translations.t('cat_prod', page)),
            ft.dropdown.Option(translations.t('cat_qhse', page)),
            ft.dropdown.Option(translations.t('cat_maint', page)),
            ft.dropdown.Option(translations.t('cat_app', page)),
            ft.dropdown.Option(translations.t('cat_other', page)),
        ],
        width=400,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )
    
    message_field = ft.TextField(
        label=translations.t('feedback_msg', page),
        width=400,
        multiline=True,
        min_lines=4,
        max_lines=6,
        rtl=rtl,
        text_align=align,
        prefix_icon=ft.icons.CHAT_BUBBLE_OUTLINE,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
    )

    # Gratitude / Appreciation Display Container
    thanks_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.FAVORITE, color=ft.colors.RED_400, size=30),
                ft.Text(translations.t('feedback_thanks_title', page), size=18, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400, rtl=rtl)
            ], rtl=rtl, alignment=ft.MainAxisAlignment.CENTER),
            ft.Text(
                translations.t('feedback_thanks_msg', page),
                size=13,
                color=ft.colors.with_opacity(0.9, ft.colors.ON_SURFACE),
                rtl=rtl,
                text_align=ft.TextAlign.CENTER
            )
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=20,
        bgcolor=ft.colors.with_opacity(0.06, ft.colors.TEAL_400),
        border=ft.border.all(1, ft.colors.with_opacity(0.3, ft.colors.TEAL_400)),
        border_radius=16,
        visible=False,
        width=400
    )

    feed_column = ft.Column(spacing=15, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def load_feed():
        items = database.get_all_feedback()
        feed_column.controls.clear()
        
        if not items:
            feed_column.controls.append(
                ft.Container(
                    content=ft.Text(
                        "لا توجد ملاحظات أو نصائح مسجلة بعد. كن أول من يشاركنا برأيه!" if rtl else "Aucune remarque enregistrée pour le moment. Soyez le premier !",
                        size=14,
                        color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE)
                    ),
                    alignment=ft.alignment.center,
                    padding=30
                )
            )
        else:
            for item in items:
                role_label = item['role']
                if role_label == 'admin':
                    role_tag = "إدارة" if rtl else "Admin"
                    badge_color = ft.colors.PURPLE_400
                elif role_label == 'user':
                    role_tag = "عامل / مشغل" if rtl else "Opérateur"
                    badge_color = ft.colors.TEAL_400
                else:
                    role_tag = "زائر" if rtl else "Visiteur"
                    badge_color = ft.colors.BLUE_400
                    
                created_dt = str(item.get('created_at', ''))[:16]
                
                feed_column.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.icons.ACCOUNT_CIRCLE, color=badge_color, size=24),
                                    ft.Text(item['sender_name'], size=14, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
                                    ft.Container(
                                        content=ft.Text(role_tag, size=10, color=badge_color, weight=ft.FontWeight.BOLD),
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        bgcolor=ft.colors.with_opacity(0.12, badge_color),
                                        border_radius=6
                                    )
                                ], spacing=8, rtl=rtl),
                                ft.Text(created_dt, size=11, color=ft.colors.with_opacity(0.4, ft.colors.ON_SURFACE))
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, rtl=rtl),
                            
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(item['category'], size=11, color=ft.colors.AMBER_400, weight=ft.FontWeight.BOLD),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    bgcolor=ft.colors.with_opacity(0.1, ft.colors.AMBER_400),
                                    border_radius=8
                                )
                            ], rtl=rtl),
                            
                            ft.Text(item['message'], size=13, color=ft.colors.with_opacity(0.9, ft.colors.ON_SURFACE), rtl=rtl)
                        ], spacing=8),
                        padding=18,
                        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
                        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
                        border_radius=12
                    )
                )

    def submit_feedback(e):
        name = name_field.value.strip() if name_field.value else ("زائر" if rtl else "Visiteur")
        cat = category_dropdown.value
        msg = message_field.value.strip() if message_field.value else ""
        
        if not msg:
            page.snack_bar = ft.SnackBar(
                ft.Text("⚠️ يرجى كتابة نص الملاحظة أو النصيحة قبل الإرسال." if rtl else "⚠️ Veuillez saisir votre remarque avant d'envoyer.", color=ft.colors.WHITE),
                bgcolor=ft.colors.RED_700
            )
            page.snack_bar.open = True
            page.update()
            return
            
        # Insert to DB
        database.add_feedback(name, default_role, cat, msg)
        
        # Clear message
        message_field.value = ""
        
        # Show Thanks Card
        thanks_card.visible = True
        
        # Refresh Feed List
        load_feed()
        page.update()

    submit_btn = ft.ElevatedButton(
        text=translations.t('feedback_submit', page),
        icon=ft.icons.SEND,
        width=400,
        height=48,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.TEAL_600,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=submit_feedback
    )

    load_feed()

    # Layout Left & Right
    form_panel = ft.Container(
        content=ft.Column([
            ft.Text("إضافة ملاحظة أو نصيحة جديدة" if rtl else "Nouvelle Suggestion / Conseil", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400, rtl=rtl),
            ft.Container(height=5),
            name_field,
            category_dropdown,
            message_field,
            ft.Container(height=10),
            submit_btn,
            thanks_card
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START),
        padding=25,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        width=450
    )

    feed_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.icons.FORUM, color=ft.colors.TEAL_400, size=24),
                ft.Text(translations.t('feedback_list_title', page), size=16, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ], rtl=rtl),
            ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            feed_column
        ], spacing=12, expand=True),
        padding=25,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        border=ft.border.all(1, ft.colors.with_opacity(0.08, ft.colors.ON_SURFACE)),
        expand=True
    )

    main_row = ft.Row(
        controls=[form_panel, feed_panel] if rtl else [feed_panel, form_panel],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=25,
        expand=True
    )

    title_row = ft.Row(
        controls=[
            ft.Icon(ft.icons.RATE_REVIEW, color=ft.colors.TEAL_400, size=35),
            ft.Text(translations.t('feedback_title', page), size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
        ] if not rtl else [
            ft.Text(translations.t('feedback_title', page), size=22, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE, rtl=rtl),
            ft.Icon(ft.icons.RATE_REVIEW, color=ft.colors.TEAL_400, size=35),
        ],
        alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END
    )

    return ft.Column(
        controls=[
            title_row,
            ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
            ft.Container(height=10),
            main_row
        ],
        spacing=0,
        expand=True
    )
