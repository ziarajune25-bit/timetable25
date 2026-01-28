import pymysql
import requests
import time

# Wait a bit for Flask to be ready
time.sleep(1)

# Get combinations from database
db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()
cur.execute('''
    SELECT DISTINCT year, course_id, semester 
    FROM subjects 
    ORDER BY year, course_id, semester
''')
combos = cur.fetchall()
cur.close()
db.close()

print('Generating timetables for all combinations:\n')
success = 0
failed = 0

for combo in combos:
    year = combo[0]
    course_id = combo[1]
    semester = combo[2]
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/generate',
            json={'year': year, 'course_id': course_id, 'semester': semester},
            timeout=60
        )
        
        if response.status_code == 200:
            print(f'✓ Year {year:10} | Course {course_id} | Semester {semester:6} | Status: {response.status_code}')
            success += 1
        else:
            print(f'✗ Year {year:10} | Course {course_id} | Semester {semester:6} | Status: {response.status_code}')
            failed += 1
            print(f'  Response: {response.text[:100]}')
            
    except requests.exceptions.ConnectionError:
        print(f'✗ Year {year:10} | Course {course_id} | Semester {semester:6} | Connection Error')
        failed += 1
    except Exception as e:
        print(f'✗ Year {year:10} | Course {course_id} | Semester {semester:6} | Error: {str(e)[:50]}')
        failed += 1

print(f'\n{"="*60}')
print(f'Results: {success} successful, {failed} failed')
print(f'{"="*60}')
