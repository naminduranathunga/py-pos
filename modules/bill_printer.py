import json, os
import win32ui
import win32con
import win32gui
import win32print, win32api
import numpy as np
import PIL.Image as Image
from PIL import ImageWin

printer_name = os.getenv("POS_PRINTER_NAME", "POS-58")
char_width = 14
template = []
dynamics = []

# load template
with open("bill.json") as f:
    template = json.load(f)
    


def put_image(dc, t, cursor=0):
    img = Image.open(t["file"]).convert("L")  # Convert image to grayscale
    win32ui.CreateBitmap()
    dib = ImageWin.Dib(img)
    dib.draw(dc.GetHandleOutput(), (t['x'], cursor + t['y'], t['x'] + t["w"], cursor + t["h"]))
    return cursor + t["h"]

"""
{total}
{balance}
{cash}

"""
# 


def parse_dynamic_text(text: str, bill):
    # replace dynamic tags
    text = text.replace("{total}", str(bill["total"]))
    text = text.replace("{date}", str(bill["date"]))
    text = text.replace("{time}", str(bill["time"]))
    text = text.replace("{bill_id}", str(bill["bill_id"]))
    return text

def print_items(dc, bill, cursor=0, line_h=30):
    ind = 0
    dc.TextOut(375 - len(str("Total"))*char_width, cursor, "Total")
    dc.TextOut(275 - len(str("Qty"))*char_width, cursor, "Qty")
    dc.TextOut(222 - len(str("Unit P."))*char_width, cursor, "Unit P.")
    dc.TextOut(0, cursor, "Name")
    cursor += line_h
    dc.TextOut(0, cursor, "====================================")
    cursor += int(line_h * 1.05)

    for i in bill["products"]:
        dc.TextOut(0, cursor, str(ind + 1) + ". " + i["product_name"])
        cursor += line_h
        ttl = "%.2f" % i["total"]
        dc.TextOut(384 - len(ttl)*char_width, cursor, ttl)
        qty = "%.0f" % i["quantity"]
        dc.TextOut(275 - len(qty)*char_width, cursor, qty)
        price = "%.2f *" % i["product_price"]
        dc.TextOut(200 - len(price)*char_width, cursor, price)
        cursor += int(line_h * 1.25)
        ind += 1


    dc.TextOut(0, cursor, "====================================")
    cursor += int(line_h * 1.05)

    dc.TextOut(0, cursor, "Subtotal")
    num = "%.2f" % bill["total"]
    dc.TextOut(375 - len(num)*char_width, cursor, num)
    cursor += line_h

    dc.TextOut(0, cursor, "Cash")
    num = "%.2f" % bill["cash"]
    dc.TextOut(375 - len(num)*char_width, cursor, num)
    cursor += line_h
    
    dc.TextOut(0, cursor, "Balance")
    num = "%.2f" % bill["balance"]
    dc.TextOut(375 - len(num)*char_width, cursor, num)
    cursor += line_h

    return cursor


def print_bill(bill):
    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(printer_name)
    dc.StartDoc('bill')
    dc.StartPage()
    cursor = 0

    font = win32ui.CreateFont({"name": "Cascadia Mono", "height": 28, "weight": 400})
    dc.SelectObject(font)

    for t in template:
        if (t["type"] == "image"):
            cursor = put_image(dc, t, cursor)
            pass
        elif (t["type"] == "text"):
            dc.TextOut(0, cursor, parse_dynamic_text(t["text"], bill))
            cursor += 30
            pass
        
        elif (t["type"] == "product_table"):
            cursor = print_items(dc, bill, cursor)
            pass
    
    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()
    pass

"""
print_bill({
    "total": 255,
    "items": [
        {
            "product_price": 50,
            "product_name": "Test Product",
            "quantity": 1,
            "total": 50,
        }
    ],
    "cash": 300,
    "balance": 45,
    "date": "2021-09-09",
    "bill_id": "123456",
    "time": "12:00 PM"
})
"""