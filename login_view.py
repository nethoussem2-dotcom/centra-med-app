import flet as ft
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import auth
import translations
import threading
import time

def get_view(page: ft.Page, on_login_success):
    page.title = translations.t('login_title', page)
    rtl = translations.is_rtl(page)
    align = ft.TextAlign.RIGHT if rtl else ft.TextAlign.LEFT
    
    # Text fields
    username_field = ft.TextField(
        label=translations.t('username', page),
        width=300,
        text_align=align,
        rtl=rtl,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
        prefix_icon=ft.icons.PERSON_OUTLINE,
    )
    
    password_field = ft.TextField(
        label=translations.t('password', page),
        password=True,
        can_reveal_password=True,
        width=300,
        text_align=align,
        rtl=rtl,
        border_color=ft.colors.with_opacity(0.3, ft.colors.ON_SURFACE),
        focused_border_color=ft.colors.TEAL_400,
        prefix_icon=ft.icons.LOCK_OUTLINE,
    )
    
    error_text = ft.Text(
        value="",
        color=ft.colors.RED_400,
        size=14,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
        rtl=rtl
    )
    
    def perform_login(e):
        error_text.value = ""
        page.update()
        
        username = username_field.value.strip()
        password = password_field.value
        
        if not username or not password:
            error_text.value = translations.t('fill_required', page)
            page.update()
            return
            
        success, result = auth.login(username, password)
        if success:
            on_login_success(result)
        else:
            if "كلمة المرور خاطئة" in result or "Invalid credentials" in result or "اسم المستخدم غير موجود" in result:
                error_text.value = translations.t('err_invalid_credentials', page) if 'err_invalid_credentials' in translations.translations['ar'] else result
            else:
                error_text.value = result
            page.update()
 
    def perform_guest_login(e):
        success, result = auth.login("visitor", "visitor123")
        if success:
            on_login_success(result)
        else:
            error_text.value = translations.t('guest_login_fail', page)
            page.update()
 
    login_button = ft.ElevatedButton(
        text=translations.t('login_btn', page),
        icon=ft.icons.LOGIN,
        width=300,
        height=50,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.TEAL_600,
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=perform_login
    )
    
    guest_button = ft.TextButton(
        text=translations.t('guest_btn', page),
        icon=ft.icons.REMOVE_RED_EYE,
        style=ft.ButtonStyle(
            color=ft.colors.TEAL_300,
        ),
        on_click=perform_guest_login
    )
    
    # Glassmorphic Login Card
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    name=ft.icons.PRECISION_MANUFACTURING, 
                    size=60, 
                    color=ft.colors.TEAL_400
                ),
                ft.Text(
                    value="CENTRA MED",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.TEAL_400,
                ),
                ft.Text(
                    value=translations.t('login_subtitle', page),
                    size=16,
                    color=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                    rtl=rtl
                ),
                ft.Container(height=20),
                username_field,
                password_field,
                error_text,
                ft.Container(height=10),
                login_button,
                guest_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        padding=40,
        border_radius=20,
        bgcolor=ft.colors.with_opacity(0.15, ft.colors.BLACK),
        border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.WHITE)),
        blur=ft.Blur(15, 15, ft.BlurTileMode.MIRROR),
        shadow=ft.BoxShadow(
            blur_radius=30,
            color=ft.colors.with_opacity(0.5, ft.colors.BLACK),
            offset=ft.Offset(0, 15)
        ),
        width=400,
        # Removed fixed height to prevent clipping elements
    )
    
    # Background Image for Login Interface
    bg_layer = ft.Container(
        content=ft.Image(
            src="pharma_hero.png",
            fit=ft.ImageFit.COVER,
        ),
        left=0, right=0, top=0, bottom=0,
        opacity=0.4 # Darken it so the login card pops
    )

    login_interface = ft.Stack(
        controls=[
            bg_layer,
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                left=0, right=0, top=0, bottom=0,
            )
        ],
        expand=True
    )
    
    # Splash Screen Layer (Animation)
    splash_text = ft.Text(
        "CENTRA MED\nSmart Production",
        size=45,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
        text_align=ft.TextAlign.CENTER,
    )
    
    # Create animated images for the "video" slideshow effect
    img1 = ft.Image(src="pharma_hero.png", fit=ft.ImageFit.COVER, left=0, right=0, top=0, bottom=0, opacity=1, scale=ft.transform.Scale(1.0), animate_opacity=1000, animate_scale=ft.animation.Animation(3000, ft.AnimationCurve.LINEAR))
    img2 = ft.Image(src="pharma_caps.png", fit=ft.ImageFit.COVER, left=0, right=0, top=0, bottom=0, opacity=0, scale=ft.transform.Scale(1.0), animate_opacity=1000, animate_scale=ft.animation.Animation(3000, ft.AnimationCurve.LINEAR))
    img3 = ft.Image(src="pharma_bottles.png", fit=ft.ImageFit.COVER, left=0, right=0, top=0, bottom=0, opacity=0, scale=ft.transform.Scale(1.0), animate_opacity=1000, animate_scale=ft.animation.Animation(3000, ft.AnimationCurve.LINEAR))
    
    slideshow_container = ft.Stack([img1, img2, img3], expand=True)

    splash_layer = ft.Container(
        content=ft.Stack([
            ft.Container(
                content=slideshow_container,
                left=0, right=0, top=0, bottom=0
            ),
            ft.Container(
                bgcolor=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                alignment=ft.alignment.center,
                left=0, right=0, top=0, bottom=0,
                content=ft.Column([
                    splash_text,
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            )
        ], expand=True),
        expand=True,
        opacity=1.0,
        animate_opacity=1200,
        # Ensures it blocks clicks while fading out
        left=0, right=0, top=0, bottom=0,
    )
    
    # Hide login interface initially
    login_interface.visible = False
    login_interface.opacity = 0.0
    login_interface.animate_opacity = 1000
    
    main_stack = ft.Stack(
        controls=[
            ft.Container(
                content=login_interface,
                bgcolor=ft.colors.BLACK,
                left=0, right=0, top=0, bottom=0
            ),
            splash_layer
        ],
        expand=True
    )

    def run_animation():
        # Slide 1 start zooming
        img1.scale = 1.05
        try: page.update()
        except: return
        time.sleep(2.5)
        
        # Slide 2 crossfade and zoom
        img2.opacity = 1
        img1.opacity = 0
        img2.scale = 1.05
        try: page.update()
        except: return
        time.sleep(2.5)
        
        # Slide 3 crossfade and zoom
        img3.opacity = 1
        img2.opacity = 0
        img3.scale = 1.05
        try: page.update()
        except: return
        time.sleep(2.5)
        
        # Fade out splash entirely
        splash_layer.opacity = 0.0
        try: page.update()
        except: return
        
        time.sleep(1.2)
        splash_layer.visible = False
        
        # Fade in login screen
        login_interface.visible = True
        try: page.update()
        except: return
        
        time.sleep(0.1)
        login_interface.opacity = 1.0
        try: page.update()
        except: pass

    # Start animation thread
    threading.Thread(target=run_animation, daemon=True).start()

    return main_stack
