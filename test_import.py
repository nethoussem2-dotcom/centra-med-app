import sys
sys.path.append(r"C:\Users\DELL pro\.gemini\antigravity\scratch\centra-med-app")
try:
    import views.history_view
    print("history_view compiles successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
