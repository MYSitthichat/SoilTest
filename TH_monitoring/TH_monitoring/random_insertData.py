import mariadb
import time
import datetime
import random  # For example data, remove or adapt as needed

# Database credentials
DB_HOST = "localhost"  # Replace with your database host
DB_USER = "username"  # Replace with your database user
DB_PASSWORD = "password"  # Replace with your database password
DB_NAME = "sensor_databases"  # Replace with your database name


def generate_sample_data():
    """Generates sample data for demonstration. Replace with your actual data source."""
    # Example: Generating random temperature and humidity
    temperature = round(random.uniform(20, 35), 2)  # Temperature between 20 and 35
    humidity = random.randint(40, 80)  # Humidity between 40 and 80
    return temperature, humidity

def insert_data(conn):
    """Inserts data into the database."""
    temperature, humidity = generate_sample_data()
    insert_temperature_data(conn, "node1", temperature)
    insert_humidity_data(conn, "node1", humidity)
    
    temperature, humidity = generate_sample_data()
    insert_temperature_data(conn, "node2", temperature)
    insert_humidity_data(conn, "node2", humidity)
    
    temperature, humidity = generate_sample_data()
    insert_temperature_data(conn, "node3", temperature)
    insert_humidity_data(conn, "node3", humidity)

def insert_temperature_data(conn, node_name, temperature):
    """Inserts data into the database."""
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now()
        # Adapt this SQL query to your table structure
        query = "INSERT INTO temperature (dTime, node, temperature) VALUES (?, ?, ?)"
        data = (now, node_name, temperature)
        cursor.execute(query, data)
        conn.commit()  # Important: Commit the transaction

    except mariadb.Error as e:
        print(f"Error inserting data: {e}")
        conn.rollback() # Rollback in case of error to maintain data integrity
    finally:
        cursor.close()
        
def insert_humidity_data(conn, node_name, humidity):
    """Inserts data into the database."""
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now()
        # Adapt this SQL query to your table structure
        query = "INSERT INTO humidity (dTime, node, humidity) VALUES (?, ?, ?)"
        data = (now, node_name, humidity)
        cursor.execute(query, data)
        conn.commit()  # Important: Commit the transaction

    except mariadb.Error as e:
        print(f"Error inserting data: {e}")
        conn.rollback() # Rollback in case of error to maintain data integrity
    finally:
        cursor.close()



def mainLoop():
    try:
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        while True:
            insert_data(conn)
            time.sleep(2)  # Wait for 1 minute (60 seconds)

    except mariadb.Error as e:
        print(f"Database connection error: {e}")
    except KeyboardInterrupt: # Handle Ctrl+C gracefully
        print("Script stopped by user.")
    finally:
        if 'conn' in locals() and conn.is_connected(): # Check if connection exists before closing
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    mainLoop()