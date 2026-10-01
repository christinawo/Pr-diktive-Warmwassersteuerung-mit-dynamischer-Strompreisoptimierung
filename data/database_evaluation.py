import sqlite3

DATABASE = "evaluation.db"

def create_database():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results(
        strategy TEXT,
        cost REAL,
        comfort REAL,
        energy REAL
                   )
        """)
    
    connection.commit()
    connection.close()


def save_result(strategy, cost, comfort, energy):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO results
    VALUES (?, ?, ?, ?)
    """, (strategy, cost, comfort, energy))

    connection.commit()
    connection.close()
