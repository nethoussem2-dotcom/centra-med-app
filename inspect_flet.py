import flet as ft
import inspect

print("LineChartData properties:")
lcd = ft.LineChartData()
for attr in sorted(dir(lcd)):
    if not attr.startswith('_'):
        print(f"  {attr}")
