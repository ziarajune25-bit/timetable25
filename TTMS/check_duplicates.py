import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()

# Check for duplicate subjects
cur.execute('''
    SELECT code, COUNT(*) as count
    FROM subjects
    GROUP BY code
    HAVING count > 1
    ORDER BY count DESC
''')

duplicates = cur.fetchall()
if duplicates:
    print('DUPLICATE SUBJECTS FOUND:')
    print('='*60)
    for row in duplicates:
        print(f'\n{row[0]}: appears {row[1]} times')
        cur.execute('SELECT id, code, name, weekly_hours FROM subjects WHERE code=%s', (row[0],))
        for detail in cur.fetchall():
            print(f'  ID {detail[0]}: {detail[1]} - {detail[2]} ({detail[3]} hrs/week)')
else:
    print('✓ No duplicate subjects\n')

# Check for duplicate staff-subject assignments
cur.execute('''
    SELECT ss.staff_id, ss.subject_id, s.code, st.name, COUNT(*) as count
    FROM staff_subjects ss
    JOIN subjects s ON ss.subject_id = s.id
    JOIN staff st ON ss.staff_id = st.id
    GROUP BY ss.staff_id, ss.subject_id
    HAVING count > 1
''')

dup_assign = cur.fetchall()
if dup_assign:
    print('DUPLICATE STAFF-SUBJECT ASSIGNMENTS:')
    print('='*60)
    for row in dup_assign:
        print(f'{row[3]} -> {row[2]}: assigned {row[4]} times')
else:
    print('✓ No duplicate assignments')

cur.close()
db.close()
