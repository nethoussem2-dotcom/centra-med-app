import sys
sys.path.append(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app")
try:
    import flet as ft
    import translations
    import auth
    
    # Mock auth
    auth.get_current_user = lambda: {'username': 'admin', 'role': 'admin', 'full_name': 'Test User'}
    
    from views import login_view, dashboard_view, entry_view, history_view, admin_view
    
    def test_main(page: ft.Page):
        # Set to French and verify
        page.client_storage.set("language", "fr")
        
        print("Testing Login View...")
        lv = login_view.get_view(page, lambda u: None)
        
        print("Testing Dashboard View...")
        dv = dashboard_view.get_view(page)
        
        print("Testing Entry View...")
        ev = entry_view.get_view(page)
        
        print("Testing History View...")
        hv = history_view.get_view(page)
        
        print("Testing Admin View...")
        av = admin_view.get_view(page)
        
        print("All views rendered successfully in test!")
        page.window.close()
        
    ft.app(target=test_main)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
