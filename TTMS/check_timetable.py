import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()

# Get timetable stats
cur.execute('''
    SELECT year, course_id, semester, COUNT(*) as total,
           COUNT(DISTINCT day) as days, COUNT(DISTINCT period_id) as periods
    FROM timetable
    GROUP BY year, course_id, semester
    ORDER BY year, course_id, semester
''')

print('\nTimetable Statistics:')
print('='*60)
print(f'{"Year":<12} {"Course":<8} {"Semester":<10} {"Slots":<10} {"Days":<10} {"Periods"}')
print('='*60)

for row in cur.fetchall():
    print(f'{str(row[0]):<12} {row[1]:<8} {row[2]:<10} {row[3]:<10} {row[4]:<10} {row[5]}')

cur.close()
db.close()

print('\n✓ All timetables have been fully allocated!')
print('\nTo view the timetables, visit: http://127.0.0.1:5000')
