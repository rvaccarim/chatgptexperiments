import os
import requests
import sqlite3

def create_db_and_table():
    if not os.path.exists('db'):
        os.makedirs('db')

    # Create a SQLite database and 'winrate' table
    conn = sqlite3.connect('db/winrate.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS winrate (
            name TEXT,
            wr REAL,
            count INTEGER
        )
    ''')
    # Truncate the 'winrate' table
    cursor.execute('DELETE FROM winrate')
    conn.commit()
    conn.close()

def insert_data_into_db(name, wr, count):
    conn = sqlite3.connect('db/winrate.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO winrate (name, wr, count) VALUES (?, ?, ?)', (name, wr, count))
    conn.commit()
    conn.close()

def fetch_and_store_data(url, payload):
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            meta = data.get("meta", [])
            for element in meta:
                name = element.get("name", "N/A")
                wr = element.get("wr", "N/A")
                count = element.get("count", "N/A")
                insert_data_into_db(name, wr, count)
        else:
            print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def pretty_print_database_records():
    conn = sqlite3.connect('db/winrate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM winrate')
    records = cursor.fetchall()
    conn.close()

    print("Database Records:")
    print("{:<20} {:<10} {:<10}".format("Name", "Win Rate", "Count"))
    for record in records:
        name, wr, count = record
        print("{:<20} {:<10.2f} {:<10}".format(name, wr, count))

def select_top_3_records():
    conn = sqlite3.connect('db/winrate.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM winrate ORDER BY count DESC LIMIT 3')
    records = cursor.fetchall()
    conn.close()

    print("Top 3 Records by Count (Ordered by Count Descending):")
    print("{:<20} {:<10} {:<10}".format("Name", "Win Rate", "Count"))
    for record in records:
        name, wr, count = record
        print("{:<20} {:<10.2f} {:<10}".format(name, wr, count))

def main():
    # URL to query
    url = "https://runeterra.ar/api/meta/get/filter/everyone/en_us?take=20&type=two&filter=true&format=client_Formats_Standard_name&matches=3&wr=3"

    # Data to send in the POST request
    payload = {
        "region": [],
        "champ": [],
        "set": []
    }

    create_db_and_table()

    try:
        # Fetch and store data from the URL
        fetch_and_store_data(url, payload)

        # Pretty-print database records
        pretty_print_database_records()

        # Print a separator
        print("-" * 50)

        # Select and print the top 3 records
        select_top_3_records()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
