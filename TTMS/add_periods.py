import pymysql

# Connect to database
db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()

# Check current periods
cur.execute('SELECT period_no, start_time, end_time FROM periods ORDER BY period_no')
periods = cur.fetchall()
print('Current periods:')
for p in periods:
    print(f'  P{p[0]}: {p[1]} - {p[2]}')

# Check if P7 exists
cur.execute("SELECT COUNT(*) FROM periods WHERE period_no = 7")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO periods (period_no, start_time, end_time) VALUES (7, '14:00', '14:45')")
    db.commit()
    print('\nAdded P7 (14:00-14:45)')
else:
    print('\nP7 already exists')

# Show updated periods
cur.execute('SELECT period_no, start_time, end_time FROM periods ORDER BY period_no')
periods = cur.fetchall()
print('\nUpdated periods:')
for p in periods:
    print(f'  P{p[0]}: {p[1]} - {p[2]}')

cur.close()
db.close()
