@echo off
mode con: cols=120 lines=30
color 08
title Build
cls

title Building...

timeout /t 2 /NOBREAK >nul

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in path.
    color 0c
    pause
    color 07
    title Command Prompt
    exit /b
)


git --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo Git is not installed or not in path.
    pause
    color 07
    title Command Prompt
    exit /b
)
echo.
pip install -r requirements.txt
cls

color 07

choice /c:YN /n /m "? build calculator-tk? (Y/n)"
if %errorlevel% equ 2 (
    echo Exiting builder...
    timeout /t 1 /NOBREAK >nul
    exit /b
) else (
    echo Opening builder...
    timeout /t 1 /NOBREAK >nul
)

python builder.py
if %errorlevel% equ 0 (
    echo Thank you for building our app!
    choice /c:YN /n /m "? open built calculator app? (Y/n)"
    if %errorlevel% neq 2 (
        echo Opening...
        start dist\calculator.exe
    ) else (
        echo Exiting...
        timeout /t 1 /NOBREAK >nul
    )
) else (
    echo.
    echo An error occurred, please report this issue to https://github.com/srpcd/calculator-tk/issues
)

echo.
pause
title Command Prompt
color 07
