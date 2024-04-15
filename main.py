"""
Options:
Add products to inventory
Create a Bill
Exit
"""
#load .env file
from dotenv import load_dotenv
load_dotenv()

from modules import mysql_db
from modules import inventory, create_bill, reports
#inventory.load_inventory()

#inventory.add_all_products_to_db()

def add_product():
    inventory.add_product()


def main_menu():
    print("Options:")
    print("1. Add products to inventory")
    print("2. Create a Bill")
    print("3. Reports")
    print("4. Exit")
    
    choise = int(input("Enter your choice: "))
    if choise == 1:
        add_product()
    elif choise == 2:
        while create_bill.create_bill():
            pass
    elif choise == 3:
        reports.show_report_menu()
    elif choise == 4:
        exit()
    else:
        print("Invalid choice")
    main_menu()


# Main
inventory.load_inventory()
create_bill.init(inventory)
main_menu()
