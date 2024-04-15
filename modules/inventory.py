from __future__ import absolute_import
import json
from . import mysql_db

jwt_secret = ""
inventory = []
conn = mysql_db.connect()
cursor = conn.cursor()

def save_inventory():
    with open("inventory.json", "w") as file:
        json.dump(inventory, file, indent=4)

def load_inventory():
    global inventory
    import os 
    if not os.path.exists("inventory.json"):
        save_inventory()

    with open("inventory.json", "r") as file:
        inventory = json.load(file)

def add_all_products_to_db():
    cursor.execute("DELETE FROM products")

    for product in inventory:
        cursor.execute("""
            INSERT INTO products (product_name, product_price, product_quantity, bar_code)
            VALUES (%s, %s, %s, %s)
        """, (product["product_name"], product["product_price"], product["product_quantity"], product["bar_code"]))
        # print if any error
        print(cursor.statement)

    conn.commit()

def add_product():
    print ("Add product to inventory (\exit to go back)")
    print ("=======================")
    product_name = input("Enter the product name: ")
    if product_name == "\exit":
        return
    product_price = float(input("Enter the product price: "))
    if product_price == "\exit":
        return
    product_quantity = int(input("Enter the product quantity: "))
    if product_quantity == "\exit":
        return
    bar_code = input("Enter the bar code: ")
    if bar_code == "\exit":
        return

    product = {
        "product_name": product_name,
        "product_price": product_price,
        "product_quantity": product_quantity,
        "bar_code": bar_code
    }
    
    # add to database
    cursor.execute("""
        INSERT INTO products (product_name, product_price, product_quantity, bar_code)
        VALUES (%s, %s, %s, %s)
    """, (product_name, product_price, product_quantity, bar_code))
    conn.commit()

def get_product_by_bar_code(bar_code):
    # from the database
    cursor.execute("SELECT * FROM products WHERE bar_code = %s", (bar_code,))
    product = cursor.fetchone()
    if product:
        return {
            "product_id": product[0],
            "product_name": product[1],
            "product_price": product[2],
            "product_quantity": product[3],
            "bar_code": product[4]
        }
    return None

def get_product_by_id(product_id):
    # from the database
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    if product:
        return {
            "product_id": product[0],
            "product_name": product[1],
            "product_price": product[2],
            "product_quantity": product[3],
            "bar_code": product[4]
        }
    return None

def search_product_by_name(product_name):
    products = []
    # from the database
    cursor.execute("SELECT * FROM products WHERE product_name LIKE %s", ("%" + product_name + "%",))
    products_ = cursor.fetchall()
    for product in products_:
        products.append({
            "product_id": product[0],
            "product_name": product[1],
            "product_price": product[2],
            "product_quantity": product[3],
            "bar_code": product[4]
        })
    return products


def update_product_quantity(product_id, quantity):
    
    # database
    cursor.execute("SELECT product_quantity FROM products WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    if product:
        new_quantity = product[0] - quantity
        cursor.execute("UPDATE products SET product_quantity = %s WHERE product_id = %s", (new_quantity, product_id))
        conn.commit()
        return True
    return False



