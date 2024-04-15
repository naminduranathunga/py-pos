from __future__ import absolute_import
import tabulate
import datetime, json, os
from . import bill_printer
from . import mysql_db

inventory = None


def init(inventory_instance):
    global inventory
    inventory = inventory_instance

"""
Commands:
    - /canel: Cancel the bill -- if the bill is empty, exit from the bill loop
    - /remove <item index>: Remove an item from the bill
    - /pay: Pay the bill
"""

def next_bill_id():
    bill_id = 3234
    with open("bills/next_bill_id.txt", "r") as f:
        bill_id = int(f.read())
    with open("bills/next_bill_id.txt", "w") as f:
        f.write(str(bill_id + 1))
    return bill_id



def __print_items_table(bill):
    items = []
    print("Date: %s,    Total: %0.2f" % (bill["date"], bill["total"]))
    print("Time: %s,    Bill: %s" % (bill["time"], bill["bill_id"]))
    print("===================================")
    for index, item in enumerate(bill["products"]):
        items.append([index, item["product_name"], item["product_price"], item["quantity"], item["total"]])
    print(tabulate.tabulate(items, headers=["#", "Product", "U. Price", "Qty", "Total"], tablefmt="fancy_grid"))
    print()

def __pay_bill(bill):
    print("")
    while True:
        bill['cash'] = int(input("Enter Cash Amount: "))
        if bill['cash'] < bill['total']:
            print("Insufficient cash amount")
            continue
        break
    bill['balance'] = bill['cash'] - bill['total']
    bill_printer.print_bill(bill)
    __save_bill(bill)
    pass

"""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INT AUTO_INCREMENT PRIMARY KEY,
        total FLOAT,
        time TIME,
        date DATE,
        cash FLOAT,
        balance FLOAT
    )
    """
def __save_bill(bill):
    fname = "bills/%s_%s.json" % (bill['bill_id'], bill['date'])
    with open(fname, "w") as f:
        json.dump(bill, f)
    # save to database
    conn = mysql_db.connect()
    cursor = conn.cursor()
    # add bill and get the bill id
    cursor.execute("INSERT INTO bills (total, time, date, cash, balance) VALUES (%s, %s, %s, %s, %s)", (bill['total'], bill['time'], bill['date'], bill['cash'], bill['balance']))
    bill_id = cursor.lastrowid
    # add bill products
    for item in bill['products']:
        cursor.execute("INSERT INTO bill_products (bill_id, product_id, product_name, product_price, quantity, total) VALUES (%s, %s, %s, %s, %s, %s)", (bill_id, item['product_id'], item['product_name'], item['product_price'], item['quantity'], item['total']))
    conn.commit()

"""
@return Boolean
"""
def create_bill() -> bool:
    bill = {
        "products": [],
        "total": 0,
        "time": datetime.datetime.now().strftime("%H:%M"),
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "bill_id": "FR" + str(next_bill_id())
    }
    while True:
        os.system("cls")    
        print("Create a bill")
        print("================================")
        print("             Flexaro            ")
        print("================================")
        print("")
        __print_items_table(bill)
        new_cmd = input(">>> ")

        # check for commands
        if (new_cmd.startswith("/")):
            if new_cmd == "/cancel" or new_cmd == "/c":
                print("Bill canceled")
                if len(bill["products"]) > 0:
                    return True # Create a new bill
                return False # Exit from bill loop
            
            if new_cmd.startswith("/remove") or new_cmd.startswith("/r"):
                parts = new_cmd.split(" ")
                if len(parts) != 2:
                    print("Invalid command")
                    continue
                index = int(parts[1])
                if index < 0 or index >= len(bill["products"]):
                    print("Invalid index")
                    continue
                product = bill["products"][index]
                bill["total"] -= product["total"]
                bill["products"].remove(product)
                continue
            if new_cmd == "/pay" or new_cmd == "/p":
                __pay_bill(bill)
                return True
            print("Invalid command")
            continue
        
        # this support <quantity>*<product_name>
        # decode if quantity is provided
        quantity = 1
        if (new_cmd.find("*") != -1):
            parts = new_cmd.split("*")
            quantity = int(parts[0])
            new_cmd = parts[1]
        # check for product
        product = inventory.get_product_by_bar_code(new_cmd)
        
        if (product == None):
            product = inventory.search_product_by_name(new_cmd)
            if len(product) == 0:
                print("Product not found")
                os.system("pause")
                continue
            for index, item in enumerate(product):
                print("%d. %s" % (index, item["product_name"]))
                pass

            cmd_2 = input("Select a product \\c - Cancel: ")
            if cmd_2 == "\\c" or cmd_2 == "\\cancel":
                continue
            try:
                index = int(cmd_2)
                product = product[index]
            except:
                print("Invalid choice")
                continue
        
        # check if product is already in the bill
        found = False
        for i in range(len(bill["products"])):
            if bill["products"][i]["product_id"] == product["product_id"]:
                bill["products"][i]["quantity"] += quantity
                bill["products"][i]["total"] += (product["product_price"] * quantity)
                bill["total"] += (product["product_price"] * quantity)
                found = True
                break
        if found:
            continue

        item = {
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "product_price": product["product_price"],
            "quantity": quantity,
            "total": product["product_price"] * quantity
        }
        bill["products"].append(item)
        bill["total"] += (product["product_price"] * quantity)
    
