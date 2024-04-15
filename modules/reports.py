from __future__ import absolute_import
import tabulate
import datetime
from . import mysql_db, report_printer


"""
This support today/yesterday/this week/this month/this year
"""

def get_date_range():
    pass

def show_sales_report():
    print ("Enter the start date: dd/mm/yyyy")
    start_date = input(" (today) >> ")
    end_date = None
    # parse the start date
    if (start_date == "" or start_date == "today"):
        start_date = datetime.datetime.now().strftime("%d/%m/%Y")
    elif (start_date == "yesterday"):
        start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    elif (start_date == "this week"):
        start_date = datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())
        end_date = datetime.datetime.now() + datetime.timedelta(days=6-datetime.datetime.now().weekday())
    elif (start_date == "this month"):
        start_date = datetime.datetime.now().replace(day=1)
        end_date = datetime.datetime.now().replace(day=1, month=datetime.datetime.now().month+1) - datetime.timedelta(days=1)
    elif (start_date == "this year"):
        start_date = datetime.datetime.now().replace(day=1, month=1)
        end_date = datetime.datetime.now().replace(day=31, month=12)
    else:
        start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    
    if (end_date == None):
        print ("Enter the end date: dd/mm/yyyy")
        end_date = input(" (today) >> ")

        # parse the end date
        if (end_date == "" or end_date == "today"):
            end_date = datetime.datetime.now().strftime("%d/%m/%Y")
        elif (end_date == "yesterday"):
            end_date = datetime.datetime.now() - datetime.timedelta(days=1)
        else:
            end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y")

    # get the sales report
    conn = mysql_db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bills WHERE date BETWEEN %s AND %s", (start_date, end_date))
    bills = cursor.fetchall()
    conn.close()

    # totals
    total = 0
    no_of_bills = 0
    for bill in bills:
        total += bill[1]
        no_of_bills += 1

    # print the sales report
    report_str = "Sales Report \n"
    report_str += "From: " + start_date.strftime("%d/%m/%Y") + " To: " + end_date.strftime("%d/%m/%Y") + "\n"
    report_str += "\n"
    report_str += "======================================================================"
    report_str += "\n"
    report_str += tabulate.tabulate(bills, headers=["Bill ID", "Total", "Time", "Date", "Cash", "Balance"])
    report_str += "\n"
    report_str += "======================================================================"
    report_str += "\n"
    report_str += "Total Sales      : Rs %0.2f \n".format(total)
    report_str += "Total no of bills: %d \n" .format(no_of_bills)
    report_str += "\n"

    print(report_str)
    n = input("Do you want to print this report? (y/n) >> ")
    if n == "y":
        report_printer.print_report_string(report_str)
    input("Press Enter to continue...")

def show_inventory_report():
    conn = mysql_db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    print(tabulate.tabulate(products, headers=["Product ID", "Product Name", "Price", "Quantity"]))
    input("Press Enter to continue...")


def show_report_menu():
    while True:
        print("1. Sales Report")
        print("2. Inventory Report")
        print("3. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            show_sales_report()
        elif choice == "2":
            show_inventory_report()
        elif choice == "3":
            return
        else:
            print("Invalid Choice")
            input("Press Enter to continue...")


if __name__ == "__main__":
    show_report_menu()