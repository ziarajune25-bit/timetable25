#!/usr/bin/env python
"""
Interactive MySQL Database Connection
Type SQL queries and press Enter to execute
Type 'exit' or 'quit' to close the connection
"""

import pymysql
import sys

def main():
    # Connect to database
    try:
        print("Connecting to MySQL...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='nazila',
            database='timetable_db4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected successfully to timetable_db4!")
        print("Type SQL queries or 'exit'/'quit' to close.\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    cur = conn.cursor()
    
    try:
        while True:
            try:
                query = input("sql> ").strip()
                
                # Exit commands
                if query.lower() in ['exit', 'quit', 'close']:
                    print("Closing connection...")
                    break
                
                # Skip empty queries
                if not query:
                    continue
                
                # Execute query
                try:
                    cur.execute(query)
                    
                    # Check if it's a SELECT query
                    if query.strip().upper().startswith('SELECT'):
                        results = cur.fetchall()
                        if results:
                            # Print headers
                            if results:
                                headers = list(results[0].keys())
                                print("\n" + " | ".join(headers))
                                print("-" * 80)
                                # Print rows
                                for row in results:
                                    print(" | ".join(str(row[h]) for h in headers))
                                print(f"\n({len(results)} rows)\n")
                        else:
                            print("No results found.\n")
                    else:
                        # For INSERT, UPDATE, DELETE
                        conn.commit()
                        print(f"Query executed. Rows affected: {cur.rowcount}\n")
                        
                except Exception as e:
                    print(f"Error: {e}\n")
                    conn.rollback()
                    
            except KeyboardInterrupt:
                print("\n\nClosing connection...")
                break
                
    finally:
        cur.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
