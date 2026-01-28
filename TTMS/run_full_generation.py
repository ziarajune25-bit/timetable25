#!/usr/bin/env python
import pymysql
import requests
import time
import subprocess
import sys
import os
from threading import Thread

def start_flask():
    """Start Flask app in a separate thread"""
    subprocess.Popen([sys.executable, 'backend/app.py'], cwd=os.getcwd())
    time.sleep(3)  # Give Flask time to start

def generate_timetables():
    """Generate timetables for all year/course/semester combinations"""
    # Connect to database
    db = pymysql.connect(host='localhost', user='root', passwd='nazila', db='timetable_db4')
    cur = db.cursor()
    
    # Get all combinations
    cur.execute('''
        SELECT DISTINCT year, course_id, semester 
        FROM subjects 
        ORDER BY year, course_id, semester
    ''')
    combinations = cur.fetchall()
    cur.close()
    db.close()
    
    print('\nGenerating timetables for all combinations...\n')
    success_count = 0
    
    for combo in combinations:
        year = combo[0]
        course_id = combo[1]
        semester = combo[2]
        
        try:
            response = requests.post(
                'http://127.0.0.1:5000/generate_timetable',
                json={
                    'year': year,
                    'course_id': course_id,
                    'semester': semester
                },
                timeout=30
            )
            if response.status_code == 200:
                print(f'✓ Generated: Year {year}, Course {course_id}, Semester {semester}')
                success_count += 1
            else:
                print(f'✗ Failed: Year {year}, Course {course_id}, Semester {semester} (Status: {response.status_code})')
        except Exception as e:
            print(f'✗ Error for Year {year}, Course {course_id}: {str(e)}')
    
    print(f'\n✓ Successfully generated {success_count} timetables!')

if __name__ == '__main__':
    print('Starting Flask app...')
    start_flask()
    
    try:
        generate_timetables()
    except KeyboardInterrupt:
        print('\nInterrupted by user')
    except Exception as e:
        print(f'Error: {e}')
