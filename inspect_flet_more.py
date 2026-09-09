import flet as ft

lcd = ft.LineChartData()
print("default below_line:", type(lcd.below_line), lcd.below_line)
print("default below_line_bgcolor:", type(lcd.below_line_bgcolor), lcd.below_line_bgcolor)
print("default below_line_gradient:", type(lcd.below_line_gradient), lcd.below_line_gradient)

# Let's inspect the ft.LineChartData constructor signature
import inspect
print("\nLineChartData constructor signature:")
sig = inspect.signature(ft.LineChartData.__init__)
for name, param in sig.parameters.items():
    if name not in ['self', 'args', 'kwargs']:
        print(f"  {name}: {param.default}")
