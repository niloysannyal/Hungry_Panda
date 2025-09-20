import mysql.connector
import os


# Get Connection function

# For localhost
# def get_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="root",
#         database="pandeyji_eatery"
#     )

# For deployment
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST", "switchback.proxy.rlwy.net"),
        user=os.getenv("MYSQLUSER", "root"),
        password=os.getenv("MYSQLPASSWORD", "UtrlxdUtwZCUAHzBnJFOUZyqryDBfAAU"),
        database=os.getenv("MYSQLDATABASE", "railway"),
        port=int(os.getenv("MYSQLPORT", 17233))
    )

def insert_order_tracking(order_id, status):
    cnx = get_connection()
    cursor = cnx.cursor()

    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))
    cnx.commit()
    cursor.close()
    cnx.close()



def get_total_order_price(order_id: int):
    cnx = get_connection()
    cursor = cnx.cursor()

    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    return result



def insert_order_item(item: str, quantity: int, next_order_id: int):
    try:
        cnx = get_connection()
        cursor = cnx.cursor()
        cursor.callproc("insert_order_item", (item, quantity, next_order_id))
        cnx.commit()
        cursor.close()
        print("Order item inserted succesfully!")

        return 1

    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        cnx.rollback()

        return -1

    except Exception as e:
        print(f"An error occurred: {e}")
        cnx.rollback()

        return -1




def get_next_order_id():
    cnx = get_connection()
    # Create cursor object
    cursor = cnx.cursor()
    # Write a SQL query
    query = ("SELECT MAX(order_id) FROM orders")

    cursor.execute(query)

    max_order_id = cursor.fetchone()[0]

    return max_order_id+1 if max_order_id else 1




def get_order_status(order_id: int):
    cnx = get_connection()
    # Create cursor object
    cursor = cnx.cursor()

    # Write a SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Execute the query
    cursor.execute(query, (order_id,))

    # Fetch the Result
    result = cursor.fetchone()

    # Close the cursor
    cursor.close()

    return result[0] if result else None



if __name__ == "__main__":
    print(get_total_order_price(1001))
