from flask import Flask, render_template, request, redirect, session, jsonify
import pymysql
import random
import sys
import os

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.auth import login_required

# Get the parent directory (project root)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, 
    template_folder=os.path.join(BASE_DIR, 'template'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.secret_key = "timetable_secret_key"

# ---------------- DB CONNECTION ----------------
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="nazila",
        database="timetable_db4",
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------- HELPERS ----------------
def get_request_data():
    """Get data from either JSON or form submission"""
    if request.is_json:
        return request.get_json()
    return request.form.to_dict()

def json_response(success, message, **kwargs):
    """Return a JSON response"""
    resp = {"success": success, "message": message}
    resp.update(kwargs)
    return jsonify(resp)

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = get_request_data()
        username = data.get("username")
        password = data.get("password")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT role FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            role = user["role"]
            session["role"] = role

            if request.is_json:
                redirect_url = "/admin" if role == "admin" else "/faculty" if role == "faculty" else "/student"
                return json_response(True, "Login successful", redirect=redirect_url)
            
            if role == "admin":
                return redirect("/admin")
            elif role == "faculty":
                return redirect("/faculty")
            else:
                return redirect("/student")
        
        msg = "Invalid credentials"
        if request.is_json:
            return json_response(False, msg)
        return msg

    return render_template("login.html")

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
@login_required(role="admin")
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()

    cur.execute("SELECT * FROM staff")
    faculty = cur.fetchall()

    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin_dashboard.html", subjects=subjects, faculty=faculty, courses=courses)

# ---------------- ADD SUBJECT ----------------
@app.route("/add_subject", methods=["POST"])
@login_required(role="admin")
def add_subject():
    data = get_request_data()
    code = data.get("code")
    name = data.get("name")
    year = data.get("year")
    course_id = data.get("course_id")
    weekly_hours = data.get("weekly_hours", 4)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO subjects (code, name, year, course_id, weekly_hours)
            VALUES (%s, %s, %s, %s, %s)
        """, (code, name, year, course_id, weekly_hours))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Subject added successfully", redirect="/admin")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- ADD FACULTY ----------------
@app.route("/add_faculty", methods=["POST"])
@login_required(role="admin")
def add_faculty():
    data = get_request_data()
    staff_code = data.get("staff_code")
    name = data.get("name")
    department = data.get("department")
    max_hours = data.get("max_hours", 20)
    subjects = data.get("subjects", []) if request.is_json else request.form.getlist("subjects")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert staff
        cur.execute("""
            INSERT INTO staff (staff_code, name, department, max_hours)
            VALUES (%s, %s, %s, %s)
        """, (staff_code, name, department, max_hours))

        staff_db_id = cur.lastrowid
        conn.commit()

        # Assign subjects
        for subject_id in subjects:
            cur.execute("""
                INSERT INTO staff_subjects (staff_id, subject_id)
                VALUES (%s, %s)
            """, (staff_db_id, subject_id))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Faculty added successfully", redirect="/admin")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- EDIT SUBJECT ----------------
@app.route("/edit_subject/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def edit_subject(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        data = get_request_data()
        name = data.get("name")
        weekly_hours = data.get("weekly_hours")

        try:
            cur.execute("""
                UPDATE subjects
                SET name=%s, weekly_hours=%s
                WHERE id=%s
            """, (name, weekly_hours, id))

            conn.commit()
            cur.close()
            conn.close()

            if request.is_json:
                return json_response(True, "Subject updated", redirect="/admin")
            return redirect("/admin")
        except Exception as e:
            if request.is_json:
                return json_response(False, str(e))
            return str(e), 400

    cur.execute("SELECT * FROM subjects WHERE id=%s", (id,))
    subject = cur.fetchone()

    cur.close()
    conn.close()
    return render_template("edit_subject.html", subject=subject)

# ---------------- DELETE SUBJECT ----------------
@app.route("/delete_subject/<int:id>", methods=["POST"])
@login_required(role="admin")
def delete_subject(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM staff_subjects WHERE subject_id=%s", (id,))
        cur.execute("DELETE FROM subjects WHERE id=%s", (id,))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Subject deleted")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- EDIT FACULTY ----------------
@app.route("/edit_faculty/<int:id>", methods=["GET", "POST"])
@login_required(role="admin")
def edit_faculty(id):
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        data = get_request_data()
        name = data.get("name")
        max_hours = data.get("max_hours")

        try:
            cur.execute("""
                UPDATE staff SET name=%s, max_hours=%s WHERE id=%s
            """, (name, max_hours, id))

            conn.commit()
            cur.close()
            conn.close()

            if request.is_json:
                return json_response(True, "Faculty updated", redirect="/admin")
            return redirect("/admin")
        except Exception as e:
            if request.is_json:
                return json_response(False, str(e))
            return str(e), 400

    cur.execute("SELECT * FROM staff WHERE id=%s", (id,))
    faculty = cur.fetchone()

    cur.execute("SELECT id, code, name FROM subjects")
    subjects = cur.fetchall()

    cur.execute("SELECT subject_id FROM staff_subjects WHERE staff_id=%s", (id,))
    assigned = [s["subject_id"] for s in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty,
        subjects=subjects,
        assigned=assigned
    )

# ---------------- DELETE FACULTY ----------------
@app.route("/delete_faculty/<int:id>", methods=["POST"])
@login_required(role="admin")
def delete_faculty(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM staff_subjects WHERE staff_id=%s", (id,))
        cur.execute("DELETE FROM staff WHERE id=%s", (id,))

        conn.commit()
        cur.close()
        conn.close()

        if request.is_json:
            return json_response(True, "Faculty deleted")
        return redirect("/admin")
    except Exception as e:
        if request.is_json:
            return json_response(False, str(e))
        return str(e), 400

# ---------------- FACULTY WORKLOAD ----------------
@app.route('/view_workload')
@login_required(role="admin")
def view_workload():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM faculty_workload")
    data = cur.fetchall()
    cur.close()
    conn.close()

    if request.is_json:
        return json_response(True, "Workload data", workload=data)
    return render_template('faculty_workload.html', workload=data)

# ----------------STUDENT DASHBOARD ----------------
@app.route("/student")
@login_required(role="student")
def student_dashboard():
    return render_template("student_dashboard.html")

# -------- FACULTY DASHBOARD ----------------
@app.route("/faculty", methods=["GET", "POST"])
@login_required(role="faculty")
def faculty_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM staff")
    staff_list = cur.fetchall()

    schedule = None

    if request.method == "POST":
        staff_id = request.form["staff_id"]
        cur.execute("""
            SELECT t.day, p.period_no, s.code, s.name, t.year, t.course_id
            FROM timetable t
            JOIN subjects s ON t.subject_id = s.id
            JOIN periods p ON t.period_id = p.id
            WHERE t.staff_id = %s
            ORDER BY t.day, p.period_no
        """, (staff_id,))
        schedule = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "faculty_dashboard.html",
        staff_list=staff_list,
        schedule=schedule
    )

# -------- AI TIMETABLE GENERATION --------
@app.route("/generate", methods=["POST"])
@login_required(role="admin")
def generate_timetable():
    data = get_request_data()
    year = data.get("year")
    course_id = data.get("course_id")

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Delete existing timetable
        cur.execute(
            "DELETE FROM timetable WHERE year=%s AND course_id=%s",
            (year, course_id)
        )

        # Get subjects for that year & course
        cur.execute("""
            SELECT s.id, s.weekly_hours
            FROM subjects s
            WHERE s.year=%s AND s.course_id=%s
        """, (year, course_id))
        subjects = cur.fetchall()

        # Get staff assignments
        cur.execute("""
            SELECT ss.staff_id, ss.subject_id
            FROM staff_subjects ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.year=%s AND s.course_id=%s
        """, (year, course_id))
        assignments = cur.fetchall()

        # Check if there are assignments
        if not assignments:
            cur.close()
            conn.close()
            if request.is_json:
                return json_response(False, "No staff assigned to subjects for this year and course")
            return "Error: No staff assigned to subjects for this year and course. Please assign faculty to subjects first.", 400

        # Get period IDs mapped to period numbers
        cur.execute("SELECT id, period_no FROM periods ORDER BY period_no")
        period_map = {int(p["period_no"]): p["id"] for p in cur.fetchall()}

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        period_nos = sorted(period_map.keys())

        staff_busy = {}
        room_busy = {}

        # Get available classrooms
        cur.execute("SELECT id FROM classrooms")
        rooms = [r["id"] for r in cur.fetchall()]
        if not rooms:
            rooms = [1]

        random.shuffle(assignments)
        placed_count = 0

        for assignment in assignments:
            subject_id = assignment["subject_id"]
            staff_id = assignment["staff_id"]
            placed = False
            random.shuffle(days)

            for day in days:
                random.shuffle(period_nos)
                for period_no in period_nos:
                    if (staff_id, day, period_no) in staff_busy:
                        continue
                    room = rooms[0] if rooms else 1
                    if (room, day, period_no) in room_busy:
                        continue

                    period_id = period_map[period_no]
                    cur.execute("""
                        INSERT INTO timetable
                        (day, period_id, subject_id, staff_id, classroom_id, year, course_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (day, period_id, subject_id, staff_id, room, year, course_id))

                    staff_busy[(staff_id, day, period_no)] = True
                    room_busy[(room, day, period_no)] = True
                    placed = True
                    placed_count += 1
                    break

                if placed:
                    break

        conn.commit()
        cur.close()
        conn.close()

        redirect_url = f"/view_timetable?year={year}&course_id={course_id}"
        if request.is_json:
            return json_response(True, f"Timetable generated! Placed {placed_count} assignments.", redirect=redirect_url)
        return redirect(redirect_url)

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        if request.is_json:
            return json_response(False, str(e))
        return f"Error generating timetable: {str(e)}", 500

# -------- FETCH TIMETABLE --------
def get_timetable_dict(year, course_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            t.day,
            p.period_no,
            s.code,
            s.name,
            st.name as staff_name
        FROM timetable t
        JOIN subjects s ON t.subject_id = s.id
        JOIN staff st ON t.staff_id = st.id
        JOIN periods p ON t.period_id = p.id
        WHERE t.year=%s AND t.course_id=%s
        ORDER BY t.day, p.period_no
    """, (year, course_id))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    timetable = {
        "Monday": [""] * 7,
        "Tuesday": [""] * 7,
        "Wednesday": [""] * 7,
        "Thursday": [""] * 7,
        "Friday": [""] * 7
    }

    for row in rows:
        day = row["day"]
        period_no = row["period_no"]
        code = row["code"]
        name = row["name"]
        staff = row["staff_name"]
        timetable[day][period_no - 1] = (
            f"<b>{code}</b><br>"
            f"<small>{name}</small><br>"
            f"<small>{staff}</small>"
        )

    return timetable

# -------- VIEW TIMETABLE --------
@app.route("/view_timetable")
@login_required()
def view_timetable():
    year = request.args.get("year")
    course_id = request.args.get("course_id")

    timetable = get_timetable_dict(year, course_id)

    return render_template(
        "timetable_view.html",
        timetable=timetable,
        year=year,
        course_id=course_id
    )

# -------- PRINT --------
@app.route("/print")
@login_required()
def print_timetable():
    year = request.args.get("year")
    course_id = request.args.get("course_id")

    timetable = get_timetable_dict(year, course_id)

    return render_template(
        "timetable_print.html",
        timetable=timetable,
        year=year,
        course_id=course_id
    )

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
