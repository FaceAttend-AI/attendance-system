@echo off
color 0A
cls

echo ================================================
echo   FaceAttend - Docker Launcher
echo ================================================
echo.

:MENU
echo  [1] Start All Services (Dashboard + Mobile)
echo  [2] Stop All Services
echo  [3] View Logs
echo  [4] Rebuild Containers
echo  [5] Run Attendance (Local - needs webcam)
echo  [6] Send Email Report (Local)
echo  [7] Open Dashboard in Browser
echo  [8] Exit
echo.
set /p choice="Select option: "

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto LOGS
if "%choice%"=="4" goto REBUILD
if "%choice%"=="5" goto ATTENDANCE
if "%choice%"=="6" goto EMAIL
if "%choice%"=="7" goto BROWSER
if "%choice%"=="8" goto EXIT

:START
echo.
echo [INFO] Starting FaceAttend services...
docker-compose up -d
echo.
echo [OK] Services started!
echo [OK] Dashboard  → http://localhost:8501
echo [OK] Mobile App → http://localhost:5000
echo.
pause
goto MENU

:STOP
echo.
echo [INFO] Stopping all services...
docker-compose down
echo [OK] All stopped.
echo.
pause
goto MENU

:LOGS
echo.
echo [INFO] Showing logs (Ctrl+C to exit)...
docker-compose logs -f
pause
goto MENU

:REBUILD
echo.
echo [INFO] Rebuilding containers (this takes a few minutes)...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo [OK] Rebuild complete!
echo.
pause
goto MENU

:ATTENDANCE
echo.
echo [INFO] Starting attendance system (local)...
cd /d "C:\Users\MANIKANDAN L.R\AttendanceSystem"
"C:\Users\MANIKANDAN L.R\AppData\Local\Programs\Python\Python310\python.exe" attendance.py
pause
goto MENU

:EMAIL
echo.
echo [INFO] Sending email report...
"C:\Users\MANIKANDAN L.R\AppData\Local\Programs\Python\Python310\python.exe" email_report.py
pause
goto MENU

:BROWSER
start http://localhost:8501
goto MENU

:EXIT
exit