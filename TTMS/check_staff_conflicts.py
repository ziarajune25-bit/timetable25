#!/usr/bin/env python3
"""
Staff Conflict Checker
Identifies staff members with scheduling conflicts (overlapping classes)
"""

import pymysql
import sys
import os

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'nazila'
DB_NAME = 'timetable_db4'

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def check_staff_conflicts():
    """Find staff members with scheduling conflicts"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 80)
    print("STAFF SCHEDULING CONFLICT CHECKER")
    print("=" * 80)
    print()
    
    # Get all timetable entries grouped by staff
    cur.execute("""
        SELECT 
            st.id, 
            st.name, 
            st.department,
            COUNT(*) as total_classes,
            COUNT(DISTINCT t.day) as days_with_class,
            COUNT(DISTINCT CONCAT(t.day, '-', p.period_no)) as total_slots
        FROM timetable t
        JOIN periods p ON t.period_id = p.id
        JOIN staff st ON t.staff_id = st.id
        GROUP BY st.id, st.name, st.department
        ORDER BY st.name
    """)
    
    staff_list = cur.fetchall()
    conflicts_found = 0
    
    for staff in staff_list:
        staff_id = staff['id']
        staff_name = staff['name']
        
        # Find conflicts for this staff
        cur.execute("""
            SELECT 
                t1.day,
                p.period_no,
                s1.code as subject1,
                s2.code as subject2,
                c1.year as year1,
                c1.semester as semester1,
                c2.year as year2,
                c2.semester as semester2,
                COUNT(*) as conflict_count
            FROM timetable t1
            JOIN periods p ON t1.period_id = p.id
            JOIN subjects s1 ON t1.subject_id = s1.id
            JOIN courses c1 ON t1.course_id = c1.id
            JOIN timetable t2 ON t1.staff_id = t2.staff_id 
                AND t1.day = t2.day 
                AND t1.period_id = t2.period_id 
                AND t1.id < t2.id
            JOIN subjects s2 ON t2.subject_id = s2.id
            JOIN courses c2 ON t2.course_id = c2.id
            WHERE t1.staff_id = %s
            GROUP BY t1.day, p.period_no, s1.code, s2.code
        """, (staff_id,))
        
        conflicts = cur.fetchall()
        
        if conflicts:
            conflicts_found += 1
            print(f"⚠️  CONFLICT FOUND - Staff: {staff_name}")
            print(f"    Department: {staff['department']}")
            print(f"    Total Classes: {staff['total_classes']}")
            print(f"    Days with Class: {staff['days_with_class']}")
            print()
            
            for conf in conflicts:
                print(f"    🔴 {conf['day']} | Period {conf['period_no']}")
                print(f"       ├─ {conf['subject1']} (Year {conf['year1']} {conf['semester1']})")
                print(f"       └─ {conf['subject2']} (Year {conf['year2']} {conf['semester2']})")
            print()
    
    if conflicts_found == 0:
        print("✅ NO CONFLICTS FOUND")
        print("All staff members have valid schedules with no overlapping classes.")
    else:
        print("=" * 80)
        print(f"⚠️  Total Staff with Conflicts: {conflicts_found}")
        print("=" * 80)
        print()
        print("RECOMMENDED ACTIONS:")
        print("1. Regenerate timetable (try different random allocation)")
        print("2. Unassign conflicting subjects from staff member")
        print("3. Assign conflicting subject to different staff member")
        print("4. Combine class sections to reduce total slots needed")
    
    cur.close()
    conn.close()

def check_staff_workload():
    """Check if any staff exceed their max hours"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    print()
    print("=" * 80)
    print("STAFF WORKLOAD ANALYSIS")
    print("=" * 80)
    print()
    
    cur.execute("""
        SELECT 
            st.id,
            st.name,
            st.department,
            st.max_hours,
            COUNT(DISTINCT s.id) as subjects_assigned,
            SUM(s.weekly_hours) as total_weekly_hours
        FROM staff st
        LEFT JOIN staff_subjects ss ON st.id = ss.staff_id
        LEFT JOIN subjects s ON ss.subject_id = s.id
        GROUP BY st.id, st.name, st.department, st.max_hours
        ORDER BY st.name
    """)
    
    staff_workload = cur.fetchall()
    overload_count = 0
    
    for staff in staff_workload:
        hours = staff['total_weekly_hours'] or 0
        max_hours = staff['max_hours']
        subjects = staff['subjects_assigned']
        
        status = "✅"
        if hours > max_hours:
            status = "⚠️ OVERLOAD"
            overload_count += 1
        
        print(f"{status} {staff['name']} ({staff['department']})")
        print(f"    Subjects: {subjects} | Hours: {hours}/{max_hours}")
        if hours > max_hours:
            print(f"    EXCEEDS by: {hours - max_hours} hours")
        print()
    
    if overload_count > 0:
        print(f"⚠️  {overload_count} staff members are overloaded!")
    else:
        print("✅ All staff within workload limits")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_staff_conflicts()
    check_staff_workload()
