import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="soiltester",
        password="111777000",
        database="soil_tester"
    )
    print("✅ Database connected successfully")

except mysql.connector.Error as err:
    print(f"❌ Database connection error: {err}")

finally:
    if conn.is_connected():
        conn.close()
        print("🔌 Database connection closed")
