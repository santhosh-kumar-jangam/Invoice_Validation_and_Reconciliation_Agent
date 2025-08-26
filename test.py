import sqlite3

# Connect to (or create) the SQLite database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# cursor.execute("drop table events")
# cursor.execute("drop table user_states")
# cursor.execute("drop table sessions")


# # Create the RunSessions table
cursor.execute("delete from invoices")
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS runsessions (
#         runID TEXT PRIMARY KEY,
#         sessionID TEXT NOT NULL
#     )
# ''')

# # Insert a sample session
# cursor.execute('''
#     INSERT INTO RunSessions (SessionID) VALUES (?)
# ''', ('session_abc123',))

# Commit changes
conn.commit()

# # Retrieve and display all records
# cursor.execute('SELECT * FROM RunSessions')
# rows = cursor.fetchall()
# for row in rows:
#     print(f'RunID: {row[0]}, SessionID: {row[1]}')

# Close the connection
conn.close()