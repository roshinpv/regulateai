import sqlite3
import os
from tabulate import tabulate

def get_db_path():
    """Get the database path from the environment or use the default."""
    # Check if DATABASE_URL is set in environment
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///./regulatory_compliance.db')
    
    # Extract the path from the URL
    if db_url.startswith('sqlite:///'):
        return db_url[10:]
    return 'regulatory_compliance.db'

def view_table_data(db_path, table_name=None):
    """View all data in the specified table, or all tables if none specified."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Get all tables if no specific table is requested
        if table_name is None:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            tables = [table_name]
        
        # For each table, print all rows
        for table in tables:
            print(f"\n{'=' * 80}")
            print(f"TABLE: {table}")
            print(f"{'=' * 80}")
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get all rows
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                print("No data in this table.")
                continue
            
            # Convert rows to list of dicts for better display
            row_dicts = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                row_dicts.append(row_dict)
            
            # Print table data
            print(tabulate(row_dicts, headers="keys", tablefmt="grid"))
            print(f"Total rows: {len(rows)}")
            
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    db_path = get_db_path()
    print(f"Database: {db_path}")
    
    # Get list of tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print("\nAvailable tables:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    while True:
        choice = input("\nEnter table number to view (0 for all tables, q to quit): ")
        
        if choice.lower() == 'q':
            break
        
        try:
            choice = int(choice)
            if choice == 0:
                view_table_data(db_path)
            elif 1 <= choice <= len(tables):
                view_table_data(db_path, tables[choice-1])
            else:
                print("Invalid table number.")
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")

if __name__ == "__main__":
    main()