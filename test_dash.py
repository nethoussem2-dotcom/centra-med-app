import sys, traceback
sys.path.append(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app")
try:
    import database
    database.init_db()
    import auth
    auth._current_user = {"username": "admin", "role": "admin", "full_name": "Admin User"}
    from views import dashboard_view
    import flet as ft
    from unittest.mock import MagicMock
    page = MagicMock(spec=ft.Page)
    view = dashboard_view.get_view(page)
    with open(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app\error.log", "w", encoding='utf-8') as f:
        f.write("Success")
except Exception as e:
    with open(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app\error.log", "w", encoding='utf-8') as f:
        traceback.print_exc(file=f)
