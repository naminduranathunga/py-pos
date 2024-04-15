import mysql.connector
import os

def connect():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def create_database():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(os.getenv("MYSQL_DATABASE")))
    conn.close()

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(255),
        product_price FLOAT,
        product_quantity INT,
        bar_code VARCHAR(255)
    )
    """)
    #{"products": [], "total": 0, "time": "18:58", "date": "2024-03-29", "bill_id": "FR1263", "cash": 0, "balance": 0}
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        bill_id INT AUTO_INCREMENT PRIMARY KEY,
        total FLOAT,
        time TIME,
        date DATE,
        cash FLOAT,
        balance FLOAT
    )
    """)

    #{"product_id": "23", "product_name": "Hero Ink BLUE", "product_price": 350.0, "quantity": 1, "total": 350.0}
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bill_products (
            bill_id INT,
            product_id INT,
            product_name VARCHAR(255),
            product_price FLOAT,
            quantity INT,
            total FLOAT,
            PRIMARY KEY (bill_id, product_id)
        ) 
    """)
    conn.commit()
    conn.close()

create_database()
create_tables()