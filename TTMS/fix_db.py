import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='nazila',
    database='timetable_db4'
)

cur = conn.cursor()

try:
    # Insert staff
    cur.execute("""
        INSERT INTO staff (staff_code, name, department, max_hours) VALUES
        ('FAC001', 'Dr. Ravi', 'CSE', 20),
        ('FAC002', 'Ms. Anita', 'CSE', 18),
        ('FAC003', 'Mr. Kumar', 'AIDS', 20),
        ('FAC004', 'Dr. Suresh', 'ECE', 20),
        ('FAC005', 'Ms. Priya', 'ECE', 18)
    """)
    print("✓ Staff inserted")
    
    # Insert classrooms
    cur.execute("""
        INSERT INTO classrooms (room_code, room_type, capacity) VALUES
        ('C101', 'CLASSROOM', 60),
        ('C102', 'CLASSROOM', 60),
        ('C103', 'CLASSROOM', 60),
        ('LAB1', 'LAB', 40),
        ('LAB2', 'LAB', 40)
    """)
    print("✓ Classrooms inserted")
    
    # Insert courses first
    cur.execute("""
        INSERT IGNORE INTO courses (name) VALUES
        ('CSE'),
        ('AIDS'),
        ('ECE')
    """)
    print("✓ Courses inserted")
    
    # Insert subjects
    cur.execute("""
        INSERT INTO subjects (code, name, weekly_hours, year, course_id, required_room) VALUES
        ('MATH1', 'Engineering Mathematics I', 4, 'I', 1, 'CLASSROOM'),
        ('PHY', 'Engineering Physics', 3, 'I', 1, 'CLASSROOM'),
        ('C_PROG', 'C Programming', 4, 'I', 1, 'LAB'),
        ('DS', 'Data Structures', 4, 'II', 1, 'LAB'),
        ('OOPS', 'Object Oriented Programming', 3, 'II', 1, 'CLASSROOM'),
        ('DBMS', 'Database Management Systems', 3, 'II', 1, 'CLASSROOM'),
        ('AI', 'Artificial Intelligence', 4, 'III', 2, 'CLASSROOM'),
        ('ML', 'Machine Learning', 3, 'III', 2, 'LAB'),
        ('BD', 'Big Data Analytics', 3, 'III', 2, 'LAB'),
        ('VLSI', 'VLSI Design', 4, 'IV', 3, 'LAB'),
        ('ES', 'Embedded Systems', 3, 'IV', 3, 'LAB'),
        ('CN', 'Computer Networks', 3, 'IV', 3, 'CLASSROOM')
    """)
    print("✓ Subjects inserted")
    
    # Insert users
    cur.execute("""
        INSERT IGNORE INTO users (username, password, role) VALUES
        ('admin', 'admin123', 'admin'),
        ('faculty1', 'faculty123', 'faculty'),
        ('student1', 'student123', 'student')
    """)
    print("✓ Users inserted")
    
    # Insert staff-subject assignments
    cur.execute("""
        INSERT IGNORE INTO staff_subjects (staff_id, subject_id) VALUES
        (1, 1), (1, 4), (1, 7),
        (2, 2), (2, 5), (2, 8),
        (3, 3), (3, 6), (3, 9),
        (4, 10), (4, 11),
        (5, 12)
    """)
    print("✓ Staff-subject assignments inserted")

    conn.commit()
    print("\n✅ Database setup complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()

finally:
    cur.close()
    conn.close()
