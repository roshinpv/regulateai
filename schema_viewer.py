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

def print_schema(db_path):
    """Print the schema of all tables in the SQLite database."""
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        
        print(f"Database: {db_path}\n")
        print(f"Found {len(tables)} tables:\n")
        
        # For each table, get its schema
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Format the column information
            column_data = []
            for col in columns:
                cid, name, type_, notnull, default_value, pk = col
                column_data.append([
                    name, 
                    type_, 
                    "NOT NULL" if notnull else "", 
                    f"DEFAULT {default_value}" if default_value is not None else "",
                    "PRIMARY KEY" if pk else ""
                ])
            
            # Print table schema
            print(tabulate(column_data, headers=["Column", "Type", "Nullable", "Default", "Key"], tablefmt="grid"))
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print("\nForeign Keys:")
                fk_data = []
                for fk in foreign_keys:
                    id_, seq, table, from_, to, on_update, on_delete, match = fk
                    fk_data.append([from_, f"→ {table}({to})", on_update, on_delete])
                
                print(tabulate(fk_data, headers=["Column", "References", "On Update", "On Delete"], tablefmt="grid"))
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            if indexes:
                print("\nIndexes:")
                for idx in indexes:
                    idx_name = idx[1]
                    cursor.execute(f"PRAGMA index_info({idx_name})")
                    idx_columns = cursor.fetchall()
                    columns = ", ".join([col[2] for col in idx_columns])
                    print(f"- {idx_name}: {columns}")
            
            print("\n" + "-" * 80 + "\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    db_path = get_db_path()
    print_schema(db_path)