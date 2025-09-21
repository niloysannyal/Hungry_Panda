import mysql.connector
import os


# Database Connection
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "switchback.proxy.rlwy.net"),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", "UtrlxdUtwZCUAHzBnJFOUZyqryDBfAAU"),
        database=os.getenv("MYSQLDATABASE", "railway"),
        port=int(os.getenv("MYSQLPORT", 17233))
    )


def insert_order_tracking(order_id, status):
    cnx, cursor = None, None
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def get_total_order_price(order_id: int):
    cnx, cursor = None, None
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def insert_order_item(item: str, quantity: int, next_order_id: int):
    cnx, cursor = None, None
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        cursor.callproc("insert_order_item", (item, quantity, next_order_id))
        cnx.commit()
        print("Order item inserted successfully!")
        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        if cnx:
            cnx.rollback()
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        if cnx:
            cnx.rollback()
        return -1
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def get_next_order_id():
    cnx, cursor = None, None
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)
        max_order_id = cursor.fetchone()[0]
        return max_order_id + 1 if max_order_id else 1
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def get_order_status(order_id: int):
    cnx, cursor = None, None
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


if __name__ == "__main__":
    print(get_next_order_id())
