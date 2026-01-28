@echo off
REM Start Flask in background and generate timetables

cd /d e:\TTMS

REM Activate venv and start Flask
call .venv\Scripts\activate.bat
start python backend/app.py

REM Wait for Flask to start
timeout /t 3 /nobreak

REM Generate timetables using curl
echo Generating timetables...

curl -X POST http://127.0.0.1:5000/generate_timetable -H "Content-Type: application/json" -d "{\"year\":\"Year I\",\"course_id\":1,\"semester\":\"ODD\"}"
echo Year I, Course 1, Semester ODD

curl -X POST http://127.0.0.1:5000/generate_timetable -H "Content-Type: application/json" -d "{\"year\":\"Year II\",\"course_id\":1,\"semester\":\"ODD\"}"
echo Year II, Course 1, Semester ODD

curl -X POST http://127.0.0.1:5000/generate_timetable -H "Content-Type: application/json" -d "{\"year\":\"Year III\",\"course_id\":1,\"semester\":\"EVEN\"}"
echo Year III, Course 1, Semester EVEN

curl -X POST http://127.0.0.1:5000/generate_timetable -H "Content-Type: application/json" -d "{\"year\":\"Year IV\",\"course_id\":2,\"semester\":\"EVEN\"}"
echo Year IV, Course 2, Semester EVEN

echo.
echo Timetable generation complete!
echo.
echo Access the timetable at: http://127.0.0.1:5000
pause
