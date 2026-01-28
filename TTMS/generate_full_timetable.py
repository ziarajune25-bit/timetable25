import pymysql
import requests

# Connect to database to get available year/course combinations
db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
cur = db.cursor()

# Get all year/course combinations
cur.execute("""
    SELECT DISTINCT year, course_id 
    FROM subjects 
    ORDER BY year, course_id
""")
combinations = cur.fetchall()

print("Available year/course combinations:")
for combo in combinations:
    print(f"  Year {combo['year']}, Course {combo['course_id']}")

cur.close()
db.close()

# Generate timetable for each combination
print("\nGenerating timetables...")
for combo in combinations:
    year = combo['year']
    course_id = combo['course_id']
    semester = 'ODD'  # or 'EVEN' - adjust as needed
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/generate_timetable',
            json={
                'year': year,
                'course_id': course_id,
                'semester': semester
            }
        )
        if response.status_code == 200:
            print(f"✓ Generated timetable for Year {year}, Course {course_id}, Semester {semester}")
        else:
            print(f"✗ Failed for Year {year}, Course {course_id}: {response.text}")
    except Exception as e:
        print(f"✗ Error generating for Year {year}, Course {course_id}: {str(e)}")

print("\nTimetable generation complete!")
