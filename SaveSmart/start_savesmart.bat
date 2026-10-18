@echo off
set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=%~dp0..\.venv\Scripts\python.exe"

:menu
echo.
echo SaveSmart
echo 1. Open JavaScript Procedural
echo 2. Run Python OOP
echo 3. Run comparison tests
echo 4. Exit
set /p "choice=Choose an option: "

if "%choice%"=="1" goto javascript
if "%choice%"=="2" goto python
if "%choice%"=="3" goto tests
if "%choice%"=="4" exit /b 0
echo Please choose 1, 2, 3, or 4.
goto menu

:javascript
start "" "%PROJECT_DIR%procedural-js\index.html"
goto menu

:python
if not exist "%PYTHON_EXE%" (
    echo Python virtual environment not found at %PYTHON_EXE%
    echo Install the requirements using the command in README.md.
    pause
    goto menu
)
pushd "%PROJECT_DIR%oop-python"
"%PYTHON_EXE%" app.py
popd
goto menu

:tests
if not exist "%PYTHON_EXE%" (
    echo Python virtual environment not found at %PYTHON_EXE%
    pause
    goto menu
)
"%PYTHON_EXE%" "%PROJECT_DIR%tests\verify_systems.py"
pause
goto menu
