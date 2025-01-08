@echo off
set /p FILEPATH="Bitte den Dateipfad eingeben: "
set FILEPATH=%FILEPATH:"=%
if "%FILEPATH%"=="" (
    echo Es wurde kein Pfad eingegeben. Das Programm wird beendet.
    pause
    exit /b
)
set BAT_DIR=%~dp0
set SCRIPT_PATH=%BAT_DIR%src\ammonit\generator.py
set PYTHON_PATH=
if exist "C:\Users\%USERNAME%\anaconda3\python.exe" set PYTHON_PATH=C:\Users\%USERNAME%\anaconda3\python.exe
if exist "C:\ProgramData\Anaconda3\python.exe" set PYTHON_PATH=C:\ProgramData\Anaconda3\python.exe
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe" set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\python.exe
if exist "C:\Program Files\Python39\python.exe" set PYTHON_PATH=C:\Program Files\Python39\python.exe
if exist "C:\Program Files (x86)\Python39\python.exe" set PYTHON_PATH=C:\Program Files (x86)\Python39\python.exe
if defined PYTHON_PATH (
    echo Python gefunden: %PYTHON_PATH%
    "%PYTHON_PATH%" "%SCRIPT_PATH%" "%FILEPATH%"
) else (
    echo Achtung: Python wurde nicht gefunden.
    echo Stellen Sie sicher, dass Python installiert und die Python-Installation korrekt konfiguriert ist.
)
if %ERRORLEVEL% neq 0 (
    echo Es ist ein Fehler aufgetreten. Fehlercode: %ERRORLEVEL%
    pause
) else (
    echo Das Skript wurde erfolgreich ausgefuehrt.
    pause
)
