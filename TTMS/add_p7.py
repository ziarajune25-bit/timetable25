import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()

# Check current periods
cur.execute('SELECT period_no, start_time, end_time FROM periods ORDER BY period_no')
periods = cur.fetchall()
print('Current periods:')
for p in periods:
    print(f'  P{p[0]}: {p[1]} - {p[2]}')

# Add P7 only
cur.execute('INSERT INTO periods (period_no, start_time, end_time) VALUES (7, "14:00", "14:45")')
db.commit()

print('\nAdded P7')

# Verify P7 was added
cur.execute('SELECT period_no, start_time, end_time FROM periods ORDER BY period_no')
periods = cur.fetchall()
print('\nUpdated periods:')
for p in periods:
    print(f'  P{p[0]}: {p[1]} - {p[2]}')

cur.close()
db.close()
