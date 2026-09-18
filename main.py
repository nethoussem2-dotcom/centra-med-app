import flet as ft
# Support Flet versions where colors namespace is capitalized as Colors
if not hasattr(ft, "colors") and hasattr(ft, "Colors"):
    ft.colors = ft.Colors

import os
import sys
import threading

def log_exception(exc_type, exc_value, exc_traceback):
    import traceback
    # Ignore RuntimeError about event loop being closed on exit
    if exc_type is RuntimeError and "Event loop is closed" in str(exc_value):
        return
    with open("app_error.log", "a", encoding="utf-8") as f:
        f.write(f"\nUnhandled Exception:\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)

sys.excepthook = log_exception
threading.excepthook = lambda args: log_exception(args.exc_type, args.exc_value, args.exc_traceback)

# Ensure database path is resolvable in imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import database
import auth
import translations
from views import login_view, dashboard_view, entry_view, history_view, admin_view, suivi_view, analysis_view, batch_view, kpi_view, feedback_view, transfert_view

def main(page: ft.Page):
    # 1. Desktop Window Properties
    page.title = translations.t('app_title', page)
    page.window.maximized = True
    page.window.min_width = 1100
    page.window.min_height = 700
    page.theme_mode = ft.ThemeMode.DARK

    page.padding = 0
    page.spacing = 0
    
    # Use local Material Symbols font for faster offline rendering
    page.fonts = {
        "Material Symbols Outlined": "/fonts/MaterialSymbolsOutlined.ttf"
    }
    
    # Custom Modern Theme Colors
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.TEAL_600,
            secondary=ft.colors.BLUE_600,
            background=ft.colors.GREY_50,
            surface=ft.colors.WHITE,
            on_background=ft.colors.BLACK87,
            on_surface=ft.colors.BLACK87
        )
    )
    
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.colors.TEAL_400,
            secondary=ft.colors.BLUE_400,
            background=ft.colors.BLUE_GREY_900,
            surface=ft.colors.GREY_900,
            on_background=ft.colors.WHITE,
            on_surface=ft.colors.WHITE
        )
    )


    # Database Initialization Check
    database.init_db()

    # Active dynamic area inside the shell
    content_area = ft.Container(expand=True, padding=25)

    def change_view(view_name):
        """Dynamic route renderer inside the shell content area."""
        try:
            # Load the selected view control
            if view_name == "dashboard":
                content_area.content = dashboard_view.get_view(page)
            elif view_name == "entry":
                content_area.content = entry_view.get_view(page, on_save_success=lambda: change_view("suivi"))
            elif view_name == "history":
                content_area.content = history_view.get_view(page)
            elif view_name == "suivi":
                content_area.content = suivi_view.get_view(page)
            elif view_name == "analysis":
                content_area.content = analysis_view.get_view(page)
            elif view_name == "kpi":
                content_area.content = kpi_view.get_view(page)
            elif view_name == "batch":
                content_area.content = batch_view.get_view(page)
            elif view_name == "feedback":
                content_area.content = feedback_view.get_view(page)
            elif view_name == "admin":
                content_area.content = admin_view.get_view(page)
                
            page.update()
        except Exception as ex:
            import traceback
            with open("app_error.log", "a", encoding="utf-8") as f:
                f.write(f"\nError in change_view for {view_name}:\n")
                traceback.print_exc(file=f)
            raise ex

    def toggle_language(e, user):
        current_lang = page.client_storage.get("language") or "ar"
        new_lang = "fr" if current_lang == "ar" else "ar"
        page.client_storage.set("language", new_lang)
        # Re-render shell
        show_app_shell(user)

    def build_sidebar(user):
        """Constructs an elegant, modern side navigation drawer based on user permissions."""
        rtl = translations.is_rtl(page)
        nav_items = []

        dest_routes = ["entry", "suivi", "transfert", "analysis", "kpi", "batch", "feedback", "admin"]
        destinations = [
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.EDIT_NOTE, color=ft.colors.TEAL_400),
                label=translations.t('nav_entry', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.TABLE_CHART, color=ft.colors.TEAL_400),
                label=translations.t('nav_suivi', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.LOCAL_SHIPPING, color=ft.colors.TEAL_400),
                label=translations.t('nav_transfert', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.INSIGHTS, color=ft.colors.TEAL_400),
                label=translations.t('nav_analysis', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.SPEED, color=ft.colors.TEAL_400),
                label=translations.t('nav_kpi', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.CATEGORY, color=ft.colors.TEAL_400),
                label=translations.t('nav_batch', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.RATE_REVIEW, color=ft.colors.TEAL_400),
                label=translations.t('nav_feedback', page),
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.ADMIN_PANEL_SETTINGS, color=ft.colors.TEAL_400),
                label=translations.t('nav_admin', page),
            )
        ]

        active_index = [1 if user['role'] == 'visitor' else 0]

        def on_nav_change(e):
            selected_dest = e.control.selected_index
            if selected_dest < len(dest_routes):
                target_route = dest_routes[selected_dest]
                
                if user['role'] == 'visitor' and target_route not in ["suivi", "analysis", "kpi", "batch", "feedback"]:
                    warn_msg = "⚠️ أنت زائر. لا تملك الصلاحية للدخول إلى هذه الصفحة." if translations.is_rtl(page) else "⚠️ Vous êtes visiteur. Accès refusé."
                    page.snack_bar = ft.SnackBar(ft.Text(warn_msg, color=ft.colors.WHITE), bgcolor=ft.colors.RED_700)
                    page.snack_bar.open = True
                    e.control.selected_index = active_index[0]
                    page.update()
                    return
                    
                if user['role'] == 'user' and target_route == "admin":
                    page.snack_bar = ft.SnackBar(ft.Text("⚠️ " + translations.t('admin_unauthorized_title', page), color=ft.colors.WHITE), bgcolor=ft.colors.RED_700)
                    page.snack_bar.open = True
                    e.control.selected_index = active_index[0]
                    page.update()
                    return
                
                active_index[0] = selected_dest
                sidebar_drawer.open = False
                change_view(target_route)
            
        role_text = translations.t('system_admin', page) if user['role'] == 'admin' else (translations.t('production_user', page) if user['role'] == 'user' else translations.t('guest_user', page))

        sidebar_drawer = ft.NavigationDrawer(
            selected_index=active_index[0],
            on_change=on_nav_change,
            controls=[
                ft.Container(height=15),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.LOCAL_HOSPITAL, size=40, color=ft.colors.TEAL_400),
                        ft.Text("CENTRA MED", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.TEAL_400),
                        ft.Text(translations.t('app_title_short', page), size=11, color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.center,
                    padding=15
                ),
                ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
                *destinations,
                ft.Divider(color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)),
                
                # Dynamic User badge details
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(translations.t('active', page), size=11, color=ft.colors.GREEN_400, weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.icons.CIRCLE, size=8, color=ft.colors.GREEN_400),
                        ], alignment=ft.MainAxisAlignment.END if rtl else ft.MainAxisAlignment.START, spacing=5),
                        ft.Text(user['full_name'], size=13, weight=ft.FontWeight.BOLD, rtl=rtl),
                        ft.Text(
                            role_text, 
                            size=11, 
                            color=ft.colors.with_opacity(0.6, ft.colors.ON_SURFACE),
                            rtl=rtl
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END if rtl else ft.CrossAxisAlignment.START),
                    padding=15,
                    rtl=rtl
                ),
                
                # Logout action button
                ft.Container(
                    content=ft.ElevatedButton(
                        text=translations.t('logout', page),
                        icon=ft.icons.LOGOUT,
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.RED_800,
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        width=200,
                        on_click=lambda e: do_logout()
                    ),
                    alignment=ft.alignment.center,
                    padding=10
                )
            ],
            bgcolor=ft.colors.with_opacity(0.04, ft.colors.SURFACE),
        )
        return sidebar_drawer

    def show_app_shell(user):
        """Launches the complete authenticated application workspace frame."""
        page.controls.clear()
        page.title = translations.t('app_title', page)
        rtl = translations.is_rtl(page)
        
        # Sidebar drawer build
        sidebar = build_sidebar(user)
        
        # Language Toggle Button
        lang_btn = ft.TextButton(
            text=translations.t('lang_toggle', page),
            icon=ft.icons.LANGUAGE,
            style=ft.ButtonStyle(color=ft.colors.TEAL_400),
            on_click=lambda e: toggle_language(e, user)
        )
        
        # Upper Top Bar
        top_bar = ft.Container(
            content=ft.Row(
                controls=[
                    # Left side items
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.DARK_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE_OUTLINED,
                            on_click=toggle_theme,
                            tooltip=translations.t('theme_tooltip', page)
                        ),
                        lang_btn,
                    ], spacing=5),
                    
                    # Right side Title
                    ft.Row([
                        ft.Text("CENTRA MED PRODUCTION SYSTEMS", size=14, weight=ft.FontWeight.W_500, color=ft.colors.TEAL_400),
                        ft.Icon(ft.icons.STAR_OUTLINE, size=18, color=ft.colors.TEAL_400),
                    ], spacing=10)
                ] if not rtl else [
                    # Left side items (when RTL, row reverses visually, so we keep order)
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.DARK_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE_OUTLINED,
                            on_click=toggle_theme,
                            tooltip=translations.t('theme_tooltip', page)
                        ),
                        lang_btn,
                    ], spacing=5),
                    
                    # Right side Title
                    ft.Row([
                        ft.Icon(ft.icons.STAR_OUTLINE, size=18, color=ft.colors.TEAL_400),
                        ft.Text("CENTRA MED PRODUCTION SYSTEMS", size=14, weight=ft.FontWeight.W_500, color=ft.colors.TEAL_400),
                    ], spacing=10)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.colors.with_opacity(0.06, ft.colors.SURFACE),
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)))
        )
        
        # Side Nav Drawer trigger bar
        menu_button = ft.IconButton(
            icon=ft.icons.MENU, 
            icon_color=ft.colors.TEAL_400, 
            tooltip=translations.t('menu_tooltip', page),
            on_click=lambda e: page.open(sidebar)
        )
        
        # Dynamic Main Shell column
        page.add(
            ft.Column(
                controls=[
                    top_bar,
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                menu_button,
                                ft.Text(translations.t('menu_helper', page), size=12, color=ft.colors.with_opacity(0.4, ft.colors.ON_SURFACE), rtl=rtl)
                            ] if not rtl else [
                                ft.Text(translations.t('menu_helper', page), size=12, color=ft.colors.with_opacity(0.4, ft.colors.ON_SURFACE), rtl=rtl),
                                menu_button
                            ],
                            alignment=ft.MainAxisAlignment.START if not rtl else ft.MainAxisAlignment.END,
                        ),
                        padding=ft.padding.only(left=15 if not rtl else 0, right=15 if rtl else 0, top=5)
                    ),
                    content_area
                ],
                spacing=0,
                expand=True
            )
        )
        
        # Load appropriate view initially
        initial_route = "entry" if user['role'] != 'visitor' else "suivi"
        change_view(initial_route)
        page.open(sidebar)

    def do_login(user):
        """Login handler to load the primary app frame."""
        show_app_shell(user)

    def do_logout():
        """Clears sessions and returns to standard credentials login frame."""
        auth.logout()
        page.controls.clear()
        load_login_screen()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        e.control.icon = ft.icons.DARK_MODE_OUTLINED if page.theme_mode == ft.ThemeMode.LIGHT else ft.icons.LIGHT_MODE_OUTLINED
        page.update()

    def load_login_screen():
        page.controls.clear()
        page.add(login_view.get_view(page, on_login_success=do_login))
        page.update()

    # Initial frame bootstrap
    load_login_screen()

if __name__ == "__main__":
    assets_path = os.path.join(os.path.dirname(__file__), "assets")
    # Run as a Local Web Server to allow access from mobile devices on the local network (Wi-Fi)
    ft.app(target=main, assets_dir=assets_path, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8000)
