import json, os
import win32ui
import win32con
import win32gui
import win32print, win32api
import numpy as np
import PIL.Image as Image
from PIL import ImageWin
import tabulate

printer_name = os.getenv("REPORT_PRINTER_NAME", "Canon G1010 series")

def _report_str_to_image(report):
    pass

def calculate_font_size(mm, dpi=600):
    return int(mm * dpi / 25.4)

def print_report_string(report_str):

    dc = win32ui.CreateDC()
    print(printer_name)
    dc.CreatePrinterDC(printer_name)
    dc.StartDoc("Report")
    dc.StartPage()

    # get printer metrics
    dpi = dc.GetDeviceCaps(win32con.LOGPIXELSX)
    font_size = calculate_font_size(3, dpi=dpi)
    line_height = calculate_font_size(5, dpi=dpi)
    print("Font size: ", font_size)

    # convert str to a single image
    # set text
    line = 200
    
    font = win32ui.CreateFont({"name": "Cascadia Mono", "height": font_size, "weight": 400})
    dc.SelectObject(font)

    # set text color LOGCOLORSPACE
    color_attr = win32ui.CreatePen(win32con.PS_SOLID, 1, win32api.RGB(200, 23, 0))
    dc.SelectObject(color_attr)
    dc.SetTextColor(win32api.RGB(200, 23, 0))
    
    for i in report_str.split("\n"):
        dc.TextOut(40, line, i)
        line += line_height
    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()
    pass


if __name__ == "__main__":
    # create a dummy report
    report_str = "Sales Report \n"
    report_str += "From: 01/01/2020 To: 01/01/2021\n"
    report_str += "\n"
    report_str += "======================================================================"
    report_str += "\n"
    report_str += tabulate.tabulate([[1, 100, "10:00", "01/01/2020", 100, 0], [1, 100, "10:00", "01/01/2020", 100, 0]], headers=["Bill ID", "Total", "Time", "Date", "Cash", "Balance"])
    report_str += "\n"
    report_str += "======================================================================"
    report_str += "Total Sales      : Rs 200 \n"
    report_str += "Total no of bills: 2 \n"
    report_str += "\n"
    print_report_string(report_str)
    pass