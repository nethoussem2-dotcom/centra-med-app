import sys
sys.path.append(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app")
try:
    import views.history_view
    import flet as ft
    
    # mock auth
    import auth
    auth.get_current_user = lambda: {'username': 'test', 'role': 'admin'}
    
    def test_main(page: ft.Page):
        view = views.history_view.get_view(page)
        print("View rendered successfully!")
        page.add(view)
        page.window_close()
        
    ft.app(target=test_main)
except Exception as e:
    import traceback
    traceback.print_exc()
